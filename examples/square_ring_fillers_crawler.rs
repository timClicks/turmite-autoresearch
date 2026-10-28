//! experiments/archive/2026-10-square-ring-fillers, P1: does the explicit edge configuration C_k translate?
//! usage: square_ring_fillers_crawler K RULE [PERIODS=16]
//! Builds C_k (README table: crawler on the north side moving west, ant at (0,0) heading N; a=k, b=k+1, c=2k+1, d=2k+2
//! visits) on a finite strip, runs the plain ant (turn = RULE[visits mod n]) for PERIODS * 8(k+1) steps, and after every
//! period compares the whole strip with C_k translated by (-4 p, 0). Prints one line:
//! `k=.. rule=.. periods_ok=.. first_fail=.. reads=v:count,...` where reads are counted over all steps run.
//! Visit counts are kept as integers (u32), so the comparison is on visits, not on colours.
use std::collections::BTreeMap;
use turmite::{DIRS, Rule};

fn ck(k: u32, wall: i64, x: i64, y: i64) -> u32 {
    let (a, b, c, d) = (k, k + 1, 2 * k + 1, 2 * k + 2);
    let u = x - wall; // position relative to the ant column
    let m = u.rem_euclid(4);
    match y {
        y if y <= -2 => 0,
        -1 => {
            if u >= 1 && (m == 1 || m == 2) {
                a
            } else {
                0
            }
        }
        0 => {
            if u < 0 {
                if m == 2 || m == 3 { a } else { 0 }
            } else if u == 0 {
                a
            } else if m == 1 || m == 2 {
                c
            } else {
                b
            }
        }
        1 => {
            if u < 0 {
                if m == 2 || m == 3 { c } else { b }
            } else {
                d
            }
        }
        _ => d,
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let k: u32 = args[1].parse().unwrap();
    let rule: Rule = args[2].parse().unwrap();
    let periods: i64 = args.get(3).map_or(16, |v| v.parse().unwrap());
    let n = rule.len() as u32;
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let period = 8 * (k as i64 + 1);
    // Strip: columns x in [x0, x1], rows y in [y0, y1]; the ant stays in rows -1..1 and moves left 4 per period.
    let (x0, x1) = (-4 * periods - 16, 16i64);
    let (y0, y1) = (-4i64, 5i64);
    let w = (x1 - x0 + 1) as usize;
    let idx = |x: i64, y: i64| ((y - y0) as usize) * w + (x - x0) as usize;
    let mut cells = vec![0u32; w * (y1 - y0 + 1) as usize];
    for y in y0..=y1 {
        for x in x0..=x1 {
            cells[idx(x, y)] = ck(k, 0, x, y);
        }
    }
    let (mut x, mut y, mut h) = (0i64, 0i64, 0u8);
    let mut reads: BTreeMap<u32, u64> = BTreeMap::new();
    let mut ok = 0i64;
    let mut first_fail: Option<String> = None;
    'outer: for p in 1..=periods {
        for _ in 0..period {
            let i = idx(x, y);
            let v = cells[i];
            *reads.entry(v).or_default() += 1;
            h = (h + turn[(v % n) as usize]) & 3;
            cells[i] = v + 1;
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            if x <= x0 || x >= x1 || y <= y0 || y >= y1 {
                first_fail = Some(format!("p={p}:left_strip"));
                break 'outer;
            }
        }
        let wall = -4 * p;
        if (x, y, h) != (wall, 0, 0) {
            first_fail = Some(format!("p={p}:ant=({x},{y},{h})"));
            break;
        }
        for yy in y0..=y1 {
            for xx in x0..=x1 {
                if cells[idx(xx, yy)] != ck(k, wall, xx, yy) {
                    first_fail = Some(format!("p={p}:cell=({xx},{yy})"));
                    break 'outer;
                }
            }
        }
        ok = p;
    }
    let r: Vec<String> = reads.iter().map(|(v, c)| format!("{v}:{c}")).collect();
    println!(
        "k={k} rule={rule} periods_ok={ok} first_fail={} reads={}",
        first_fail.unwrap_or_else(|| "none".into()),
        r.join(",")
    );
}
