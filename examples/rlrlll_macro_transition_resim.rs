//! experiments/archive/2026-10-rlrlll-macro-transition, Task D: re-simulate the base case two ways and compare fingerprints.
//! usage: rlrlll_macro_transition_resim RULE STEPS GRID
//! (a) `fast::run` (proptested against `reference`); (b) the plain loop of `rlrlll_macro_transition_window`.
//! Prints pos, heading, FNV-1a of every cell's colour (row-major) and the non-zero cell count for each.
use turmite::fast::{Config, Grid, run};
use turmite::{DIRS, Rule};

fn fingerprint(cells: impl Iterator<Item = u8>) -> (u64, u64) {
    let (mut h, mut nz) = (0xcbf29ce484222325u64, 0u64);
    for c in cells {
        h = (h ^ c as u64).wrapping_mul(0x100000001b3);
        nz += (c != 0) as u64;
    }
    (h, nz)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let steps: u64 = a[2].parse().unwrap();
    let size: usize = a[3].parse().unwrap();

    let t0 = std::time::Instant::now();
    let mut grid = Grid::new(size);
    let cfg = Config { max_steps: steps, ..Config::default() };
    let r = run(&rule, &mut grid, &cfg);
    let (fh, fnz) = fingerprint(grid.cells.iter().copied());
    println!("fast  steps={} stop={:?} pos={:?} h={} hash={fh:016x} nonzero={fnz} secs={:.0}", r.steps, r.stop, r.pos, r.heading, t0.elapsed().as_secs_f64());

    let t0 = std::time::Instant::now();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    for t in 1..=steps {
        let i = (y as usize) * size + x as usize;
        let col = cells[i] as usize;
        h = (h + turn[col]) & 3;
        cells[i] = ((col + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            println!("plain left board at step {t}");
            return;
        }
    }
    let (ph, pnz) = fingerprint(cells.iter().copied());
    println!("plain steps={steps} pos=({}, {}) h={h} hash={ph:016x} nonzero={pnz} secs={:.0}", x - c, y - c, t0.elapsed().as_secs_f64());
    println!("identical: {}", (r.pos.0 as i64, r.pos.1 as i64) == (x - c, y - c) && r.heading == h && fh == ph && fnz == pnz);
}
