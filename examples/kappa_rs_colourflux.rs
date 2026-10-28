//! W4 of experiments/archive/2026-10-kappa-rule-space: colour-resolved boundary occupancy.
//!
//! usage: kappa_rs_colourflux MIN_LOG2 MAX_LOG2 [GRID] < specs.txt > colourflux.csv
//! Specs as `bin/probe`: RULE, RULE@SEED (random 5x5 patch), rotor:SEED, pw:Q:SEED.
//! MAX_LOG2 is probe's (27 gives windows k = MIN_LOG2..26). One CSV row per (spec, window);
//! the per-colour columns are colon-joined, n entries for an n-colour ant, 4 for the rotor
//! (arrow states), 1 for the memoryless walker. Rows come out in input order, so the output
//! does not depend on the thread count. Tested in tests/colourflux.rs.

use rayon::prelude::*;
use std::io::Write;
use turmite::Rule;
use turmite::colourflux::{FluxResult, flux_walker};
use turmite::walkers::{AntWalker, PatchedAnt, PersistentWalk, Rotor};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let min_log2: u32 = a[1].parse().unwrap();
    let max_log2: u32 = a[2].parse().unwrap();
    let size: usize = a.get(3).map(|s| s.parse().unwrap()).unwrap_or(8192);
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    eprintln!("{} specs", specs.len());
    let blocks: Vec<String> = specs
        .par_iter()
        .map(|r| {
            let (res, ncol): (FluxResult, usize) = if let Some(seed) = r.strip_prefix("rotor:") {
                (flux_walker(Rotor { seed: seed.parse().unwrap() }, size, min_log2, max_log2), 4)
            } else if let Some(spec) = r.strip_prefix("pw:") {
                let (q, seed) = spec.split_once(':').unwrap();
                (flux_walker(PersistentWalk::new(seed.parse().unwrap(), q.parse().unwrap()), size, min_log2, max_log2), 1)
            } else if let Some((rule, seed)) = r.split_once('@') {
                let rule: Rule = rule.parse().unwrap();
                (flux_walker(PatchedAnt::new(&rule, seed.parse().unwrap(), 2), size, min_log2, max_log2), rule.len())
            } else {
                let rule: Rule = r.parse().unwrap();
                (flux_walker(AntWalker::new(&rule), size, min_log2, max_log2), rule.len())
            };
            let join = |v: &[u64; turmite::colourflux::MAXC]| v[..ncol].iter().map(|x| x.to_string()).collect::<Vec<_>>().join(":");
            let mut s = String::new();
            for w in &res.windows {
                let k = w.t_start.trailing_zeros();
                s += &format!(
                    "{r},{k},{},{},{},{},{},{},{},{},{}\n",
                    w.area,
                    w.perimeter,
                    w.new_cells,
                    w.boundary_steps,
                    join(&w.steps_by_colour),
                    join(&w.boundary_by_colour),
                    join(&w.new_by_colour),
                    join(&w.hist_all),
                    join(&w.hist_boundary)
                );
            }
            if res.escaped {
                s += &format!("{r},escaped,,,,,,,,,\n");
            }
            s
        })
        .collect();
    let out = std::io::stdout();
    let mut out = std::io::BufWriter::new(out.lock());
    writeln!(out, "rule,k,area,perimeter,new_cells,boundary_steps,steps_by_colour,boundary_by_colour,new_by_colour,hist_all,hist_boundary").unwrap();
    for b in blocks {
        out.write_all(b.as_bytes()).unwrap();
    }
}
