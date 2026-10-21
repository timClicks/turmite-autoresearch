use proptest::prelude::*;
use std::collections::HashSet;
use turmite::reference::Ant;
use turmite::seed::{DepCounter, SeedCollector, Tracked, least_rotation, to_ant_frame};
use turmite::{DIRS, Rule};

fn rule_strategy() -> impl Strategy<Value = Rule> {
    (2usize..=8, any::<u32>()).prop_map(|(n, bits)| Rule::from_bits(bits, n))
}

/// Brute force: nonzero cells after `tau` steps that are stood on at some step in (tau, end].
fn brute_d(rule: &Rule, tau: u64, end: u64) -> (HashSet<(i32, i32)>, Ant) {
    let mut a = Ant::new(rule.clone());
    a.run(tau);
    let snap = a.clone();
    let nonzero: HashSet<(i32, i32)> = a.cells.iter().filter(|(_, c)| **c != 0).map(|(p, _)| *p).collect();
    let mut read = HashSet::new();
    for _ in tau..end {
        read.insert(a.pos);
        a.step();
    }
    (nonzero.intersection(&read).copied().collect(), snap)
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(64))]

    #[test]
    fn tracked_matches_reference(rule in rule_strategy(), steps in 0u64..5_000) {
        let mut r = Ant::new(rule.clone());
        let mut t = Tracked::new(&rule, 2048);
        for _ in 0..steps {
            let read = t.step().unwrap();
            prop_assert_eq!(read.pos, r.pos);
            r.step();
            prop_assert_eq!((t.pos, t.heading), (r.pos, r.heading));
        }
    }

    #[test]
    fn counts_match_brute_force(rule in rule_strategy(), taus in proptest::collection::btree_set(0u64..3_000, 1..6),
                                extra in 1u64..3_000, delta in 1u64..2_000) {
        let queries: Vec<u64> = taus.into_iter().collect();
        let end = queries.last().unwrap() + extra;
        let mut t = Tracked::new(&rule, 2048);
        let mut dc = DepCounter::new(queries.clone(), delta);
        while t.t < end {
            dc.observe(&t.step().unwrap());
        }
        let (full, trunc) = dc.finish();
        for (k, &tau) in queries.iter().enumerate() {
            let (d, _) = brute_d(&rule, tau, end);
            prop_assert_eq!(full[k] as usize, d.len(), "full tau {}", tau);
            let (dt, _) = brute_d(&rule, tau, (tau + delta).min(end));
            prop_assert_eq!(trunc[k] as usize, dt.len(), "trunc tau {}", tau);
        }
    }

    #[test]
    fn seed_is_sufficient(rule in rule_strategy(), tau in 0u64..3_000, extra in 1u64..3_000) {
        // D(tau) on a blank board reproduces the trajectory over (tau, end].
        let end = tau + extra;
        let (d, snap) = brute_d(&rule, tau, end);
        let mut t = Tracked::new(&rule, 2048);
        let mut sc = SeedCollector::new(tau);
        let mut path = vec![];
        while t.t < end {
            let r = t.step().unwrap();
            sc.observe(&r);
            if r.t > tau { path.push(r.pos); }
        }
        let got: HashSet<(i32, i32)> = sc.cells.iter().map(|c| c.pos).collect();
        prop_assert_eq!(&got, &d);
        for c in &sc.cells {
            prop_assert_eq!(c.colour, snap.colour_at(c.pos));
        }
        let cells: Vec<_> = sc.cells.iter().map(|c| (c.pos, c.colour)).collect();
        let mut b = Tracked::with_cells(&rule, 2048, &cells, snap.pos, snap.heading, tau);
        for &p in &path {
            prop_assert_eq!(b.step().unwrap().pos, p);
        }
    }
}

#[test]
fn ant_frame_puts_heading_north() {
    for h in 0..4u8 {
        assert_eq!(to_ant_frame(DIRS[h as usize], h), (0, -1));
    }
}

#[test]
fn least_rotation_is_canonical() {
    assert_eq!(least_rotation(&[3, 1, 1, 3]), vec![1, 1, 3, 3]);
    assert_eq!(least_rotation(&[1, 3, 1, 3]), least_rotation(&[3, 1, 3, 1]));
}
