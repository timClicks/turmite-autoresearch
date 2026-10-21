//! highway_preconditions_scan highway SPECFILE OUTDIR
//! highway_preconditions_scan control SPECFILE OUTDIR
//!
//! Experiment `2026-10-21-highway-preconditions` (see its README for definitions).
//! `highway`: SPECFILE lines `RULE PERIOD DX DY ONSET` (census values). Per rule: the dependency
//! curve |D(tau)| around onset, the seed D(tau*) with turn words in the ant's frame, and a
//! transplant check of the seed. Writes events.csv, seeds.tsv, curves.csv.
//! `control`: SPECFILE lines `RULE`. Truncated |D_delta(tau)|, delta = 20000, over
//! tau in [1e6, 1e6 + 50000). Writes control.csv.
//! Deterministic; rayon over rules, output in spec order.
use rayon::prelude::*;
use std::fmt::Write as _;
use std::io::Write as _;
use turmite::Rule;
use turmite::seed::{DepCounter, NEVER, Read, SeedCollector, Tracked, least_rotation, to_ant_frame};

const DELTA: u64 = 20_000;
const MARGIN: i32 = 64;
const MAX_SIZE: usize = 16_384;

struct Spec {
    rule: Rule,
    p: u64,
    d: (i32, i32),
    onset: u64,
}

#[derive(Debug)]
struct OffBoard;

fn word(w: &[u8]) -> String {
    w.iter().map(|&t| if t == 1 { 'R' } else { 'L' }).collect()
}

fn fnv(s: &str) -> u64 {
    s.bytes().fold(0xcbf29ce484222325u64, |h, b| (h ^ b as u64).wrapping_mul(0x100000001b3))
}

fn step(a: &mut Tracked) -> Result<Read, OffBoard> {
    a.step().ok_or(OffBoard)
}

/// Seed cells as `dx,dy:WORD;` in the ant's frame (heading north), sorted.
fn seed_key(sc: &SeedCollector, ant: (i32, i32), heading: u8) -> String {
    let mut key: Vec<((i32, i32), String)> =
        sc.cells.iter().map(|c| (to_ant_frame((c.pos.0 - ant.0, c.pos.1 - ant.1), heading), word(&c.word))).collect();
    key.sort();
    let mut s = String::new();
    for ((x, y), wd) in &key {
        let _ = write!(s, "{x},{y}:{wd};");
    }
    s
}

fn highway(s: &Spec, size: usize) -> Result<(String, String, String), OffBoard> {
    let (p, t_on) = (s.p, s.onset);
    let w = t_on.min((100 * p).max(50_000));
    // README Deviation 1: never reach back to the blank board, where |D| = 0 trivially.
    let (lo, hi) = ((t_on - w).max(t_on.div_ceil(2)), t_on + 20 * p);
    let (c0, c1) = if t_on / 2 < lo { (t_on / 2, lo) } else { (t_on / 4, t_on / 2) };
    let mut chaotic: Vec<u64> = vec![];
    if c0 < c1 && c0 > 0 {
        let (a, b) = (c0 as f64, (c1 - 1) as f64);
        chaotic = (0..32).map(|k| (a * (b / a.max(1.0)).powf(k as f64 / 31.0)).round() as u64).collect();
        chaotic.dedup();
        chaotic.retain(|&x| x < c1);
    }
    let mut queries = chaotic.clone();
    queries.extend(lo..hi);

    // Pass A: dependency counts, onset, highway word, colours used, end of the read window.
    let mut a = Tracked::new(&s.rule, size);
    let mut dc = DepCounter::new(queries, DELTA);
    let mut ring = vec![(0i32, 0i32); p as usize];
    let mut last_bad = 0u64;
    let (mut bx0, mut by0, mut bx1, mut by1) = (0, 0, 0, 0);
    let mut hw_word = vec![];
    let mut max_colour = 0u8;
    let mut t_end = u64::MAX;
    let mut t_end2 = u64::MAX;
    while a.t < t_end2 {
        let r = step(&mut a)?;
        if r.t <= t_end {
            dc.observe(&r);
        }
        max_colour = max_colour.max(r.colour);
        let slot = (r.t % p) as usize;
        let prev = ring[slot];
        ring[slot] = a.pos;
        if r.t < p || (a.pos.0 - prev.0, a.pos.1 - prev.1) != s.d {
            last_bad = r.t;
        }
        if r.t <= hi {
            (bx0, by0, bx1, by1) = (bx0.min(r.pos.0), by0.min(r.pos.1), bx1.max(r.pos.0), by1.max(r.pos.1));
        } else if r.t <= hi + p {
            hw_word.push(r.turn);
        }
        if t_end == u64::MAX && r.t >= t_on + 40 * p {
            let (x, y) = a.pos;
            if x < bx0 - MARGIN || x > bx1 + MARGIN || y < by0 - MARGIN || y > by1 + MARGIN {
                t_end = r.t + 20 * p;
                t_end2 = t_end + 200 * p;
            }
        }
    }
    let my_onset = (last_bad + 1).saturating_sub(p);
    let (full, trunc) = dc.finish();
    let nc = chaotic.len();
    let dense = &full[nc..];
    let at = |tau: u64| dense[(tau - lo) as usize];
    let dmin = *dense.iter().min().unwrap();
    let k_star = dense.iter().position(|&v| v == dmin).unwrap();
    let tau_star = lo + k_star as u64;
    let pre = &dense[..=(t_on - lo) as usize];
    let d_pre = *pre.iter().min().unwrap();
    let tau_pre = lo + pre.iter().position(|&v| v == d_pre).unwrap() as u64;
    let d_onset = at(t_on);
    let hwin = &dense[(t_on + 10 * p - lo) as usize..];
    let (h_min, h_max) = (*hwin.iter().min().unwrap(), *hwin.iter().max().unwrap());
    let mut launch = hi;
    for k in (0..dense.len()).rev() {
        if dense[k] > h_max {
            break;
        }
        launch = lo + k as u64;
    }
    let chaos_level = if nc > 0 {
        let mut v = full[..nc].to_vec();
        v.sort();
        v[nc / 2] as f64
    } else {
        f64::NAN
    };
    let d_trunc_star = trunc[nc + k_star];
    drop(a);

    // Pass B: the seed itself, territory geometry at tau*, and the path for the transplant.
    let mut b = Tracked::new(&s.rule, size);
    let mut pre_sc = SeedCollector::new(tau_pre);
    while b.t < tau_pre {
        step(&mut b)?;
    }
    let (ant_pre, heading_pre) = (b.pos, b.heading);
    while b.t < tau_star {
        let r = step(&mut b)?;
        pre_sc.observe(&r);
    }
    let (ant, heading) = (b.pos, b.heading);
    let half = (size / 2) as i64;
    let (mut n_old, mut sx, mut sy) = (0u64, 0f64, 0f64);
    let (mut ox0, mut oy0, mut ox1, mut oy1) = (i32::MAX, i32::MAX, i32::MIN, i32::MIN);
    for (i, &l) in b.last.iter().enumerate() {
        if l != NEVER {
            let (x, y) = ((i % size) as i64 - half, (i / size) as i64 - half);
            let (x, y) = (x as i32, y as i32);
            n_old += 1;
            sx += x as f64;
            sy += y as f64;
            (ox0, oy0, ox1, oy1) = (ox0.min(x), oy0.min(y), ox1.max(x), oy1.max(y));
        }
    }
    let (cx, cy) = (sx / n_old as f64, sy / n_old as f64);
    let (vx, vy) = (ant.0 as f64 - cx, ant.1 as f64 - cy);
    let cos_out = (vx * s.d.0 as f64 + vy * s.d.1 as f64) / ((vx * vx + vy * vy).sqrt() * ((s.d.0 * s.d.0 + s.d.1 * s.d.1) as f64).sqrt());
    let mut sc = SeedCollector::new(tau_star);
    let mut path = vec![];
    let mut old_read = std::collections::HashSet::new();
    let mut t_leave = tau_star;
    while b.t < t_end2 {
        let r = step(&mut b)?;
        if r.t <= t_end {
            sc.observe(&r);
            pre_sc.observe(&r);
            if r.prev != NEVER && r.prev <= tau_star {
                old_read.insert(r.pos);
            }
        }
        if r.pos.0 >= ox0 && r.pos.0 <= ox1 && r.pos.1 >= oy0 && r.pos.1 <= oy1 {
            t_leave = r.t;
        }
        path.push(r.pos);
    }
    drop(b);
    let cells: Vec<_> = sc.cells.iter().map(|c| (c.pos, c.colour)).collect();
    let mut tr = Tracked::with_cells(&s.rule, size, &cells, ant, heading, tau_star);
    let mut mismatch = 0u64;
    for &q in &path {
        let r = step(&mut tr)?;
        if r.pos != q {
            mismatch = r.t;
            break;
        }
    }

    let key_s = seed_key(&sc, ant, heading);
    let pre_key = seed_key(&pre_sc, ant_pre, heading_pre);
    let hw = word(&least_rotation(&hw_word));
    let n = s.rule.len() as u8;
    let used = if max_colour + 1 < n { format!("{}+", &s.rule.to_string()[..=max_colour as usize]) } else { s.rule.to_string() };
    let words_len: usize = sc.cells.iter().map(|c| c.word.len()).sum();
    let ev = format!(
        "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{:.6},{},{},{},{},{},{},{},{:016x},{:016x},{},{},{},{},{},{:016x}\n",
        s.rule, n, p, s.d.0, s.d.1, t_on, my_onset, w, tau_star, dmin, sc.cells.len(), h_min, h_max, launch,
        if nc > 0 { format!("{chaos_level}") } else { String::new() }, d_trunc_star, old_read.len(), n_old,
        t_leave, cos_out, t_end, t_end2, mismatch == 0, mismatch, max_colour, used, words_len, fnv(&key_s), fnv(&hw), size,
        lo, d_onset, tau_pre, d_pre, fnv(&pre_key)
    );
    let seed = format!("{}\t{}\t{}\t{}\t{}\t{}\t{}\n", s.rule, used, tau_star, hw, key_s, tau_pre, pre_key);
    let mut curve = String::new();
    for (k, &tau) in chaotic.iter().enumerate() {
        let _ = writeln!(curve, "{},chaos,{},{},{}", s.rule, tau as i64 - t_on as i64, full[k], full[k]);
    }
    let pbin = |tau: u64| (tau as i64 - t_on as i64).div_euclid(p as i64);
    let mut k = lo;
    while k < hi {
        let bin = pbin(k);
        let (mut mn, mut mx) = (u32::MAX, 0);
        while k < hi && pbin(k) == bin {
            mn = mn.min(at(k));
            mx = mx.max(at(k));
            k += 1;
        }
        let _ = writeln!(curve, "{},period,{},{},{}", s.rule, bin, mn, mx);
    }
    Ok((ev, seed, curve))
}

fn control(rule: &Rule) -> String {
    let lo = 1_000_000u64;
    let queries: Vec<u64> = (lo..lo + 50_000).collect();
    let mut a = Tracked::new(rule, 4096);
    let mut dc = DepCounter::new(queries, DELTA);
    while a.t < lo + 50_000 + DELTA {
        match a.step() {
            Some(r) => dc.observe(&r),
            None => return format!("{rule},offboard,,,\n"),
        }
    }
    let (_, mut tr) = dc.finish();
    tr.sort();
    format!("{rule},ok,{},{},{}\n", tr[0], tr[tr.len() / 2], tr[tr.len() - 1])
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (mode, spec, out) = (a[1].as_str(), &a[2], std::path::Path::new(&a[3]));
    let lines: Vec<String> = std::fs::read_to_string(spec).unwrap().lines().filter(|l| !l.trim().is_empty()).map(String::from).collect();
    let file = |name: &str| std::fs::File::create(out.join(name)).unwrap();
    if mode == "control" {
        let rows: Vec<String> = lines.par_iter().map(|l| control(&l.trim().parse().unwrap())).collect();
        let mut f = file("control.csv");
        writeln!(f, "rule,status,dtrunc_min,dtrunc_median,dtrunc_max").unwrap();
        for r in rows {
            f.write_all(r.as_bytes()).unwrap();
        }
        return;
    }
    let specs: Vec<Spec> = lines
        .iter()
        .map(|l| {
            let v: Vec<&str> = l.split_whitespace().collect();
            Spec { rule: v[0].parse().unwrap(), p: v[1].parse().unwrap(), d: (v[2].parse().unwrap(), v[3].parse().unwrap()), onset: v[4].parse().unwrap() }
        })
        .collect();
    let rows: Vec<(String, String, String)> = specs
        .par_iter()
        .map(|s| {
            let mut size = 1024;
            loop {
                match highway(s, size) {
                    Ok(r) => return r,
                    Err(OffBoard) if size < MAX_SIZE => size *= 2,
                    Err(OffBoard) => return (format!("{},offboard\n", s.rule), String::new(), String::new()),
                }
            }
        })
        .collect();
    let (mut ev, mut sd, mut cv) = (file("events.csv"), file("seeds.tsv"), file("curves.csv"));
    writeln!(ev, "rule,n,period,dx,dy,onset,onset_recomputed,window,tau_star,d_star,seed_cells,h_min,h_max,launch,chaos_level,dtrunc_star,old_cells_read,territory_at_tau,t_leave,cos_out,t_end,t_end2,transplant_ok,mismatch_step,max_colour,used,word_letters,seed_key,highway_key,board,window_lo,d_onset,tau_pre,d_pre,pre_key").unwrap();
    writeln!(sd, "rule\tused\ttau_star\thighway_word\tseed_key\ttau_pre\tpre_key").unwrap();
    writeln!(cv, "rule,kind,x,dmin,dmax").unwrap();
    for (e, s, c) in rows {
        ev.write_all(e.as_bytes()).unwrap();
        sd.write_all(s.as_bytes()).unwrap();
        cv.write_all(c.as_bytes()).unwrap();
    }
}
