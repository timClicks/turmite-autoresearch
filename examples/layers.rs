//! Arm A of notes/kappa-experiment-design.md: edge-layer anatomy.
//!
//! usage: layers MAX_LOG2 [GRID] < walkers.txt > layers.csv
//! Same walker specs as bin/probe (RULE, RULE@SEED, rotor:SEED, pw:Q:SEED).
//! For each octave window (2^k, 2^(k+1)] with k >= 20 it tallies the steps that
//! start at layer d = 0..NL-1 (Manhattan distance to the nearest never-visited
//! cell, minus one; the last bucket is "NL or deeper"), the number of cells at
//! each layer at the window's start and end, and the edge-phase visit count v_e of
//! the cells whose edge phase ended in the window. Layer 0 are the boundary cells
//! of the probe, so rho(0) is the probe's kappa up to the choice of area/perimeter
//! normalisation (checked in experiments/archive/2026-10-layers-colours/scripts/layers_stats.py).

use rayon::prelude::*;
use turmite::Rule;
use turmite::walkers::{AntWalker, PersistentWalk, Rotor, Walker};

const NL: usize = 6;
const UNV: u8 = 255;
const DIRS: [(i64, i64); 4] = [(0, -1), (1, 0), (0, 1), (-1, 0)];

struct Out {
    rows: Vec<String>,
}

/// Cells at each layer over the bounding box, by an exact two-pass Manhattan
/// distance transform from the never-visited cells (the box is padded by one).
fn census(unv: &[u8], size: usize, lo: (usize, usize), hi: (usize, usize)) -> [u64; NL] {
    let (w, h) = (hi.0 - lo.0 + 3, hi.1 - lo.1 + 3);
    let mut d = vec![0u16; w * h];
    for y in 1..h - 1 {
        for x in 1..w - 1 {
            let gi = (lo.1 + y - 1) * size + lo.0 + x - 1;
            d[y * w + x] = if unv[gi] == UNV { 0 } else { u16::MAX / 2 };
        }
    }
    for y in 1..h - 1 {
        for x in 1..w - 1 {
            let v = d[y * w + x].min(d[(y - 1) * w + x] + 1).min(d[y * w + x - 1] + 1);
            d[y * w + x] = v;
        }
    }
    for y in (1..h - 1).rev() {
        for x in (1..w - 1).rev() {
            let v = d[y * w + x].min(d[(y + 1) * w + x] + 1).min(d[y * w + x + 1] + 1);
            d[y * w + x] = v;
        }
    }
    let mut n = [0u64; NL];
    for y in 1..h - 1 {
        for x in 1..w - 1 {
            let gi = (lo.1 + y - 1) * size + lo.0 + x - 1;
            if unv[gi] != UNV {
                n[((d[y * w + x] as usize).saturating_sub(1)).min(NL - 1)] += 1;
            }
        }
    }
    n
}

fn run<W: Walker>(name: &str, mut walker: W, size: usize, max_log2: u32) -> Out {
    let c = size / 2;
    let s = size as isize;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            *cell = walker.initial_cell((i % size) as i64 - c as i64, (i / size) as i64 - c as i64);
        }
    }
    // unv[i] = UNV if never visited, else the number of unvisited 4-neighbours.
    let mut unv = vec![UNV; size * size];
    let nbr = [-s, 1, s, -1];
    let mut ev = vec![0u32; size * size];
    let mut fin = vec![false; size * size];
    let (mut area, mut perim) = (0u64, 0u64);
    let (mut lo, mut hi) = ((c, c), (c, c));

    // Manhattan ball offsets by radius 1..=NL, so the first radius containing an
    // unvisited cell gives layer = radius - 1.
    let mut balls: Vec<Vec<isize>> = vec![vec![]; NL + 1];
    for dy in -(NL as isize)..=(NL as isize) {
        for dx in -(NL as isize)..=(NL as isize) {
            let r = (dx.abs() + dy.abs()) as usize;
            if (1..=NL).contains(&r) {
                balls[r].push(dy * s + dx);
            }
        }
    }

    let visit = |idx: usize, unv: &mut Vec<u8>, area: &mut u64, perim: &mut u64| {
        let mut u = 0u8;
        for d in nbr {
            let j = (idx as isize + d) as usize;
            if unv[j] == UNV {
                u += 1;
            } else {
                unv[j] -= 1;
                if unv[j] == 0 {
                    *perim -= 1;
                }
            }
        }
        unv[idx] = u;
        if u > 0 {
            *perim += 1;
        }
        *area += 1;
    };

    let (mut x, mut y, mut h) = (c as i64, c as i64, 0u8);
    let mut idx = c * size + c;
    visit(idx, &mut unv, &mut area, &mut perim);
    let mut rows = vec![];
    let mut t: u64 = 0;
    for k in 0..max_log2 {
        let t_end = 1u64 << (k + 1);
        let record = k >= 20;
        let before = if record { census(&unv, size, lo, hi) } else { [0; NL] };
        let mut layer_steps = [0u64; NL];
        let (mut fin_sum, mut fin_n, mut new_cells) = (0u64, 0u64, 0u64);
        let mut escaped = false;
        while t < t_end {
            if record {
                let mut l = NL - 1;
                for r in 1..=NL {
                    if balls[r].iter().any(|&o| unv[(idx as isize + o) as usize] == UNV) {
                        l = r - 1;
                        break;
                    }
                }
                layer_steps[l] += 1;
            }
            if unv[idx] > 0 {
                ev[idx] += 1;
            }
            walker.step(&mut colour[idx], &mut h);
            let (dx, dy) = DIRS[h as usize];
            x += dx;
            y += dy;
            idx = (idx as isize + dy as isize * s + dx as isize) as usize;
            t += 1;
            if unv[idx] == UNV {
                new_cells += 1;
                visit(idx, &mut unv, &mut area, &mut perim);
                lo = (lo.0.min(x as usize), lo.1.min(y as usize));
                hi = (hi.0.max(x as usize), hi.1.max(y as usize));
                // Edge phase ends for any visited cell that just lost its last unvisited neighbour.
                for j in std::iter::once(0isize).chain(nbr) {
                    let q = (idx as isize + j) as usize;
                    if unv[q] == 0 && !fin[q] {
                        fin[q] = true;
                        fin_sum += ev[q] as u64;
                        fin_n += 1;
                    }
                }
            }
            if x < 8 || y < 8 || x >= size as i64 - 8 || y >= size as i64 - 8 {
                escaped = true;
                break;
            }
        }
        if escaped {
            break;
        }
        if record {
            let after = census(&unv, size, lo, hi);
            let f = |a: &[u64; NL]| a.iter().map(|v| v.to_string()).collect::<Vec<_>>().join(",");
            rows.push(format!(
                "{name},{k},{area},{perim},{new_cells},{fin_sum},{fin_n},{},{},{}\n",
                f(&layer_steps),
                f(&before),
                f(&after)
            ));
        }
    }
    Out { rows }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let max_log2: u32 = a[1].parse().unwrap();
    let size: usize = a.get(2).map(|v| v.parse().unwrap()).unwrap_or(8192);
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    let outs: Vec<Out> = specs
        .par_iter()
        .map(|r| {
            if let Some(seed) = r.strip_prefix("rotor:") {
                run(r, Rotor { seed: seed.parse().unwrap() }, size, max_log2)
            } else if let Some(spec) = r.strip_prefix("pw:") {
                let (q, seed) = spec.split_once(':').unwrap();
                run(r, PersistentWalk::new(seed.parse().unwrap(), q.parse().unwrap()), size, max_log2)
            } else {
                run(r, AntWalker::new(&r.parse::<Rule>().unwrap()), size, max_log2)
            }
        })
        .collect();
    let nl = (0..NL).map(|d| format!("n{d}")).collect::<Vec<_>>();
    let cols = |p: &str| nl.iter().map(|n| format!("{p}{n}")).collect::<Vec<_>>().join(",");
    println!("walker,k,area,perimeter,new_cells,fin_sum,fin_n,{},{},{}", cols("s"), cols("b"), cols("e"));
    for o in outs {
        for r in o.rows {
            print!("{r}");
        }
    }
}
