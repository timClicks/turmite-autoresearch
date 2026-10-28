//! Per-colour exposure and fresh-cell launch tallies (experiments/archive/2026-10-kappa-prefix-exposure).
//!
//! usage: kappa_prefix_exposure_sampler OUT_DIR STEP_CAP GRID W LO-HI[,LO-HI...] < specs
//!
//! Each stdin line is `RULE@SEED`: the ant on a blank board with the radius-2 random patch derived
//! from SEED and the rule length (so a base and a mutant of equal length share their patch). The
//! rule is used exactly as written, never mirrored. Per spec it writes into OUT_DIR
//! `NAME.bands.csv`, `NAME.reads.csv` (sparse: band, colour, depth, cycle, n), `NAME.whole.csv`,
//! `NAME.episodes.csv` (per band and threshold: episodes begun in band, those reaching the threshold, in-band interior steps in such episodes), `NAME.status.csv`, then `NAME.done` last. A spec whose `.done` carries the same parameters is
//! skipped, so a rerun resumes and yields the same bytes. Payload files contain no timestamps
//! (wall time goes to stderr). Set RAYON_NUM_THREADS; each job holds a dense GRID^2 x 4 byte board.
//! No mid-run checkpoint: a run is seconds, and a spec is the unit of resumption.

use rayon::prelude::*;
use std::path::Path;
use turmite::Rule;
use turmite::fixed_area::Stop;
use turmite::prefix_exposure::*;
use turmite::walkers::PatchedAnt;

/// Episode-length thresholds for the tail counts; fixed here and recorded in the .done marker.
const WS: [u64; 5] = [1, 16, 64, 256, 1024];

const HEADER: &str = "spec,band_id,lo,hi,reached_lo,reached_hi,t_start,t_end,area_start,area_end,perim_start,perim_end,\
steps,b_dep,i_dep,sum_pa,fresh_colour,launch_n,launch_n_interior_start,launch_left,launch_long,launch_overlap,\
launch_sum_fwd,launch_sum_lat,launch_sum_r2,launch_cens,launch_cens_long";

fn write_atomic(dir: &Path, name: &str, body: &str) {
    let tmp = dir.join(format!("{name}.tmp"));
    std::fs::write(&tmp, body).unwrap();
    std::fs::rename(&tmp, dir.join(name)).unwrap();
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let out = Path::new(&a[1]);
    let cap: u64 = a[2].parse().unwrap();
    let grid: usize = a[3].parse().unwrap();
    let w: u64 = a[4].parse().unwrap();
    let bands: Vec<(u64, u64)> = a[5]
        .split(',')
        .map(|b| {
            let (lo, hi) = b.split_once('-').unwrap();
            (lo.parse().unwrap(), hi.parse().unwrap())
        })
        .collect();
    std::fs::create_dir_all(out).unwrap();
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    let marker = format!("kpe_v2 cap={cap} grid={grid} w={w} ws={WS:?} bands={bands:?}\n");
    specs.par_iter().for_each(|spec| {
        let name = spec.replace('@', "_");
        if std::fs::read_to_string(out.join(format!("{name}.done"))).is_ok_and(|d| d == marker) {
            eprintln!("skip {spec}");
            return;
        }
        let t0 = std::time::Instant::now();
        let (rule, seed) = spec.split_once('@').expect("RULE@SEED");
        let r = run(PatchedAnt::new(&rule.parse::<Rule>().unwrap(), seed.parse().unwrap(), 2), grid, cap, &bands, w, &WS);
        let nc = rule.len();
        let mut csv = format!("{HEADER}\n");
        let mut reads = String::from("spec,band_id,colour,depth,cycle,n\n");
        for (k, b) in r.bands.iter().enumerate() {
            let l = &b.launch;
            let fc = b.fresh_colour[..nc].iter().map(u64::to_string).collect::<Vec<_>>().join(";");
            csv.push_str(&format!(
                "{spec},{k},{},{},{},{}",
                b.lo, b.hi, b.reached_lo as u8, b.reached_hi as u8
            ));
            if b.reached_lo {
                csv.push_str(&format!(
                    ",{},{},{},{},{},{},{},{},{},{:?},{fc},{},{},{},{},{},{},{},{},{},{}",
                    b.t_start, b.t_end, b.area_start, b.area_end, b.perim_start, b.perim_end, b.steps, b.b_dep, b.i_dep, b.sum_pa,
                    l.n, l.n_interior_start, l.left, l.long, l.overlap, l.sum_fwd, l.sum_lat, l.sum_r2, l.cens, l.cens_long
                ));
            } else {
                csv.push_str(&",".repeat(HEADER.matches(',').count() - 5));
            }
            csv.push('\n');
            for c in 0..nc {
                for d in 0..DEPTH_CLASSES {
                    for y in 0..CYCLE_CLASSES {
                        let n = b.reads[reads_idx(c, d, y)];
                        if n > 0 {
                            reads.push_str(&format!("{spec},{k},{c},{d},{y},{n}\n"));
                        }
                    }
                }
            }
        }
        let mut episodes = String::from("spec,band_id,w,ep_n,ep_long_n,tail_steps\n");
        for (k, b) in r.bands.iter().enumerate().filter(|(_, b)| b.reached_lo) {
            for (i, wv) in WS.iter().enumerate() {
                episodes.push_str(&format!("{spec},{k},{wv},{},{},{}\n", b.ep_n, b.ep_long_n[i], b.tail_steps[i]));
            }
        }
        let mut whole = String::from("spec,colour,reads,first_t,first_area,first_depth\n");
        for c in 0..nc {
            let (t, ar, dp) = r.whole.first_read[c].map_or((String::new(), String::new(), String::new()), |(t, ar, dp)| (t.to_string(), ar.to_string(), dp.to_string()));
            whole.push_str(&format!("{spec},{c},{},{t},{ar},{dp}\n", r.whole.reads[c]));
        }
        let stop = match r.stop {
            Stop::Sink => "complete",
            Stop::Budget => "budget",
            Stop::Escaped => "escaped",
        };
        // An interior episode still open at the stop: its classification at thresholds above open_len is unknown.
        let (ob, ol) = r.whole.open_episode.map_or((String::new(), String::new()), |(b, l)| (b.map_or(String::from("-"), |k| k.to_string()), l.to_string()));
        let status = format!("spec,stop,t_final,area_final,grid,cap,w,open_begin_band,open_len\n{spec},{stop},{},{},{grid},{cap},{w},{ob},{ol}\n", r.t_final, r.area_final);
        // Payloads first, marker last; write-then-rename so a crash never leaves a partial file.
        write_atomic(out, &format!("{name}.bands.csv"), &csv);
        write_atomic(out, &format!("{name}.reads.csv"), &reads);
        write_atomic(out, &format!("{name}.whole.csv"), &whole);
        write_atomic(out, &format!("{name}.episodes.csv"), &episodes);
        write_atomic(out, &format!("{name}.status.csv"), &status);
        std::fs::write(out.join(format!("{name}.done")), &marker).unwrap();
        eprintln!("{spec}: {stop} t={} area={} {:.2}s", r.t_final, r.area_final, t0.elapsed().as_secs_f64());
    });
}
