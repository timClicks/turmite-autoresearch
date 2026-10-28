//! crystal-rules S4 (experiments/archive/2026-10-crystal-rules): census of the "ground state" and of highways on it.
//! For each rule in FILE (one per line): (A) blank-board run of 2^22 steps on 2048^2: bbox, visited, modal visit count
//! Gv and modal colour Gc of visited cells, fraction of visited cells in that ground state; (B) for every colour g the
//! lone ant on a uniform 1024^2 board of colour g, 2^20 steps, heading 0: bitmask of g's from which it leaves the board.
//! Deterministic; rayon with order-preserving collect (output identical for any thread count).
//! usage: crystal_s4 FILE > csv
use rayon::prelude::*;
use turmite::{DIRS, Rule};

fn blank(turn: &[u8], n: usize, size: usize, steps: u64) -> (bool, [i64; 4], u64, usize, usize, f64, u16) {
    let mut col = vec![0u8; size * size];
    let mut vis = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut bb = [x, x, y, y];
    let mut left = false;
    for _ in 0..steps {
        let i = y as usize * size + x as usize;
        let cc = col[i] as usize;
        h = (h + turn[cc]) & 3;
        col[i] = ((cc + 1) % n) as u8;
        vis[i] = vis[i].saturating_add(1);
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        bb = [bb[0].min(x), bb[1].max(x), bb[2].min(y), bb[3].max(y)];
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            left = true;
            break;
        }
    }
    let seen = vis.iter().filter(|&&v| v > 0).count() as u64;
    let mut hv = [0u64; 256];
    let mut hc = vec![0u64; n];
    for i in 0..vis.len() {
        if vis[i] > 0 {
            hv[vis[i] as usize] += 1;
            hc[col[i] as usize] += 1;
        }
    }
    let gv = (1..256).max_by_key(|&k| (hv[k], std::cmp::Reverse(k))).unwrap();
    let gc = (0..n).max_by_key(|&k| (hc[k], std::cmp::Reverse(k))).unwrap();
    let ground = (0..vis.len()).filter(|&i| vis[i] as usize == gv && col[i] as usize == gc).count();
    let maxv = *vis.iter().max().unwrap() as u16;
    (left, bb, seen, gv, gc, ground as f64 / seen as f64, maxv)
}

fn lone(turn: &[u8], n: usize, g: u8, size: usize, steps: u64) -> bool {
    let mut cells = vec![g; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    for _ in 0..steps {
        let i = y as usize * size + x as usize;
        let cc = cells[i] as usize;
        h = (h + turn[cc]) & 3;
        cells[i] = ((cc + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        if x < 2 || y < 2 || x >= size as i64 - 2 || y >= size as i64 - 2 {
            return true;
        }
    }
    false
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rules: Vec<String> = std::fs::read_to_string(&a[1]).unwrap().lines().map(|s| s.trim().to_string()).filter(|s| !s.is_empty()).collect();
    println!("rule,n,left_board,bbox_w,bbox_h,visited,visited_over_bbox,steps_per_visited,Gv,Gc,ground_frac,max_visits,lone_escape_mask");
    let rows: Vec<String> = rules
        .par_iter()
        .map(|r| {
            let rule: Rule = r.parse().unwrap();
            let n = rule.len();
            let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
            let steps = 1u64 << 22;
            let (left, bb, seen, gv, gc, gf, maxv) = blank(&turn, n, 2048, steps);
            let (w, h) = (bb[1] - bb[0] + 1, bb[3] - bb[2] + 1);
            let mut mask = 0u32;
            for g in 0..n {
                if lone(&turn, n, g as u8, 1024, 1 << 20) {
                    mask |= 1 << g;
                }
            }
            format!("{r},{n},{left},{w},{h},{seen},{:.4},{:.3},{gv},{gc},{gf:.4},{maxv},{mask}", seen as f64 / (w * h) as f64, steps as f64 / seen as f64)
        })
        .collect();
    for r in rows {
        println!("{r}");
    }
}
