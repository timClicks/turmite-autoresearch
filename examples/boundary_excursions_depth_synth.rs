//! boundary_excursions_depth_synth BASE_SEED REPS > synth_dhist.csv
//!
//! Revision 4 G1 synthetic gate for the depth–duration readout
//! (experiments/active/2026-10-boundary-excursion-durations, README
//! "Revision 4 registration"). For each law, replicate, pseudo-seed (4) and
//! window k = 16..24 (L_k = 6 * 2^{3(k-16)/8}, depth cap M = round(2L)),
//! excursions (tau, d) are drawn until sum tau >= 2^{k-2} and binned by d with
//! the instrument's fine bins. Output rows use the `--dhist` layout (axis d only;
//! sum_distinct is 0: the revisit readout is not part of G1):
//! spec,k,axis,bin,lo,hi,count,sum_tau,sum_d,sum_distinct with spec LAW:REP:PSEUDO.
//! Laws: SD (SRW from depth 1, absorbed at 0, reflecting at M), SDL (40% lazy SRW,
//! 60% shallow atom d in {1,2,3}, tau ~ Geom(mean L)), SA (area sweep tau = d^2 +
//! U{0..d}), SB (ballistic tau = 2d-1 + Geom(1/2) pauses per step), SC (chord
//! tau = ceil(2 sqrt(d (2R - d))), R = 2L). SA/SB/SC draw d with P(d >= x) = 1/x
//! capped at M. RNG: SplitMix64.
use std::io::Write;
use turmite::walkers::splitmix_next;

const FINE_PER_OCT: usize = 8;
const MAX_FINE: usize = 40 * FINE_PER_OCT;

fn fine_index(v: u64) -> usize {
    let b = 63 - v.leading_zeros() as u64;
    let sub = ((v << 3) >> b) - 8;
    (b as usize) * FINE_PER_OCT + sub as usize
}

fn fine_range(f: usize) -> (u64, u64) {
    let b = (f / FINE_PER_OCT) as u32;
    let sub = (f % FINE_PER_OCT) as u64;
    (
        ((8 + sub) << b).div_ceil(8),
        ((9 + sub) << b).div_ceil(8) - 1,
    )
}

fn unif(st: &mut u64) -> f64 {
    (splitmix_next(st) >> 11) as f64 / (1u64 << 53) as f64
}

/// d with P(d >= x) = 1/x, capped at m.
fn d_law(st: &mut u64, m: u64) -> u64 {
    let u = 1.0 - unif(st); // (0, 1]
    ((1.0 / u).floor() as u64).clamp(1, m)
}

/// SRW (lazy if `lazy`) from depth 1, absorbed at 0, reflecting at m.
fn srw(st: &mut u64, m: u64, lazy: bool) -> (u64, u64) {
    let (mut pos, mut tau, mut d) = (1u64, 0u64, 1u64);
    let mut bits = 0u64;
    let mut nb = 0;
    loop {
        tau += 1;
        if nb < 2 {
            bits = splitmix_next(st);
            nb = 64;
        }
        let b0 = bits & 1;
        let b1 = (bits >> 1) & 1;
        bits >>= 2;
        nb -= 2;
        if lazy && b1 == 0 {
            continue; // stay (step still counted)
        }
        if pos == m || b0 == 0 {
            pos -= 1;
        } else {
            pos += 1;
        }
        if pos == 0 {
            return (tau, d);
        }
        d = d.max(pos);
    }
}

fn draw(law: &str, st: &mut u64, l: f64, m: u64) -> (u64, u64) {
    match law {
        "SD" => srw(st, m, false),
        "SDL" => {
            if unif(st) < 0.6 {
                let d = 1 + splitmix_next(st) % 3;
                let p = 1.0 / l;
                let u = 1.0 - unif(st);
                let tau = 1 + (u.ln() / (1.0 - p).ln()).floor() as u64;
                (tau.max(2 * d - 1), d)
            } else {
                srw(st, m, true)
            }
        }
        "SA" => {
            let d = d_law(st, m);
            (d * d + splitmix_next(st) % (d + 1), d)
        }
        "SB" => {
            let d = d_law(st, m);
            let mut tau = 2 * d - 1;
            for _ in 0..(2 * d - 1) {
                tau += splitmix_next(st).trailing_ones() as u64;
            }
            (tau, d)
        }
        "SC" => {
            let d = d_law(st, m);
            let r = 2.0 * l;
            let df = d as f64;
            (
                ((2.0 * (df * (2.0 * r - df)).sqrt()).ceil() as u64).max(1),
                d,
            )
        }
        _ => panic!("unknown law {law}"),
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let base: u64 = a.get(1).expect("BASE_SEED").parse().unwrap();
    let reps: u64 = a.get(2).map(|s| s.parse().unwrap()).unwrap_or(20);
    // Self-check: fine bins are contiguous and contain their members.
    let mut next = 1u64;
    for f in 0..MAX_FINE {
        let (lo, hi) = fine_range(f);
        if lo > hi {
            continue;
        }
        assert_eq!(lo, next);
        assert_eq!(fine_index(lo), f);
        assert_eq!(fine_index(hi), f);
        next = hi + 1;
    }
    let laws = ["SD", "SDL", "SA", "SB", "SC"];
    let mut out = std::io::stdout().lock();
    writeln!(
        out,
        "spec,k,axis,bin,lo,hi,count,sum_tau,sum_d,sum_distinct"
    )
    .unwrap();
    for (li, law) in laws.iter().enumerate() {
        for rep in 0..reps {
            for ps in 0..4u64 {
                for k in 16u64..=24 {
                    let key = (((li as u64 * 64 + rep) * 8 + ps) * 64) + k;
                    let mut st = base ^ key.wrapping_mul(0x9E37_79B9_7F4A_7C15);
                    let l = 6.0 * 2f64.powf(3.0 * (k as f64 - 16.0) / 8.0);
                    let m = (2.0 * l).round() as u64;
                    let target = 1u64 << (k - 2);
                    let mut n = vec![0u64; MAX_FINE];
                    let mut stau = vec![0u64; MAX_FINE];
                    let mut sd = vec![0u64; MAX_FINE];
                    let mut tot = 0u64;
                    while tot < target {
                        let (tau, d) = draw(law, &mut st, l, m);
                        assert!(d >= 1 && d <= m && tau >= 1);
                        let f = fine_index(d);
                        n[f] += 1;
                        stau[f] += tau;
                        sd[f] += d;
                        tot += tau;
                    }
                    for f in 0..MAX_FINE {
                        if n[f] > 0 {
                            let (lo, hi) = fine_range(f);
                            assert!(sd[f] >= lo * n[f] && sd[f] <= hi * n[f]);
                            writeln!(
                                out,
                                "{law}:{rep}:{ps},{k},d,{f},{lo},{hi},{},{},{},0",
                                n[f], stau[f], sd[f]
                            )
                            .unwrap();
                        }
                    }
                }
            }
        }
    }
}
