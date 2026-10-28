//! The GPU sweep must return exactly what the CPU oracle chain returns, whatever the lane count, slice
//! length, tile-pool pressure or batch composition. Needs `--features cuda`, a CUDA device and
//! `libnvrtc.so.12` on LD_LIBRARY_PATH:
//!     source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
//!     cargo test --release --features cuda --test gpu
#![cfg(feature = "cuda")]

use proptest::prelude::*;
use std::sync::{Mutex, OnceLock};
use turmite::ext::bg_colour;
use turmite::fast::{self, Config, Grid, RunResult, Stop};
use turmite::gpu::{GpuConfig, GpuSweeper, Job};
use turmite::{DIRS, Rule};

// One sweeper per configuration, shared by all cases (NVRTC + VRAM setup is slow), and serialised
// because the tests share one device.
struct Rig {
    name: &'static str,
    sweeper: GpuSweeper,
}

fn rigs() -> &'static Mutex<Vec<Rig>> {
    static RIGS: OnceLock<Mutex<Vec<Rig>>> = OnceLock::new();
    RIGS.get_or_init(|| {
        let mk = |name, lanes, grid, slice_steps, pool_tiles, history, max_period| Rig {
            name,
            sweeper: GpuSweeper::new(GpuConfig { lanes, grid, slice_steps, pool_tiles, history, max_period, ..GpuConfig::default() })
                .unwrap(),
        };
        Mutex::new(vec![
            // grid = exactly one tile, so every edge is a tile edge; slice not a multiple of 16
            mk("one-tile", 5, 64, 997, Some(256), 300, 100),
            // grid not a multiple of the tile size, partial edge tiles, few lanes so jobs queue
            mk("ragged", 3, 100, 4093, Some(256), 1_000, 400),
            // pool of exactly the 4x4 tiles one ant can touch: concurrent lanes starve and requeue
            mk("tight-pool", 4, 200, 1_501, Some(16), 700, 300),
            // many lanes, big slices
            mk("wide", 64, 256, 1 << 20, Some(2_048), 5_000, 1_000),
        ])
    })
}

fn oracle(rule: &Rule, size: usize, steps: u64, history: usize, max_period: usize) -> RunResult {
    let cfg = Config { max_steps: steps, checkpoint: 1_000, max_period, history };
    fast::run(rule, &mut Grid::new(size), &cfg)
}

fn same(a: &RunResult, b: &RunResult) -> Result<(), TestCaseError> {
    prop_assert_eq!(a.steps, b.steps);
    prop_assert_eq!(a.stop, b.stop);
    prop_assert_eq!(a.pos, b.pos);
    prop_assert_eq!(a.heading, b.heading);
    prop_assert_eq!(a.highway, b.highway);
    prop_assert_eq!(a.periodic_tail, b.periodic_tail);
    prop_assert_eq!(a.extent, b.extent);
    Ok(())
}

fn blank_jobs(specs: &[(u32, usize, u64)]) -> Vec<Job> {
    specs
        .iter()
        .map(|&(bits, n, steps)| Job { rule: Rule::from_bits(bits, n), bg_seed: None, max_steps: steps })
        .collect()
}

proptest! {
    #[test]
    fn gpu_equals_fast(specs in prop::collection::vec((1u32..4096, 2usize..12, 0u64..40_000), 1..14)) {
        let jobs = blank_jobs(&specs);
        let mut rigs = rigs().lock().unwrap_or_else(|e| e.into_inner());
        for rig in rigs.iter_mut() {
            let (size, hist, per) = (rig.sweeper.cfg.grid, rig.sweeper.cfg.history, rig.sweeper.cfg.max_period);
            let got = rig.sweeper.run(&jobs, |_| {}).unwrap();
            for (j, g) in jobs.iter().zip(&got) {
                let want = oracle(&j.rule, size, j.max_steps, hist, per);
                same(g, &want).map_err(|e| TestCaseError::fail(format!("rig {} rule {} steps {}: {e}", rig.name, j.rule, j.max_steps)))?;
            }
        }
    }

    // Same jobs through rigs with different lane/slice/pool settings and in a different order.
    #[test]
    fn independent_of_scheduling(specs in prop::collection::vec((1u32..1024, 2usize..10, 1u64..30_000), 2..10)) {
        let jobs = blank_jobs(&specs);
        let mut rev = jobs.clone();
        rev.reverse();
        let mut rigs = rigs().lock().unwrap_or_else(|e| e.into_inner());
        // "wide" and "tight-pool" have different grids, so compare each rig with itself, reordered.
        for rig in rigs.iter_mut() {
            let a = rig.sweeper.run(&jobs, |_| {}).unwrap();
            let mut b = rig.sweeper.run(&rev, |_| {}).unwrap();
            b.reverse();
            for (x, y) in a.iter().zip(&b) {
                same(x, y).map_err(|e| TestCaseError::fail(format!("rig {}: {e}", rig.name)))?;
            }
        }
    }
}

/// Dense CPU reference for a seeded background: steps, stop, pos, heading, extent.
fn bg_reference(rule: &Rule, seed: u64, size: usize, max_steps: u64) -> (u64, Stop, (i32, i32), u8, (u32, u32)) {
    let c = size / 2;
    let n = rule.len();
    let mut cells: Vec<u8> = (0..size * size)
        .map(|i| bg_colour(seed, (i % size) as i64 - c as i64, (i / size) as i64 - c as i64, n))
        .collect();
    let (mut x, mut y, mut h) = (c as i64, c as i64, 0u8);
    let (mut minx, mut maxx, mut miny, mut maxy) = (x, x, y, y);
    let mut steps = 0;
    let mut stop = Stop::Budget;
    while steps < max_steps {
        let i = y as usize * size + x as usize;
        let col = cells[i] as usize;
        h = (h + rule.0[col].delta()) & 3;
        cells[i] = ((col + 1) % n) as u8;
        x += DIRS[h as usize].0 as i64;
        y += DIRS[h as usize].1 as i64;
        steps += 1;
        if x < 0 || y < 0 || x >= size as i64 || y >= size as i64 {
            stop = Stop::Escaped;
            break;
        }
        minx = minx.min(x);
        maxx = maxx.max(x);
        miny = miny.min(y);
        maxy = maxy.max(y);
    }
    let pos = ((x - c as i64) as i32, (y - c as i64) as i32);
    (steps, stop, pos, h, ((maxx - minx + 1) as u32, (maxy - miny + 1) as u32))
}

proptest! {
    #[test]
    fn seeded_background_equals_dense_reference(specs in prop::collection::vec((1u32..2048, 2usize..9, 0u64..30_000, any::<u64>()), 1..10)) {
        let jobs: Vec<Job> = specs
            .iter()
            .map(|&(bits, n, steps, seed)| Job { rule: Rule::from_bits(bits, n), bg_seed: Some(seed), max_steps: steps })
            .collect();
        let mut rigs = rigs().lock().unwrap_or_else(|e| e.into_inner());
        for rig in rigs.iter_mut() {
            let size = rig.sweeper.cfg.grid;
            let got = rig.sweeper.run(&jobs, |_| {}).unwrap();
            for (j, g) in jobs.iter().zip(&got) {
                let (steps, stop, pos, h, ext) = bg_reference(&j.rule, j.bg_seed.unwrap(), size, j.max_steps);
                prop_assert_eq!((g.steps, g.stop, g.pos, g.heading, g.extent), (steps, stop, pos, h, ext), "rig {} rule {} seed {:?}", rig.name, j.rule, j.bg_seed);
            }
        }
    }
}

/// Highways are only decided after >= 20k steps of periodic motion, which the random cases above
/// rarely reach, so check the known ones explicitly (Langton's ant: period 104, onset ~10k).
#[test]
fn highways_match_fast() {
    let mut sw = GpuSweeper::new(GpuConfig { lanes: 8, grid: 512, slice_steps: 50_000, pool_tiles: Some(1_024), ..GpuConfig::default() }).unwrap();
    let jobs: Vec<Job> = ["RL", "RRL", "RLRL", "RRLL", "RLLR", "RRLLLRLLLRRR", "LLRR", "RLR"]
        .iter()
        .map(|r| Job { rule: r.parse().unwrap(), bg_seed: None, max_steps: 400_000 })
        .collect();
    let got = sw.run(&jobs, |_| {}).unwrap();
    let mut found = 0;
    for (j, g) in jobs.iter().zip(&got) {
        let want = oracle(&j.rule, 512, j.max_steps, 250_000, 50_000);
        assert_eq!((g.steps, g.stop, g.pos, g.heading, g.highway, g.periodic_tail, g.extent), (want.steps, want.stop, want.pos, want.heading, want.highway, want.periodic_tail, want.extent), "{}", j.rule);
        found += g.highway.is_some() as usize;
    }
    assert!(found >= 1, "expected at least Langton's ant to leave on a highway");
    let rl = &got[0];
    assert_eq!(rl.highway.map(|h| h.period), Some(104));
}

/// A solo job that cannot fit in the pool is an error, never a wrong row.
#[test]
fn pool_too_small_is_an_error() {
    let mut sw = GpuSweeper::new(GpuConfig { lanes: 2, grid: 512, pool_tiles: Some(2), slice_steps: 10_000, ..GpuConfig::default() }).unwrap();
    let job = Job { rule: "RL".parse().unwrap(), bg_seed: None, max_steps: 200_000 };
    let e = sw.run(&[job], |_| {}).unwrap_err();
    assert!(e.0.contains("tile pool"), "{e}");
}

#[test]
fn unsupported_colour_count_is_an_error() {
    let mut sw = GpuSweeper::new(GpuConfig { lanes: 2, grid: 64, pool_tiles: Some(64), ..GpuConfig::default() }).unwrap();
    let rule = Rule(vec![turmite::Turn::R; 129]);
    assert!(sw.run(&[Job { rule, bg_seed: None, max_steps: 10 }], |_| {}).is_err());
    // 128 colours is the limit and works
    let rule = Rule(vec![turmite::Turn::R; 128]);
    let r = sw.run(&[Job { rule: rule.clone(), bg_seed: None, max_steps: 1_000 }], |_| {}).unwrap();
    let want = oracle(&rule, 64, 1_000, 250_000, 50_000);
    assert_eq!((r[0].steps, r[0].pos, r[0].extent), (want.steps, want.pos, want.extent));
}

/// With the pool sized for one ant, concurrent lanes starve, get requeued, and results stay exact.
#[test]
fn pool_pressure_requeues_and_stays_correct() {
    let mut sw = GpuSweeper::new(GpuConfig {
        lanes: 4,
        grid: 200,
        pool_tiles: Some(16),
        slice_steps: 1_501,
        history: 700,
        max_period: 300,
        ..GpuConfig::default()
    })
    .unwrap();
    let rules = ["RLR", "RRLLLRLLLRRR", "RRLL", "RLLR", "RLRRRLLR", "RRLLLRLLLRRR", "RRRLLR", "RLLLRRRLLR"];
    let jobs: Vec<Job> = rules.iter().map(|r| Job { rule: r.parse().unwrap(), bg_seed: None, max_steps: 60_000 }).collect();
    let got = sw.run(&jobs, |_| {}).unwrap();
    assert!(sw.stats.oom_requeues > 0, "expected pool starvation, stats: {:?}", sw.stats);
    for (j, g) in jobs.iter().zip(&got) {
        let want = oracle(&j.rule, 200, j.max_steps, 700, 300);
        assert_eq!((g.steps, g.stop, g.pos, g.heading, g.extent), (want.steps, want.stop, want.pos, want.heading, want.extent), "{}", j.rule);
    }
}
