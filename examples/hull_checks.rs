//! Frozen hull_width instrument plus profiles for 2026-10-hull-checks.
//!
//! usage: hull_checks MAX_LOG2 [GRID] [MIN_LOG2] < specs.txt > hull.csv
//! Specs as in `shape`: an ant rule, `RULE@SEED` (random 5x5 patch), `rotor:SEED`.
//! One `hull` row per (spec, checkpoint t = 2^k, k = MIN_LOG2..=MAX_LOG2).
//!
//! Exterior = unvisited cells 4-connected to the grid border. Surface cells (as in `shape`'s
//! Wsurf and the probe's P) are visited cells with an unvisited 4-neighbour; we split them:
//!   outer  touches at least one exterior cell      (the coastline)
//!   hole   touches only unvisited cells that are not exterior (rims of lakes/pockets)
//! Columns:
//!   A, Pall, Pouter, Phole      visited area and the three surface-cell counts
//!   nholes, holearea            4-connected non-exterior unvisited components and their total size
//!   Wall, Wout                  sd of radius about the visited centroid of all / outer surface cells
//!   wang                        sd of the outermost-cell radius r(theta) (512 angular bins) after
//!                               removing Fourier modes m = 0,1,2 (global size and shift/shape modes)
//!   empty                       number of empty angular bins (spectrum is blank if > 0)
//!   spec                        sum of |r_m|^2 (m = 3..256) in bands 3-4,5-8,...,129-256, `;`-joined,
//!                               in units of rbar^2 so it is size free
//!   boxc                        box counts of the outer cells at box sizes 1,2,4,...,64, `;`-joined
//! Deterministic: the only randomness is the seed in the spec.
use rayon::prelude::*;
use std::collections::HashSet;
use std::io::Write;
use turmite::walkers::{AntWalker, PatchedAnt, Rotor, Walker};
use turmite::{DIRS, Rule};

const NB: usize = 512;

fn run<W: Walker>(mut w: W, label: &str, size: usize, max_log2: u32, min_log2: u32) -> String {
    let c = (size / 2) as i64;
    let mut colour = vec![0u8; size * size];
    if W::RANDOM_INIT {
        for (i, cell) in colour.iter_mut().enumerate() {
            *cell = w.initial_cell((i % size) as i64 - c, (i / size) as i64 - c);
        }
    }
    let mut visited = vec![false; size * size];
    let s = size as isize;
    let (mut x, mut y, mut h) = (0i64, 0i64, 0u8);
    let mut idx = (c * size as i64 + c) as usize;
    visited[idx] = true;
    let mut out = String::new();
    let mut t: u64 = 0;
    let mut k = min_log2;
    while k <= max_log2 {
        let target = 1u64 << k;
        while t < target {
            w.step(&mut colour[idx], &mut h);
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            idx = (idx as isize + dy as isize * s + dx as isize) as usize;
            visited[idx] = true;
            t += 1;
            if x.abs() >= c - 2 || y.abs() >= c - 2 {
                return out + &format!("# {label} escaped at t={t}\n");
            }
        }
        out += &checkpoint(&visited, size, label, k);
        k += 1;
    }
    out
}

/// Flood the unvisited cells 4-connected to `seed`; marks them in `comp` and returns their count.
fn flood(visited: &[bool], comp: &mut [u8], size: usize, seed: usize, tag: u8) -> usize {
    let mut stack = vec![seed];
    comp[seed] = tag;
    let mut n = 0;
    while let Some(i) = stack.pop() {
        n += 1;
        let (x, y) = (i % size, i / size);
        let mut push = |j: usize| {
            if !visited[j] && comp[j] == 0 {
                comp[j] = tag;
                stack.push(j);
            }
        };
        if x > 0 { push(i - 1); }
        if x + 1 < size { push(i + 1); }
        if y > 0 { push(i - size); }
        if y + 1 < size { push(i + size); }
    }
    n
}

fn checkpoint(visited: &[bool], size: usize, label: &str, k: u32) -> String {
    let (mut a, mut sx, mut sy) = (0f64, 0f64, 0f64);
    for y in 0..size {
        for x in 0..size {
            if visited[y * size + x] {
                a += 1.0;
                sx += x as f64;
                sy += y as f64;
            }
        }
    }
    let (mx, my) = (sx / a, sy / a);
    // comp: 0 = unlabelled/visited, 1 = exterior, 2.. = hole components (4-connected)
    let mut comp = vec![0u8; size * size];
    flood(visited, &mut comp, size, 0, 1); // the grid corner is always unvisited (no escape)
    let (mut nholes, mut holearea) = (0usize, 0usize);
    for i in 0..size * size {
        if !visited[i] && comp[i] == 0 {
            // tag 2 for every hole: only the exterior/non-exterior distinction is used downstream
            holearea += flood(visited, &mut comp, size, i, 2);
            nholes += 1;
        }
    }
    let (mut pall, mut pout, mut phole) = (0usize, 0usize, 0usize);
    let (mut s1a, mut s2a, mut s1o, mut s2o) = (0f64, 0f64, 0f64, 0f64);
    let mut rmax = [0f64; NB];
    let mut outer_cells: Vec<(usize, usize)> = Vec::new();
    for y in 1..size - 1 {
        for x in 1..size - 1 {
            let i = y * size + x;
            if !visited[i] {
                continue;
            }
            let (fx, fy) = (x as f64 - mx, y as f64 - my);
            let r = (fx * fx + fy * fy).sqrt();
            let th = fy.atan2(fx) + std::f64::consts::PI;
            let b = ((th / (2.0 * std::f64::consts::PI)) * NB as f64) as usize % NB;
            if r > rmax[b] {
                rmax[b] = r;
            }
            let nb = [i - 1, i + 1, i - size, i + size];
            let touches_ext = nb.iter().any(|&j| !visited[j] && comp[j] == 1);
            let touches_unv = nb.iter().any(|&j| !visited[j]);
            if touches_unv {
                pall += 1;
                s1a += r;
                s2a += r * r;
                if touches_ext {
                    pout += 1;
                    s1o += r;
                    s2o += r * r;
                    outer_cells.push((x, y));
                } else {
                    phole += 1;
                }
            }
        }
    }
    let sd = |s1: f64, s2: f64, n: usize| (s2 / n as f64 - (s1 / n as f64).powi(2)).max(0.0).sqrt();
    let (wall, wout) = (sd(s1a, s2a, pall), sd(s1o, s2o, pout));
    // angular profile roughness and spectrum
    let empty = rmax.iter().filter(|&&r| r == 0.0).count();
    let rbar = rmax.iter().sum::<f64>() / NB as f64;
    let (mut wang, mut bands) = (f64::NAN, vec![f64::NAN; 7]);
    if empty == 0 {
        let amp = |m: usize| {
            let (mut re, mut im) = (0.0, 0.0);
            for (b, r) in rmax.iter().enumerate() {
                let ang = 2.0 * std::f64::consts::PI * m as f64 * (b as f64 + 0.5) / NB as f64;
                re += r * ang.cos();
                im += r * ang.sin();
            }
            (re / NB as f64, im / NB as f64) // r(theta) = sum_m 2 Re(c_m e^{-i m theta}) form; |c_m|^2 below
        };
        let mut tot = 0.0;
        let mut b = vec![0f64; 7];
        for m in 3..=NB / 2 {
            let (re, im) = amp(m);
            let p = 2.0 * (re * re + im * im) / (rbar * rbar);
            tot += p;
            let band = (usize::BITS - (m - 1).leading_zeros()) as usize - 2; // 3-4 -> 0, 5-8 -> 1, ...
            if band < 7 {
                b[band] += p;
            }
        }
        // variance of r(theta) with modes 0,1,2 removed equals sum over m >= 3 of 2|c_m|^2
        wang = (tot * rbar * rbar).sqrt();
        bands = b;
    }
    let boxc: Vec<String> = (0..7)
        .map(|j| {
            let sz = 1usize << j;
            let set: HashSet<(usize, usize)> = outer_cells.iter().map(|&(x, y)| (x / sz, y / sz)).collect();
            set.len().to_string()
        })
        .collect();
    let spec: Vec<String> = bands.iter().map(|v| format!("{v:.6e}")).collect();
    format!(
        "hull,{label},{k},{a},{pall},{pout},{phole},{nholes},{holearea},{wall:.4},{wout:.4},{wang:.4},{empty},{},{},{rbar:.17},{}\n",
        spec.join(";"),
        boxc.join(";"),
        rmax.iter().map(|r| format!("{r:.17}")).collect::<Vec<_>>().join(";")
    )
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let max_log2: u32 = a[1].parse().unwrap();
    let size: usize = a.get(2).map(|s| s.parse().unwrap()).unwrap_or(4096);
    let min_log2: u32 = a.get(3).map(|s| s.parse().unwrap()).unwrap_or(24);
    assert!(size >= 16 && min_log2 <= max_log2 && max_log2 < 63);
    let specs: Vec<String> = std::io::stdin().lines().map(|l| l.unwrap().trim().to_string()).filter(|l| !l.is_empty()).collect();
    let blocks: Vec<String> = specs
        .par_iter()
        .map(|r| {
            if let Some(seed) = r.strip_prefix("rotor:") {
                run(Rotor { seed: seed.parse().unwrap() }, r, size, max_log2, min_log2)
            } else if r.contains('@') {
                let mut it = r.split('@');
                let rule = it.next().unwrap();
                let seed = it.next().unwrap();
                run(PatchedAnt::new(&rule.parse::<Rule>().unwrap(), seed.parse().unwrap(), 2), r, size, max_log2, min_log2)
            } else {
                run(AntWalker::new(&r.parse::<Rule>().unwrap()), r, size, max_log2, min_log2)
            }
        })
        .collect();
    let mut out = std::io::stdout().lock();
    writeln!(
        out,
        "kind,spec,k,A,Pall,Pouter,Phole,nholes,holearea,Wall,Wout,wang,empty,spec_bands,boxc,rbar,profile"
    )
    .unwrap();
    for b in blocks {
        out.write_all(b.as_bytes()).unwrap();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Synthetic oracle: a filled square with one 3x3 hole and one 1-cell hole. Outer hull and
    /// hole rims are known by hand, so the split must be exact.
    #[test]
    fn square_with_holes() {
        let size = 64;
        let mut v = vec![false; size * size];
        for y in 20..40 {
            for x in 20..40 {
                v[y * size + x] = true;
            }
        }
        for y in 25..28 {
            for x in 25..28 {
                v[y * size + x] = false; // 3x3 hole
            }
        }
        v[33 * size + 33] = false; // single-cell hole
        let row = checkpoint(&v, size, "t", 16);
        let f: Vec<&str> = row.trim().split(',').collect();
        // A = 400 - 9 - 1; outer ring of a 20x20 square = 76; hole rims = 12 (3x3, 4-neighbours) + 4
        assert_eq!(f[3], "390");
        assert_eq!(f[5], "76");
        assert_eq!(f[6], "16");
        assert_eq!(f[7], "2");
        assert_eq!(f[8], "10");
    }
}

