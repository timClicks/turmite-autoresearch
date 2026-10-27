//! Instrumented runs: one CSV row per (rule, octave window).
//!
//! usage: probe MAX_LOG2 [GRID] < walkers.txt > probe.csv
//! Each input line is an ant rule (e.g. RLR), `rotor:SEED`, `rw:SEED`, or
//! `RULE@SEED` (the ant on a blank board with a random 5x5 patch at the start).

use rayon::prelude::*;
use std::io::Write;
use turmite::Rule;
use turmite::probe::{probe, probe_walker};
use turmite::walkers::{BiasedRotor, NoisyRotor, PatchedAnt, PersistentWalk, RandomWalk, Rotor, SparseBgAnt};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let max_log2: u32 = a[1].parse().unwrap();
    let size: usize = a.get(2).map(|s| s.parse().unwrap()).unwrap_or(8192);
    let rules: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    eprintln!("{} rules", rules.len());
    let done = std::sync::atomic::AtomicUsize::new(0);
    let blocks: Vec<String> = rules
        .par_iter()
        .map(|r| {
            let res = if let Some(seed) = r.strip_prefix("rotor:") {
                probe_walker(Rotor { seed: seed.parse().unwrap() }, size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("sbg:") {
                // sbg:RULE:SEED:DENSITY (B2b: ant on a sparse random background)
                let p: Vec<&str> = spec.split(':').collect();
                probe_walker(SparseBgAnt::new(&p[0].parse::<Rule>().unwrap(), p[1].parse().unwrap(), p[2].parse().unwrap()), size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("brotor:") {
                // brotor:SEED:BIAS (C2: rotor with arrows biased towards north)
                let (seed, bias) = spec.split_once(':').unwrap();
                probe_walker(BiasedRotor::new(seed.parse().unwrap(), bias.parse().unwrap()), size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("nrotor:") {
                // nrotor:EPS:SEED (Arm B: rotor whose arrow is randomised with probability EPS)
                let (eps, seed) = spec.split_once(':').unwrap();
                probe_walker(NoisyRotor::new(seed.parse().unwrap(), eps.parse().unwrap()), size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("pw:") {
                // pw:Q:SEED (A1d: memoryless walker turning right with probability Q)
                let (q, seed) = spec.split_once(':').unwrap();
                probe_walker(PersistentWalk::new(seed.parse().unwrap(), q.parse().unwrap()), size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("cookie:").or_else(|| r.strip_prefix("rcookie:")) {
                let (bias, seed) = spec.split_once(':').unwrap();
                probe_walker(turmite::walkers::CookieWalk::new(seed.parse().unwrap(), bias.parse().unwrap(), r.starts_with("rcookie:")), size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("errw:") {
                let (increment, seed) = spec.split_once(':').unwrap();
                probe_walker(turmite::walkers::EdgeReinforcedWalk::new(seed.parse().unwrap(), increment.parse().unwrap()), size, 8, max_log2)
            } else if let Some(spec) = r.strip_prefix("hy:") {
                // hy:RULE:EV:EF:SEED (wall-vs-memory: turn noise EV on revisited cells, EF on fresh ones)
                let p: Vec<&str> = spec.split(':').collect();
                let w = turmite::walkers::HybridWalker::new(&p[0].parse::<Rule>().unwrap(), p[3].parse().unwrap(), p[1].parse().unwrap(), p[2].parse().unwrap());
                probe_walker(w, size, 8, max_log2)
            } else if let Some(seed) = r.strip_prefix("rw:") {
                probe_walker(RandomWalk { state: seed.parse().unwrap() }, size, 8, max_log2)
            } else if let Some((rule, seed)) = r.split_once('@') {
                probe_walker(PatchedAnt::new(&rule.parse::<Rule>().unwrap(), seed.parse().unwrap(), 2), size, 8, max_log2)
            } else {
                probe(&r.parse::<Rule>().unwrap(), size, 8, max_log2)
            };
            let k = done.fetch_add(1, std::sync::atomic::Ordering::Relaxed);
            if k % 200 == 0 {
                eprintln!("{k}");
            }
            turmite::probe::csv_rows(r, &res)
        })
        .collect();
    let mut out = std::io::stdout().lock();
    writeln!(out, "{}", turmite::probe::CSV_HEADER).unwrap();
    for b in blocks {
        out.write_all(b.as_bytes()).unwrap();
    }
}
