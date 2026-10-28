//! Oracle test for `prefix_horizon` and for the prefix lemma it supports
//! (`experiments/archive/2026-10-prefix-causal-horizon/README.md`): rules `w`, `w'` (`n <= n'`) whose letters first disagree with
//! the periodic extension of `w` at colour `q` have identical positions until the first step that reads colour `q`.

use proptest::prelude::*;
use std::collections::HashMap;
use turmite::prefix_horizon::{PairRun, canonical_hash, first_mismatch, first_position_difference, horizon, touched_shape, touched_shape_bg};
use turmite::reference::Ant;
use turmite::Rule;

const CAP: u64 = 2_500;
const BOARD: usize = 2 * CAP as usize + 5; // the ant cannot reach the edge in CAP steps

/// Obvious version of `horizon` on the reference ant.
fn horizon_ref(rule: &Rule, cap: u64) -> (Vec<Option<u64>>, Option<u64>) {
    let n = rule.len();
    let mut a = Ant::new(rule.clone());
    let mut first = vec![None; n];
    let mut visits: HashMap<(i32, i32), usize> = HashMap::new();
    for step in 1..=cap {
        let c = a.colour_at(a.pos) as usize;
        let v = visits.entry(a.pos).or_insert(0);
        if *v >= n {
            return (first, Some(step));
        }
        *v += 1;
        if first[c].is_none() {
            first[c] = Some(step);
        }
        a.step();
    }
    (first, None)
}

/// First `t >= 1` with different positions after `t` steps, within `cap` steps.
fn first_difference(w: &Rule, w2: &Rule, cap: u64) -> Option<u64> {
    let (mut a, mut b) = (Ant::new(w.clone()), Ant::new(w2.clone()));
    (1..=cap).find(|_| {
        a.step();
        b.step();
        a.pos != b.pos
    })
}

#[test]
fn lockstep_difference_matches_reference_on_all_pairs_up_to_length_5() {
    let rules: Vec<Rule> = (1..=5usize).flat_map(|n| (0..(1u32 << n)).map(move |b| rule_from(b, n))).collect();
    for (i, w) in rules.iter().enumerate() {
        for w2 in &rules[i..] {
            let want = first_difference(w, w2, 1_200);
            match first_position_difference(w, w2, 1_200, 2 * 1_200 + 5) {
                PairRun::Differ(t) => assert_eq!(Some(t), want, "{w} vs {w2}"),
                PairRun::Same(_) => assert_eq!(want, None, "{w} vs {w2}"),
                PairRun::Left(_) => panic!("{w} vs {w2}: left a board that cannot be left in 1200 steps"),
            }
        }
    }
}

fn rule_from(bits: u32, n: usize) -> Rule {
    Rule::from_bits(bits, n)
}

#[derive(Debug, Default)]
struct Tally {
    exact_differs: u32,    // (i), colour q read within the cap and positions differ exactly then
    exact_unreached: u32,  // (i), colour q not read within the cap and no difference seen
    repeated: u32,         // (ii)
    wrapped_bound_hit: u32, // (iii) with an actual difference, checked against the wrapped read
    wrapped_bound_none: u32, // (iii), no difference within the cap
}

fn check_pair(w: &Rule, w2: &Rule) -> &'static str {
    let (w, w2) = if w.len() <= w2.len() { (w, w2) } else { (w2, w) };
    let (n, m) = (w.len(), w2.len());
    let diff = first_difference(w, w2, CAP);
    let h2 = horizon(w2, CAP, BOARD);
    match first_mismatch(w, w2) {
        Some(q) => match h2.first[q] {
            // (i) differs exactly when colour q is first read
            Some(f) => {
                assert_eq!(diff, Some(f), "{w} vs {w2}, q = {q}");
                "exact_differs"
            }
            None => {
                assert_eq!(diff, None, "{w} vs {w2}: colour {q} not read within the cap");
                "exact_unreached"
            }
        },
        None if m % n == 0 => {
            assert_eq!(diff, None, "{w} vs {w2}: w' is w repeated"); // (ii)
            "repeated"
        }
        None => {
            // (iii) positions agree until the first read of a wrapped cell
            if let Some(d) = diff {
                let wr = h2.wrapped_read.unwrap_or_else(|| panic!("{w} vs {w2} differ at {d} before any wrapped read"));
                assert!(d >= wr, "{w} vs {w2}: differ at {d} < wrapped read {wr}");
                "wrapped_bound_hit"
            } else {
                "wrapped_bound_none"
            }
        }
    }
}

#[test]
fn horizon_matches_reference_on_all_rules_up_to_length_8() {
    for n in 1..=8usize {
        for bits in 0..(1u32 << n) {
            let r = rule_from(bits, n);
            let h = horizon(&r, CAP, BOARD);
            let (first, wrapped) = horizon_ref(&r, CAP);
            assert_eq!(h.first, first, "{r}");
            assert_eq!(h.wrapped_read, wrapped, "{r}");
        }
    }
}

#[test]
fn lemma_exhaustive_pairs_up_to_length_6() {
    let rules: Vec<Rule> = (1..=6usize).flat_map(|n| (0..(1u32 << n)).map(move |b| rule_from(b, n))).collect();
    let mut t = Tally::default();
    for (i, w) in rules.iter().enumerate() {
        for w2 in &rules[i..] {
            match check_pair(w, w2) {
                "exact_differs" => t.exact_differs += 1,
                "exact_unreached" => t.exact_unreached += 1,
                "repeated" => t.repeated += 1,
                "wrapped_bound_hit" => t.wrapped_bound_hit += 1,
                _ => t.wrapped_bound_none += 1,
            }
        }
    }
    eprintln!("{t:?}");
    // The test must exercise every branch of the statement, not pass vacuously.
    assert!(t.exact_differs > 1000 && t.repeated > 10 && t.wrapped_bound_hit + t.wrapped_bound_none > 10, "{t:?}");
}

#[test]
fn prefix_extensions_up_to_length_12() {
    // The case the census meets: a longer rule that shares a long prefix with a shorter one.
    for n in 2..=8usize {
        for bits in 0..(1u32 << n) {
            let w = rule_from(bits, n);
            for extra in 1..=4usize {
                for tail in 0..(1u32 << extra) {
                    let w2 = rule_from(bits | (tail << n), n + extra);
                    let _ = check_pair(&w, &w2);
                }
            }
        }
    }
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(400))]
    #[test]
    fn lemma_random_pairs(a in 1usize..=12, b in 1usize..=12, x in any::<u32>(), y in any::<u32>(), shared in 0usize..=12) {
        // Force a common prefix of length `shared` so the interesting cases are common.
        let k = shared.min(a).min(b);
        let mask = (1u32 << k) - 1;
        let w = rule_from(x & ((1u32 << a) - 1), a);
        let w2 = rule_from((y & !mask | x & mask) & ((1u32 << b) - 1), b);
        let _ = check_pair(&w, &w2);
    }
}

/// Visited cells of the reference ant (positions before each step), with the cell the ant stands on after the last step excluded,
/// matching `touched_shape`, which marks a cell when the ant writes it.
fn visited_ref(rule: &Rule, steps: u64) -> Vec<(i64, i64)> {
    let mut a = Ant::new(rule.clone());
    let mut seen = std::collections::HashSet::new();
    for _ in 0..steps {
        seen.insert((a.pos.0 as i64, a.pos.1 as i64));
        a.step();
    }
    seen.into_iter().collect()
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(150))]
    #[test]
    fn touched_shape_matches_reference_and_is_symmetry_invariant(n in 2usize..=10, bits in any::<u32>(), steps in 1u64..=6_000) {
        let r = rule_from(bits & ((1u32 << n) - 1), n);
        let cells = visited_ref(&r, steps);
        let s = touched_shape(&r, steps, 2 * steps as usize + 7).expect("cannot leave this board");
        prop_assert_eq!(s.cells, cells.len());
        let (xs, ys): (Vec<i64>, Vec<i64>) = cells.iter().cloned().unzip();
        prop_assert_eq!(s.width as i64, xs.iter().max().unwrap() - xs.iter().min().unwrap() + 1);
        prop_assert_eq!(s.height as i64, ys.iter().max().unwrap() - ys.iter().min().unwrap() + 1);
        prop_assert_eq!(s.hash, canonical_hash(&cells));
        // translation and the eight symmetries must not change the hash
        let moved: Vec<(i64, i64)> = cells.iter().map(|&(x, y)| (-y + 17, x - 5)).collect();
        prop_assert_eq!(canonical_hash(&moved), s.hash);
        let flipped: Vec<(i64, i64)> = cells.iter().map(|&(x, y)| (y, x)).collect();
        prop_assert_eq!(canonical_hash(&flipped), s.hash);
    }
}

#[test]
fn canonical_hash_separates_different_shapes() {
    let line: Vec<(i64, i64)> = (0..5).map(|i| (i, 0)).collect();
    let ell: Vec<(i64, i64)> = (0..5).map(|i| (i, 0)).chain([(0, 1)]).collect();
    assert_ne!(canonical_hash(&line), canonical_hash(&ell));
    let vertical: Vec<(i64, i64)> = (0..5).map(|i| (0, i)).collect();
    assert_eq!(canonical_hash(&line), canonical_hash(&vertical));
}

/// Independent reference for a uniform background: HashMap with default colour `k` (the reference Ant has default 0).
fn visited_ref_bg(rule: &Rule, steps: u64, k: u8) -> Vec<(i64, i64)> {
    let n = rule.len() as u8;
    let mut cells: HashMap<(i32, i32), u8> = HashMap::new();
    let (mut pos, mut heading) = ((0i32, 0i32), 0u8);
    let mut seen = std::collections::HashSet::new();
    for _ in 0..steps {
        seen.insert((pos.0 as i64, pos.1 as i64));
        let c = *cells.get(&pos).unwrap_or(&k);
        heading = (heading + rule.0[c as usize].delta()) % 4;
        cells.insert(pos, (c + 1) % n);
        let (dx, dy) = turmite::DIRS[heading as usize];
        pos = (pos.0 + dx, pos.1 + dy);
    }
    seen.into_iter().collect()
}

fn rotated(w: &Rule, k: usize) -> Rule {
    Rule((0..w.len()).map(|c| w.0[(c + k) % w.len()]).collect())
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(200))]
    /// The uniform-background identity: w on background k == rot_k(w) on a blank board, and both match an independent reference.
    #[test]
    fn uniform_background_equals_rotated_rule(n in 2usize..=10, bits in any::<u32>(), k_raw in any::<usize>(), steps in 1u64..=5_000) {
        let w = rule_from(bits & ((1u32 << n) - 1), n);
        let k = k_raw % n;
        let board = 2 * steps as usize + 7;
        let on_bg = touched_shape_bg(&w, steps, board, k).expect("cannot leave");
        let rot = touched_shape(&rotated(&w, k), steps, board).expect("cannot leave");
        prop_assert_eq!(on_bg, rot);
        let cells = visited_ref_bg(&w, steps, k as u8);
        prop_assert_eq!(on_bg.cells, cells.len());
        prop_assert_eq!(on_bg.hash, canonical_hash(&cells));
    }
}
