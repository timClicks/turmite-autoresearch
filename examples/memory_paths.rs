//! Equal-step illustrations, not selected for appearance.
//! cargo run --release --example memory_paths -- 301 16 > experiments/archive/2026-10-memory-walkers/dumps/memory_paths.csv
use std::collections::BTreeMap;
use std::io::Write;
use turmite::{DIRS, walkers::{CookieWalk, EdgeReinforcedWalk, RandomWalk, Rotor, Walker, AntWalker}};

fn run(mut w: impl Walker, label: &str, n: u64) {
    // Buffer the export: per-line writes are costly on the WSL-mounted drive.
    let mut out = std::io::BufWriter::new(std::io::stdout().lock());
    let mut cells = BTreeMap::new();
    let mut pos = (0i64, 0i64);
    let mut h = 0;
    writeln!(out, "{label},0,0,0").unwrap();
    for t in 1..=n {
        let cell = cells.entry(pos).or_insert_with(|| w.initial_cell(pos.0, pos.1));
        w.step(cell, &mut h);
        let (dx, dy) = DIRS[h as usize];
        pos = (pos.0 + dx as i64, pos.1 + dy as i64);
        writeln!(out, "{label},{t},{},{}", pos.0, pos.1).unwrap();
    }
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let seed = args[1].parse().unwrap();
    let k: u32 = args[2].parse().unwrap();
    let n = 1u64 << k;
    println!("spec,t,x,y");
    run(AntWalker::new(&"RLR".parse().unwrap()), "ant:RLR", n);
    run(Rotor { seed }, "rotor", n);
    run(RandomWalk { state: seed }, "rw", n);
    run(CookieWalk::new(seed, 0.25, false), "cookie:0.25", n);
    run(CookieWalk::new(seed, 0.75, false), "cookie:0.75", n);
    run(CookieWalk::new(seed, 0.25, true), "rcookie:0.25", n);
    run(CookieWalk::new(seed, 0.75, true), "rcookie:0.75", n);
    run(EdgeReinforcedWalk::new(seed, 1), "errw:1", n);
    run(EdgeReinforcedWalk::new(seed, 4), "errw:4", n);
}
