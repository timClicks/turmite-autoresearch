//! experiments/archive/2026-10-rlrlll-macro-transition, Task A: cell-level windows at the sweeper's own front.
//! usage: rlrlll_macro_transition_window RULE T_TRACK OUTDIR GRID TARGET[,TARGET...] [APRON=450]
//! Hot loop, DIRS and update order are those of `rlrlll_macro_transition_trace` (no state bits added to `cells`).
//! The front is the ant's own minimum x since T_TRACK (not the global front, which belongs to the old blob).
//! An event is the step at which the ant's x first goes below that minimum and equals a TARGET column (absolute
//! x relative to the start cell). At an event, writes OUTDIR/ev_<x>.bin: header line
//! "x t ant_x ant_y h x0 y0 w hgt" then hgt rows of w bytes for columns x0..x0+w, rows y0..y0+hgt (255 = unvisited,
//! else colour), with x0 = x - 320, w = 384, y0 = ant_y - APRON, hgt = 2 APRON + 1 (APRON = 7th argument, default 450). At step T_TRACK it writes OUTDIR/ref.bin in the
//! same format for columns [-2030, -1400), rows [-2000, 0): the board before the sweeper left the blob's corner.
//! Stops after the last (westmost) target.
use std::io::Write;
use turmite::{DIRS, Rule};

const SEEN: u8 = 0x80;

fn dump(cells: &[u8], size: usize, c: i64, path: &std::path::Path, hdr: &str, x0: i64, y0: i64, w: i64, hgt: i64) {
    let mut f = std::io::BufWriter::new(std::fs::File::create(path).unwrap());
    writeln!(f, "{hdr} {} {} {w} {hgt}", x0, y0).unwrap();
    let mut row = vec![0u8; w as usize];
    for yy in 0..hgt {
        let ya = (c + y0 + yy) as usize;
        for xx in 0..w {
            let v = cells[ya * size + (c + x0 + xx) as usize];
            row[xx as usize] = if v & SEEN == 0 { 255 } else { v & !SEEN };
        }
        f.write_all(&row).unwrap();
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let t_track: u64 = a[2].parse().unwrap();
    let out = std::path::PathBuf::from(&a[3]);
    let size: usize = a[4].parse().unwrap();
    let apron: i64 = a.get(6).map_or(450, |v| v.parse().unwrap()); // rows above and below the ant
    let mut targets: Vec<i64> = a[5].split(',').map(|v| v.parse().unwrap()).collect();
    targets.sort_unstable_by(|p, q| q.cmp(p)); // east to west
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut xf = i64::MAX; // ant's minimum x since t_track (absolute)
    let mut next = 0usize;
    let mut t: u64 = 0;
    let mut last_t = 0u64;
    loop {
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
        if t == t_track {
            xf = x;
            eprintln!("tracking from step {t}: ant at ({}, {})", x - c, y - c);
            assert!(x - c > -1549, "ant must start east of -1549");
            dump(&cells, size, c, &out.join("ref.bin"), &format!("{t}"), -2030, -2000, 630, 2000);
        }
        if t >= t_track && x < xf {
            xf = x;
            if next < targets.len() && x - c == targets[next] {
                assert!(t > last_t);
                last_t = t;
                let (ax, ay) = (x - c, y - c);
                dump(&cells, size, c, &out.join(format!("ev_{ax}.bin")), &format!("{ax} {t} {ax} {ay} {h}"), ax - 320, ay - apron, 384, 2 * apron + 1);
                eprintln!("event x={ax} t={t} ant=({ax},{ay}) h={h}");
                next += 1;
                if next == targets.len() {
                    break;
                }
            }
            // A target the ant skipped (column reached before t_track's minimum) never fires; drop it.
            while next < targets.len() && x - c < targets[next] {
                eprintln!("target {} skipped (front already at {})", targets[next], x - c);
                next += 1;
            }
            if next == targets.len() {
                break;
            }
        }
    }
}
