//! The falsification harness is checked against the oracle (`reference::Ant`), against two exact
//! symmetries of the dynamics, and on claims whose answer is known.

use proptest::prelude::*;
use turmite::falsify::*;
use turmite::reference::Ant;
use turmite::walkers::splitmix_next;
use turmite::Rule;

fn rule(s: &str) -> Rule {
    s.parse().unwrap()
}

fn rule_strategy() -> impl Strategy<Value = Rule> {
    (2usize..=8, any::<u32>()).prop_map(|(n, bits)| Rule::from_bits(bits, n))
}

fn init_strategy(n: usize) -> impl Strategy<Value = Init> {
    (proptest::collection::btree_map((-4i32..=4, -4i32..=4), 1..n as u8, 0..40), 0u8..4)
        .prop_map(|(m, heading)| Init { cells: m.into_iter().collect(), heading })
}

fn reference_from(rule: &Rule, init: &Init) -> Ant {
    let mut a = Ant::new(rule.clone());
    for &(p, c) in &init.cells {
        a.cells.insert(p, c);
    }
    a.heading = init.heading;
    a
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(96))]

    /// Seeded runner == oracle on arbitrary finite starts (no escape: board is far larger than the walk).
    #[test]
    fn simulate_matches_reference((rule, init) in rule_strategy().prop_flat_map(|r| { let n = r.len(); (Just(r), init_strategy(n)) }),
                                  steps in 0u64..4_000, off in (-300i32..300, -300i32..300)) {
        let mut sim = Sim::centred(2048, steps);
        sim.start = ((1024 + off.0) as usize, (1024 + off.1) as usize);
        let run = simulate(&rule, &init, &sim, None);
        let mut a = reference_from(&rule, &init);
        a.run(steps);
        prop_assert_eq!((run.pos, run.heading), (a.pos, a.heading));
    }

    /// The mid-run obstacle equals: run the oracle to `at`, write the same patch, carry on.
    #[test]
    fn perturbation_matches_reference(rule in rule_strategy(), at in 1u64..6_000, extra in 0u64..2_000,
                                      ahead in 0i32..15, radius in 0i32..7, pseed in any::<u64>()) {
        let n = rule.len() as u64;
        let sim = Sim::centred(2048, at + extra);
        let p = Perturb { at, ahead, radius, seed: pseed };
        let run = simulate(&rule, &Init::default(), &sim, Some(&p));

        let mut a = Ant::new(rule.clone());
        let mut positions = vec![a.pos];
        for _ in 0..at { a.step(); positions.push(a.pos); }
        let back = positions[(at as usize).saturating_sub(4000)];
        let (vx, vy) = (a.pos.0 - back.0, a.pos.1 - back.1);
        let m = vx.abs().max(vy.abs()).max(1) as f64;
        let c = (a.pos.0 + (vx as f64 / m * ahead as f64).round() as i32, a.pos.1 + (vy as f64 / m * ahead as f64).round() as i32);
        let mut st = pseed;
        for dy in -radius..=radius {
            for dx in -radius..=radius {
                let colour = (splitmix_next(&mut st) % n) as u8;
                if colour == 0 { a.cells.remove(&(c.0 + dx, c.1 + dy)); } else { a.cells.insert((c.0 + dx, c.1 + dy), colour); }
            }
        }
        a.run(extra);
        prop_assert_eq!((run.pos, run.heading), (a.pos, a.heading));
    }

    /// Metamorphic: a window of uniform colour k under rule R behaves as the blank board under
    /// the rule rotated by k (R[k..] ++ R[..k]), while the ant stays inside the window.
    #[test]
    fn uniform_background_is_a_rotated_rule(rule in rule_strategy(), k in 1usize..8, steps in 0u64..60) {
        let n = rule.len();
        let k = k % n;
        prop_assume!(k != 0);
        let rotated = Rule([&rule.0[k..], &rule.0[..k]].concat());
        let w = 64;
        let init = Init {
            cells: (-w..=w).flat_map(|y| (-w..=w).map(move |x| ((x, y), k as u8))).collect(),
            heading: 0,
        };
        let a = simulate(&rule, &init, &Sim::centred(512, steps), None);
        let b = simulate(&rotated, &Init::default(), &Sim::centred(512, steps), None);
        prop_assert_eq!((a.pos, a.heading), (b.pos, b.heading));
    }

    /// Rotating the whole picture by h quarter turns (heading h on a blank board) rotates the walk.
    #[test]
    fn heading_is_a_rotation(rule in rule_strategy(), h in 0u8..4, steps in 0u64..3_000) {
        let a = simulate(&rule, &Init::default(), &Sim::centred(2048, steps), None);
        let b = simulate(&rule, &Init { cells: vec![], heading: h }, &Sim::centred(2048, steps), None);
        let mut p = a.pos;
        for _ in 0..h { p = (-p.1, p.0); }
        prop_assert_eq!(b.pos, p);
        prop_assert_eq!(b.heading, (a.heading + h) % 4);
    }
}

#[test]
fn attacks_are_deterministic_and_seed_sensitive() {
    let r = rule("RLL");
    let base = baseline(&r, 512, 20_000);
    let a = make_trial(&r, Class::Patch, 3, 7, 512, 20_000, &base);
    let b = make_trial(&r, Class::Patch, 3, 7, 512, 20_000, &base);
    let c = make_trial(&r, Class::Patch, 3, 8, 512, 20_000, &base);
    assert_eq!(a.init, b.init);
    assert_ne!(a.init, c.init);
}

#[test]
fn clopper_pearson_matches_known_values() {
    // Rule of three: 0 failures in 100 -> upper 95% one-sided ~ 0.03; two-sided 97.5% -> 0.0362.
    let (lo, hi) = clopper_pearson(0, 100, 0.05);
    assert_eq!(lo, 0.0);
    assert!((hi - 0.0362).abs() < 5e-4, "{hi}");
    let (lo, hi) = clopper_pearson(5, 10, 0.05);
    assert!((lo - 0.1871).abs() < 1e-3 && (hi - 0.8129).abs() < 1e-3, "{lo} {hi}");
}

fn claim(line: &str) -> Claim {
    Claim::parse(&format!("{line} registered=test")).unwrap()
}

fn attack(c: &Claim) -> (Baseline, Report, Vec<TrialResult>) {
    use rayon::prelude::*;
    let top = c.horizon * 4u64.pow(c.ladder);
    let base = baseline(&c.rule, c.size, top);
    let mut res: Vec<TrialResult> = plan(c, &base)
        .par_iter()
        .map(|&(k, i)| run_trial(&c.rule, &make_trial(&c.rule, k, i, c.seed, c.size, top, &base)))
        .collect();
    res.sort_by_key(|r| (r.trial.class, r.trial.index));
    let rep = evaluate(c, &base, &res);
    (base, rep, res)
}

// Known answers. RL is Langton's ant (period-104 highway drifting (2,2) from a blank board, onset
// 9976: `experiments/archive/2026-10-census-sweeps/results/confirmed_v2.csv`); RRL builds a 18-step
// highway almost at once; RLL never has one in the census (`non_highway.txt`).

#[test]
fn baseline_matches_the_census() {
    let b = baseline(&rule("RL"), 1024, 200_000);
    assert_eq!(b.canon, Some((104, 2, 2)));
    assert_eq!(b.onset, Some(9976));
    let b = baseline(&rule("RRL"), 1024, 100_000);
    assert_eq!(b.canon, Some((18, 1, 1)));
}

#[test]
fn false_chaos_claim_is_falsified() {
    // "RL has no highway" is false; any start that builds one refutes it, and the blank start does.
    let c = claim("id=t kind=chaotic rule=RL attacks=patch,mono trials=8 horizon=150000 size=1024 seed=1 ladder=0");
    let (_, rep, _) = attack(&c);
    assert_eq!(rep.verdict, Verdict::Falsified, "{:?}", rep.reasons);
    assert!(!rep.counterexamples.is_empty());
}

#[test]
fn true_chaos_claim_survives_only_at_the_horizon() {
    let c = claim("id=t kind=chaotic rule=RLL attacks=patch,mono,half,stripe,sparse,obstacle trials=8 horizon=60000 size=1024 seed=1 ladder=0");
    let (_, rep, _) = attack(&c);
    assert_eq!(rep.verdict, Verdict::Survived, "{:?}", rep.reasons);
}

#[test]
fn highway_claim_on_a_chaotic_rule_is_not_supported() {
    let c = claim("id=t kind=highway rule=RLL attacks=patch,mono trials=8 horizon=60000 size=1024 seed=1 ladder=0");
    let (_, rep, _) = attack(&c);
    assert_eq!(rep.verdict, Verdict::Unsupported);
}

#[test]
fn instrument_controls_pass_on_a_highway_rule() {
    let c = claim("id=t kind=highway rule=RRL attacks=boundary trials=24 horizon=100000 size=2048 seed=3 ladder=0");
    let (_, rep, res) = attack(&c);
    assert_ne!(rep.verdict, Verdict::Invalid, "{:?}", rep.reasons);
    assert_eq!(res.iter().filter(|r| r.trial.class == Class::Heading).count(), 4);
}

#[test]
fn counterexample_shrinks_and_still_falsifies() {
    let r = rule("RL");
    let base = baseline(&r, 1024, 150_000);
    let t = make_trial(&r, Class::Patch, 0, 1, 1024, 150_000, &base);
    let hit = |init: &Init| matches!(simulate(&r, init, &t.sim, None).outcome, Outcome::Highway(_));
    if hit(&t.init) {
        let small = shrink(&t.init, 200, hit);
        assert!(small.cells.len() <= t.init.cells.len());
        assert!(hit(&small));
    }
}

#[test]
fn claim_lines_round_trip_and_reject_typos() {
    assert!(Claim::parse("id=a kind=highway rule=RL registered=2026-10-22T09:00").is_ok());
    assert!(Claim::parse("id=a kind=highway rule=RL").is_err(), "unregistered claims are refused");
    assert!(Claim::parse("id=a kind=highway rule=RL registered=x tirals=5").is_err());
    let cells = vec![((-1, 2), 3u8), ((0, 0), 1)];
    assert_eq!(cells_from_string(&cells_to_string(&cells)).unwrap(), cells);
}

#[test]
fn late_highway_is_flagged_as_horizon_sensitive() {
    // Langton's ant starts its highway at step 9976. A "chaotic" claim made at horizon 5000 survives
    // there, and only an attack past the stated horizon refutes it.
    let c = claim("id=t kind=chaotic rule=RL attacks=patch trials=4 horizon=5000 ladder=2 size=1024 seed=1");
    let (_, rep, _) = attack(&c);
    assert_eq!(rep.verdict, Verdict::Falsified);
    assert!(rep.late, "{:?}", rep.reasons);
    assert_eq!(rep.rungs[0].1, 0, "nothing escapes by the stated horizon");
    assert!(rep.rungs[2].1 > 0);
}
#[test]
fn malformed_claims_are_rejected_without_lossy_numeric_casts() {
    let prefix = "id=t kind=highway rule=RL registered=test";
    for field in ["seed=-1", "seed=1.5", "trials=0", "size=32", "ladder=32", "horizon=0", "p_min=NaN", "same_canon=yes", "quantifier=universl", "id=../escape"] {
        assert!(Claim::parse(&format!("{prefix} {field}")).is_err(), "{field}");
    }
    let c = Claim::parse(&format!("{prefix} seed=18446744073709551615 # comment")).unwrap();
    assert_eq!(c.seed, u64::MAX);
}

#[test]
fn adaptive_attacks_do_not_produce_binomial_confidence() {
    let c = claim("id=t kind=highway rule=RRL quantifier=probabilistic trials=1 horizon=10000 ladder=0 size=128");
    let (_, rep, _) = attack(&c);
    assert!(rep.success_ci.is_none());
    assert_ne!(rep.verdict, Verdict::Survived);
    assert_ne!(rep.verdict, Verdict::Falsified);
}

#[test]
fn cli_rejects_missing_arguments_and_unregistered_claims() {
    use std::process::Command;
    let binary = env!("CARGO_BIN_EXE_falsify");
    let missing = Command::new(binary).output().unwrap();
    assert_eq!(missing.status.code(), Some(2));
    let dir = std::env::temp_dir().join(format!("turmite-falsify-registration-{}", std::process::id()));
    std::fs::create_dir(&dir).unwrap();
    assert!(Command::new("git").args(["init", "--quiet"]).current_dir(&dir).status().unwrap().success());
    std::fs::write(dir.join(".gitignore"), "claims.txt\n").unwrap();
    std::fs::write(dir.join("claims.txt"), "id=t kind=highway rule=RL registered=test\n").unwrap();
    let output = Command::new(binary).args(["claims.txt", "out"]).current_dir(&dir).output().unwrap();
    assert_eq!(output.status.code(), Some(2), "{}", String::from_utf8_lossy(&output.stderr));
    assert!(!dir.join("out").exists());
    std::fs::remove_dir_all(&dir).unwrap();
}

#[test]
fn evolve_chain_is_deterministic_and_spends_exactly_its_budget() {
    let r = rule("RRRL");
    let base = baseline(&r, 512, 60_000);
    let a = evolve_chain(&r, Kind::Highway, 3, 24, true, 9, 0, 512, 60_000, &base);
    let b = evolve_chain(&r, Kind::Highway, 3, 24, true, 9, 0, 512, 60_000, &base);
    assert_eq!(a.len(), 24);
    assert!(a.iter().zip(&b).all(|(x, y)| x.trial.init == y.trial.init && x.run.steps == y.run.steps));
    let c = evolve_chain(&r, Kind::Highway, 4, 24, true, 9, 0, 512, 60_000, &base);
    assert!(a.iter().zip(&c).any(|(x, y)| x.trial.init != y.trial.init), "replicates must differ");
}

#[test]
fn evolve_beats_one_cell_climb_on_a_planted_tail() {
    // Planted-effect calibration: on RL, the best of 120 evaluations by `evolve_chain` should exceed
    // the best of 120 by the old one-cell climb in most of 8 replicates (registered result: p < 1e-8 at 200 x 30).
    let r = rule("RL");
    let base = baseline(&r, 1024, 400_000);
    let best = |v: Vec<TrialResult>| v.iter().map(|t| t.run.steps).max().unwrap();
    let wins = (0..8u32)
        .filter(|&rep| {
            let e = best(evolve_chain(&r, Kind::Highway, rep, 120, true, 5, 0, 1024, 400_000, &base));
            let o = best(adaptive_chain(&r, Kind::Highway, rep, 120, 5, 1024, 400_000, &base));
            e > o
        })
        .count();
    assert!(wins >= 6, "evolve won only {wins}/8");
}
