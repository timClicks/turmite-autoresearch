//! experiments/archive/2026-10-sweeper-generalisation, Stage 2 probe: the ant's trace over one stretch of a square-spiral builder, plus the
//! outer band of the configuration before and after it.
//! usage: sweeper_generalisation_spiral_probe RULE T0 T1 GRID OUTDIR D
//! Plain loop from a blank board (same DIRS and update order as the other tracers). At T0 and at T1 writes OUTDIR/band_T.txt: first line
//! `T x0 x1 y0 y1 antx anty h` (bounding box of the visited cells, ant state, coordinates relative to the start cell), then one `x y c`
//! line per non-zero cell within D cells of the bounding box boundary (inside the box). Between T0 and T1 writes OUTDIR/trace.bin: the ant's
//! position before each step as little-endian i32 pairs (x, y).
use std::io::Write;
use turmite::{DIRS, Rule};

const SEEN: u8 = 0x80;

fn dump_band(cells: &[u8], size: usize, c: i64, bb: [i64; 4], t: u64, ant: (i64, i64, u8), d: i64, path: &std::path::Path) {
    let mut f = std::io::BufWriter::new(std::fs::File::create(path).unwrap());
    writeln!(f, "{t} {} {} {} {} {} {} {}", bb[0] - c, bb[1] - c, bb[2] - c, bb[3] - c, ant.0 - c, ant.1 - c, ant.2).unwrap();
    for y in bb[2]..=bb[3] {
        for x in bb[0]..=bb[1] {
            let near = x < bb[0] + d || x > bb[1] - d || y < bb[2] + d || y > bb[3] - d;
            if near {
                let v = cells[(y as usize) * size + x as usize] & !SEEN;
                if v != 0 {
                    writeln!(f, "{} {} {v}", x - c, y - c).unwrap();
                }
            }
        }
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let t0: u64 = a[2].parse().unwrap();
    let t1: u64 = a[3].parse().unwrap();
    let size: usize = a[4].parse().unwrap();
    let out = std::path::PathBuf::from(&a[5]);
    let d: i64 = a[6].parse().unwrap();
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut bb = [c, c, c, c];
    let mut trace = std::io::BufWriter::new(std::fs::File::create(out.join("trace.bin")).unwrap());
    let mut t: u64 = 0;
    while t < t1 {
        if t == t0 {
            dump_band(&cells, size, c, bb, t, (x, y, h), d, &out.join(format!("band_{t0}.txt")));
        }
        if t >= t0 {
            trace.write_all(&((x - c) as i32).to_le_bytes()).unwrap();
            trace.write_all(&((y - c) as i32).to_le_bytes()).unwrap();
        }
        let i = (y as usize) * size + x as usize;
        let col = (cells[i] & !SEEN) as usize;
        h = (h + turn[col]) & 3;
        cells[i] = SEEN | ((col + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        t += 1;
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            eprintln!("left board at step {t}");
            return;
        }
        bb = [bb[0].min(x), bb[1].max(x), bb[2].min(y), bb[3].max(y)];
    }
    dump_band(&cells, size, c, bb, t, (x, y, h), d, &out.join(format!("band_{t1}.txt")));
}
