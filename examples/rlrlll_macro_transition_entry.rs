//! experiments/archive/2026-10-rlrlll-macro-transition: entry probe for the RLRLLL sweeper.
//! usage: rlrlll_macro_transition_entry RULE T_END LOG_FROM OUTDIR [GRID=32768] [MINSWING=40]
//! Plain loop as in `rlrlll_macro_transition_trace`, stopped at step T_END. From step LOG_FROM writes
//! OUTDIR/turns.csv (t,x,y,kind: kind +1 = y-maximum, -1 = y-minimum, each after a swing >= MINSWING rows)
//! and at the end OUTDIR/columns.csv (x, visited count, top y, bottom y, relative to the start cell).
use std::io::Write;
use turmite::{DIRS, Rule};

const SEEN: u8 = 0x80;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let t_end: u64 = a[2].parse().unwrap();
    let log_from: u64 = a[3].parse().unwrap();
    let out = std::path::PathBuf::from(&a[4]);
    let size: usize = a.get(5).map_or(32768, |v| v.parse().unwrap());
    let min_swing: i64 = a.get(6).map_or(40, |v| v.parse().unwrap());
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut turns = std::io::BufWriter::new(std::fs::File::create(out.join("turns.csv")).unwrap());
    writeln!(turns, "t,x,y,kind").unwrap();
    // Zigzag state: track the running extremum in the current direction; emit it once y has
    // moved min_swing back from it.
    let (mut dir, mut ext_y, mut ext_x, mut ext_t) = (0i8, c, c, 0u64);
    let mut t: u64 = 0;
    while t < t_end {
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
            break;
        }
        if t < log_from {
            continue;
        }
        if t == log_from {
            ext_y = y;
            ext_x = x;
            ext_t = t;
        }
        match dir {
            0 => {
                if y >= ext_y + min_swing { dir = 1; ext_y = y; ext_x = x; ext_t = t; }
                else if y <= ext_y - min_swing { dir = -1; ext_y = y; ext_x = x; ext_t = t; }
            }
            1 => {
                if y > ext_y { ext_y = y; ext_x = x; ext_t = t; }
                else if ext_y - y >= min_swing {
                    writeln!(turns, "{ext_t},{},{},1", ext_x - c, ext_y - c).unwrap();
                    dir = -1; ext_y = y; ext_x = x; ext_t = t;
                }
            }
            _ => {
                if y < ext_y { ext_y = y; ext_x = x; ext_t = t; }
                else if y - ext_y >= min_swing {
                    writeln!(turns, "{ext_t},{},{},-1", ext_x - c, ext_y - c).unwrap();
                    dir = 1; ext_y = y; ext_x = x; ext_t = t;
                }
            }
        }
    }
    eprintln!("stopped at step {t}, ant at ({}, {})", x - c, y - c);
    let mut f = std::io::BufWriter::new(std::fs::File::create(out.join("columns.csv")).unwrap());
    writeln!(f, "x,count,top,bottom").unwrap();
    for xx in 0..size {
        let (mut cnt, mut lo, mut hi) = (0, i64::MAX, i64::MIN);
        for yy in 0..size {
            if cells[yy * size + xx] & SEEN != 0 {
                cnt += 1;
                lo = lo.min(yy as i64);
                hi = hi.max(yy as i64);
            }
        }
        if cnt > 0 {
            writeln!(f, "{},{cnt},{},{}", xx as i64 - c, lo - c, hi - c).unwrap();
        }
    }
}
