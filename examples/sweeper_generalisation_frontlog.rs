//! experiments/archive/2026-10-sweeper-generalisation: direction-agnostic front log of one blank-board run.
//! usage: sweeper_generalisation_frontlog RULE STEPS GRID OUTDIR [WIN=1000000]
//! Runs from a blank GRID x GRID board (ant at the centre, heading 0), for STEPS steps or until the ant is within one cell of the
//! edge. Writes to OUTDIR:
//!   events_xmin.csv, events_xmax.csv, events_ymin.csv, events_ymax.csv: one row per step at which the global extreme of the
//!     visited cells advances in that direction: `t,front,pmin,pmax` (front relative to the start cell; pmin/pmax = range of the
//!     perpendicular coordinate of the ant over the steps since the previous advance in that direction, including this step).
//!   windows.csv: every WIN steps, `t_end,new_cells,x0,x1,y0,y1` (box of the cells first visited in the window).
//! Prints `fingerprint t=.. x=.. y=.. h=.. hash=.. nonzero=..` (FNV-1a of every cell's colour, row-major) on stdout, comparable
//! with `fast::run` on the same grid size. Same plain loop, DIRS and update order as `rlrlll_macro_transition_trace`.
use std::io::Write;
use turmite::{DIRS, Rule};

const SEEN: u8 = 0x80;

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let steps: u64 = a[2].parse().unwrap();
    let size: usize = a[3].parse().unwrap();
    let out = std::path::PathBuf::from(&a[4]);
    let win: u64 = a.get(5).map_or(1_000_000, |v| v.parse().unwrap());
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let open = |name: &str, head: &str| {
        let mut f = std::io::BufWriter::new(std::fs::File::create(out.join(name)).unwrap());
        writeln!(f, "{head}").unwrap();
        f
    };
    let mut ev = [
        open("events_xmin.csv", "t,front,pmin,pmax"),
        open("events_xmax.csv", "t,front,pmin,pmax"),
        open("events_ymin.csv", "t,front,pmin,pmax"),
        open("events_ymax.csv", "t,front,pmin,pmax"),
    ];
    let mut wf = open("windows.csv", "t_end,new_cells,x0,x1,y0,y1");
    // front[d]: xmin, xmax, ymin, ymax of visited cells (start cell counts as visited).
    let mut front = [c, c, c, c];
    // Perpendicular range since the last advance, per direction: (min, max). xmin/xmax events track y; ymin/ymax events track x.
    let mut pr = [(c, c); 4];
    cells[(y as usize) * size + x as usize] |= SEEN;
    let (mut w_new, mut wb) = (0u64, [i64::MAX, i64::MIN, i64::MAX, i64::MIN]);
    let mut t: u64 = 0;
    while t < steps {
        let i = (y as usize) * size + x as usize;
        let col = (cells[i] & !SEEN) as usize;
        h = (h + turn[col]) & 3;
        cells[i] = SEEN | ((col + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        t += 1;
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            eprintln!("left board at step {t} (x={}, y={})", x - c, y - c);
            break;
        }
        let j = (y as usize) * size + x as usize;
        if cells[j] & SEEN == 0 {
            cells[j] |= SEEN;
            w_new += 1;
            wb = [wb[0].min(x - c), wb[1].max(x - c), wb[2].min(y - c), wb[3].max(y - c)];
        }
        for d in 0..4 {
            let p = if d < 2 { y } else { x };
            pr[d] = (pr[d].0.min(p), pr[d].1.max(p));
        }
        let advanced = [x < front[0], x > front[1], y < front[2], y > front[3]];
        let pos = [x, x, y, y];
        for d in 0..4 {
            if advanced[d] {
                front[d] = pos[d];
                writeln!(ev[d], "{t},{},{},{}", pos[d] - c, pr[d].0 - c, pr[d].1 - c).unwrap();
                let p = if d < 2 { y } else { x };
                pr[d] = (p, p);
            }
        }
        if t % win == 0 {
            writeln!(wf, "{t},{w_new},{},{},{},{}", wb[0], wb[1], wb[2], wb[3]).unwrap();
            w_new = 0;
            wb = [i64::MAX, i64::MIN, i64::MAX, i64::MIN];
        }
    }
    let (mut hash, mut nz) = (0xcbf29ce484222325u64, 0u64);
    for &v in &cells {
        let col = v & !SEEN;
        hash = (hash ^ col as u64).wrapping_mul(0x100000001b3);
        nz += (col != 0) as u64;
    }
    println!("fingerprint t={t} x={} y={} h={h} hash={hash:016x} nonzero={nz}", x - c, y - c);
}
