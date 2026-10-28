//! `FreshTurnAnt` (wall-vs-memory Stage 3, gate T0) against an independent sparse reference
//! written from the README semantics; the identity `ft:RULE:<rule[0]>` = the ant; and the
//! fresh-run bound the registration states (at most 4 consecutive steps from fresh cells under
//! a quarter-turn policy, at most 2 under reversal).
use proptest::prelude::*;
use std::collections::{HashMap, HashSet};
use turmite::probe::{probe, probe_walker};
use turmite::reference::Ant;
use turmite::walkers::{FreshTurnAnt, Walker};
use turmite::{DIRS, Rule};

/// Sparse reference: colours and the set of cells departed from, kept apart.
struct RefFreshTurn {
    rule: Rule,
    fresh_turn: u8,
    colours: HashMap<(i32, i32), usize>,
    departed: HashSet<(i32, i32)>,
    pos: (i32, i32),
    heading: u8,
}

impl RefFreshTurn {
    /// One step; returns whether it was taken from a fresh cell.
    fn step(&mut self) -> bool {
        let fresh = !self.departed.contains(&self.pos);
        let c = *self.colours.get(&self.pos).unwrap_or(&0);
        let turn = if fresh { self.fresh_turn } else { self.rule.0[c].delta() };
        self.heading = (self.heading + turn) % 4;
        self.colours.insert(self.pos, (c + 1) % self.rule.len());
        self.departed.insert(self.pos);
        let (dx, dy) = DIRS[self.heading as usize];
        self.pos = (self.pos.0 + dx, self.pos.1 + dy);
        fresh
    }
}

fn rule_strategy() -> impl Strategy<Value = Rule> {
    (2usize..=12).prop_flat_map(|n| (0u32..(1 << n)).prop_map(move |b| Rule::from_bits(b, n)))
}

fn turn_strategy() -> impl Strategy<Value = &'static str> {
    prop_oneof![Just("R"), Just("L"), Just("U")]
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 96, rng_seed: proptest::test_runner::RngSeed::Fixed(20261028), ..ProptestConfig::default() })]

    #[test]
    fn matches_sparse_reference_and_bounds_fresh_runs(rule in rule_strategy(), t in turn_strategy()) {
        let ft = FreshTurnAnt::parse_turn(t);
        let mut w = FreshTurnAnt::new(&rule, ft);
        let mut r = RefFreshTurn { rule, fresh_turn: ft, colours: HashMap::new(), departed: HashSet::new(), pos: (0, 0), heading: 0 };
        let mut cells: HashMap<(i32, i32), u8> = HashMap::new();
        let (mut pos, mut h) = ((0i32, 0i32), 0u8);
        let bound = if t == "U" { 2 } else { 4 };
        let (mut run, mut longest) = (0usize, 0usize);
        for _ in 0..20_000 {
            let cell = cells.entry(pos).or_insert_with(|| w.initial_cell(pos.0 as i64, pos.1 as i64));
            w.step(cell, &mut h);
            let fresh = r.step();
            prop_assert_eq!(h, r.heading);
            prop_assert_eq!((*cell & 0x7f) as usize, r.colours[&pos]);
            let (dx, dy) = DIRS[h as usize];
            pos = (pos.0 + dx, pos.1 + dy);
            prop_assert_eq!(pos, r.pos);
            run = if fresh { run + 1 } else { 0 };
            longest = longest.max(run);
            prop_assert!(run <= bound, "fresh run {} > {} ({})", run, bound, t);
        }
        // The bound is attained for quarter turns (a 2x2 block from the start cell).
        if t != "U" {
            prop_assert_eq!(longest, 4);
        }
    }

    #[test]
    fn colour_zero_turn_is_the_reference_ant(rule in rule_strategy()) {
        let mut w = FreshTurnAnt::new(&rule, rule.0[0].delta());
        let mut ant = Ant::new(rule);
        let mut cells: HashMap<(i32, i32), u8> = HashMap::new();
        let mut h = 0u8;
        for _ in 0..20_000 {
            let p = ant.pos;
            let cell = cells.entry(p).or_insert(0);
            w.step(cell, &mut h);
            ant.step();
            prop_assert_eq!(h, ant.heading);
            prop_assert_eq!(*cells.get(&p).unwrap() & 0x7f, ant.colour_at(p));
        }
    }
}

#[test]
fn colour_zero_turn_probe_equals_ant_probe() {
    for rule in ["RL", "RLR", "RRLLLRLRRRLL", "RRRLLLLR", "LR", "LLRR"] {
        let rule: Rule = rule.parse().unwrap();
        let a = probe(&rule, 1024, 8, 18);
        let b = probe_walker(FreshTurnAnt::new(&rule, rule.0[0].delta()), 1024, 8, 18);
        assert_eq!(a.windows, b.windows, "{rule}");
        assert_eq!(a.escaped, b.escaped);
    }
}

/// The control: a different fresh turn changes the trajectory, so the identity above is not
/// vacuous.
#[test]
fn other_fresh_turns_differ_from_the_ant() {
    let rule: Rule = "RRLLLRLRRRLL".parse().unwrap();
    let ant = probe(&rule, 1024, 8, 18);
    for t in ["L", "U"] {
        let b = probe_walker(FreshTurnAnt::new(&rule, FreshTurnAnt::parse_turn(t)), 1024, 8, 18);
        assert_ne!(ant.windows, b.windows, "{t}");
    }
}
