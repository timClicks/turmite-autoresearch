//! W5 of experiments/archive/2026-10-kappa-rule-space: bulk fingerprint on an area-matched mature field.
//!
//! usage: kappa_rs_bulk A0 T_REC D0 [GRID] < specs.txt > bulk.csv
//! Specs as `bin/probe`: RULE, RULE@SEED (random 5x5 patch), rotor:SEED, pw:Q:SEED, rw:SEED.
//! One CSV row per spec, in input order (so the output does not depend on the thread count). Raw integer tallies
//! only; every derived statistic is computed in scripts/w5_analyse.py. Logic and tests: src/bulk.rs, tests/kappa_rs_bulk.rs.

use rayon::prelude::*;
use std::io::Write;
use turmite::Rule;
use turmite::bulk::{BulkParams, BulkRun, Status, run_bulk};
use turmite::walkers::{AntWalker, PatchedAnt, PersistentWalk, RandomWalk, Rotor};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let a0: u64 = a[1].parse().unwrap();
    let t_rec: usize = a[2].parse().unwrap();
    let d0: u32 = a[3].parse().unwrap();
    let size: usize = a.get(4).map(|s| s.parse().unwrap()).unwrap_or(2048);
    let params = BulkParams { size, a0, t_rec, d0, max_steps: 1 << 26 };
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    eprintln!("{} specs", specs.len());
    let rows: Vec<String> = specs
        .par_iter()
        .map(|r| {
            let (res, ncol): (BulkRun, usize) = if let Some(seed) = r.strip_prefix("rotor:") {
                (run_bulk(Rotor { seed: seed.parse().unwrap() }, &params, false), 4)
            } else if let Some(spec) = r.strip_prefix("pw:") {
                let (q, seed) = spec.split_once(':').unwrap();
                (run_bulk(PersistentWalk::new(seed.parse().unwrap(), q.parse().unwrap()), &params, false), 1)
            } else if let Some(seed) = r.strip_prefix("rw:") {
                (run_bulk(RandomWalk { state: seed.parse().unwrap() }, &params, false), 1)
            } else if let Some((rule, seed)) = r.split_once('@') {
                let rule: Rule = rule.parse().unwrap();
                (run_bulk(PatchedAnt::new(&rule, seed.parse().unwrap(), 2), &params, false), rule.len())
            } else {
                let rule: Rule = r.parse().unwrap();
                (run_bulk(AntWalker::new(&rule), &params, false), rule.len())
            };
            let status = match res.status {
                Status::Ok => "ok",
                Status::NoA0 => "noa0",
                Status::Escaped => "escaped",
            };
            fn join<T: ToString>(v: &[T]) -> String {
                v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(":")
            }
            let head = format!("{r},{status},{ncol},{},{},{},{}", res.t_star, res.area0, res.area_end, res.mask_cells);
            match &res.fp {
                Some(fp) => format!(
                    "{head},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n",
                    fp.n_rec,
                    fp.n_bulk,
                    fp.sum_s,
                    fp.sum_s2,
                    join(&fp.dh_hist),
                    join(&fp.turn_s[1..]),
                    join(&fp.turn_n[1..]),
                    join(&fp.msd_sum),
                    join(&fp.msd_n),
                    fp.head_sum,
                    fp.head_n,
                    fp.ret_hit,
                    fp.ret_elig,
                    join(&fp.gap_hist),
                    fp.n_reuse,
                    join(&fp.col_steps[..ncol]),
                    join(&res.core_hist[..ncol])
                ),
                None => format!("{head},,,,,,,,,,,,,,,,,\n"),
            }
        })
        .collect();
    let out = std::io::stdout();
    let mut out = std::io::BufWriter::new(out.lock());
    writeln!(out, "spec,status,ncol,t_star,area0,area_end,mask_cells,n_rec,n_bulk,sum_s,sum_s2,dh_hist,turn_s,turn_n,msd_sum,msd_n,head_sum,head_n,ret_hit,ret_elig,gap_hist,n_reuse,col_steps,core_hist").unwrap();
    for b in rows {
        out.write_all(b.as_bytes()).unwrap();
    }
}
