//! Fixed-area sampling with cycle accounting (experiments/archive/2026-10-fixed-area-cycles).
//!
//! usage: fixed_area_cycles_sampler OUT_DIR STEP_CAP GRID LO-HI[,LO-HI...] < specs
//!
//! Each stdin line is `RULE@SEED` (ant, random 5x5 patch), `rotor:SEED` or `rw:SEED`.
//! Per spec it writes OUT_DIR/<name>.bands.csv (one row per band, all unreached bands
//! included) and OUT_DIR/<name>.status.csv, then OUT_DIR/<name>.done last. A spec with a
//! .done marker is skipped, so a rerun resumes and yields the same bytes. The payload
//! files (plus NAME.idurK.u32: raw complete-contained I durations of band K) contain no timestamps or runtimes (wall time goes to stderr only).
//! Concurrency: set RAYON_NUM_THREADS; each job holds a dense GRID^2 x 2 byte board.

use rayon::prelude::*;
use std::path::Path;
use turmite::Rule;
use turmite::fixed_area::{BandOut, RunOut, Stop, run};
use turmite::walkers::{PatchedAnt, RandomWalk, Rotor};

const HEADER: &str = "spec,band_id,lo,hi,reached_lo,reached_hi,t_start,t_end,area_start,area_end,perim_start,perim_end,\
steps,new_cells,b_dep,i_dep,fresh_from_interior,sum_pa,\
w_start,h_start,sx_start,sy_start,sxx_start,w_end,h_end,sx_end,sy_end,sxx_end,\
b_complete,b_complete_steps,b_clip_frags,b_clip_steps,b_clip_max,\
i_complete,i_complete_steps,i_clip_frags,i_clip_steps,i_clip_max,\
cycles,cycle_d_sum,cycle_t_sum,i_q50,i_q90,i_q99,i_q999,i_q9999,i_max,b_bin_n,b_bin_steps,i_bin_n,i_bin_steps";

fn join(v: &[u64]) -> String {
    v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(";")
}

fn row(spec: &str, k: usize, b: &BandOut) -> String {
    let mut s = format!("{spec},{k},{},{},{},{}", b.lo, b.hi, b.reached_lo as u8, b.reached_hi as u8);
    if !b.reached_lo {
        s.push_str(&",".repeat(HEADER.matches(',').count() - 5));
        return s;
    }
    let (gs, ge) = (b.geom_start, b.geom_end);
    let q = |p: f64| b.i_quantile(p).map_or(String::new(), |v| v.to_string());
    let imax = b.i_durations.iter().max().map_or(String::new(), |v| v.to_string());
    let f = |x: u64| x.to_string();
    let mut cols: Vec<String> = vec![
        f(b.t_start), f(b.t_end), f(b.area_start), f(b.area_end), f(b.perim_start), f(b.perim_end), f(b.steps), f(b.new_cells()),
        f(b.b_dep), f(b.i_dep), f(b.fresh_from_interior), format!("{:?}", b.sum_pa),
    ];
    for g in [gs, ge] {
        cols.extend([g.width.to_string(), g.height.to_string(), g.sx.to_string(), g.sy.to_string(), g.sxx.to_string()]);
    }
    for e in [&b.b, &b.i] {
        cols.extend([f(e.complete), f(e.complete_steps), f(e.clipped_frags), f(e.clipped_steps), f(e.clipped_max)]);
    }
    cols.extend([f(b.cycles), f(b.cycle_d_sum), f(b.cycle_t_sum), q(0.5), q(0.9), q(0.99), q(0.999), q(0.9999), imax]);
    cols.extend([join(&b.b.bin_n), join(&b.b.bin_steps), join(&b.i.bin_n), join(&b.i.bin_steps)]);
    assert_eq!(cols.len() + 6, HEADER.matches(',').count() + 1);
    s.push(',');
    s.push_str(&cols.join(","));
    s
}

fn exec(spec: &str, grid: usize, cap: u64, bands: &[(u64, u64)]) -> RunOut {
    if let Some(seed) = spec.strip_prefix("rotor:") {
        run(Rotor { seed: seed.parse().unwrap() }, grid, cap, bands)
    } else if let Some(seed) = spec.strip_prefix("rw:") {
        run(RandomWalk { state: seed.parse().unwrap() }, grid, cap, bands)
    } else if let Some((rule, seed)) = spec.split_once('@') {
        run(PatchedAnt::new(&rule.parse::<Rule>().unwrap(), seed.parse().unwrap(), 2), grid, cap, bands)
    } else {
        panic!("bad spec {spec}")
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let out = Path::new(&a[1]);
    let cap: u64 = a[2].parse().unwrap();
    let grid: usize = a[3].parse().unwrap();
    let bands: Vec<(u64, u64)> = a[4]
        .split(',')
        .map(|b| {
            let (lo, hi) = b.split_once('-').unwrap();
            (lo.parse().unwrap(), hi.parse().unwrap())
        })
        .collect();
    std::fs::create_dir_all(out).unwrap();
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    // The marker records the parameters; a rerun with different ones recomputes instead of reusing.
    let marker = format!("fixed_area_v1 cap={cap} grid={grid} bands={bands:?}\n");
    specs.par_iter().for_each(|spec| {
        let name = spec.replace([':', '@'], "_");
        if std::fs::read_to_string(out.join(format!("{name}.done"))).is_ok_and(|d| d == marker) {
            eprintln!("skip {spec}");
            return;
        }
        let t0 = std::time::Instant::now();
        let r = exec(spec, grid, cap, &bands);
        let mut csv = format!("{HEADER}\n");
        for (k, b) in r.bands.iter().enumerate() {
            csv.push_str(&row(spec, k, b));
            csv.push('\n');
        }
        let stop = match r.stop {
            Stop::Sink => "complete",
            Stop::Budget => "budget",
            Stop::Escaped => "escaped",
        };
        let status = format!("spec,stop,t_final,area_final,grid,cap\n{spec},{stop},{},{},{grid},{cap}\n", r.t_final, r.area_final);
        // Payloads first, marker last; write-then-rename so a crash never leaves a partial file.
        for (suffix, body) in [("bands.csv", &csv), ("status.csv", &status)] {
            let tmp = out.join(format!("{name}.{suffix}.tmp"));
            std::fs::write(&tmp, body).unwrap();
            std::fs::rename(&tmp, out.join(format!("{name}.{suffix}"))).unwrap();
        }
        // Raw complete-contained I durations (little-endian u32, completion order) for pooled quantiles.
        for (k, b) in r.bands.iter().enumerate().filter(|(_, b)| b.reached_lo) {
            let bytes: Vec<u8> = b.i_durations.iter().flat_map(|d| d.to_le_bytes()).collect();
            let tmp = out.join(format!("{name}.idur{k}.u32.tmp"));
            std::fs::write(&tmp, bytes).unwrap();
            std::fs::rename(&tmp, out.join(format!("{name}.idur{k}.u32"))).unwrap();
        }
        std::fs::write(out.join(format!("{name}.done")), &marker).unwrap();
        eprintln!("{spec}: {stop} t={} area={} {:.1}s", r.t_final, r.area_final, t0.elapsed().as_secs_f64());
    });
}
