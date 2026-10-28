//! GPU sweep: thousands of independent (rule, seed) ants on one CUDA device.
//!
//! Behind the `cuda` cargo feature. Kernels are compiled at run time with NVRTC (no `nvcc`), and
//! `libcuda`/`libnvrtc` are found with `dlopen`, so building needs no CUDA toolkit; running needs
//! `libnvrtc.so.12` on `LD_LIBRARY_PATH` (see `experiments/active/2026-10-gpu-ant-sweep/README.md`).
//!
//! # Contract
//! For every [`Job`], [`GpuSweeper::run`] returns exactly the [`RunResult`] that [`fast::run`] returns
//! for the same rule, step budget, grid size and detection `Config` (blank background), or, when
//! `bg_seed` is `Some(s)`, the same run on a background filled by [`crate::ext::bg_colour`]`(s, ..)`.
//! The result for a job depends only on the job: not on lane count, slice length, scheduling or the
//! other jobs in the batch. `tests/gpu.rs` checks this against the CPU oracles.
//!
//! # How it works
//! * One thread per ant. Each ant's virtual `grid x grid` byte grid is a directory of 64x64 tiles taken
//!   from a global pool on first touch, so thousands of ants fit in VRAM and the escape boundary is
//!   unchanged (a dense 8192^2 grid would be 64 MB per ant).
//! * The kernel only keeps what is cheap in registers: position, heading, bounding box, step count and
//!   the headings of the last `history` steps (2 bits each, in a per-lane ring). The host rebuilds the
//!   position trail backwards from the final state and runs the unchanged [`crate::detect`] code.
//! * Launches are sliced (`slice_steps` per kernel) to stay under the display-driver watchdog. Between
//!   slices the host retires finished lanes, refills them from the job queue and overlaps detection of
//!   the retired jobs with the next slice. Results are stored by job index.
//! * If the tile pool runs dry the lane is retired, its job requeued and the active-lane cap halved; a
//!   job that fails while running alone returns [`GpuError`] rather than a wrong row.

use crate::detect::{MIN_SPAN, exit_confirms, find_highway};
use crate::fast::{RunResult, Stop};
use crate::{DIRS, Rule, Turn};
use cudarc::driver::{
    CudaContext, CudaFunction, CudaSlice, CudaStream, DeviceRepr, LaunchConfig, PushKernelArg, ValidAsZeroBits,
};
use cudarc::nvrtc::{CompileOptions, compile_ptx_with_opts};
use rayon::prelude::*;
use std::collections::VecDeque;
use std::fmt;
use std::sync::Arc;

mod probe;
pub use probe::{GpuProber, PATCH_RADIUS, ProbeConfig, ProbeJob, ProbeStats};

const KERNELS: &str = include_str!("ant.cu");
const TILE_BYTES: usize = 4096;
const TILE_DIM: usize = 64;
/// Lanes retired per `retire_kernel` batch; bounds the staging buffer.
const STAGE_LANES: usize = 1024;
const MAX_COLOURS: usize = 128;

const ST_BUDGET: u32 = 1;
const ST_ESCAPED: u32 = 2;
const ST_OOM: u32 = 3;
const ST_IDLE: u32 = 255;

#[repr(C)]
#[derive(Clone, Copy, Default, Debug)]
struct Lane {
    steps: u64,
    budget: u64,
    bg_seed: u64,
    job: u32,
    status: u32,
    x: i32,
    y: i32,
    minx: i32,
    maxx: i32,
    miny: i32,
    maxy: i32,
    h: u32,
    acc: u32,
    turn: [u32; 4],
    n: u32,
    has_bg: u32,
    pad: [u32; 2],
}
// SAFETY: plain-old-data, layout mirrored in ant.cu (`struct Lane`), all-zero is a valid value.
unsafe impl DeviceRepr for Lane {}
unsafe impl ValidAsZeroBits for Lane {}

#[repr(C)]
#[derive(Clone, Copy, Default, Debug)]
struct Assign {
    budget: u64,
    bg_seed: u64,
    lane: u32,
    job: u32,
    turn: [u32; 4],
    n: u32,
    has_bg: u32,
}
unsafe impl DeviceRepr for Assign {}
unsafe impl ValidAsZeroBits for Assign {}

const _: () = assert!(std::mem::size_of::<Lane>() == 96);
const _: () = assert!(std::mem::size_of::<Assign>() == 48);

/// One ant to run.
#[derive(Clone, Debug)]
pub struct Job {
    pub rule: Rule,
    /// `None`: blank background (the census instrument). `Some(s)`: i.i.d. uniform background colours
    /// from [`crate::ext::bg_colour`] with seed `s`.
    pub bg_seed: Option<u64>,
    pub max_steps: u64,
}

#[derive(Clone, Debug)]
pub struct GpuConfig {
    /// CUDA device ordinal. Note the order can differ from `nvidia-smi`; the name is logged.
    pub device: usize,
    /// Ants resident at once. More lanes hide memory latency; 8k-32k is typical on a 48-SM card.
    pub lanes: usize,
    /// Side of the virtual grid, as in `fast::Grid::new(grid)`.
    pub grid: usize,
    /// Tile pool size in 4 KiB tiles. `None`: all free VRAM minus a safety margin.
    pub pool_tiles: Option<usize>,
    /// Steps per kernel launch (keep each launch well under the ~2 s display watchdog).
    pub slice_steps: u64,
    /// Positions kept for highway detection (`fast::Config::history`).
    pub history: usize,
    /// `fast::Config::max_period`.
    pub max_period: usize,
}

impl Default for GpuConfig {
    fn default() -> GpuConfig {
        GpuConfig {
            device: 0,
            lanes: 8192,
            grid: 8192,
            pool_tiles: None,
            slice_steps: 1 << 20,
            history: 250_000,
            max_period: 50_000,
        }
    }
}

#[derive(Debug)]
pub struct GpuError(pub String);

impl fmt::Display for GpuError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "gpu: {}", self.0)
    }
}
impl std::error::Error for GpuError {}

fn err<E: fmt::Debug>(what: &str) -> impl FnOnce(E) -> GpuError + use<E> {
    let what = what.to_string();
    move |e| GpuError(format!("{what}: {e:?}"))
}

/// Counters from the last [`GpuSweeper::run`], for benchmarking.
#[derive(Clone, Debug, Default)]
pub struct RunStats {
    pub jobs: usize,
    pub total_steps: u64,
    pub launches: usize,
    pub oom_requeues: usize,
    pub wall_secs: f64,
    /// Host time spent rebuilding trails and detecting highways (overlaps the next kernel launch).
    pub host_detect_secs: f64,
    /// Host time blocked waiting for the device after the overlapped work was done.
    pub device_wait_secs: f64,
}

pub struct GpuSweeper {
    pub cfg: GpuConfig,
    pub device_name: String,
    pub pool_tiles: usize,
    pub stats: RunStats,
    stream: Arc<CudaStream>,
    f_step: CudaFunction,
    f_retire: CudaFunction,
    f_assign: CudaFunction,
    dir_w: usize,
    ring_words: usize,
    lanes_dev: CudaSlice<Lane>,
    dirs: CudaSlice<u32>,
    rings: CudaSlice<u32>,
    pool: CudaSlice<u8>,
    freelist: CudaSlice<u32>,
    free_count: CudaSlice<i32>,
    staging: CudaSlice<u32>,
    assign_dev: CudaSlice<Assign>,
    ids_dev: CudaSlice<u32>,
}

impl GpuSweeper {
    pub fn new(cfg: GpuConfig) -> Result<GpuSweeper, GpuError> {
        if cfg.lanes == 0 || cfg.grid < 2 || cfg.slice_steps == 0 {
            return Err(GpuError("lanes, grid and slice_steps must be positive".into()));
        }
        let ctx = CudaContext::new(cfg.device).map_err(err("open device"))?;
        let device_name = ctx.name().map_err(err("device name"))?;
        let ptx = compile_ptx_with_opts(
            KERNELS,
            CompileOptions { arch: Some("sm_89"), ..Default::default() },
        )
        .map_err(err("nvrtc compile"))?;
        let module = ctx.load_module(ptx).map_err(err("load module"))?;
        let get = |n: &str| module.load_function(n).map_err(err(n));
        let (f_step, f_retire, f_assign, f_init) =
            (get("step_kernel")?, get("retire_kernel")?, get("assign_kernel")?, get("init_freelist")?);
        let stream = ctx.default_stream();

        let dir_w = cfg.grid.div_ceil(TILE_DIM);
        let ring_words = cfg.history.div_ceil(16) + 1;
        let lanes = cfg.lanes;
        let stage = STAGE_LANES.min(lanes);
        let fixed_bytes = lanes * (dir_w * dir_w * 4 + ring_words * 4 + std::mem::size_of::<Lane>() + 48 + 4)
            + stage * ring_words * 4;
        let (free, _total) = ctx.mem_get_info().map_err(err("mem_get_info"))?;
        let margin = 256 << 20;
        let budget = free.saturating_sub(fixed_bytes + margin);
        let pool_tiles = match cfg.pool_tiles {
            Some(t) => t,
            None => budget / (TILE_BYTES + 4),
        };
        if pool_tiles == 0 || pool_tiles >= u32::MAX as usize {
            return Err(GpuError(format!(
                "no room for a tile pool ({} MiB free, {} MiB needed for {lanes} lanes): lower lanes or history",
                free >> 20,
                fixed_bytes >> 20
            )));
        }

        let lanes_dev = {
            let mut l = stream.alloc_zeros::<Lane>(lanes).map_err(err("alloc lanes"))?;
            let idle = vec![Lane { status: ST_IDLE, ..Lane::default() }; lanes];
            stream.memcpy_htod(&idle, &mut l).map_err(err("init lanes"))?;
            l
        };
        let dirs = stream.alloc_zeros::<u32>(lanes * dir_w * dir_w).map_err(err("alloc dirs"))?;
        let rings = stream.alloc_zeros::<u32>(lanes * ring_words).map_err(err("alloc rings"))?;
        let pool = stream.alloc_zeros::<u8>(pool_tiles * TILE_BYTES).map_err(err("alloc pool"))?;
        let mut freelist = stream.alloc_zeros::<u32>(pool_tiles).map_err(err("alloc freelist"))?;
        let mut free_count = stream.alloc_zeros::<i32>(1).map_err(err("alloc free_count"))?;
        stream.memcpy_htod(&[pool_tiles as i32], &mut free_count).map_err(err("init free_count"))?;
        let staging = stream.alloc_zeros::<u32>(stage * ring_words).map_err(err("alloc staging"))?;
        let assign_dev = stream.alloc_zeros::<Assign>(lanes).map_err(err("alloc assign"))?;
        let ids_dev = stream.alloc_zeros::<u32>(stage).map_err(err("alloc ids"))?;
        let n = pool_tiles as u32;
        let mut b = stream.launch_builder(&f_init);
        b.arg(&mut freelist).arg(&n);
        // SAFETY: argument types match `init_freelist(unsigned*, unsigned)`.
        unsafe { b.launch(LaunchConfig::for_num_elems(n)) }.map_err(err("init freelist"))?;
        stream.synchronize().map_err(err("sync"))?;

        Ok(GpuSweeper {
            cfg,
            device_name,
            pool_tiles,
            stats: RunStats::default(),
            stream,
            f_step,
            f_retire,
            f_assign,
            dir_w,
            ring_words,
            lanes_dev,
            dirs,
            rings,
            pool,
            freelist,
            free_count,
            staging,
            assign_dev,
            ids_dev,
        })
    }

    /// Run every job; `results[i]` belongs to `jobs[i]`. `progress` is called with the number of
    /// finished jobs after each batch.
    pub fn run(&mut self, jobs: &[Job], mut progress: impl FnMut(usize)) -> Result<Vec<RunResult>, GpuError> {
        for (i, j) in jobs.iter().enumerate() {
            let n = j.rule.len();
            if !(1..=MAX_COLOURS).contains(&n) {
                return Err(GpuError(format!("job {i}: {n} colours (supported: 1..={MAX_COLOURS})")));
            }
        }
        let t0 = std::time::Instant::now();
        let lanes = self.cfg.lanes;
        let mut results: Vec<Option<RunResult>> = vec![None; jobs.len()];
        let mut queue: VecDeque<usize> = (0..jobs.len()).collect();
        let mut lane_job: Vec<Option<usize>> = vec![None; lanes];
        let mut free_lanes: Vec<usize> = (0..lanes).rev().collect();
        let mut active = 0usize;
        let mut max_active = lanes;
        let mut host_lanes = vec![Lane::default(); lanes];
        let mut pending: Option<Harvest> = None;
        let mut done = 0usize;
        let mut stats = RunStats { jobs: jobs.len(), ..RunStats::default() };
        let (size, history, max_period) = (self.cfg.grid, self.cfg.history, self.cfg.max_period);

        loop {
            // Hand queued jobs to idle lanes.
            let mut recs: Vec<Assign> = Vec::new();
            while active < max_active {
                let Some(&job) = queue.front() else { break };
                let Some(lane) = free_lanes.pop() else { break };
                queue.pop_front();
                let j = &jobs[job];
                let mut turn = [0u32; 4];
                for (k, t) in j.rule.0.iter().enumerate() {
                    if *t == Turn::R {
                        turn[k / 32] |= 1 << (k % 32);
                    }
                }
                recs.push(Assign {
                    budget: j.max_steps,
                    bg_seed: j.bg_seed.unwrap_or(0),
                    lane: lane as u32,
                    job: job as u32,
                    turn,
                    n: j.rule.len() as u32,
                    has_bg: j.bg_seed.is_some() as u32,
                });
                lane_job[lane] = Some(job);
                active += 1;
            }
            if !recs.is_empty() {
                let mut dst = self.assign_dev.slice_mut(0..recs.len());
                self.stream.memcpy_htod(&recs, &mut dst).map_err(err("upload jobs"))?;
                let k = recs.len() as i32;
                let mut b = self.stream.launch_builder(&self.f_assign);
                let sz = size as u32;
                b.arg(&mut self.lanes_dev).arg(&self.assign_dev).arg(&k).arg(&sz);
                // SAFETY: matches `assign_kernel(Lane*, const Assign*, int, unsigned)`.
                unsafe { b.launch(LaunchConfig::for_num_elems(k as u32)) }.map_err(err("assign"))?;
            }
            if active == 0 {
                if let Some(h) = pending.take() {
                    let t = std::time::Instant::now();
                    done += h.finish_into(&mut results, size, history, max_period);
                    stats.host_detect_secs += t.elapsed().as_secs_f64();
                    progress(done);
                }
                break;
            }

            let active_at_launch = active;
            {
                let nl = lanes as i32;
                let (sz, dw, rw, slice) =
                    (size as u32, self.dir_w as u32, self.ring_words as u32, self.cfg.slice_steps);
                let mut b = self.stream.launch_builder(&self.f_step);
                b.arg(&mut self.lanes_dev)
                    .arg(&nl)
                    .arg(&mut self.dirs)
                    .arg(&mut self.pool)
                    .arg(&self.freelist)
                    .arg(&mut self.free_count)
                    .arg(&mut self.rings)
                    .arg(&sz)
                    .arg(&dw)
                    .arg(&rw)
                    .arg(&slice);
                let cfg = LaunchConfig { grid_dim: ((lanes as u32).div_ceil(128), 1, 1), block_dim: (128, 1, 1), shared_mem_bytes: 0 };
                // SAFETY: matches `step_kernel(...)` in ant.cu argument for argument.
                unsafe { b.launch(cfg) }.map_err(err("step"))?;
                stats.launches += 1;
            }

            // The kernel is running: detect the previous batch on the CPU meanwhile.
            if let Some(h) = pending.take() {
                let t = std::time::Instant::now();
                done += h.finish_into(&mut results, size, history, max_period);
                stats.host_detect_secs += t.elapsed().as_secs_f64();
                progress(done);
            }

            let t = std::time::Instant::now();
            self.stream.memcpy_dtoh(&self.lanes_dev, &mut host_lanes).map_err(err("download lanes"))?;
            stats.device_wait_secs += t.elapsed().as_secs_f64();
            let finished: Vec<usize> = (0..lanes)
                .filter(|&l| lane_job[l].is_some() && (ST_BUDGET..=ST_OOM).contains(&host_lanes[l].status))
                .collect();
            if finished.is_empty() {
                continue;
            }
            let mut harvest = Harvest::default();
            let mut oom_jobs = Vec::new();
            for chunk in finished.chunks(STAGE_LANES.min(lanes)) {
                let ids: Vec<u32> = chunk.iter().map(|&l| l as u32).collect();
                let mut dst = self.ids_dev.slice_mut(0..ids.len());
                self.stream.memcpy_htod(&ids, &mut dst).map_err(err("upload ids"))?;
                let (de, rw) = ((self.dir_w * self.dir_w) as u32, self.ring_words as u32);
                let mut b = self.stream.launch_builder(&self.f_retire);
                b.arg(&mut self.lanes_dev)
                    .arg(&self.ids_dev)
                    .arg(&mut self.dirs)
                    .arg(&mut self.pool)
                    .arg(&mut self.freelist)
                    .arg(&mut self.free_count)
                    .arg(&self.rings)
                    .arg(&mut self.staging)
                    .arg(&de)
                    .arg(&rw);
                let cfg = LaunchConfig { grid_dim: (ids.len() as u32, 1, 1), block_dim: (256, 1, 1), shared_mem_bytes: 0 };
                // SAFETY: matches `retire_kernel(...)` in ant.cu.
                unsafe { b.launch(cfg) }.map_err(err("retire"))?;
                let mut ring_host = vec![0u32; ids.len() * self.ring_words];
                let src = self.staging.slice(0..ring_host.len());
                self.stream.memcpy_dtoh(&src, &mut ring_host).map_err(err("download rings"))?;
                for (i, &l) in chunk.iter().enumerate() {
                    let job = lane_job[l].take().expect("finished lane has a job");
                    let lane = host_lanes[l];
                    free_lanes.push(l);
                    active -= 1;
                    if lane.status == ST_OOM {
                        oom_jobs.push(job);
                    } else {
                        harvest.jobs.push(job);
                        harvest.lanes.push(lane);
                        harvest.rings.extend_from_slice(&ring_host[i * self.ring_words..(i + 1) * self.ring_words]);
                    }
                }
            }
            if !oom_jobs.is_empty() {
                if active_at_launch == 1 {
                    return Err(GpuError(format!(
                        "job {} ({}) needs more than the whole tile pool ({} tiles = {} MiB); raise pool_tiles or lower grid",
                        oom_jobs[0],
                        jobs[oom_jobs[0]].rule,
                        self.pool_tiles,
                        self.pool_tiles * TILE_BYTES >> 20
                    )));
                }
                stats.oom_requeues += oom_jobs.len();
                max_active = (active_at_launch / 2).max(1);
                for j in oom_jobs.into_iter().rev() {
                    queue.push_front(j);
                }
            }
            pending = Some(harvest);
        }
        self.stream.synchronize().map_err(err("sync"))?;
        stats.wall_secs = t0.elapsed().as_secs_f64();
        let out: Vec<RunResult> = results
            .into_iter()
            .map(|r| r.expect("every job produced a result"))
            .collect();
        stats.total_steps = out.iter().map(|r| r.steps).sum();
        self.stats = stats;
        Ok(out)
    }
}

/// Finished jobs waiting for host-side detection.
#[derive(Default)]
struct Harvest {
    jobs: Vec<usize>,
    lanes: Vec<Lane>,
    /// `ring_words` words per entry, concatenated.
    rings: Vec<u32>,
}

impl Harvest {
    fn finish_into(self, out: &mut [Option<RunResult>], size: usize, history: usize, max_period: usize) -> usize {
        if self.jobs.is_empty() {
            return 0;
        }
        let rw = self.rings.len() / self.jobs.len();
        let res: Vec<RunResult> = (0..self.jobs.len())
            .into_par_iter()
            .map(|i| finish(&self.lanes[i], &self.rings[i * rw..(i + 1) * rw], size, history, max_period))
            .collect();
        let n = res.len();
        for (job, r) in self.jobs.into_iter().zip(res) {
            out[job] = Some(r);
        }
        n
    }
}

/// Rebuild the trail from the heading ring and classify it exactly as `fast::run` does.
fn finish(lane: &Lane, ring: &[u32], size: usize, history: usize, max_period: usize) -> RunResult {
    let c = (size / 2) as i32;
    let steps = lane.steps;
    let stop = if lane.status == ST_ESCAPED { Stop::Escaped } else { Stop::Budget };
    let h = lane.h as u8;
    let heading_of = |s: u64| -> usize {
        let w = ring[(((s - 1) >> 4) % ring.len() as u64) as usize];
        ((w >> (2 * ((s - 1) & 15))) & 3) as usize
    };
    // Trail = positions at times 0..=last_t, last `history` of them (fast::Trail). Position p_t is
    // reached by step t, so p_{t-1} = p_t - DIRS[heading of step t].
    let last_t = if stop == Stop::Escaped { steps - 1 } else { steps };
    let len = (history as u64).min(last_t + 1) as usize;
    let mut p = (lane.x - c, lane.y - c);
    if stop == Stop::Escaped {
        let d = DIRS[heading_of(steps)];
        p = (p.0 - d.0, p.1 - d.1);
    }
    let mut trail = vec![(0i32, 0i32); len];
    trail[len - 1] = p;
    for k in (0..len - 1).rev() {
        let t = last_t - (len - 1 - (k + 1)) as u64; // time of trail[k + 1]
        let d = DIRS[heading_of(t)];
        p = (p.0 - d.0, p.1 - d.1);
        trail[k] = p;
    }
    let periodic_tail = find_highway(&trail, max_period, MIN_SPAN);
    let highway = if stop == Stop::Escaped {
        periodic_tail.or_else(|| find_highway(&trail, max_period, 2_000)).filter(|&hw| exit_confirms(hw, h))
    } else {
        None
    };
    RunResult {
        steps,
        stop,
        pos: (lane.x - c, lane.y - c),
        heading: h,
        highway,
        periodic_tail,
        extent: ((lane.maxx - lane.minx + 1) as u32, (lane.maxy - lane.miny + 1) as u32),
    }
}
