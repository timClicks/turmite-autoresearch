//! Square-loop instrument (examples/kappa_square_loop_sampler.rs; experiments/archive/2026-10-kappa-square-loop).
//! 1. Identity: the sampler's area, perimeter, new_cells, boundary_steps, escaped flag and window set equal
//!    `probe_walker`, and its loop counters equal a store-the-whole-path reference that counts by definition.
//! 2. Calibration: blank-board lead-k traps (exactly k laps), PersistentWalk loop fraction against the exact value.
//! 3. Determinism: byte-identical output at 1 and 6 rayon threads.
#![allow(dead_code)]
use proptest::prelude::*;
use std::collections::{HashMap, HashSet};
use turmite::probe::probe_walker;
use turmite::reference;
use turmite::walkers::{AntWalker, PatchedAnt, PersistentWalk, Rotor, Walker, mix64};
use turmite::{DIRS, Rule};

#[path = "../examples/kappa_square_loop_sampler.rs"]
mod sampler;
use sampler::{Win, lead_of, run_spec, run_walker};

type P = (i32, i32);

#[derive(Clone, Copy)]
struct Stp {
    start: P,
    end: P,
    col: u8,
    d: u8,
}

fn escaped_at(p: P, c: i64) -> bool {
    (p.0 as i64).abs() >= c - 2 || (p.1 as i64).abs() >= c - 2
}

/// Reference ant path (unbounded HashMap ant with the same random 5x5 patch); stops after the escaping step.
fn ref_ant_path(rule: &Rule, seed: u64, c: i64, nsteps: u64) -> (Vec<Stp>, Option<usize>) {
    let init = PatchedAnt::new(rule, seed, 2);
    let mut ant = reference::Ant::new(rule.clone());
    for y in -2..=2 {
        for x in -2..=2 {
            let v = init.initial_cell(x, y);
            if v != 0 {
                ant.cells.insert((x as i32, y as i32), v);
            }
        }
    }
    let mut path = vec![];
    for _ in 0..nsteps {
        let (start, col) = (ant.pos, ant.colour_at(ant.pos));
        let d = rule.0[col as usize].delta(); // the rule's letter, not a heading difference
        ant.step();
        path.push(Stp { start, end: ant.pos, col, d });
        if escaped_at(ant.pos, c) {
            return (path.clone(), Some(path.len() - 1));
        }
    }
    (path, None)
}

/// Reference path for any walker, on a HashMap board.
fn ref_walker_path<W: Walker>(mut w: W, c: i64, nsteps: u64) -> (Vec<Stp>, Option<usize>) {
    let mut board: HashMap<P, u8> = HashMap::new();
    let (mut pos, mut h) = ((0i32, 0i32), 0u8);
    let mut path = vec![];
    for _ in 0..nsteps {
        let init = if W::RANDOM_INIT { w.initial_cell(pos.0 as i64, pos.1 as i64) } else { 0 };
        let cell = board.entry(pos).or_insert(init);
        let (col, h0) = (*cell, h);
        w.step(cell, &mut h);
        let (dx, dy) = DIRS[h as usize];
        let start = pos;
        pos = (pos.0 + dx, pos.1 + dy);
        path.push(Stp { start, end: pos, col, d: h.wrapping_sub(h0) & 3 });
        if escaped_at(pos, c) {
            return (path.clone(), Some(path.len() - 1));
        }
    }
    (path, None)
}

#[derive(Clone, Copy, Default, Debug, PartialEq)]
struct Flags {
    boundary: bool,
    new_cell: bool,
    is_loop: bool,
    is_lead: bool,
}

/// By definition, from the whole stored path: flags per step, plus the visited set after each step is built on the fly.
fn flags(path: &[Stp], lead: u8, mut at_end: impl FnMut(usize, &HashSet<P>)) -> Vec<Flags> {
    let mut visited: HashSet<P> = HashSet::from([(0, 0)]);
    let mut out = vec![];
    for (t, s) in path.iter().enumerate() {
        let boundary = DIRS.iter().any(|&(dx, dy)| !visited.contains(&(s.start.0 + dx, s.start.1 + dy)));
        let new_cell = !visited.contains(&s.end);
        visited.insert(s.end);
        let is_loop = t >= 3 && {
            let q = &path[t - 3..=t];
            q[0].start == s.end && q.iter().all(|z| z.d == q[0].d) && (q[0].d == 1 || q[0].d == 3)
        };
        let is_lead = is_loop && lead > 0 && path[t - 3..=t].iter().all(|z| z.col < lead);
        out.push(Flags { boundary, new_cell, is_loop, is_lead });
        at_end(t, &visited);
    }
    out
}

fn window_of(t: usize) -> u32 {
    if t == 0 { 0 } else { 63 - (t as u64).leading_zeros() }
}

fn perimeter(v: &HashSet<P>) -> u64 {
    v.iter().filter(|p| DIRS.iter().any(|&(dx, dy)| !v.contains(&(p.0 + dx, p.1 + dy)))).count() as u64
}

/// Window table by definition. `esc` is the pre-index of the escaping step, if any.
fn ref_windows(path: &[Stp], esc: Option<usize>, lead: u8, min_log2: u32, max_log2: u32) -> Vec<Win> {
    let mut snaps: HashMap<usize, (u64, u64)> = HashMap::new(); // t -> (area, perimeter) at the last step of a window
    let ends: HashSet<usize> = (min_log2..max_log2).map(|k| (1usize << (k + 1)) - 1).collect();
    let fl = flags(path, lead, |t, v| {
        if ends.contains(&t) {
            snaps.insert(t, (v.len() as u64, perimeter(v)));
        }
    });
    let mut out = vec![];
    for k in min_log2..max_log2 {
        let last = (1usize << (k + 1)) - 1;
        if esc.is_some_and(|e| e <= last) || last >= path.len() {
            break;
        }
        let mut w = Win { k, t_end: 1 << (k + 1), steps: 1 << k, ..Win::default() };
        for t in (1usize << k)..=last {
            let f = fl[t];
            w.boundary_steps += f.boundary as u64;
            w.new_cells += f.new_cell as u64;
            if f.is_loop {
                w.loops[f.is_lead as usize][f.boundary as usize] += 1;
                if !(t > 0 && fl[t - 1].is_loop) {
                    w.entries[f.is_lead as usize][f.boundary as usize] += 1;
                }
            }
        }
        // runs of lead-colour loop steps whose terminating step lies in this window
        for t in (1usize << k)..=last {
            if t > 0 && fl[t - 1].is_lead && !fl[t].is_lead {
                let mut a = t - 1;
                while a > 0 && fl[a - 1].is_lead {
                    a -= 1;
                }
                let len = (t - a) as u64;
                w.laps[(((len + 3) / 4).min(9) - 1) as usize] += 1;
            }
        }
        (w.area, w.perimeter) = snaps[&last];
        out.push(w);
    }
    out
}

fn check_against_probe_and_reference<W: Walker>(
    mk: impl Fn() -> W,
    path: (Vec<Stp>, Option<usize>),
    lead: u8,
    size: usize,
    min_log2: u32,
    max_log2: u32,
) -> Result<(), TestCaseError> {
    let got = run_walker(mk(), lead, size, min_log2, max_log2);
    let probe = probe_walker(mk(), size, min_log2, max_log2);
    prop_assert_eq!(got.escaped, probe.escaped);
    prop_assert_eq!(got.windows.len(), probe.windows.len());
    for (g, p) in got.windows.iter().zip(&probe.windows) {
        prop_assert_eq!(g.t_end, p.t_end);
        prop_assert_eq!((g.area, g.perimeter, g.new_cells, g.boundary_steps), (p.area, p.perimeter, p.new_cells, p.boundary_steps));
    }
    let want = ref_windows(&path.0, path.1, lead, min_log2, max_log2);
    prop_assert_eq!(got.windows, want);
    Ok(())
}

fn rule_string(lead: usize, right_first: bool, tail: &[bool]) -> String {
    let (a, b) = if right_first { ('R', 'L') } else { ('L', 'R') };
    let mut s: String = std::iter::repeat(a).take(lead).collect();
    s.push(b);
    s.extend(tail.iter().map(|&t| if t { 'R' } else { 'L' }));
    s
}

proptest! {
    #![proptest_config(ProptestConfig { failure_persistence: Some(Box::new(proptest::test_runner::FileFailurePersistence::Direct("tests/kappa_square_loop.proptest-regressions"))), ..ProptestConfig::with_cases(150) })]
    /// Rules with a designed opening run (lead 1..7), where lead-colour loops and traps actually occur.
    #[test]
    fn lead_rules_match_probe_and_path_reference(
        lead in 1usize..8, right_first in any::<bool>(), tail in prop::collection::vec(any::<bool>(), 0..9),
        seed in any::<u64>(), size_ix in 0usize..3, max_log2 in 7u32..14, min_log2 in 1u32..6,
    ) {
        let s = rule_string(lead, right_first, &tail);
        let rule: Rule = s.parse().unwrap();
        let size = [64usize, 128, 256][size_ix];
        let path = ref_ant_path(&rule, seed, (size / 2) as i64, 1u64 << max_log2);
        check_against_probe_and_reference(|| PatchedAnt::new(&rule, seed, 2), path, lead_of(&s), size, min_log2, max_log2)?;
    }

    /// Arbitrary rules (lead mostly 1-2) so "other" loops are exercised.
    #[test]
    fn random_rules_match_probe_and_path_reference(
        bits in prop::collection::vec(any::<bool>(), 2..13), seed in any::<u64>(),
        size_ix in 0usize..3, max_log2 in 7u32..14, min_log2 in 1u32..6,
    ) {
        let s: String = bits.iter().map(|b| if *b { 'R' } else { 'L' }).collect();
        let rule: Rule = s.parse().unwrap();
        let size = [64usize, 128, 256][size_ix];
        let path = ref_ant_path(&rule, seed, (size / 2) as i64, 1u64 << max_log2);
        check_against_probe_and_reference(|| PatchedAnt::new(&rule, seed, 2), path, lead_of(&s), size, min_log2, max_log2)?;
    }

    /// Walkers: persistent walk (several q) and rotor.
    #[test]
    fn walkers_match_probe_and_path_reference(
        seed in any::<u64>(), qi in 0usize..4, size_ix in 0usize..3, max_log2 in 7u32..14, min_log2 in 1u32..6,
    ) {
        let size = [64usize, 128, 256][size_ix];
        let c = (size / 2) as i64;
        if qi == 3 {
            check_against_probe_and_reference(|| Rotor { seed }, ref_walker_path(Rotor { seed }, c, 1u64 << max_log2), 0, size, min_log2, max_log2)?;
        } else {
            let q = [0.5, 0.7, 0.3][qi];
            check_against_probe_and_reference(|| PersistentWalk::new(seed, q), ref_walker_path(PersistentWalk::new(seed, q), c, 1u64 << max_log2), 0, size, min_log2, max_log2)?;
        }
    }
}

/// The plain ant (AntWalker, blank board) matches the reference ant too, on the blank board of P1.
fn splitmix(s: &mut u64) -> u64 {
    *s = s.wrapping_add(0x9E37_79B9_7F4A_7C15);
    mix64(*s)
}

#[test]
fn blank_board_lead_k_trap_is_exactly_k_laps() {
    // Calibration (a): R^k L tail (and mirror) on a blank board. By definition (whole path, 4k+1 steps): 4k-3 lead-colour
    // loop steps, one entry, one completed run of k laps terminated by step 4k+1, nothing else. Then the sampler's octave
    // windows over the first 32 steps equal the same definition-based count on the 32-step path.
    let mut st = 20261016u64;
    let mut n = 0;
    for k in 1..=6usize {
        for right_first in [true, false] {
            for _ in 0..20 {
                let tail: Vec<bool> = (0..8).map(|_| splitmix(&mut st) & 1 == 1).collect();
                let s = rule_string(k, right_first, &tail);
                let rule: Rule = s.parse().unwrap();
                // blank board: reference ant without a patch
                let mut ant = reference::Ant::new(rule.clone());
                let mut path = vec![];
                for _ in 0..(4 * k + 1) {
                    let (start, col) = (ant.pos, ant.colour_at(ant.pos));
                    let d = rule.0[col as usize].delta();
                    ant.step();
                    path.push(Stp { start, end: ant.pos, col, d });
                }
                let fl = flags(&path, k as u8, |_, _| {});
                let lead_steps: Vec<usize> = (0..path.len()).filter(|&t| fl[t].is_lead).collect();
                assert_eq!(lead_steps, (3..4 * k).collect::<Vec<_>>(), "{s}: lead loop steps must be pre-index 3..4k-1 ({} steps)", 4 * k - 3);
                // the trap is the only loop in these 4k+1 steps, and the step after it is not a loop step
                assert_eq!(fl.iter().filter(|f| f.is_loop).count(), 4 * k - 3, "{s}");
                assert!(!fl[4 * k].is_loop, "{s}: step 4k+1 (L turn) must break the trap");
                // sampler vs definition on the first 32 steps (4k+1 <= 25 < 32), octave windows 1..=4
                let o = run_walker(AntWalker::new(&rule), lead_of(&s), 256, 1, 5);
                let mut ant = reference::Ant::new(rule.clone());
                let mut p32 = vec![];
                for _ in 0..32 {
                    let (start, col) = (ant.pos, ant.colour_at(ant.pos));
                    let d = rule.0[col as usize].delta();
                    ant.step();
                    p32.push(Stp { start, end: ant.pos, col, d });
                }
                let want = ref_windows(&p32, None, lead_of(&s), 1, 5);
                assert_eq!(o.windows, want, "{s}");
                let lead_total: u64 = o.windows.iter().map(|w| w.loops[1][0] + w.loops[1][1]).sum();
                assert!(lead_total >= (4 * k - 3) as u64);
                let laps_k: u64 = o.windows.iter().map(|w| w.laps[k - 1]).sum();
                assert!(laps_k >= 1, "{s}: expected a completed {k}-lap run");
                n += 1;
            }
        }
    }
    assert_eq!(n, 240);
}

#[test]
fn persistent_walk_loop_fraction_matches_exact_value() {
    // Calibration (b). PersistentWalk turns are i.i.d. (R with probability q). A step is a loop step iff the last four
    // turns are equal (a closed path follows from four equal turns): P = q^4 + (1-q)^4. Entry iff additionally the four
    // turns before were not all equal: P_entry = P - (q^5 + (1-q)^5). Exact for every step with pre-index >= 3, so for
    // all windows k >= 2. q = 0.5 gives 1/8 and 1/16. Tolerance: 5 standard errors from the seed-to-seed spread.
    for (q, tol_sd) in [(0.5f64, 5.0f64), (0.7, 5.0), (0.3, 5.0)] {
        let p = q.powi(4) + (1.0 - q).powi(4);
        let pe = p - (q.powi(5) + (1.0 - q).powi(5));
        let (mut fr, mut en) = (vec![], vec![]);
        for seed in 1..=24u64 {
            let o = run_walker(PersistentWalk::new(seed, q), 0, 8192, 10, 21);
            if o.escaped {
                continue;
            }
            let (mut l, mut e, mut n) = (0u64, 0u64, 0u64);
            for w in &o.windows {
                assert_eq!(w.loops[1], [0, 0], "no lead-colour loops for a walker");
                l += w.loops.iter().flatten().sum::<u64>();
                e += w.entries.iter().flatten().sum::<u64>();
                n += w.steps;
            }
            fr.push(l as f64 / n as f64);
            en.push(e as f64 / n as f64);
        }
        assert!(fr.len() >= 16, "too many escapes for q={q}");
        for (name, v, want) in [("fraction", &fr, p), ("entry rate", &en, pe)] {
            let m = v.iter().sum::<f64>() / v.len() as f64;
            let sd = (v.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (v.len() as f64 - 1.0)).sqrt();
            let se = sd / (v.len() as f64).sqrt();
            eprintln!("PW q={q} {name}: measured {m:.5} +- {se:.5} (seed sd {sd:.5}), exact {want:.5}, z {:.2}", (m - want) / se);
            assert!((m - want).abs() < tol_sd * se.max(1e-5), "q={q} {name}: {m} vs exact {want}");
        }
    }
}

#[test]
fn rotor_has_exactly_zero_loop_steps() {
    // Calibration (c), a theorem rather than a rate. A loop step needs turns R,R,R,R (or L x4) closing a 2x2 lap, so the
    // step before the first of the four entered cell A from D (the lap's last cell) and the lap's last step leaves D in the
    // same direction again: D would exit in the same direction on two consecutive visits, but a rotor cell advances its
    // arrow by one quarter turn on every visit. So the rotor has no loop steps at all; the sampler must report 0.
    // (The proptest identity check is vacuous for rotor loop counters; it still checks the other columns, and the
    // persistent walk above is the non-trivial walker calibration of the counters.)
    for seed in 1..=8u64 {
        let o = run_walker(Rotor { seed }, 0, 4096, 10, 19);
        if o.escaped {
            continue;
        }
        for w in &o.windows {
            assert_eq!(w.loops, [[0, 0], [0, 0]], "rotor seed {seed} k {}", w.k);
            assert_eq!(w.entries, [[0, 0], [0, 0]]);
            assert!(w.boundary_steps > 0);
        }
    }
}

#[test]
fn one_and_six_threads_give_identical_bytes() {
    let mut specs: Vec<String> = vec![];
    for (i, r) in ["RL", "RRLLR", "RLLLLLLRLRRRR", "RRRLRLLRLRRRLR", "LLLLRLRRL", "RRRRRLLRLRL"].iter().enumerate() {
        for sd in 601..605u64 {
            specs.push(format!("{r}@{}", sd + i as u64));
        }
    }
    specs.extend(["pw:0.5:7", "pw:0.7:8", "rotor:3", "rotor:4"].map(String::from));
    let run = |n: usize| {
        rayon::ThreadPoolBuilder::new().num_threads(n).build().unwrap().install(|| sampler::batch_csv(&specs, 1024, 5, 17, false))
    };
    let (a, b) = (run(1), run(6));
    assert!(a.lines().count() > specs.len());
    assert_eq!(a.as_bytes(), b.as_bytes());
    // and the single-spec path equals the batch path
    let o = run_spec(&specs[0], 1024, 5, 17);
    assert!(a.contains(&sampler::csv_rows(&specs[0], &o)));
}
