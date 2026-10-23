//! Native GPU census sweeps through wgpu. macOS uses Metal; other native
//! platforms use Vulkan or DX12. Enable the optional `wgpu` Cargo feature.
//!
//! Each invocation runs one independent ant. Sparse tiles keep memory use
//! proportional to the cells reached. Blank runs match [`crate::fast::run`].
//! Seeded runs use [`crate::ext::bg_colour`] with the same bounded escape and
//! CPU highway detection.

use bytemuck::{Pod, Zeroable};
use rayon::prelude::*;
use std::collections::VecDeque;
use std::fmt;
use wgpu::util::DeviceExt;

use crate::detect::{MIN_SPAN, exit_confirms, find_highway};
use crate::fast::{RunResult, Stop};
use crate::{DIRS, Rule, Turn};

const TILE_DIM: usize = 64;
const TILE_BYTES: u64 = 4096;
const WORKGROUP: u32 = 64;
const IDLE: u32 = 255;
const BUDGET: u32 = 1;
const ESCAPED: u32 = 2;
const OOM: u32 = 3;
const SHADER: &str = include_str!("ant.wgsl");

/// One independent ant, with an optional deterministic random background.
#[derive(Clone, Debug)]
pub struct Job {
    pub rule: Rule,
    pub bg_seed: Option<u64>,
    pub max_steps: u64,
}

/// Buffer sizes and scheduling controls. These do not change a job's result.
#[derive(Clone, Debug)]
pub struct GpuConfig {
    /// Adapter ordinal among native hardware adapters.
    pub device: usize,
    /// Maximum number of resident ants.
    pub lanes: usize,
    /// Side of the bounded square board.
    pub grid: usize,
    /// Shared pool of 64-by-64 byte tiles. Exhaustion retries fewer ants.
    pub pool_tiles: usize,
    /// Steps per dispatch. Keep slices short on a GPU that drives a display.
    pub slice_steps: u32,
    /// Recent positions used for highway detection.
    pub history: usize,
    pub max_period: usize,
}

impl Default for GpuConfig {
    fn default() -> Self {
        Self {
            device: 0,
            lanes: 1024,
            grid: 8192,
            pool_tiles: 65_536,
            slice_steps: 65_536,
            history: 250_000,
            max_period: 50_000,
        }
    }
}

/// Counters for the last successful batch. No hardware speedup is implied.
#[derive(Clone, Debug, Default)]
pub struct RunStats {
    pub jobs: usize,
    pub total_steps: u64,
    pub launches: usize,
    pub oom_requeues: usize,
}

/// A configuration, adapter, allocation or GPU execution error.
#[derive(Debug)]
pub struct GpuError(pub String);

impl fmt::Display for GpuError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "wgpu: {}", self.0)
    }
}

impl std::error::Error for GpuError {}

fn error(context: &str, cause: impl fmt::Display) -> GpuError {
    GpuError(format!("{context}: {cause}"))
}

// Field offsets and the 96-byte stride match Lane in ant.wgsl.
#[repr(C)]
#[derive(Clone, Copy, Debug, Default, Pod, Zeroable)]
struct Lane {
    steps: [u32; 2],
    budget: [u32; 2],
    seed: [u32; 2],
    status: u32,
    n: u32,
    x: i32,
    y: i32,
    minx: i32,
    maxx: i32,
    miny: i32,
    maxy: i32,
    heading: u32,
    acc: u32,
    turn: [u32; 4],
    has_bg: u32,
    ring_cursor: u32,
    padding: [u32; 2],
}

const _: () = assert!(size_of::<Lane>() == 96);

fn words(value: u64) -> [u32; 2] {
    [value as u32, (value >> 32) as u32]
}

impl Lane {
    fn new(job: &Job, grid: usize) -> Self {
        let c = (grid / 2) as i32;
        let mut turn = [0; 4];

        for (i, t) in job.rule.0.iter().enumerate() {
            if *t == Turn::R {
                turn[i / 32] |= 1 << (i % 32);
            }
        }

        Self {
            budget: words(job.max_steps),
            seed: words(job.bg_seed.unwrap_or(0)),
            n: job.rule.len() as u32,
            x: c,
            y: c,
            minx: c,
            maxx: c,
            miny: c,
            maxy: c,
            turn,
            has_bg: u32::from(job.bg_seed.is_some()),
            ..Self::default()
        }
    }

    fn steps(self) -> u64 {
        self.steps[0] as u64 | ((self.steps[1] as u64) << 32)
    }
}

#[repr(C)]
#[derive(Clone, Copy, Pod, Zeroable)]
struct Params {
    grid: u32,
    dir_w: u32,
    ring_words: u32,
    lanes: u32,
    slice_steps: u32,
    retire_count: u32,
    pool_tiles: u32,
    padding: u32,
}

/// Reusable native GPU buffers and pipelines. Construction requires hardware;
/// missing adapters return an error instead of falling back to CPU execution.
pub struct GpuSweeper {
    cfg: GpuConfig,
    pub device_name: String,
    pub backend: wgpu::Backend,
    pub stats: RunStats,
    device: wgpu::Device,
    queue: wgpu::Queue,
    params: Params,
    params_buffer: wgpu::Buffer,
    states: wgpu::Buffer,
    dirs: wgpu::Buffer,
    pool: wgpu::Buffer,
    free_count: wgpu::Buffer,
    rings: wgpu::Buffer,
    retired: wgpu::Buffer,
    state_readback: wgpu::Buffer,
    ring_readback: wgpu::Buffer,
    bindings: wgpu::BindGroup,
    init_pipeline: wgpu::ComputePipeline,
    step_pipeline: wgpu::ComputePipeline,
    retire_pipeline: wgpu::ComputePipeline,
}

impl GpuSweeper {
    /// Create a sweeper. Returns an error for invalid sizes, unsupported
    /// adapters, shader validation failures or allocation failures.
    pub fn new(cfg: GpuConfig) -> Result<Self, GpuError> {
        validate_config(&cfg)?;
        let backends = if cfg!(target_os = "macos") {
            wgpu::Backends::METAL
        } else {
            wgpu::Backends::PRIMARY
        };
        let instance = wgpu::Instance::new(wgpu::InstanceDescriptor {
            backends,
            ..wgpu::InstanceDescriptor::new_without_display_handle()
        });
        let adapter = pollster::block_on(instance.enumerate_adapters(backends))
            .into_iter()
            .filter(|a| !matches!(a.get_info().device_type, wgpu::DeviceType::Cpu))
            .nth(cfg.device)
            .ok_or_else(|| {
                GpuError(format!(
                    "no native GPU adapter {} available ({backends:?})",
                    cfg.device
                ))
            })?;
        let info = adapter.get_info();
        let limits = adapter.limits();
        let params = Params {
            grid: cfg.grid as u32,
            dir_w: cfg.grid.div_ceil(TILE_DIM) as u32,
            ring_words: (cfg.history.div_ceil(16) + 1) as u32,
            lanes: cfg.lanes as u32,
            slice_steps: cfg.slice_steps,
            retire_count: 0,
            pool_tiles: cfg.pool_tiles as u32,
            padding: 0,
        };
        let lane_bytes = cfg.lanes as u64 * size_of::<Lane>() as u64;
        let dir_bytes = cfg.lanes as u64 * (params.dir_w as u64).pow(2) * 4;
        let ring_bytes = cfg.lanes as u64 * params.ring_words as u64 * 4;
        let pool_bytes = cfg.pool_tiles as u64 * TILE_BYTES;

        for (name, bytes) in [
            ("lanes", lane_bytes),
            ("directory", dir_bytes),
            ("history", ring_bytes),
            ("tile pool", pool_bytes),
        ] {
            if bytes > limits.max_storage_buffer_binding_size as u64
                || bytes > limits.max_buffer_size
            {
                return Err(GpuError(format!(
                    "{name} needs {bytes} bytes; adapter binding limit is {} and buffer limit is {}; lower lanes, grid, history or pool_tiles",
                    limits.max_storage_buffer_binding_size, limits.max_buffer_size
                )));
            }
        }

        if limits.max_storage_buffers_per_shader_stage < 7
            || cfg.lanes as u64 > limits.max_compute_workgroups_per_dimension as u64
        {
            return Err(GpuError(
                "adapter has insufficient compute limits for this lane count".into(),
            ));
        }

        let (device, queue) = pollster::block_on(adapter.request_device(&wgpu::DeviceDescriptor {
            label: Some("turmite compute"),
            required_limits: limits,
            ..Default::default()
        }))
        .map_err(|e| error("request device", e))?;
        let validation = device.push_error_scope(wgpu::ErrorFilter::Validation);
        let allocation = device.push_error_scope(wgpu::ErrorFilter::OutOfMemory);
        let storage = |label, size| {
            device.create_buffer(&wgpu::BufferDescriptor {
                label: Some(label),
                size,
                usage: wgpu::BufferUsages::STORAGE
                    | wgpu::BufferUsages::COPY_SRC
                    | wgpu::BufferUsages::COPY_DST,
                mapped_at_creation: false,
            })
        };
        let readback = |label, size| {
            device.create_buffer(&wgpu::BufferDescriptor {
                label: Some(label),
                size,
                usage: wgpu::BufferUsages::MAP_READ | wgpu::BufferUsages::COPY_DST,
                mapped_at_creation: false,
            })
        };
        let params_buffer = device.create_buffer_init(&wgpu::util::BufferInitDescriptor {
            label: Some("parameters"),
            contents: bytemuck::bytes_of(&params),
            usage: wgpu::BufferUsages::UNIFORM | wgpu::BufferUsages::COPY_DST,
        });
        let states = storage("ant states", lane_bytes);
        let dirs = storage("tile directories", dir_bytes);
        let pool = storage("packed cells", pool_bytes);
        let freelist = storage("tile free list", cfg.pool_tiles as u64 * 4);
        let free_count = storage("free tile count", 4);
        let rings = storage("heading history", ring_bytes);
        let retired = storage("retired lanes", cfg.lanes as u64 * 4);
        let state_readback = readback("state readback", lane_bytes);
        let ring_readback = readback("history readback", ring_bytes);
        let layout = device.create_bind_group_layout(&wgpu::BindGroupLayoutDescriptor {
            label: Some("ant buffers"),
            entries: &(0..8)
                .map(|binding| wgpu::BindGroupLayoutEntry {
                    binding,
                    visibility: wgpu::ShaderStages::COMPUTE,
                    ty: wgpu::BindingType::Buffer {
                        ty: if binding == 0 {
                            wgpu::BufferBindingType::Uniform
                        } else {
                            wgpu::BufferBindingType::Storage {
                                read_only: binding == 7,
                            }
                        },
                        has_dynamic_offset: false,
                        min_binding_size: None,
                    },
                    count: None,
                })
                .collect::<Vec<_>>(),
        });
        let buffers = [
            &params_buffer,
            &states,
            &dirs,
            &pool,
            &freelist,
            &free_count,
            &rings,
            &retired,
        ];
        let bindings = device.create_bind_group(&wgpu::BindGroupDescriptor {
            label: Some("ant buffers"),
            layout: &layout,
            entries: &buffers
                .iter()
                .enumerate()
                .map(|(i, buffer)| wgpu::BindGroupEntry {
                    binding: i as u32,
                    resource: buffer.as_entire_binding(),
                })
                .collect::<Vec<_>>(),
        });
        let pipeline_layout = device.create_pipeline_layout(&wgpu::PipelineLayoutDescriptor {
            label: Some("ant compute"),
            bind_group_layouts: &[Some(&layout)],
            ..Default::default()
        });
        let shader = device.create_shader_module(wgpu::ShaderModuleDescriptor {
            label: Some("ant WGSL"),
            source: wgpu::ShaderSource::Wgsl(SHADER.into()),
        });
        let pipeline = |entry| {
            device.create_compute_pipeline(&wgpu::ComputePipelineDescriptor {
                label: Some(entry),
                layout: Some(&pipeline_layout),
                module: &shader,
                entry_point: Some(entry),
                compilation_options: Default::default(),
                cache: None,
            })
        };
        let init_pipeline = pipeline("init_pool");
        let step_pipeline = pipeline("step");
        let retire_pipeline = pipeline("retire");

        if let Some(e) = pollster::block_on(allocation.pop()) {
            return Err(error("allocate buffers", e));
        }
        if let Some(e) = pollster::block_on(validation.pop()) {
            return Err(error("validate compute pipeline", e));
        }

        Ok(Self {
            cfg,
            device_name: info.name,
            backend: info.backend,
            stats: RunStats::default(),
            device,
            queue,
            params,
            params_buffer,
            states,
            dirs,
            pool,
            free_count,
            rings,
            retired,
            state_readback,
            ring_readback,
            bindings,
            init_pipeline,
            step_pipeline,
            retire_pipeline,
        })
    }

    /// The immutable configuration used to allocate the buffers.
    pub fn config(&self) -> &GpuConfig {
        &self.cfg
    }

    fn dispatch(
        &self,
        encoder: &mut wgpu::CommandEncoder,
        pipeline: &wgpu::ComputePipeline,
        groups: u32,
    ) {
        let mut pass = encoder.begin_compute_pass(&wgpu::ComputePassDescriptor::default());
        pass.set_pipeline(pipeline);
        pass.set_bind_group(0, &self.bindings, &[]);
        pass.dispatch_workgroups(groups, 1, 1);
    }

    fn reset(&self) {
        let idle = vec![
            Lane {
                status: IDLE,
                ..Lane::default()
            };
            self.cfg.lanes
        ];
        self.queue
            .write_buffer(&self.states, 0, bytemuck::cast_slice(&idle));
        self.queue.write_buffer(
            &self.free_count,
            0,
            bytemuck::bytes_of(&(self.cfg.pool_tiles as i32)),
        );
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());
        encoder.clear_buffer(&self.dirs, 0, None);
        encoder.clear_buffer(&self.pool, 0, None);
        self.dispatch(
            &mut encoder,
            &self.init_pipeline,
            (self.cfg.pool_tiles as u32).div_ceil(WORKGROUP),
        );
        self.queue.submit([encoder.finish()]);
    }

    fn read<T: Pod>(&self, buffer: &wgpu::Buffer, bytes: u64) -> Result<Vec<T>, GpuError> {
        let (tx, rx) = std::sync::mpsc::channel();
        let slice = buffer.slice(..bytes);
        slice.map_async(wgpu::MapMode::Read, move |result| {
            let _ = tx.send(result);
        });
        self.device
            .poll(wgpu::PollType::wait_indefinitely())
            .map_err(|e| error("wait for GPU", e))?;
        rx.recv()
            .map_err(|e| error("readback callback", e))?
            .map_err(|e| error("map readback", e))?;
        let mapped = slice
            .get_mapped_range()
            .map_err(|e| error("read mapped range", e))?;
        let values = mapped
            .chunks_exact(size_of::<T>())
            .map(bytemuck::pod_read_unaligned)
            .collect();
        drop(mapped);
        buffer.unmap();
        Ok(values)
    }

    fn advance(&self) -> Result<Vec<Lane>, GpuError> {
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());
        self.dispatch(
            &mut encoder,
            &self.step_pipeline,
            (self.cfg.lanes as u32).div_ceil(WORKGROUP),
        );
        encoder.copy_buffer_to_buffer(&self.states, 0, &self.state_readback, 0, self.states.size());
        self.queue.submit([encoder.finish()]);
        self.read(&self.state_readback, self.states.size())
    }

    fn retire(&mut self, finished: &[usize]) -> Result<Vec<u32>, GpuError> {
        let ids = finished.iter().map(|&l| l as u32).collect::<Vec<_>>();
        self.params.retire_count = ids.len() as u32;
        self.queue
            .write_buffer(&self.params_buffer, 0, bytemuck::bytes_of(&self.params));
        self.queue
            .write_buffer(&self.retired, 0, bytemuck::cast_slice(&ids));
        let mut encoder = self
            .device
            .create_command_encoder(&wgpu::CommandEncoderDescriptor::default());
        let ring_bytes = self.params.ring_words as u64 * 4;

        for (i, &lane) in finished.iter().enumerate() {
            encoder.copy_buffer_to_buffer(
                &self.rings,
                lane as u64 * ring_bytes,
                &self.ring_readback,
                i as u64 * ring_bytes,
                ring_bytes,
            );
        }

        self.dispatch(&mut encoder, &self.retire_pipeline, ids.len() as u32);
        self.queue.submit([encoder.finish()]);
        self.read(&self.ring_readback, ids.len() as u64 * ring_bytes)
    }

    /// Run a batch in input order. Results do not depend on scheduling or pool
    /// retries. Progress reports completed jobs, excluding discarded retries.
    /// A later call resets all device state, including after a failed batch.
    pub fn run(
        &mut self,
        jobs: &[Job],
        mut progress: impl FnMut(usize),
    ) -> Result<Vec<RunResult>, GpuError> {
        self.stats = RunStats::default();

        for (i, job) in jobs.iter().enumerate() {
            if !(1..=128).contains(&job.rule.len()) {
                return Err(GpuError(format!(
                    "job {i}: supported colour count is 1..=128"
                )));
            }
        }

        if jobs.is_empty() {
            return Ok(Vec::new());
        }

        self.reset();
        let mut results = vec![None; jobs.len()];
        let mut pending = (0..jobs.len()).collect::<VecDeque<_>>();
        let mut lane_jobs = vec![None; self.cfg.lanes];
        let mut free_lanes = (0..self.cfg.lanes).rev().collect::<Vec<_>>();
        let mut active = 0;
        let mut max_active = self.cfg.lanes;
        let mut done = 0;
        let mut stats = RunStats {
            jobs: jobs.len(),
            ..RunStats::default()
        };

        while done < jobs.len() {
            while active < max_active {
                let Some(&job) = pending.front() else { break };
                let Some(lane) = free_lanes.pop() else { break };
                pending.pop_front();
                let state = Lane::new(&jobs[job], self.cfg.grid);
                self.queue.write_buffer(
                    &self.states,
                    (lane * size_of::<Lane>()) as u64,
                    bytemuck::bytes_of(&state),
                );
                lane_jobs[lane] = Some(job);
                active += 1;
            }

            let active_at_launch = active;
            let states = self.advance()?;
            stats.launches += 1;
            let finished = (0..self.cfg.lanes)
                .filter(|&l| lane_jobs[l].is_some() && (BUDGET..=OOM).contains(&states[l].status))
                .collect::<Vec<_>>();

            if finished.is_empty() {
                continue;
            }

            let rings = self.retire(&finished)?;
            let ring_words = self.params.ring_words as usize;
            let mut completed = Vec::new();
            let mut retries = Vec::new();

            for (i, &lane) in finished.iter().enumerate() {
                let job = lane_jobs[lane]
                    .take()
                    .ok_or_else(|| GpuError("finished lane has no job".into()))?;
                let idle = Lane {
                    status: IDLE,
                    ..Lane::default()
                };
                self.queue.write_buffer(
                    &self.states,
                    (lane * size_of::<Lane>()) as u64,
                    bytemuck::bytes_of(&idle),
                );
                free_lanes.push(lane);
                active -= 1;

                if states[lane].status == OOM {
                    if active_at_launch == 1 {
                        return Err(GpuError(format!(
                            "job {job} ({}) exceeds the tile pool ({} tiles); increase pool_tiles",
                            jobs[job].rule, self.cfg.pool_tiles
                        )));
                    }
                    retries.push(job);
                } else {
                    completed.push((job, states[lane], i));
                }
            }

            if !retries.is_empty() {
                stats.oom_requeues += retries.len();
                max_active = (active_at_launch / 2).max(1);

                for job in retries.into_iter().rev() {
                    pending.push_front(job);
                }
            }

            let finished_results = completed
                .par_iter()
                .map(|&(job, state, i)| {
                    (
                        job,
                        finish(
                            state,
                            &rings[i * ring_words..(i + 1) * ring_words],
                            &self.cfg,
                        ),
                    )
                })
                .collect::<Vec<_>>();

            for (job, result) in finished_results {
                stats.total_steps = stats
                    .total_steps
                    .checked_add(result.steps)
                    .ok_or_else(|| GpuError("batch step count exceeds u64".into()))?;
                results[job] = Some(result);
                done += 1;
            }

            if !completed.is_empty() {
                progress(done);
            }
        }

        self.stats = stats;
        results
            .into_iter()
            .map(|r| r.ok_or_else(|| GpuError("job did not produce a result".into())))
            .collect()
    }
}

fn validate_config(cfg: &GpuConfig) -> Result<(), GpuError> {
    if cfg.lanes == 0
        || cfg.lanes > u32::MAX as usize
        || !(2..=i32::MAX as usize).contains(&cfg.grid)
        || cfg.pool_tiles == 0
        || cfg.pool_tiles > (u32::MAX as usize / 1024)
        || cfg.slice_steps == 0
        || cfg.history == 0
        || cfg.history > u32::MAX as usize - 32
    {
        return Err(GpuError(
            "invalid lanes, grid, pool_tiles, slice_steps or history".into(),
        ));
    }

    // Check products before allocation or shader-side u32 address calculations.
    let directory_words = (cfg.grid.div_ceil(TILE_DIM) as u64).pow(2);
    let history_words = cfg.history.div_ceil(16) as u64 + 1;

    for words_per_lane in [directory_words, history_words] {
        if words_per_lane
            .checked_mul(cfg.lanes as u64)
            .is_none_or(|n| n > u32::MAX as u64)
        {
            return Err(GpuError(
                "directory or history exceeds 32-bit shader addressing".into(),
            ));
        }
    }

    Ok(())
}

// Same trail reconstruction and detection rules as the CUDA sweep. The extra
// history word preserves partially written words across arbitrary slices.
fn finish(lane: Lane, ring: &[u32], cfg: &GpuConfig) -> RunResult {
    let c = (cfg.grid / 2) as i32;
    let steps = lane.steps();
    let stop = if lane.status == ESCAPED {
        Stop::Escaped
    } else {
        Stop::Budget
    };
    let heading_of = |step: u64| -> usize {
        let word = ring[(((step - 1) >> 4) % ring.len() as u64) as usize];
        ((word >> (2 * ((step - 1) & 15))) & 3) as usize
    };
    let last_t = if stop == Stop::Escaped {
        steps - 1
    } else {
        steps
    };
    let len = (cfg.history as u64).min(last_t.saturating_add(1)) as usize;
    let mut pos = (lane.x - c, lane.y - c);

    if stop == Stop::Escaped {
        let d = DIRS[heading_of(steps)];
        pos = (pos.0 - d.0, pos.1 - d.1);
    }

    let mut trail = vec![(0, 0); len];
    trail[len - 1] = pos;

    for k in (0..len - 1).rev() {
        let step = last_t - (len - 1 - (k + 1)) as u64;
        let d = DIRS[heading_of(step)];
        pos = (pos.0 - d.0, pos.1 - d.1);
        trail[k] = pos;
    }

    let periodic_tail = find_highway(&trail, cfg.max_period, MIN_SPAN);
    let highway = if stop == Stop::Escaped {
        periodic_tail
            .or_else(|| find_highway(&trail, cfg.max_period, 2000))
            .filter(|&hw| exit_confirms(hw, lane.heading as u8))
    } else {
        None
    };

    RunResult {
        steps,
        stop,
        pos: (lane.x - c, lane.y - c),
        heading: lane.heading as u8,
        highway,
        periodic_tail,
        extent: (
            (lane.maxx - lane.minx + 1) as u32,
            (lane.maxy - lane.miny + 1) as u32,
        ),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn shader_validates_without_optional_integer_extensions() {
        let module = wgpu::naga::front::wgsl::parse_str(SHADER).unwrap();
        wgpu::naga::valid::Validator::new(
            wgpu::naga::valid::ValidationFlags::all(),
            wgpu::naga::valid::Capabilities::empty(),
        )
        .validate(&module)
        .unwrap();
    }

    #[test]
    fn rejects_invalid_sizes_before_requesting_an_adapter() {
        for cfg in [
            GpuConfig {
                lanes: 0,
                ..GpuConfig::default()
            },
            GpuConfig {
                grid: 1,
                ..GpuConfig::default()
            },
            GpuConfig {
                grid: usize::MAX,
                ..GpuConfig::default()
            },
            GpuConfig {
                lanes: u32::MAX as usize,
                ..GpuConfig::default()
            },
            GpuConfig {
                pool_tiles: 0,
                ..GpuConfig::default()
            },
            GpuConfig {
                pool_tiles: usize::MAX,
                ..GpuConfig::default()
            },
            GpuConfig {
                slice_steps: 0,
                ..GpuConfig::default()
            },
            GpuConfig {
                history: 0,
                ..GpuConfig::default()
            },
        ] {
            assert!(GpuSweeper::new(cfg).is_err());
        }
    }

    #[test]
    #[ignore = "requires GPU hardware; run with --ignored"]
    fn step_counter_crosses_32_bit_boundary() {
        let mut sw = GpuSweeper::new(GpuConfig {
            lanes: 1,
            grid: 64,
            slice_steps: 17,
            pool_tiles: 4,
            history: 32,
            ..GpuConfig::default()
        })
        .unwrap();
        sw.reset();
        let job = Job {
            rule: "RR".parse().unwrap(),
            bg_seed: None,
            max_steps: (1 << 32) + 3,
        };
        let mut lane = Lane::new(&job, 64);
        let before = (1u64 << 32) - 4;
        lane.steps = words(before);
        lane.ring_cursor = ((before >> 4) % sw.params.ring_words as u64) as u32;
        sw.queue
            .write_buffer(&sw.states, 0, bytemuck::bytes_of(&lane));
        let got = sw.advance().unwrap()[0];
        assert_eq!(got.steps(), job.max_steps);
        assert_eq!(got.status, BUDGET);
        assert_eq!((got.x, got.y, got.heading), (32, 33, 3));

        let rings = sw.retire(&[0]).unwrap();

        for offset in 0..7u64 {
            let step = before + offset + 1;
            let word = rings[(((step - 1) >> 4) % sw.params.ring_words as u64) as usize];
            let heading = (word >> (2 * ((step - 1) & 15))) & 3;
            assert_eq!(heading, ((offset + 1) & 3) as u32);
        }
    }
}
