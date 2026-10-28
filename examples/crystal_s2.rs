//! crystal-rules S2 (experiments/archive/2026-10-crystal-rules): the ant on a uniform ground board.
//! Fill a SIZE^2 board with colour G, put the ant in the centre with heading H, run STEPS (or until it
//! leaves a margin of 2 cells). Prints position / bbox of changed cells at doubling checkpoints.
//! If L > 0 only the central L x L square is ground; the rest is blank (colour 0).
//! usage: crystal_s2 RULE G H STEPS [SIZE=4096] [L=0]
use turmite::{DIRS, Rule};

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let g: u8 = a[2].parse().unwrap();
    let h0: u8 = a[3].parse().unwrap();
    let steps: u64 = a[4].parse().unwrap();
    let size: usize = a.get(5).map_or(4096, |v| v.parse().unwrap());
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let l: i64 = a.get(6).map_or(0, |v| v.parse().unwrap());
    let mut cells = vec![g; size * size];
    if l > 0 {
        let c = (size / 2) as i64;
        for yy in 0..size { for xx in 0..size {
            if (xx as i64 - c).abs() > l / 2 || (yy as i64 - c).abs() > l / 2 { cells[yy * size + xx] = 0; }
        } }
    }
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, h0);
    let mut bb = [x, x, y, y];
    let mut next_report = 1u64;
    println!("rule,G,h0,t,x,y,bbox_x0,bbox_x1,bbox_y0,bbox_y1");
    for t in 1..=steps {
        let i = y as usize * size + x as usize;
        let cc = cells[i] as usize;
        h = (h + turn[cc]) & 3;
        cells[i] = ((cc + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        bb = [bb[0].min(x), bb[1].max(x), bb[2].min(y), bb[3].max(y)];
        let off = x < 2 || y < 2 || x >= size as i64 - 2 || y >= size as i64 - 2;
        if t == next_report || t == steps || off {
            println!("{},{g},{h0},{t},{},{},{},{},{},{}", a[1], x - c, y - c, bb[0] - c, bb[1] - c, bb[2] - c, bb[3] - c);
            if t == next_report { next_report *= 4; }
            if off { break; }
        }
    }
}
