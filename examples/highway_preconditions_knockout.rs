//! highway_preconditions_knockout RESULTS_DIR
//! Experiment `2026-10-21-highway-preconditions`, Part 2. For each independent event in RESULTS_DIR/events.csv (first
//! row per `used`), rebuild the board at `tau_pre`, knock out (set to 0) each pre-onset seed cell in turn (cells from
//! seeds.tsv `pre_key`, in the ant's frame), run `B = (onset - tau_pre) + 200p` steps and score whether the original
//! highway (period, drift) holds over the last 20p steps. Controls: no knock-out (K2) and up to 3 nonzero non-seed cells
//! (K1, trajectory must be identical). Writes RESULTS_DIR/knockout.csv. Deterministic; rayon over events, output in order.
use rayon::prelude::*;
use std::collections::HashSet;
use std::io::Write as _;
use turmite::{DIRS, Rule};

struct Event {
    rule: Rule,
    used: String,
    p: u64,
    d: (i32, i32),
    onset: u64,
    tau_pre: u64,
    size: usize,
    seed: Vec<(i32, i32)>,
}

/// Inverse of `seed::to_ant_frame`: ant-frame offset back to board offset.
fn from_ant_frame(v: (i32, i32), heading: u8) -> (i32, i32) {
    let mut v = v;
    for _ in 0..heading {
        v = (-v.1, v.0);
    }
    v
}

struct Board {
    size: usize,
    cells: Vec<u8>,
    pos: (i64, i64),
    h: u8,
}

impl Board {
    fn idx(&self, p: (i64, i64)) -> Option<usize> {
        let c = (self.size / 2) as i64;
        let (x, y) = (p.0 + c, p.1 + c);
        (x >= 0 && y >= 0 && x < self.size as i64 && y < self.size as i64).then(|| y as usize * self.size + x as usize)
    }
    /// Runs `k` steps, appending positions; false if the ant left the board.
    fn run(&mut self, turn: &[u8], n: u8, k: u64, path: &mut Vec<(i32, i32)>) -> bool {
        for _ in 0..k {
            let Some(i) = self.idx(self.pos) else { return false };
            let c = self.cells[i];
            self.h = (self.h + turn[c as usize]) & 3;
            self.cells[i] = (c + 1) % n;
            let (dx, dy) = DIRS[self.h as usize];
            self.pos = (self.pos.0 + dx as i64, self.pos.1 + dy as i64);
            path.push((self.pos.0 as i32, self.pos.1 as i32));
        }
        true
    }
}

fn launches(path: &[(i32, i32)], p: usize, d: (i32, i32)) -> bool {
    let n = path.len();
    n >= 21 * p && (n - 20 * p..n).all(|t| (path[t].0 - path[t - p].0, path[t].1 - path[t - p].1) == d)
}

/// Exploratory: the same period with the drift turned by a quarter turn or reflected (a highway of the same length
/// heading another way).
fn launches_any_direction(path: &[(i32, i32)], p: usize, d: (i32, i32)) -> bool {
    [(d.0, d.1), (-d.1, d.0), (-d.0, -d.1), (d.1, -d.0), (d.1, d.0), (-d.0, d.1), (d.0, -d.1), (-d.1, -d.0)]
        .iter()
        .any(|&dd| launches(path, p, dd))
}

fn event(e: &Event) -> String {
    let n = e.rule.len() as u8;
    let turn: Vec<u8> = e.rule.0.iter().map(|t| t.delta()).collect();
    let mut b = Board { size: e.size, cells: vec![0; e.size * e.size], pos: (0, 0), h: 0 };
    let mut sink = Vec::new();
    for chunk in 0..e.tau_pre.div_ceil(1 << 20) {
        let k = (e.tau_pre - chunk * (1 << 20)).min(1 << 20);
        assert!(b.run(&turn, n, k, &mut sink));
        sink.clear();
    }
    let budget = (e.onset - e.tau_pre) + 200 * e.p;
    let abs: Vec<(i64, i64)> = e
        .seed
        .iter()
        .map(|&v| {
            let r = from_ant_frame(v, b.h);
            (b.pos.0 + r.0 as i64, b.pos.1 + r.1 as i64)
        })
        .collect();
    let mut out = String::new();
    let seed_ok = abs.iter().all(|&q| b.cells[b.idx(q).unwrap()] != 0);
    let run_from = |knock: Option<(i64, i64)>| -> (bool, Vec<(i32, i32)>) {
        let mut w = Board { size: b.size, cells: b.cells.clone(), pos: b.pos, h: b.h };
        if let Some(q) = knock {
            let i = w.idx(q).unwrap();
            w.cells[i] = 0;
        }
        let mut path = Vec::with_capacity(budget as usize);
        let on = w.run(&turn, n, budget, &mut path);
        (on, path)
    };
    let (on0, base) = run_from(None);
    let base_ok = on0 && launches(&base, e.p as usize, e.d);
    out += &format!("{},{},{},{},base,-1,,,0,{},{},{},\n", e.rule, e.used, e.p, e.onset, base_ok, true, seed_ok);
    let seedset: HashSet<(i64, i64)> = abs.iter().copied().collect();
    let mut controls = vec![];
    'scan: for y in 0..b.size {
        for x in 0..b.size {
            if b.cells[y * b.size + x] != 0 {
                let c = (b.size / 2) as i64;
                let q = (x as i64 - c, y as i64 - c);
                if !seedset.contains(&q) {
                    controls.push(q);
                    if controls.len() == 3 {
                        break 'scan;
                    }
                }
            }
        }
    }
    for (k, &q) in controls.iter().enumerate() {
        let (on, path) = run_from(Some(q));
        out += &format!("{},{},{},{},control,{k},,,,{},{},{},\n", e.rule, e.used, e.p, e.onset, on && launches(&path, e.p as usize, e.d), path == base, seed_ok);
    }
    for (k, (&q, &v)) in abs.iter().zip(&e.seed).enumerate() {
        let colour = b.cells[b.idx(q).unwrap()];
        let (on, path) = run_from(Some(q));
        let cheb = v.0.abs().max(v.1.abs());
        out += &format!(
            "{},{},{},{},seed,{k},{},{},{cheb},{},{},{},{}\n",
            e.rule, e.used, e.p, e.onset, v.0, v.1, on && launches(&path, e.p as usize, e.d), path == base, colour,
            on && launches_any_direction(&path, e.p as usize, e.d)
        );
    }
    out
}

fn main() {
    let dir = std::path::PathBuf::from(std::env::args().nth(1).unwrap());
    let ev = std::fs::read_to_string(dir.join("events.csv")).unwrap();
    let sd = std::fs::read_to_string(dir.join("seeds.tsv")).unwrap();
    let mut lines = ev.lines();
    let head: Vec<&str> = lines.next().unwrap().split(',').collect();
    let col = |name: &str| head.iter().position(|h| *h == name).unwrap();
    let mut seen = HashSet::new();
    let mut events = vec![];
    for (row, srow) in lines.zip(sd.lines().skip(1)) {
        let f: Vec<&str> = row.split(',').collect();
        if !seen.insert(f[col("used")].to_string()) {
            continue;
        }
        let key = srow.split('\t').nth(6).unwrap_or("");
        let seed = key
            .split(';')
            .filter(|s| !s.is_empty())
            .map(|s| {
                let xy: Vec<i32> = s.split(':').next().unwrap().split(',').map(|v| v.parse().unwrap()).collect();
                (xy[0], xy[1])
            })
            .collect();
        events.push(Event {
            rule: f[col("rule")].parse().unwrap(),
            used: f[col("used")].to_string(),
            p: f[col("period")].parse().unwrap(),
            d: (f[col("dx")].parse().unwrap(), f[col("dy")].parse().unwrap()),
            onset: f[col("onset")].parse().unwrap(),
            tau_pre: f[col("tau_pre")].parse().unwrap(),
            size: f[col("board")].parse().unwrap(),
            seed,
        });
    }
    let rows: Vec<String> = events.par_iter().map(event).collect();
    let mut f = std::fs::File::create(dir.join("knockout.csv")).unwrap();
    writeln!(f, "rule,used,period,onset,kind,k,ax,ay,cheb,launches,identical,seed_ok_or_colour,any_direction").unwrap();
    for r in rows {
        f.write_all(r.as_bytes()).unwrap();
    }
}
