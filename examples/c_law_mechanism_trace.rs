//! Driver for `edge_trace` (experiments/archive/2026-10-c-law-mechanism). One JSON line per spec, deterministic.
//!
//!   c_law_mechanism_trace blank LOG2 SIZE   < specs.txt     # blank board, as the probe
//!   c_law_mechanism_trace band  LOG2 W H BANDROWS SEED < rules.txt   # torus, fresh band of BANDROWS rows
//!
//! Specs (blank): RULE | sbg:RULE:SEED:DENSITY | rotor:SEED | rw:SEED.  Specs (band): RULE.
//! Band: rows 0..BANDROWS are fresh (colour 0); all other rows start visited with i.i.d. uniform colours
//! 0..n-1 (hash of SEED and position). The ant starts on a visited cell next to the band, heading north.
//! Parallel over specs with rayon, output in input order, so bytes do not depend on the thread count.

use rayon::prelude::*;
use std::io::Read;
use turmite::Rule;
use turmite::edge_trace::*;
use turmite::walkers::{AntWalker, RandomWalk, Rotor, SparseBgAnt, mix64};

fn arr(v: &[u64]) -> String {
    format!("[{}]", v.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","))
}

fn json(spec: &str, t: &EdgeTrace, log2: u32) -> String {
    let nc = 24;
    let col = |f: &dyn Fn(&Tally) -> u64| arr(&t.by_colour[..nc].iter().map(f).collect::<Vec<_>>());
    let lag = t.lag.iter().map(|l| arr(&l[..41])).collect::<Vec<_>>().join(",");
    format!(
        "{{\"spec\":\"{spec}\",\"log2\":{log2},\"births\":{},\"boundary_steps\":{},\"fresh_nbrs\":{},\"area\":{},\"area_t0\":{},\"perimeter\":{},\"escaped\":{},\
\"edge\":{},\"col_births\":{},\"ahead\":{},\"left\":{},\"right\":{},\"lag\":[{lag}],\"nb_resolved\":{},\"nb_censored\":{},\"chain\":{}}}",
        t.births, t.boundary_steps, t.fresh_nbrs, t.area, t.area_t0, t.perimeter, t.escaped,
        col(&|x| x.edge), col(&|x| x.births), col(&|x| x.ahead), col(&|x| x.left), col(&|x| x.right),
        arr(&t.nb_resolved[..41]), arr(&t.nb_censored[..41]), arr(&t.chain[..17])
    )
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let mut input = String::new();
    std::io::stdin().read_to_string(&mut input).unwrap();
    let specs: Vec<&str> = input.lines().map(|l| l.trim()).filter(|l| !l.is_empty()).collect();
    let log2: u32 = a[2].parse().unwrap();
    let out: Vec<String> = match a[1].as_str() {
        "blank" => {
            let size: usize = a[3].parse().unwrap();
            specs
                .par_iter()
                .map(|s| {
                    let t = if let Some(sd) = s.strip_prefix("rotor:") {
                        trace_blank(Rotor { seed: sd.parse().unwrap() }, size, log2)
                    } else if let Some(sd) = s.strip_prefix("rw:") {
                        trace_blank(RandomWalk { state: sd.parse().unwrap() }, size, log2)
                    } else if let Some(p) = s.strip_prefix("sbg:") {
                        let p: Vec<&str> = p.split(':').collect();
                        trace_blank(SparseBgAnt::new(&p[0].parse::<Rule>().unwrap(), p[1].parse().unwrap(), p[2].parse().unwrap()), size, log2)
                    } else {
                        trace_blank(AntWalker::new(&s.parse::<Rule>().unwrap()), size, log2)
                    };
                    json(s, &t, log2)
                })
                .collect()
        }
        "band" => {
            let (w, h, band, seed): (usize, usize, usize, u64) = (a[3].parse().unwrap(), a[4].parse().unwrap(), a[5].parse().unwrap(), a[6].parse().unwrap());
            // interior kind: U uniform 0..n-1 (default), Z all 0, Y uniform 1..=m, H uniform m..n-1 (m = the rule's lead)
            let kind = a.get(7).map(|s| s.as_str()).unwrap_or("U").to_string();
            specs
                .par_iter()
                .map(|s| {
                    // "RULE" uses LOG2; "RULE@L" overrides it for that rule
                    let (rs, l) = match s.split_once('@') {
                        Some((r, l)) => (r, l.parse::<u32>().unwrap()),
                        None => (*s, log2),
                    };
                    let rule: Rule = rs.parse().unwrap();
                    let n = rule.len() as u64;
                    let b = rs.as_bytes();
                    let m = b.iter().take_while(|&&c| c == b[0]).count() as u64;
                    let kind = kind.clone();
                    let prefill = move |x: usize, y: usize| -> Option<u8> {
                        if y < band {
                            return None;
                        }
                        let r = mix64(mix64(seed) ^ ((x as u64) << 32 | y as u64));
                        Some(match kind.as_str() {
                            "Z" => 0,
                            "Y" => (1 + r % m.min(n - 1)) as u8,
                            "H" => (m.min(n - 1) + r % (n - m.min(n - 1))) as u8,
                            _ => (r % n) as u8,
                        })
                    };
                    let t = trace(AntWalker::new(&rule), Layout { w, h, wrap: true }, &prefill, (w / 2, band, 0), l);
                    json(&format!("{rs}@{l}"), &t, l)
                })
                .collect()
        }
        m => panic!("unknown mode {m}"),
    };
    for l in out {
        println!("{l}");
    }
}
