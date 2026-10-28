//! experiments/archive/2026-10-rlrlll-macro-transition, Task C1a: thin driver that runs `reference::Ant` from an explicit state
//! and prints a per-step hash, so that an independent implementation (scripts/c1_*.py) can be compared with it.
//! usage: rlrlll_c1_reference_hash STATE_FILE [CELLS_OUT [TRACE_OUT]]
//!
//! STATE_FILE is plain text written by Python (this program parses no proposal file and decides nothing about cycles):
//!   rule RLRLLL | ant X Y H | steps N | checkpoint K | cells M, then M lines "x y colour"
//! Every step is folded into a 64-bit FNV-1a accumulator as the four words (x, y of the cell read, colour read, heading after
//! the turn), each as the two's-complement u32 of an i32. The accumulator is printed every K steps and at the end.
use std::io::Write;
use turmite::Rule;
use turmite::reference::Ant;

const OFFSET: u64 = 0xcbf29ce484222325;
const PRIME: u64 = 0x0000_0100_0000_01b3;

fn fold(acc: u64, w: i32) -> u64 {
    (acc ^ (w as u32 as u64)).wrapping_mul(PRIME)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let text = std::fs::read_to_string(&a[1]).unwrap();
    let mut lines = text.lines();
    let mut rule: Option<Rule> = None;
    let (mut pos, mut h, mut steps, mut cp) = ((0i32, 0i32), 0u8, 0u64, 1000u64);
    let mut cells = Vec::new();
    while let Some(l) = lines.next() {
        let f: Vec<&str> = l.split_whitespace().collect();
        match f[0] {
            "rule" => rule = Some(f[1].parse().unwrap()),
            "ant" => {
                pos = (f[1].parse().unwrap(), f[2].parse().unwrap());
                h = f[3].parse().unwrap();
            }
            "steps" => steps = f[1].parse().unwrap(),
            "checkpoint" => cp = f[1].parse().unwrap(),
            "cells" => {
                for _ in 0..f[1].parse::<usize>().unwrap() {
                    let g: Vec<i32> = lines.next().unwrap().split_whitespace().map(|v| v.parse().unwrap()).collect();
                    cells.push(((g[0], g[1]), g[2] as u8));
                }
            }
            _ => panic!("bad line {l}"),
        }
    }
    let mut ant = Ant::new(rule.unwrap());
    for (p, c) in cells {
        ant.cells.insert(p, c);
    }
    ant.pos = pos;
    ant.heading = h;
    let mut trace = a.get(3).map(|p| std::io::BufWriter::new(std::fs::File::create(p).unwrap()));
    let mut acc = OFFSET;
    let mut minx = pos.0;
    for s in 1..=steps {
        let (x, y) = ant.pos;
        let c = ant.colour_at((x, y));
        ant.step();
        for w in [x, y, c as i32, ant.heading as i32] {
            acc = fold(acc, w);
        }
        minx = minx.min(ant.pos.0);
        if let Some(t) = trace.as_mut() {
            writeln!(t, "{x} {y} {c} {}", ant.heading).unwrap();
        }
        if s % cp == 0 {
            println!("cp {s} {acc:016x}");
        }
    }
    let mut cs: Vec<_> = ant.cells.iter().map(|(&(x, y), &c)| (x, y, c)).collect();
    cs.sort();
    let mut ch = OFFSET;
    for &(x, y, c) in &cs {
        for w in [x, y, c as i32] {
            ch = fold(ch, w);
        }
    }
    if let Some(p) = a.get(2) {
        let mut f = std::io::BufWriter::new(std::fs::File::create(p).unwrap());
        for (x, y, c) in &cs {
            writeln!(f, "{x} {y} {c}").unwrap();
        }
    }
    println!("end steps {} pos {} {} heading {} ncells {} cellhash {ch:016x} acc {acc:016x} minx {minx}", ant.steps, ant.pos.0, ant.pos.1, ant.heading, cs.len());
}
