//! experiments/archive/2026-10-square-ring-fillers, P3/P5/P6: which visit counts does the ant read late in a blank-board run?
//! usage: square_ring_fillers_footprint STEPS GRID WINDOW [--fingerprint] < specs   (CSV on stdout, one row per spec, input order)
//! spec line: `RULE`, or `RULE>RULE2@T0` (run RULE for T0 steps, then continue with RULE2 on the same integer visit counts),
//! optionally followed by `#V` (report the first step after T0, or after 0, at which a count > V is read).
//! Plain loop from a blank GRID x GRID board, ant at the centre heading 0, turn = rule[visits mod n]; stops after STEPS
//! steps or when the ant leaves the board (same convention as `fast::run`). Visits are u32 per cell.
//! Columns: spec,n,stop,steps,visited,win_start,win_steps,win_new,win_maxread,reads,x0,x1,y0,y1,first_gt,fronts_after
//!   reads = histogram of counts read in the last full WINDOW steps (`v:count;...`, v <= 63, then `64+:count`); if the run
//!   stopped early, the window is the last WINDOW steps before the stop (or the whole run if shorter).
//!   fronts_after = times of the first 8 advances of the global xmax front after T0 (`t;t;...`), empty without `>`.
//! With --fingerprint, also x,y,h,hash,nonzero,vhash: hash/nonzero = FNV-1a of every cell's colour (visits mod n of the
//! final rule) row-major over the whole grid and the non-zero count, comparable with `fast::run` (via
//! `rlrlll_macro_transition_resim`); vhash = FNV-1a of the visit counts (identical trajectories <=> identical vhash, in practice).
use rayon::prelude::*;
use turmite::{DIRS, Rule};

struct Spec {
    text: String,
    r1: Rule,
    r2: Option<(Rule, u64)>,
    gt: Option<u32>,
}

fn parse(line: &str) -> Spec {
    let (body, gt) = match line.split_once('#') {
        Some((b, v)) => (b, Some(v.parse().unwrap())),
        None => (line, None),
    };
    let (r1, r2) = match body.split_once('>') {
        Some((a, rest)) => {
            let (b, t0) = rest.split_once('@').unwrap();
            (a.parse().unwrap(), Some((b.parse().unwrap(), t0.parse().unwrap())))
        }
        None => (body.parse().unwrap(), None),
    };
    Spec { text: line.to_string(), r1, r2, gt }
}

fn fnv(it: impl Iterator<Item = u64>) -> u64 {
    let mut h = 0xcbf29ce484222325u64;
    for c in it {
        h = (h ^ c).wrapping_mul(0x100000001b3);
    }
    h
}

fn run(spec: &Spec, cells: &mut Vec<u32>, size: usize, steps: u64, win: u64, fp: bool) -> String {
    // Reuse the buffer: clear only the touched bounding box of the previous run.
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let (mut bx0, mut bx1, mut by0, mut by1) = (c, c, c, c);
    let tables: Vec<(Vec<u8>, u32)> = {
        let mk = |r: &Rule| (r.0.iter().map(|t| t.delta()).collect::<Vec<u8>>(), r.len() as u32);
        let mut v = vec![mk(&spec.r1)];
        if let Some((r2, _)) = &spec.r2 {
            v.push(mk(r2));
        }
        v
    };
    let t_switch = spec.r2.as_ref().map_or(u64::MAX, |(_, t0)| *t0);
    let t_after = spec.r2.as_ref().map_or(0, |(_, t0)| *t0);
    let mut cur = 0usize;
    let mut visited: u64 = 1;
    cells[(y as usize) * size + x as usize] = 0;
    // Ring buffer of the last WINDOW reads, as counts per capped value, maintained by adding the new read and removing the
    // read that falls out of the window (reads are stored in a circular byte buffer).
    let wlen = win as usize;
    let mut ring = vec![0u8; wlen];
    let mut hist = [0u64; 65];
    let mut newflag = vec![false; wlen];
    let mut win_new: u64 = 0;
    let mut first_gt: Option<u64> = None;
    let mut fronts: Vec<u64> = Vec::new();
    let mut xmax = x;
    let mut stop = "budget";
    let mut t: u64 = 0;
    let mut slot: usize = 0;
    while t < steps {
        if t == t_switch {
            cur = 1;
        }
        let (turn, n) = (&tables[cur].0, tables[cur].1);
        let i = (y as usize) * size + x as usize;
        let v = cells[i];
        h = (h + turn[(v % n) as usize]) & 3;
        cells[i] = v + 1;
        let cap = v.min(64) as usize;
        if t >= win {
            hist[ring[slot] as usize] -= 1;
            if newflag[slot] {
                win_new -= 1;
            }
        }
        ring[slot] = cap as u8;
        hist[cap] += 1;
        if let Some(g) = spec.gt {
            if first_gt.is_none() && t >= t_after && v > g {
                first_gt = Some(t);
            }
        }
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        t += 1;
        if x < 0 || y < 0 || x >= size as i64 || y >= size as i64 {
            stop = "escaped";
            newflag[slot] = false;
            break;
        }
        let cur_slot = slot;
        slot += 1;
        if slot == wlen {
            slot = 0;
        }
        let j = (y as usize) * size + x as usize;
        // A cell is new when first stepped on: it has 0 visits because the ant has never left it.
        let fresh = cells[j] == 0;
        newflag[cur_slot] = fresh;
        if fresh {
            visited += 1;
            win_new += 1;
        }
        bx0 = bx0.min(x);
        bx1 = bx1.max(x);
        by0 = by0.min(y);
        by1 = by1.max(y);
        if x > xmax {
            xmax = x;
            if spec.r2.is_some() && t > t_after && fronts.len() < 8 {
                fronts.push(t);
            }
        }
    }
    let wsteps = t.min(win);
    let win_start = t - wsteps;
    let maxread = (0..65).rev().find(|&v| hist[v] > 0).unwrap_or(0);
    let mut reads: Vec<String> = (0..64).filter(|&v| hist[v] > 0).map(|v| format!("{v}:{}", hist[v])).collect();
    if hist[64] > 0 {
        reads.push(format!("64+:{}", hist[64]));
    }
    let n_final = tables[cur].1;
    let mut row = format!(
        "{},{},{stop},{t},{visited},{win_start},{wsteps},{win_new},{},{},{},{},{},{},{},{}",
        spec.text,
        n_final,
        if maxread == 64 { "64+".to_string() } else { maxread.to_string() },
        reads.join(";"),
        bx0 - c,
        bx1 - c,
        by0 - c,
        by1 - c,
        first_gt.map_or(String::new(), |v| v.to_string()),
        fronts.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(";")
    );
    if fp {
        let hash = fnv(cells.iter().map(|&v| (v % n_final) as u64));
        let nz = cells.iter().filter(|&&v| v % n_final != 0).count();
        let vhash = fnv(cells.iter().map(|&v| v as u64));
        row += &format!(",{},{},{h},{hash:016x},{nz},{vhash:016x}", x - c, y - c);
    }
    // Clear the touched box (plus the cell the ant left on, if outside after escape it is off-grid anyway).
    for yy in by0.max(0)..=by1.min(size as i64 - 1) {
        let r = (yy as usize) * size;
        cells[r + bx0.max(0) as usize..=r + bx1.min(size as i64 - 1) as usize].fill(0);
    }
    row
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let steps: u64 = a[1].parse().unwrap();
    let size: usize = a[2].parse().unwrap();
    let win: u64 = a[3].parse().unwrap();
    let fp = a.iter().any(|s| s == "--fingerprint");
    let specs: Vec<Spec> = std::io::stdin()
        .lines()
        .map(|l| l.unwrap())
        .filter(|l| !l.trim().is_empty())
        .map(|l| parse(l.trim()))
        .collect();
    let rows: Vec<String> = specs
        .par_iter()
        .map_init(|| vec![0u32; size * size], |cells, s| run(s, cells, size, steps, win, fp))
        .collect();
    let mut head = "spec,n,stop,steps,visited,win_start,win_steps,win_new,win_maxread,reads,x0,x1,y0,y1,first_gt,fronts_after".to_string();
    if fp {
        head += ",x,y,h,hash,nonzero,vhash";
    }
    println!("{head}");
    for r in rows {
        println!("{r}");
    }
}
