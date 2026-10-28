//! Equal-budget comparison of attack-search strategies for the falsification harness
//! (experiment `2026-10-falsify-adaptive-search`).
//!
//! usage: falsify_search OUT_DIR [CLAIMS.txt] [--reps 30] [--budget 200]
//!
//! Arms, each given exactly `budget` evaluations per replicate on claims C1..C3 of the harness:
//! - `random`: uniform draws from the harness's own start generators (patch, mono, half, stripe, sparse, obstacle);
//! - `old`: the harness's one-cell hill-climb (`adaptive_chain`);
//! - `evolve` / `evolve2`: `falsify::evolve_chain` (the second with 1/4 fresh random draws among the children):
//!   random draws for the first quarter of the budget, then a (mu + lambda) search with multi-scale
//!   mutations that include the obstacle's parameters.
//! Everything is keyed by (claim, arm, replicate), so output does not depend on the thread count.

use rayon::prelude::*;
use std::fmt::Write as _;
use std::process::Command;
use turmite::Rule;
use turmite::falsify::*;

#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug)]
enum Arm {
    Random,
    Old,
    Evolve,
    Evolve2,
}

impl Arm {
    fn name(self) -> &'static str {
        match self {
            Arm::Random => "random",
            Arm::Old => "old",
            Arm::Evolve => "evolve",
            Arm::Evolve2 => "evolve2",
        }
    }
    fn salt(self) -> u64 {
        match self {
            Arm::Random => 0x72616e64,
            Arm::Old => 0x6f6c64,
            Arm::Evolve => 0x65766f6c,
            Arm::Evolve2 => 0x65766f32,
        }
    }
}

struct Ctx<'a> {
    rule: &'a Rule,
    base: &'a Baseline,
    size: usize,
    horizon: u64,
    claim_seed: u64,
}

/// Attacker's score: the escape step of a baseline-type highway; twice the horizon for a start that never
/// resolved; four times the horizon for a highway of a different type (a counterexample).
fn score(r: &Run, base: &Baseline, horizon: u64) -> f64 {
    match categorise(r, base) {
        Cat::HwSame => r.steps as f64,
        Cat::HwOther => 4.0 * horizon as f64,
        Cat::Edge | Cat::Unresolved => 2.0 * horizon as f64,
    }
}

#[derive(Default, Clone, Debug)]
struct Outcome1 {
    max: f64,
    steps_at_max: u64,
    other: u32,
    unresolved: u32,
    evals: u32,
}

impl Outcome1 {
    fn push(&mut self, s: f64, r: &Run, base: &Baseline) {
        if s > self.max {
            self.max = s;
            self.steps_at_max = r.steps;
        }
        match categorise(r, base) {
            Cat::HwOther => self.other += 1,
            Cat::Edge | Cat::Unresolved => self.unresolved += 1,
            Cat::HwSame => {}
        }
        self.evals += 1;
    }
}

fn run_arm(c: &Ctx, arm: Arm, rep: u32, budget: u32) -> Outcome1 {
    let mut o = Outcome1::default();
    let results: Vec<TrialResult> = match arm {
        Arm::Random => (0..budget)
            .map(|k| run_trial(c.rule, &random_draw(c.rule, rep * budget + k, c.claim_seed ^ arm.salt(), c.size, c.horizon, c.base)))
            .collect(),
        Arm::Old => adaptive_chain(c.rule, Kind::Highway, rep, budget, c.claim_seed ^ arm.salt(), c.size, c.horizon, c.base),
        Arm::Evolve | Arm::Evolve2 => {
            evolve_chain(c.rule, Kind::Highway, rep, budget, arm == Arm::Evolve2, c.claim_seed, arm.salt(), c.size, c.horizon, c.base)
        }
    };
    for r in results {
        o.push(score(&r.run, c.base, c.horizon), &r.run, c.base);
    }
    o
}

fn norm_sf(z: f64) -> f64 {
    // Abramowitz & Stegun 7.1.26, |error| < 1.5e-7
    let t = 1.0 / (1.0 + 0.3275911 * (z.abs() / 2f64.sqrt()));
    let poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741 + t * (-1.453152027 + t * 1.061405429))));
    let erfc_half = poly * (-(z * z) / 2.0).exp(); // = erfc(|z|/sqrt2)
    if z >= 0.0 { 0.5 * erfc_half } else { 1.0 - 0.5 * erfc_half }
}

/// One-sided Mann-Whitney: P(x tends larger than y), normal approximation with tie correction.
fn mann_whitney(x: &[f64], y: &[f64]) -> (f64, f64) {
    let (n1, n2) = (x.len() as f64, y.len() as f64);
    let u: f64 = x.iter().map(|a| y.iter().map(|b| if a > b { 1.0 } else if a == b { 0.5 } else { 0.0 }).sum::<f64>()).sum();
    let mut all: Vec<f64> = x.iter().chain(y).copied().collect();
    all.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let nn = n1 + n2;
    let mut tie = 0.0;
    let mut i = 0;
    while i < all.len() {
        let j = all[i..].iter().take_while(|&&v| v == all[i]).count();
        tie += (j as f64).powi(3) - j as f64;
        i += j;
    }
    let var = n1 * n2 / 12.0 * ((nn + 1.0) - tie / (nn * (nn - 1.0)));
    let z = (u - n1 * n2 / 2.0) / var.sqrt();
    (u / (n1 * n2), norm_sf(z))
}

fn median(v: &[f64]) -> f64 {
    let mut s = v.to_vec();
    s.sort_by(|a, b| a.partial_cmp(b).unwrap());
    (s[(s.len() - 1) / 2] + s[s.len() / 2]) / 2.0
}

fn git(args: &[&str]) -> String {
    Command::new("git").args(args).output().map(|o| String::from_utf8_lossy(&o.stdout).trim().to_string()).unwrap_or_default()
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let out_dir = args.first().expect("usage: falsify_search OUT_DIR [CLAIMS.txt] [--reps N] [--budget N]");
    let flag = |name: &str, d: u32| args.iter().position(|a| a == name).map_or(d, |i| args[i + 1].parse().unwrap());
    let (reps, budget) = (flag("--reps", 30), flag("--budget", 200));
    let claims_path = args.get(1).filter(|a| !a.starts_with("--")).cloned().unwrap_or("experiments/active/2026-10-falsification-harness/claims.txt".into());
    let claims: Vec<Claim> = std::fs::read_to_string(&claims_path)
        .unwrap()
        .lines()
        .map(str::trim)
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .map(|l| Claim::parse(l).unwrap())
        .filter(|c| c.kind == Kind::Highway)
        .collect();

    let mut rows: Vec<(String, Arm, u32, Outcome1)> = vec![];
    for claim in &claims {
        let base = baseline(&claim.rule, claim.size, claim.horizon);
        let ctx = Ctx { rule: &claim.rule, base: &base, size: claim.size, horizon: claim.horizon, claim_seed: claim.seed };
        let jobs: Vec<(Arm, u32)> = [Arm::Random, Arm::Old, Arm::Evolve, Arm::Evolve2].into_iter().flat_map(|a| (0..reps).map(move |r| (a, r))).collect();
        let done: Vec<(String, Arm, u32, Outcome1)> = jobs.par_iter().map(|&(a, r)| (claim.id.clone(), a, r, run_arm(&ctx, a, r, budget))).collect();
        rows.extend(done);
    }
    rows.sort_by(|a, b| (&a.0, a.1, a.2).cmp(&(&b.0, b.1, b.2)));

    let dirty = git(&["status", "--porcelain", "--", "src", "tests"]);
    let prov = format!(
        "# cmd: falsify_search {}\n# commit: {}\n# uncommitted src/tests files: {}\n# reps={reps} budget={budget}\n",
        args.join(" "),
        git(&["rev-parse", "HEAD"]),
        if dirty.is_empty() { "none".to_string() } else { dirty.replace('\n', " | ") }
    );
    let mut csv = prov.clone();
    csv.push_str("claim,arm,rep,max_score,steps_at_max,other_type,unresolved,evals\n");
    for (id, a, r, o) in &rows {
        let _ = writeln!(csv, "{id},{},{r},{},{},{},{},{}", a.name(), o.max, o.steps_at_max, o.other, o.unresolved, o.evals);
    }
    std::fs::create_dir_all(out_dir).unwrap();
    std::fs::write(format!("{out_dir}/search.csv"), csv).unwrap();

    let mut s = prov;
    let _ = writeln!(s, "max score per replicate = longest escape step; 2*horizon = unresolved; 4*horizon = different highway type");
    for claim in &claims {
        let get = |a: Arm| -> Vec<&Outcome1> { rows.iter().filter(|r| r.0 == claim.id && r.1 == a).map(|r| &r.3).collect() };
        let m = |a: Arm| get(a).iter().map(|o| o.max).collect::<Vec<_>>();
        let (rnd, old, evo, ev2) = (m(Arm::Random), m(Arm::Old), m(Arm::Evolve), m(Arm::Evolve2));
        let _ = writeln!(s, "\n{} (rule {})", claim.id, claim.rule);
        for (a, v) in [(Arm::Random, &rnd), (Arm::Old, &old), (Arm::Evolve, &evo), (Arm::Evolve2, &ev2)] {
            let other_reps = get(a).iter().filter(|o| o.other > 0).count();
            let _ = writeln!(s, "  {:<7} median max {:>9.0}  max {:>9.0}  replicates with a different-type highway: {other_reps}/{reps}", a.name(), median(v), v.iter().cloned().fold(0.0, f64::max));
        }
        for (name, x, y) in [("evolve > random", &evo, &rnd), ("old > random", &old, &rnd), ("evolve > old", &evo, &old), ("evolve2 > random", &ev2, &rnd), ("evolve2 > evolve", &ev2, &evo)] {
            let (auc, p) = mann_whitney(x, y);
            let _ = writeln!(s, "  {name:<16} P(x>y)={auc:.3}  one-sided p={p:.2e}");
        }
    }
    std::fs::write(format!("{out_dir}/search_summary.txt"), &s).unwrap();
    print!("{s}");
}
