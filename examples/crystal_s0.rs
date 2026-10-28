//! crystal-rules S0 (experiments/archive/2026-10-crystal-rules): run RULE for 2^K steps on a
//! blank SIZE^2 board (deterministic, no seed), write OUT/RULE.grid (u8 colour, 255 =
//! never visited, row-major SIZE x SIZE) and print bbox / visit statistics.
//! usage: crystal_s0 RULE K SIZE OUTDIR
use std::io::Write;
use turmite::{DIRS, Rule};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let k: u32 = a[2].parse().unwrap();
    let size: usize = a[3].parse().unwrap();
    let dir = std::path::Path::new(&a[4]);
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut col = vec![0u8; size * size];
    let mut visits = vec![0u16; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut bb = [x, x, y, y];
    let mut left = false;
    println!("t,bbox_w,bbox_h");
    for t in 1..=(1u64 << k) {
        let i = y as usize * size + x as usize;
        let cc = col[i] as usize;
        h = (h + turn[cc]) & 3;
        col[i] = ((cc + 1) % n) as u8;
        visits[i] = visits[i].saturating_add(1);
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        bb = [bb[0].min(x), bb[1].max(x), bb[2].min(y), bb[3].max(y)];
        if t.is_power_of_two() && t >= 4096 {
            println!("{t},{},{}", bb[1] - bb[0] + 1, bb[3] - bb[2] + 1);
        }
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            left = true;
            break;
        }
    }
    let seen = visits.iter().filter(|&&v| v > 0).count();
    let maxv = *visits.iter().max().unwrap();
    println!(
        "{} k={k} left_board={left} bbox_w={} bbox_h={} visited={seen} visited/bbox={:.4} steps/visited={:.2} max_visits={maxv}",
        a[1], bb[1] - bb[0] + 1, bb[3] - bb[2] + 1,
        seen as f64 / ((bb[1] - bb[0] + 1) * (bb[3] - bb[2] + 1)) as f64,
        (1u64 << k) as f64 / seen as f64
    );
    if k > 26 { return; } // no dump for the big octave runs
    let out: Vec<u8> = col.iter().zip(&visits).map(|(&c, &v)| if v == 0 { 255 } else { c }).collect();
    std::fs::create_dir_all(dir).unwrap();
    std::fs::File::create(dir.join(format!("{}.grid", a[1]))).unwrap().write_all(&out).unwrap();
    let vo: Vec<u8> = visits.iter().map(|&v| v.min(255) as u8).collect();
    std::fs::File::create(dir.join(format!("{}.visits", a[1]))).unwrap().write_all(&vo).unwrap();
}
