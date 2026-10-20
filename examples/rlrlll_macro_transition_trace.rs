//! experiments/2026-10-20-rlrlll-macro-transition: cycle-level trace of a late column sweeper (RLRLLL).
//! usage: rlrlll_macro_transition_trace RULE T_ON OUTDIR [GRID=32768] [WIN=48] [EVERY=25]
//! Runs from a blank board. From the first front advance after T_ON, a cycle ends each time the front
//! (minimum visited x) has moved 3 further columns west. Writes OUTDIR/cycles.csv (one row per cycle) and
//! OUTDIR/snap_K.bin front-window snapshots for selected cycles K: header line
//! "k t x_f ant_x ant_y h y0 y1 win", then (y1 - y0 + 1) rows of `win` bytes for columns x_f .. x_f + win
//! (255 = unvisited). Same plain loop, DIRS and update order as `g1_ribbon_breakout_builder_dump`.
use std::io::Write;
use turmite::{DIRS, Rule};

const SEEN: u8 = 0x80;

struct Board {
    size: usize,
    cells: Vec<u8>,
}

impl Board {
    fn col_extent(&self, x: i64) -> (usize, i64, i64) {
        let (mut n, mut lo, mut hi) = (0, i64::MAX, i64::MIN);
        for y in 0..self.size {
            if self.cells[y * self.size + x as usize] & SEEN != 0 {
                n += 1;
                lo = lo.min(y as i64);
                hi = hi.max(y as i64);
            }
        }
        (n, lo, hi)
    }
}

fn snapshot_wanted(k: u64, every: u64) -> bool {
    k < 64 || k % every == 0 || (1000..1064).contains(&k) || (3000..3064).contains(&k)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let t_on: u64 = a[2].parse().unwrap();
    let out = std::path::PathBuf::from(&a[3]);
    let size: usize = a.get(4).map_or(32768, |v| v.parse().unwrap());
    let win: i64 = a.get(5).map_or(48, |v| v.parse().unwrap());
    let every: u64 = a.get(6).map_or(25, |v| v.parse().unwrap());
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut b = Board { size, cells: vec![0u8; size * size] };
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut xf = c; // front: minimum visited x (absolute)
    let mut cyc = std::io::BufWriter::new(std::fs::File::create(out.join("cycles.csv")).unwrap());
    writeln!(cyc, "k,t_end,steps,x_f,ant_x,ant_y,h,reach,L_prev_col,top_prev_col,bot_prev_col").unwrap();
    // Cycle state; armed at the first front advance after t_on.
    let mut armed = false;
    let (mut k, mut t_start, mut xf_start, mut reach) = (0u64, 0u64, 0i64, 0i64);
    let mut t: u64 = 0;
    loop {
        let i = (y as usize) * size + x as usize;
        let col = (b.cells[i] & !SEEN) as usize;
        h = (h + turn[col]) & 3;
        b.cells[i] = SEEN | ((col + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        t += 1;
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            eprintln!("left board at step {t} (x={}, y={})", x - c, y - c);
            break;
        }
        if armed {
            reach = reach.max(x - xf);
        }
        if x < xf {
            xf = x;
            if !armed {
                if t > t_on {
                    armed = true;
                    t_start = t;
                    xf_start = xf;
                    reach = 0;
                    eprintln!("armed at step {t}, x_f={}", xf - c);
                }
            } else if xf_start - xf == 3 * (k as i64 + 1) {
                // The column opened at the previous boundary has now had one full cycle.
                let (lp, top, bot) = b.col_extent(xf + 3);
                writeln!(
                    cyc,
                    "{k},{t},{},{},{},{},{h},{reach},{lp},{},{}",
                    t - t_start,
                    xf - c,
                    x - c,
                    y - c,
                    top - c,
                    bot - c
                )
                .unwrap();
                if snapshot_wanted(k, every) {
                    write_snapshot(&b, &out, k, t, xf, x, y, h, win, c);
                }
                k += 1;
                t_start = t;
                reach = 0;
            }
        }
    }
    eprintln!("cycles recorded: {k}");
}

#[allow(clippy::too_many_arguments)]
fn write_snapshot(b: &Board, out: &std::path::Path, k: u64, t: u64, xf: i64, x: i64, y: i64, h: u8, win: i64, c: i64) {
    let x1 = (xf + win).min(b.size as i64);
    let (mut y0, mut y1) = (i64::MAX, i64::MIN);
    for xx in xf..x1 {
        let (_, lo, hi) = b.col_extent(xx);
        y0 = y0.min(lo);
        y1 = y1.max(hi);
    }
    let mut f = std::io::BufWriter::new(std::fs::File::create(out.join(format!("snap_{k}.bin"))).unwrap());
    writeln!(f, "{k} {t} {} {} {} {h} {} {} {}", xf - c, x - c, y - c, y0 - c, y1 - c, x1 - xf).unwrap();
    let mut row = vec![0u8; (x1 - xf) as usize];
    for yy in y0..=y1 {
        for (j, xx) in (xf..x1).enumerate() {
            let v = b.cells[yy as usize * b.size + xx as usize];
            row[j] = if v & SEEN == 0 { 255 } else { v & !SEEN };
        }
        f.write_all(&row).unwrap();
    }
}
