//! experiments/archive/2026-10-highway-decider: dump the true configuration of a blank-board run at several step counts.
//! usage: highway_decider_dump RULE STEPS_LIST P GRID OUTDIR
//! STEPS_LIST is comma separated and increasing. Plain loop from a blank GRID x GRID board (ant at the centre, heading 0; same DIRS and update
//! order as the other tracers). At each listed step count T writes OUTDIR/dump_T.txt:
//!   line 1: `rule T P`
//!   line 2: `ant x y h`                      (relative to the start cell)
//!   line 3: `ref x y h hash nonzero`         (state after P further steps of `reference::Ant` loaded from the dump, so an independent
//!                                             implementation steps the very configuration that was dumped)
//!   line 4: `cells hash nonzero`             (commutative hash of the dumped cells, see `mix`)
//!   then one `x y c` line per non-zero cell, coordinates relative to the start cell.
//! The run stops (and says so) if the ant gets within one cell of the board edge.
use std::io::Write;
use turmite::reference::Ant;
use turmite::{DIRS, Rule};

fn mix(x: i64, y: i64, c: u8) -> u64 {
    let mut z = (x as u64).wrapping_mul(0x9E37_79B9_7F4A_7C15)
        ^ (y as u64).wrapping_mul(0xC2B2_AE3D_27D4_EB4F)
        ^ (c as u64).wrapping_mul(0x1656_67B1_9E37_79F9);
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let times: Vec<u64> = a[2].split(',').map(|v| v.parse().unwrap()).collect();
    let p: u64 = a[3].parse().unwrap();
    let size: usize = a[4].parse().unwrap();
    let out = std::path::PathBuf::from(&a[5]);
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    // Bounding box of touched cells, to avoid scanning the whole board at each dump.
    let (mut x0, mut x1, mut y0, mut y1) = (c, c, c, c);
    let mut t: u64 = 0;
    for &target in &times {
        while t < target {
            let i = (y as usize) * size + x as usize;
            let col = cells[i] as usize;
            h = (h + turn[col]) & 3;
            cells[i] = ((col + 1) % n) as u8;
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            t += 1;
            if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
                eprintln!("left board at step {t}");
                return;
            }
            x0 = x0.min(x);
            x1 = x1.max(x);
            y0 = y0.min(y);
            y1 = y1.max(y);
        }
        let mut list: Vec<(i64, i64, u8)> = Vec::new();
        let mut hash = 0u64;
        for yy in y0..=y1 {
            let row = (yy as usize) * size;
            for xx in x0..=x1 {
                let v = cells[row + xx as usize];
                if v != 0 {
                    list.push((xx - c, yy - c, v));
                    hash = hash.wrapping_add(mix(xx - c, yy - c, v));
                }
            }
        }
        // Optional (env DUMP_VERIFY=1, target <= 2e7): the plain loop's state at this step against `reference::Ant` run from step 0.
        if std::env::var("DUMP_VERIFY").is_ok() && target <= 20_000_000 {
            let mut z = Ant::new(rule.clone());
            for _ in 0..target {
                z.step();
            }
            let mut zh = 0u64;
            for (&(cx, cy), &v) in &z.cells {
                zh = zh.wrapping_add(mix(cx as i64, cy as i64, v));
            }
            let same = zh == hash && z.cells.len() == list.len() && z.pos == ((x - c) as i32, (y - c) as i32) && z.heading == h;
            println!("verify {rule} T={target} reference-from-zero identical={same}");
        }
        // Reference ant loaded from the dump, stepped P times.
        let mut r = Ant::new(rule.clone());
        for &(cx, cy, v) in &list {
            r.cells.insert((cx as i32, cy as i32), v);
        }
        r.pos = ((x - c) as i32, (y - c) as i32);
        r.heading = h;
        for _ in 0..p {
            r.step();
        }
        let mut rh = 0u64;
        for (&(cx, cy), &v) in &r.cells {
            rh = rh.wrapping_add(mix(cx as i64, cy as i64, v));
        }
        let mut f = std::io::BufWriter::new(std::fs::File::create(out.join(format!("dump_{target}.txt"))).unwrap());
        writeln!(f, "{rule} {target} {p}").unwrap();
        writeln!(f, "ant {} {} {h}", x - c, y - c).unwrap();
        writeln!(f, "ref {} {} {} {rh:016x} {}", r.pos.0, r.pos.1, r.heading, r.cells.len()).unwrap();
        writeln!(f, "cells {hash:016x} {}", list.len()).unwrap();
        for (cx, cy, v) in list {
            writeln!(f, "{cx} {cy} {v}").unwrap();
        }
    }
}
