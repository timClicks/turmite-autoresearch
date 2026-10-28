// Known-answer calibration of the gate-concentration statistic (experiments/archive/2026-10-kappa-return-gates).
// No arguments; prints JSON. Uniform flow (events proportional to exposure) must give ~0, planted gates > 0.
use turmite::return_gates::{self, Key, Tally};
use turmite::walkers::mix64;

fn next(s: &mut u64) -> u64 {
    *s = s.wrapping_add(0x9E37_79B9_7F4A_7C15);
    mix64(*s)
}

fn synthetic(seed: u64, bins: usize, events: u64, planted: Option<(usize, f64)>) -> Tally {
    let mut s = seed;
    let mut t = Tally::default();
    let mut weight = Vec::new();
    for b in 0..bins {
        // heavy-tailed exposure: 10^U over three decades, like unequal tile occupation
        let e = (10f64.powf(3.0 * (next(&mut s) >> 11) as f64 / (1u64 << 53) as f64)).round() as u64 + 1;
        let key: Key = ((b / 64) as i32, (b % 64) as i32, 0, 0);
        t.exposure.insert(key, e);
        weight.push(e as f64 * planted.map_or(1.0, |(m, f)| if b % m == 0 { f } else { 1.0 }));
    }
    let total: f64 = weight.iter().sum();
    let cum: Vec<f64> = weight.iter().scan(0.0, |a, w| { *a += w / total; Some(*a) }).collect();
    for _ in 0..events {
        let u = (next(&mut s) >> 11) as f64 / (1u64 << 53) as f64;
        let b = cum.partition_point(|&c| c < u).min(bins - 1);
        *t.events.entry(((b / 64) as i32, (b % 64) as i32, 0, 0)).or_insert(0) += 1;
    }
    t
}

fn summarize(v: &[f64]) -> (f64, f64) {
    let m = v.iter().sum::<f64>() / v.len() as f64;
    (m, (v.iter().map(|x| (x - m).powi(2)).sum::<f64>() / (v.len() as f64 - 1.0)).sqrt())
}

fn main() {
    let reps = 200u64;
    let mut rows = Vec::new();
    for &(bins, events) in &[(30usize, 400u64), (300, 1000), (1000, 3000), (4000, 60000), (4000, 1_000_000)] {
        let (mut nul, mut pl) = (Vec::new(), Vec::new());
        for r in 0..reps {
            let seed = 2026102061 * 1000 + r;
            let (o, m, _, _, _) = return_gates::concentration(&synthetic(seed, bins, events, None), seed ^ 0xABCD, 100);
            nul.push(o - m);
            let (o, m, _, _, _) = return_gates::concentration(&synthetic(seed ^ 0x55, bins, events, Some((20, 6.0))), seed ^ 0xABCD, 100);
            pl.push(o - m);
        }
        let (nm, ns) = summarize(&nul);
        let (pm, ps) = summarize(&pl);
        rows.push(format!("{{\"bins\":{bins},\"events\":{events},\"null_mean\":{nm:.5},\"null_sd\":{ns:.5},\"planted_mean\":{pm:.5},\"planted_sd\":{ps:.5},\"planted_over_null_sd\":{:.2}}}", pm / ns));
    }
    println!("{{\"seed_base\":2026102061,\"replicates\":{reps},\"null_draws\":100,\"planted\":\"every 20th bin x6 rate\",\"rows\":[{}]}}", rows.join(","));
}
