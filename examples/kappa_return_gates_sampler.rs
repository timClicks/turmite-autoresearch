// Rim/interior crossing observer (experiments/archive/2026-10-kappa-return-gates).
// Args: OUT CAP GRID LO-HI,... HASH THREADS ; specs on stdin: RULE@SEED | rotor:SEED | rw:SEED.
// Output per spec: <name>.gates.csv (one row per band) and a .done marker holding the config hash.
use rayon::prelude::*;
use std::path::Path;
use turmite::fixed_area::Stop;
use turmite::return_gates::{self, Output};
use turmite::walkers::{mix64, PatchedAnt, RandomWalk, Rotor};
use turmite::Rule;

const DRAWS: usize = 100;
const MIN_EXC: u64 = 50;

fn fnv(s: &str) -> u64 {
    s.bytes().fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ b as u64).wrapping_mul(0x0000_0100_0000_01b3))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(a.len(), 7, "OUT CAP GRID LO-HI,... HASH THREADS");
    let out = Path::new(&a[1]);
    let cap: u64 = a[2].parse().unwrap();
    let grid: usize = a[3].parse().unwrap();
    let bands: Vec<(u64, u64)> = a[4].split(',').map(|b| { let (l, h) = b.split_once('-').unwrap(); (l.parse().unwrap(), h.parse().unwrap()) }).collect();
    let marker = format!("return_gates_v1 {} cap={cap} grid={grid} bands={bands:?} draws={DRAWS}\n", a[5]);
    rayon::ThreadPoolBuilder::new().num_threads(a[6].parse().unwrap()).build_global().unwrap();
    std::fs::create_dir_all(out).unwrap();
    let specs: Vec<String> = std::io::stdin().lines().map(|s| s.unwrap()).filter(|s| !s.trim().is_empty()).collect();
    specs.par_iter().for_each(|spec| {
        let name = spec.replace([':', '@'], "_");
        let done = out.join(format!("{name}.done"));
        if std::fs::read_to_string(&done).is_ok_and(|s| s == marker) { eprintln!("skip {spec}"); return; }
        assert!(!done.exists(), "different config/source marker: {spec}; use a new output directory");
        let clock = std::time::Instant::now();
        let r: Output = if let Some(s) = spec.strip_prefix("rotor:") {
            return_gates::run(Rotor { seed: s.parse().unwrap() }, grid, cap, &bands)
        } else if let Some(s) = spec.strip_prefix("rw:") {
            return_gates::run(RandomWalk { state: s.parse().unwrap() }, grid, cap, &bands)
        } else {
            let (rule, seed) = spec.split_once('@').unwrap();
            let rule: Rule = rule.parse().unwrap();
            return_gates::run(PatchedAnt::new(&rule, seed.parse().unwrap(), 2), grid, cap, &bands)
        };
        let mut csv = String::from("spec,band,lo,hi,reached_lo,reached_hi,steps,B,I,area_end,P_end,sum_pa,d0,d1,d2,d3,d4,d5,exits,entries,reclass_in,reclass_out,b_runs,b_run_steps,exc_n0,exc_n1,exc_n2,exc_n3,exc_s0,exc_s1,exc_s2,exc_s3,exc_unresolved,g1_obs,g1_null,g1_null_sd,g1_bins,g1_events,g2_spread,ext_boundary,hole_boundary\n");
        for (k, (b, t)) in r.bands.iter().zip(&r.tallies).enumerate() {
            assert_eq!(b.steps, b.b_dep + b.i_dep);
            assert_eq!(t.steps, b.steps, "tally departures differ from accountant");
            assert_eq!(t.depth_steps[0], b.b_dep, "depth 0 must be the probe's boundary label");
            assert_eq!(t.depth_steps.iter().sum::<u64>(), t.steps);
            let (o, m, sd, nb, ne) = return_gates::concentration(t, mix64(fnv(spec) ^ (k as u64 + 1)), DRAWS);
            let g2 = return_gates::return_spread(&t.exc_n, &t.exc_steps, MIN_EXC);
            let (ext, hole) = r.holes[k].map_or((String::new(), String::new()), |(e, h)| (e.to_string(), h.to_string()));
            let d = &t.depth_steps;
            let mut row: Vec<String> = vec![spec.clone(), k.to_string(), b.lo.to_string(), b.hi.to_string(), (b.reached_lo as u8).to_string(), (b.reached_hi as u8).to_string(),
                b.steps.to_string(), b.b_dep.to_string(), b.i_dep.to_string(), b.area_end.to_string(), b.perim_end.to_string(), format!("{:?}", b.sum_pa)];
            row.extend(d.iter().map(|v| v.to_string()));
            row.extend([t.exits, t.entries, t.reclass_in, t.reclass_out, t.b_runs, t.b_run_steps].map(|v| v.to_string()));
            row.extend(t.exc_n.iter().chain(&t.exc_steps).map(|v| v.to_string()));
            row.push(t.exc_unresolved.to_string());
            row.extend([o, m, sd].map(|v| format!("{v:?}")));
            row.extend([nb.to_string(), ne.to_string(), format!("{g2:?}"), ext, hole]);
            assert_eq!(row.len(), 41);
            csv.push_str(&row.join(","));
            csv.push('\n');
        }
        let stop = match r.stop { Stop::Sink => "complete", Stop::Budget => "budget", Stop::Escaped => "escaped" };
        let status = format!("spec,stop,t_final,cells\n{spec},{stop},{},{}\n", r.t, r.cells);
        for (suffix, body) in [("gates.csv", csv), ("status.csv", status), ("done", marker.clone())] {
            let tmp = out.join(format!("{name}.{suffix}.tmp"));
            std::fs::write(&tmp, body).unwrap();
            std::fs::rename(tmp, out.join(format!("{name}.{suffix}"))).unwrap();
        }
        eprintln!("{spec} {stop} t={} cells={} seconds={:.3}", r.t, r.cells, clock.elapsed().as_secs_f64());
    });
}
