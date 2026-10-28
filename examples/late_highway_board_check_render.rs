//! late_highway_board_check_render RULE GRID OUT T1 T2 ...
//! Runs RULE from a blank GRID x GRID board (ant at the centre heading north, update of `reference::Ant`) and writes a
//! snapshot at each requested step, or at the step the ant leaves the board, whichever is first:
//!   OUT_<t>.bin  u8 image of side W = min(GRID, 1024): per block of (GRID/W)^2 cells, 0 = never visited, otherwise
//!                1 + the colour of the last visited cell in scan order
//!   OUT.csv      t, ant x, y, heading, visited cells, bounding box, left_board (one row per snapshot)
//! Experiment `2026-10-late-highway-board-check`; rendered by `scripts/render.py`.
use std::io::Write;
use turmite::{DIRS, Rule};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let size: usize = a[2].parse().unwrap();
    let out = &a[3];
    let mut at: Vec<u64> = a[4..].iter().map(|v| v.parse().unwrap()).collect();
    at.sort();
    let n = rule.len() as u8;
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let mut seen = vec![false; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let (mut x0, mut y0, mut x1, mut y1) = (c, c, c, c);
    let mut visited = 0u64;
    let mut t = 0u64;
    let w = size.min(1024);
    let blk = size / w;
    let mut csv = std::fs::File::create(format!("{out}.csv")).unwrap();
    writeln!(csv, "t,x,y,heading,visited,minx,miny,maxx,maxy,left_board").unwrap();
    for &stop in &at {
        let mut left = false;
        while t < stop {
            let i = y as usize * size + x as usize;
            let col = cells[i];
            if !seen[i] {
                seen[i] = true;
                visited += 1;
            }
            h = (h + turn[col as usize]) & 3;
            cells[i] = (col + 1) % n;
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            t += 1;
            if x < 0 || y < 0 || x >= size as i64 || y >= size as i64 {
                left = true;
                break;
            }
            (x0, y0, x1, y1) = (x0.min(x), y0.min(y), x1.max(x), y1.max(y));
        }
        let mut img = vec![0u8; w * w];
        for gy in 0..size {
            for gx in 0..size {
                let i = gy * size + gx;
                if seen[i] {
                    img[(gy / blk) * w + gx / blk] = 1 + cells[i];
                }
            }
        }
        std::fs::write(format!("{out}_{t}.bin"), &img).unwrap();
        writeln!(csv, "{t},{},{},{h},{visited},{},{},{},{},{left}", x - c, y - c, x0 - c, y0 - c, x1 - c, y1 - c).unwrap();
        if left {
            return;
        }
    }
}
