//! The GPU probe must return exactly the windows the CPU probe returns (`Window` equality, floats
//! included), whatever the lane count, slice length, tile-pool pressure or batch composition. Needs
//! `--features cuda`, a CUDA device and `libnvrtc.so.12` on LD_LIBRARY_PATH:
//!     source experiments/active/2026-10-gpu-ant-sweep/scripts/env.sh
//!     cargo test --release --features cuda --test gpu_probe
#![cfg(feature = "cuda")]

use proptest::prelude::*;
use std::sync::{Mutex, OnceLock};
use turmite::Rule;
use turmite::gpu::{GpuProber, PATCH_RADIUS, ProbeConfig, ProbeJob};
use turmite::probe::{ProbeResult, probe, probe_walker};
use turmite::walkers::PatchedAnt;

const CAP: u32 = 16;

struct Rig {
    name: &'static str,
    prober: GpuProber,
}

/// One prober per configuration, shared by all cases (NVRTC + VRAM setup is slow) and serialised
/// because the tests share one device. Every pool is explicit so the rigs coexist in VRAM.
fn rigs() -> &'static Mutex<Vec<Rig>> {
    static RIGS: OnceLock<Mutex<Vec<Rig>>> = OnceLock::new();
    RIGS.get_or_init(|| {
        let mk = |name, lanes, grid, slice_steps, pool_tiles, min_log2| Rig {
            name,
            prober: GpuProber::new(ProbeConfig {
                lanes,
                grid,
                slice_steps,
                pool_tiles: Some(pool_tiles),
                min_log2,
                max_log2_cap: CAP,
                ..ProbeConfig::default()
            })
            .unwrap(),
        };
        Mutex::new(vec![
            // grid = exactly one tile: every neighbour update crosses a tile edge or the board edge;
            // slice not a multiple of anything, so window boundaries fall mid-slice
            mk("one-tile", 5, 64, 997, 256, 2),
            // grid not a multiple of the tile size: partial edge tiles; fewer lanes than jobs
            mk("ragged", 3, 100, 4093, 256, 3),
            // c = 63, 64, 65: the start cell and its 5x5 patch sit on a tile edge/corner
            mk("c63", 4, 126, 1031, 512, 4),
            mk("c64", 4, 128, 777, 512, 4),
            mk("c65", 4, 130, 2049, 512, 4),
            // pool of exactly the 4x4 tiles one ant can touch: concurrent lanes starve and requeue
            mk("tight-pool", 4, 200, 1_501, 16, 5),
            // many lanes, big slices, min_log2 as in bin/probe is out of reach at CAP 16, use 8
            mk("wide", 64, 512, 1 << 20, 4_096, 8),
        ])
    })
}

fn cpu(job: &ProbeJob, size: usize, min_log2: u32) -> ProbeResult {
    match job.patch_seed {
        None => probe(&job.rule, size, min_log2, job.max_log2),
        Some(s) => probe_walker(PatchedAnt::new(&job.rule, s, PATCH_RADIUS), size, min_log2, job.max_log2),
    }
}

fn same(g: &ProbeResult, c: &ProbeResult) -> Result<(), TestCaseError> {
    prop_assert_eq!(g.escaped, c.escaped);
    prop_assert_eq!(g.windows.len(), c.windows.len());
    for (a, b) in g.windows.iter().zip(&c.windows) {
        prop_assert_eq!(a, b);
    }
    Ok(())
}

fn jobs_from(specs: &[(u32, usize, Option<u64>, u32)]) -> Vec<ProbeJob> {
    specs
        .iter()
        .map(|&(bits, n, seed, max_log2)| ProbeJob { rule: Rule::from_bits(bits & ((1 << n) - 1), n), patch_seed: seed, max_log2 })
        .collect()
}

fn spec_strategy() -> impl Strategy<Value = Vec<(u32, usize, Option<u64>, u32)>> {
    prop::collection::vec((1u32..4096, 2usize..12, prop::option::of(any::<u64>()), 3u32..=CAP), 1..12)
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 48, ..ProptestConfig::default() })]

    #[test]
    fn gpu_equals_cpu_probe(specs in spec_strategy()) {
        let jobs = jobs_from(&specs);
        let mut rigs = rigs().lock().unwrap_or_else(|e| e.into_inner());
        for rig in rigs.iter_mut() {
            let (size, min) = (rig.prober.cfg.grid, rig.prober.cfg.min_log2);
            let got = rig.prober.run(&jobs, |_| {}).unwrap();
            for (j, g) in jobs.iter().zip(&got) {
                same(g, &cpu(j, size, min)).map_err(|e| {
                    TestCaseError::fail(format!("rig {} rule {} patch {:?} max_log2 {}: {e}", rig.name, j.rule, j.patch_seed, j.max_log2))
                })?;
            }
        }
    }

    // The same jobs in reverse order through each rig: results depend on the job only.
    #[test]
    fn independent_of_scheduling(specs in spec_strategy()) {
        let jobs = jobs_from(&specs);
        let mut rev = jobs.clone();
        rev.reverse();
        let mut rigs = rigs().lock().unwrap_or_else(|e| e.into_inner());
        for rig in rigs.iter_mut() {
            let a = rig.prober.run(&jobs, |_| {}).unwrap();
            let mut b = rig.prober.run(&rev, |_| {}).unwrap();
            b.reverse();
            for (x, y) in a.iter().zip(&b) {
                same(x, y).map_err(|e| TestCaseError::fail(format!("rig {}: {e}", rig.name)))?;
            }
        }
    }
}

/// With the pool sized for one ant, concurrent lanes starve, get requeued, and results stay exact.
#[test]
fn pool_pressure_requeues_and_stays_correct() {
    let mut p = GpuProber::new(ProbeConfig {
        lanes: 4,
        grid: 200,
        pool_tiles: Some(16),
        slice_steps: 1_501,
        min_log2: 6,
        max_log2_cap: CAP,
        ..ProbeConfig::default()
    })
    .unwrap();
    let rules = ["RLR", "RRLLLRLLLRRR", "RRLL", "RLLR", "RLRRRLLR", "LRRRRRLLR", "RRRLLR", "RLLLRRRLLR"];
    let jobs: Vec<ProbeJob> = rules
        .iter()
        .enumerate()
        .map(|(i, r)| ProbeJob { rule: r.parse().unwrap(), patch_seed: (i % 2 == 1).then_some(i as u64), max_log2: 16 })
        .collect();
    let got = p.run(&jobs, |_| {}).unwrap();
    assert!(p.stats.oom_requeues > 0, "expected pool starvation, stats: {:?}", p.stats);
    for (j, g) in jobs.iter().zip(&got) {
        let want = cpu(j, 200, 6);
        assert_eq!((g.escaped, &g.windows), (want.escaped, &want.windows), "{}", j.rule);
    }
}

/// A run that escapes mid-window emits no partial window and flags every emitted row.
#[test]
fn escape_drops_the_open_window() {
    let mut p = GpuProber::new(ProbeConfig { lanes: 2, grid: 64, pool_tiles: Some(64), min_log2: 3, max_log2_cap: CAP, ..ProbeConfig::default() }).unwrap();
    // RLLR-type rules grow fast; on a 64-board with 2^16 steps most escape after a few windows
    let jobs: Vec<ProbeJob> = ["RRLLLRLLLRRR", "LRRRRRLLR", "RL"]
        .iter()
        .map(|r| ProbeJob { rule: r.parse().unwrap(), patch_seed: None, max_log2: 16 })
        .collect();
    let got = p.run(&jobs, |_| {}).unwrap();
    assert!(got.iter().any(|g| g.escaped), "test needs at least one escaping run");
    for (j, g) in jobs.iter().zip(&got) {
        let want = cpu(j, 64, 3);
        assert_eq!((g.escaped, &g.windows), (want.escaped, &want.windows), "{}", j.rule);
    }
}

#[test]
fn bad_jobs_are_errors() {
    let mut p = GpuProber::new(ProbeConfig { lanes: 2, grid: 8192, pool_tiles: Some(64), max_log2_cap: 28, ..ProbeConfig::default() }).unwrap();
    let ok = |max_log2| ProbeJob { rule: "RL".parse().unwrap(), patch_seed: None, max_log2 };
    // beyond the cap
    assert!(p.run(&[ok(29)], |_| {}).is_err());
    // 2^28 steps on 8192: window sums could pass 2^53, so the f64 CPU sums would no longer be exact
    let e = p.run(&[ok(28)], |_| {}).unwrap_err();
    assert!(e.0.contains("2^53"), "{e}");
    let rule = Rule(vec![turmite::Turn::R; 129]);
    assert!(p.run(&[ProbeJob { rule, patch_seed: None, max_log2: 10 }], |_| {}).is_err());
}
