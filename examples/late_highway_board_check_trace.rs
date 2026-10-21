//! late_highway_board_check_trace RULE GRID T1 T2 ...
//! Plain flat-board loop (same update as `reference::Ant`); prints t, x, y, heading and the visited bounding box at
//! each requested step, or where the ant left the board. Used to compare one rule on two board sizes
//! (experiment `2026-10-21-late-highway-board-check`).
use turmite::{DIRS, Rule};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let size: usize = a[2].parse().unwrap();
    let mut at: Vec<u64> = a[3..].iter().map(|v| v.parse().unwrap()).collect();
    at.sort();
    let n = rule.len() as u8;
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let (mut x0, mut y0, mut x1, mut y1) = (c, c, c, c);
    let mut t = 0u64;
    println!("t,x,y,heading,minx,miny,maxx,maxy");
    for &stop in &at {
        while t < stop {
            let i = y as usize * size + x as usize;
            let col = cells[i];
            h = (h + turn[col as usize]) & 3;
            cells[i] = (col + 1) % n;
            let (dx, dy) = DIRS[h as usize];
            x += dx as i64;
            y += dy as i64;
            t += 1;
            if x < 0 || y < 0 || x >= size as i64 || y >= size as i64 {
                println!("left board at t={t} ({},{})", x - c, y - c);
                return;
            }
            (x0, y0, x1, y1) = (x0.min(x), y0.min(y), x1.max(x), y1.max(y));
        }
        println!("{t},{},{},{h},{},{},{},{}", x - c, y - c, x0 - c, y0 - c, x1 - c, y1 - c);
    }
}
