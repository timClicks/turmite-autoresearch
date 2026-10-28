//! lattice_c_law_colours LOG2 SIZE < specs > traces.jsonl
//! One spec per line: `LATTICE RULE` (LATTICE in square|hex|tri). One JSON line per spec, in spec order
//! (independent of thread count): the `lattice_trace` fields for the last octave (steps (2^(LOG2-1), 2^LOG2]).
//! Used by experiments/archive/2026-10-lattice-c-law-colours.

use rayon::prelude::*;
use std::io::Read;
use turmite::lattice_probe::Lattice;
use turmite::lattice_trace::*;

fn arr(v: &[u64]) -> String {
    format!("[{}]", v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","))
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (log2, size): (u32, usize) = (a[1].parse().unwrap(), a[2].parse().unwrap());
    let mut s = String::new();
    std::io::stdin().read_to_string(&mut s).unwrap();
    let specs: Vec<(Lattice, &str, String)> = s
        .lines()
        .map(|l| l.trim())
        .filter(|l| !l.is_empty())
        .map(|l| {
            let (lat, r) = l.split_once(' ').expect("LATTICE RULE");
            let (name, lat) = match lat {
                "square" => ("square", Lattice::Square),
                "hex" => ("hex", Lattice::Hex),
                "tri" => ("tri", Lattice::Tri),
                o => panic!("bad lattice {o}"),
            };
            (lat, name, r.trim().strip_prefix("ant:").unwrap_or(r.trim()).to_string())
        })
        .collect();
    let rows: Vec<String> = specs
        .par_iter()
        .map(|(lat, name, rule)| {
            let t = lattice_trace(*lat, rule, size, log2);
            let nc = 24;
            let col = |f: &dyn Fn(&Tally) -> u64| arr(&t.by_colour[..nc].iter().map(f).collect::<Vec<_>>());
            let lag = t.lag.iter().map(|l| arr(&l[..41])).collect::<Vec<_>>().join(",");
            format!(
                "{{\"lattice\":\"{name}\",\"rule\":\"{rule}\",\"log2\":{log2},\"births\":{},\"boundary_steps\":{},\"area\":{},\"escaped\":{},\"hole_births\":{},\
\"edge\":{},\"col_births\":{},\"lag\":[{lag}],\"nb_resolved\":{},\"nb_censored\":{},\"loop_len\":{},\"run_count\":{},\"run_boundary\":{}}}",
                t.births, t.boundary_steps, t.area, t.escaped, t.hole_births, col(&|x| x.edge), col(&|x| x.births),
                arr(&t.nb_resolved[..41]), arr(&t.nb_censored[..41]), t.loop_len, arr(&t.run_count), arr(&t.run_boundary)
            )
        })
        .collect();
    for r in rows {
        println!("{r}");
    }
}
