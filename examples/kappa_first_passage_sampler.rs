// Depth-crossing sampler for experiments/archive/2026-10-kappa-first-passage (schema: its SCHEMA.md).
// stdin: one spec per line (RULE@SEED, rotor:SEED, rw:SEED).
// args: OUT PAIRS CAP BOARD LO-HI,... HASH THREADS
// OUT gets compact summaries; PAIRS (scratch, ignored by git) gets the start->next state tables.
use rayon::prelude::*;
use std::path::Path;
use turmite::first_passage::{Output, Sim, StateKey};
use turmite::fixed_area::Stop;
use turmite::walkers::{PatchedAnt, RandomWalk, Rotor, Walker};
use turmite::{Rule, Turn};

fn classes(rule: &Rule) -> Vec<u8> {
    let n = rule.len();
    let t = |c: usize| (rule.0[c % n] == Turn::R) as u8;
    (0..256).map(|c| if c < n { 2 * t(c) + t(c + 1) } else { 0 }).collect()
}

fn key(k: &StateKey) -> String {
    format!("{},{},{},{},{},{}", k.m, k.dir, k.heading, k.phase, k.patch, k.hist)
}

/// `ckpt` = (file, every N steps, recipe): resume from the file when it holds a checkpoint of the same
/// recipe, write one atomically every N steps, delete it at the end. Stateless walkers only.
fn go<W: Walker + Clone>(w: W, cls: Option<Vec<u8>>, board: usize, cap: u64, bands: &[(u64, u64)], ckpt: Option<(std::path::PathBuf, u64, String)>, ctx_rows: usize) -> Output {
    let fresh = |w: W| {
        let mut s = Sim::new(w, board, cap, bands);
        if let Some(c) = &cls {
            s = s.with_classes(c.clone());
        }
        if ctx_rows > 0 {
            s = s.with_ctx4(ctx_rows);
        }
        s
    };
    // radius-4 context recording cannot be checkpointed
    let ckpt = if ctx_rows > 0 { None } else { ckpt };
    let Some((path, every, recipe)) = ckpt else {
        let mut s = fresh(w);
        s.advance(None);
        return s.finish();
    };
    let mut s = match std::fs::read(&path) {
        Ok(bytes) => match Sim::restore(w.clone(), &bytes, &recipe) {
            Ok(s) => {
                eprintln!("resume from checkpoint at t={}", s.t);
                s
            }
            Err(e) => {
                eprintln!("ignoring checkpoint {}: {e}", path.display());
                fresh(w)
            }
        },
        Err(_) => fresh(w),
    };
    while s.advance(Some(every)).is_none() {
        let tmp = path.with_extension("ckpt.tmp");
        std::fs::write(&tmp, s.snapshot(&recipe)).unwrap();
        std::fs::rename(&tmp, &path).unwrap();
    }
    let _ = std::fs::remove_file(&path);
    s.finish()
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(a.len(), 8, "OUT PAIRS CAP BOARD LO-HI,... HASH THREADS");
    let (out, pairs) = (Path::new(&a[1]), Path::new(&a[2]));
    let cap: u64 = a[3].parse().unwrap();
    let board: usize = a[4].parse().unwrap();
    let bands: Vec<(u64, u64)> = a[5].split(',').map(|b| { let (l, h) = b.split_once('-').unwrap(); (l.parse().unwrap(), h.parse().unwrap()) }).collect();
    let marker = format!("first_passage_v1 {} cap={cap} board={board} bands={bands:?}\n", a[6]);
    rayon::ThreadPoolBuilder::new().num_threads(a[7].parse().unwrap()).build_global().unwrap();
    std::fs::create_dir_all(out).unwrap();
    std::fs::create_dir_all(pairs).unwrap();
    let specs: Vec<String> = std::io::stdin().lines().map(|s| s.unwrap()).filter(|s| !s.trim().is_empty()).collect();
    specs.par_iter().for_each(|spec| {
        let name = spec.replace([':', '@'], "_");
        let done = out.join(format!("{name}.done"));
        if std::fs::read_to_string(&done).is_ok_and(|s| s == marker) {
            eprintln!("skip {spec}");
            return;
        }
        assert!(!done.exists(), "different config/source marker: {spec}; use a new output directory");
        let clock = std::time::Instant::now();
        // FP_CKPT_STEPS=N: checkpoint every N steps under PAIRS/<spec>.ckpt (stateless walkers only)
        let every: u64 = std::env::var("FP_CKPT_STEPS").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
        let ck = || (every > 0).then(|| (pairs.join(format!("{name}.ckpt")), every, format!("{marker}|{spec}")));
        // FP_CTX4_ROWS=N: also record the radius-4 context table (P4), capped at N rows, to PAIRS/<spec>.ctx4.csv
        let ctx_rows: usize = std::env::var("FP_CTX4_ROWS").ok().and_then(|v| v.parse().ok()).unwrap_or(0);
        let r = if let Some(s) = spec.strip_prefix("rotor:") {
            go(Rotor { seed: s.parse().unwrap() }, None, board, cap, &bands, ck(), ctx_rows)
        } else if let Some(s) = spec.strip_prefix("rw:") {
            go(RandomWalk { state: s.parse().unwrap() }, None, board, cap, &bands, None, ctx_rows)
        } else {
            let (rule, seed) = spec.split_once('@').unwrap();
            let rule: Rule = rule.parse().unwrap();
            go(PatchedAnt::new(&rule, seed.parse().unwrap(), 2), Some(classes(&rule)), board, cap, &bands, ck(), ctx_rows)
        };
        let mut bc = String::from("spec,band,lo,hi,reached_lo,reached_hi,t_start,t_end,area_start,area_end,perim_end,steps,b_dep,i_dep,sum_pa,seg_overlap");
        for l in ["B", "I"] {
            for f in ["entered_complete", "entered_complete_steps", "entered_unresolved", "unresolved_lower", "left_fragments", "left_fragment_overlap", "overlap", "unresolved_overlap"] {
                bc.push_str(&format!(",{l}_{f}"));
            }
        }
        bc.push('\n');
        let mut hist = String::from("spec,band,label,bin,n,steps\n");
        for (k, b) in r.bands.iter().enumerate() {
            bc.push_str(&format!("{spec},{k},{},{},{},{},{},{},{},{},{},{},{},{},{:?},{}", b.lo, b.hi, b.reached_lo as u8, b.reached_hi as u8, b.t_start, b.t_end, b.area_start, b.area_end, b.perim_end, b.steps, b.b_dep, b.i_dep, b.sum_pa, b.seg_overlap));
            for (l, e) in ["B", "I"].iter().zip(&b.eps) {
                bc.push_str(&format!(",{},{},{},{},{},{},{},{}", e.entered_complete, e.entered_complete_steps, e.entered_unresolved, e.unresolved_lower, e.left_fragments, e.left_fragment_overlap, e.overlap, e.unresolved_overlap));
                for bin in 0..e.hist_n.len() {
                    if e.hist_n[bin] > 0 {
                        hist.push_str(&format!("{spec},{k},{l},{bin},{},{}\n", e.hist_n[bin], e.hist_steps[bin]));
                    }
                }
            }
            bc.push('\n');
        }
        let stop = match r.stop { Some(Stop::Sink) => "complete", Some(Stop::Budget) => "budget", Some(Stop::Escaped) => "escaped", None => "none" };
        let status = format!(
            "spec,stop,t_final,area,perimeter,jump_steps,lipschitz_violations,depth_decreases,depth_raises,pair_rows,overflowed,seconds\n{spec},{stop},{},{},{},{},{},{},{},{},{},{:.3}\n",
            r.t, r.area, r.perimeter, r.jump_steps, r.lipschitz_violations, r.depth_decreases, r.depth_raises, r.tallies.len(), r.overflowed, clock.elapsed().as_secs_f64()
        );
        let mut pc = String::from("spec,band,m,dir,heading,phase,patch,hist,nm,ndir,nheading,nphase,npatch,nhist,n,time,skipped,jumps,revisits\n");
        for ((band, s, nx), p) in &r.tallies {
            let n = nx.as_ref().map_or("NA,NA,NA,NA,NA,NA".to_string(), key);
            pc.push_str(&format!("{spec},{band},{},{n},{},{},{},{},{}\n", key(s), p.n, p.time, p.skipped, p.jumps, p.revisits));
        }
        let write = |dir: &Path, suffix: &str, body: &str| {
            let tmp = dir.join(format!("{name}.{suffix}.tmp"));
            std::fs::write(&tmp, body).unwrap();
            std::fs::rename(tmp, dir.join(format!("{name}.{suffix}"))).unwrap();
        };
        if let Some((cm, over)) = &r.ctx4 {
            // r4 = 0 is the folded (unsupported-context) bucket; the last row (band 999) carries the overflow count in n
            let mut cc = String::from("spec,band,m,dir,heading,phase,patch,hist,r4,n,up\n");
            for ((band, s, r4), (n, up)) in cm {
                cc.push_str(&format!("{spec},{band},{},{r4},{n},{up}\n", key(s)));
            }
            cc.push_str(&format!("{spec},999,0,0,0,0,0,0,0,{over},0\n"));
            write(pairs, "ctx4.csv", &cc);
        }
        write(pairs, "pairs.csv", &pc);
        write(out, "bands.csv", &bc);
        write(out, "hist.csv", &hist);
        write(out, "status.csv", &status);
        write(out, "done", &marker);
        eprintln!("{spec} {stop} t={} area={} seconds={:.3}", r.t, r.area, clock.elapsed().as_secs_f64());
    });
}
