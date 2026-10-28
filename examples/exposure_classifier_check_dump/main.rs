//! exposure_classifier_check_dump OUT_DIR
//!
//! Truth-table and scripted-walk dump of the exposure classifier in `examples/kappa_exposure_classes.rs`
//! (experiment 2026-10-exposure-classifier-check). The instrument keeps `Region` and `run` private
//! and its `//!` header cannot be `include!`d, so `instrument_body.rs` is a byte-for-byte copy of its
//! lines 20-248; `main` refuses to run unless the instrument source still contains that copy verbatim.
//!
//! Writes OUT_DIR/table.csv (every visited pattern of a 3x3 window, every visit order),
//! OUT_DIR/walks.csv (per-window counters of scripted walks through the instrument's `run`, plus the
//! probe's own counters) and OUT_DIR/paths.csv (the scripted headings, for independent replay).
//! Deterministic: no threads are used for output order, random walks are seeded with splitmix.

mod kec {
    #![allow(dead_code, unused_imports)]
    include!("instrument_body.rs");

    use std::fmt::Write as _;
    use std::rc::Rc;

    pub const W: usize = 3;
    const BOARD: usize = 5;

    fn window_index(w: usize) -> usize {
        let (x, y) = (w % W + 1, w / W + 1);
        y * BOARD + x
    }

    /// Next permutation in lexicographic order; false when exhausted.
    fn next_perm(a: &mut [usize]) -> bool {
        if a.len() < 2 {
            return false;
        }
        let mut i = a.len() - 1;
        while i > 0 && a[i - 1] >= a[i] {
            i -= 1;
        }
        if i == 0 {
            return false;
        }
        let mut j = a.len() - 1;
        while a[j] <= a[i - 1] {
            j -= 1;
        }
        a.swap(i - 1, j);
        a[i..].reverse();
        true
    }

    /// For each 9-bit pattern: visit its cells in every order with the instrument's `Region::visit`
    /// and record the stored class of every window cell, the incremental bins `pc` and whether
    /// `scan()` agrees. Rows: mask,n_visited,n_orders,n_distinct,u0..u8,pc0..pc4,scan_ok.
    pub fn table() -> String {
        let mut out = String::from("mask,n_visited,n_orders,n_distinct,u0,u1,u2,u3,u4,u5,u6,u7,u8,pc0,pc1,pc2,pc3,pc4,scan_ok\n");
        for mask in 0u32..(1 << (W * W)) {
            let mut cells: Vec<usize> = (0..W * W).filter(|w| mask >> w & 1 == 1).collect();
            let mut outcomes: Vec<(Vec<u8>, [u64; 5])> = vec![];
            let mut n_orders = 0u64;
            let mut scan_ok = true;
            loop {
                let mut r = Region::new(BOARD);
                for &w in &cells {
                    r.visit(window_index(w));
                }
                n_orders += 1;
                scan_ok &= r.scan() == r.pc;
                let o = ((0..W * W).map(|w| r.unv[window_index(w)]).collect::<Vec<u8>>(), r.pc);
                if !outcomes.contains(&o) {
                    outcomes.push(o);
                }
                if !next_perm(&mut cells) {
                    break;
                }
            }
            let (u, pc) = &outcomes[0];
            let us: Vec<String> = u.iter().map(|v| v.to_string()).collect();
            let pcs: Vec<String> = pc.iter().map(|v| v.to_string()).collect();
            writeln!(out, "{mask},{},{n_orders},{},{},{},{}", mask.count_ones(), outcomes.len(), us.join(","), pcs.join(","), scan_ok).unwrap();
        }
        out
    }

    /// A walker that follows a fixed list of headings (0 N, 1 E, 2 S, 3 W as in `DIRS`).
    #[derive(Clone)]
    pub struct Scripted {
        path: Rc<Vec<u8>>,
        t: usize,
    }

    impl Walker for Scripted {
        const RANDOM_INIT: bool = false;
        fn initial_cell(&self, _: i64, _: i64) -> u8 {
            0
        }
        fn step(&mut self, _cell: &mut u8, heading: &mut u8) {
            *heading = self.path[self.t];
            self.t += 1;
        }
    }

    fn dir(from: (i64, i64), to: (i64, i64)) -> u8 {
        let d = (to.0 - from.0, to.1 - from.1);
        DIRS.iter().position(|&(dx, dy)| (dx as i64, dy as i64) == d).unwrap() as u8
    }

    /// Closed depth-first tour of a 4-connected cell set from (0, 0), repeated to `len` headings.
    fn tour(set: &[(i64, i64)], len: usize) -> Vec<u8> {
        fn dfs(at: (i64, i64), set: &[(i64, i64)], seen: &mut Vec<(i64, i64)>, out: &mut Vec<u8>) {
            seen.push(at);
            for &(dx, dy) in &DIRS {
                let n = (at.0 + dx as i64, at.1 + dy as i64);
                if set.contains(&n) && !seen.contains(&n) {
                    out.push(dir(at, n));
                    dfs(n, set, seen, out);
                    out.push(dir(n, at));
                }
            }
        }
        let (mut seen, mut one) = (vec![], vec![]);
        dfs((0, 0), set, &mut seen, &mut one);
        assert_eq!(seen.len(), set.len(), "set not connected");
        one.iter().copied().cycle().take(len).collect()
    }

    /// Random walk confined to |x|, |y| <= r (moves leaving the box are redrawn), seeded splitmix.
    fn bounded_rw(seed: u64, r: i64, len: usize) -> Vec<u8> {
        let (mut st, mut p, mut out) = (seed, (0i64, 0i64), vec![]);
        while out.len() < len {
            let h = (splitmix_next(&mut st) & 3) as u8;
            let (dx, dy) = DIRS[h as usize];
            let q = (p.0 + dx as i64, p.1 + dy as i64);
            if q.0.abs() <= r && q.1.abs() <= r {
                out.push(h);
                p = q;
            }
        }
        out
    }

    pub fn walks() -> (String, String) {
        let mut specs: Vec<(String, u32, Vec<u8>)> = vec![];
        for mask in 0u32..(1 << (W * W)) {
            if mask >> 4 & 1 == 0 || mask.count_ones() < 2 {
                continue;
            }
            let set: Vec<(i64, i64)> = (0..W * W).filter(|w| mask >> w & 1 == 1).map(|w| ((w % W) as i64 - 1, (w / W) as i64 - 1)).collect();
            // keep only 4-connected sets: a walker's visited set always is one
            let mut reach = vec![(0i64, 0i64)];
            let mut i = 0;
            while i < reach.len() {
                let a = reach[i];
                for &(dx, dy) in &DIRS {
                    let n = (a.0 + dx as i64, a.1 + dy as i64);
                    if set.contains(&n) && !reach.contains(&n) {
                        reach.push(n);
                    }
                }
                i += 1;
            }
            if reach.len() == set.len() {
                specs.push((format!("tour{mask}"), 10, tour(&set, 1 << 10)));
            }
        }
        for seed in 1..=64u64 {
            specs.push((format!("rw{seed}"), 12, bounded_rw(seed, 6, 1 << 12)));
        }
        let size = 64;
        let mut rows = String::from("walk,max_log2,k,area,p0,p1,p2,p3,p4,new_cells,b1,b2,b3,b4,f1,f2,f3,f4,probe_area,probe_perimeter,probe_new_cells,probe_boundary_steps,probe_fresh_nbrs,escaped\n");
        let mut paths = String::from("walk,max_log2,path\n");
        for (name, max_log2, path) in &specs {
            let path = Rc::new(path.clone());
            let w = || Scripted { path: path.clone(), t: 0 };
            let o = walker_out(w(), size, *max_log2, true);
            check_against_probe(w(), &o, size, *max_log2);
            let pr = probe_walker(w(), size, 8, *max_log2);
            assert_eq!(pr.windows.len(), o.wins.len());
            for (a, b) in pr.windows.iter().zip(&o.wins) {
                writeln!(
                    rows,
                    "{name},{max_log2},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}",
                    b.k + 1, b.area, b.p[0], b.p[1], b.p[2], b.p[3], b.p[4], b.new_cells,
                    b.b[1], b.b[2], b.b[3], b.b[4], b.f[1], b.f[2], b.f[3], b.f[4],
                    a.area, a.perimeter, a.new_cells, a.boundary_steps, a.fresh_nbrs, o.escaped
                )
                .unwrap();
            }
            let s: String = path.iter().map(|h| char::from(b'0' + h)).collect();
            writeln!(paths, "{name},{max_log2},{s}").unwrap();
        }
        (rows, paths)
    }
}

fn main() {
    let instrument = include_str!("../kappa_exposure_classes.rs");
    let body = include_str!("instrument_body.rs");
    assert!(instrument.contains(body), "instrument_body.rs is no longer a verbatim copy of examples/kappa_exposure_classes.rs");
    let dir = std::path::PathBuf::from(std::env::args().nth(1).expect("OUT_DIR"));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("table.csv"), kec::table()).unwrap();
    let (rows, paths) = kec::walks();
    std::fs::write(dir.join("walks.csv"), rows).unwrap();
    std::fs::write(dir.join("paths.csv"), paths).unwrap();
    eprintln!("wrote table.csv, walks.csv, paths.csv to {}", dir.display());
}
