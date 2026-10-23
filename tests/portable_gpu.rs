//! Hardware oracle checks. Run with `--features wgpu --test portable_gpu`.
#![cfg(feature = "wgpu")]

use proptest::prelude::*;
use std::sync::{Mutex, OnceLock};
use turmite::detect::{MIN_SPAN, exit_confirms, find_highway};
use turmite::ext::bg_colour;
use turmite::fast::{self, Config, Grid, RunResult, Stop};
use turmite::portable_gpu::{GpuConfig, GpuSweeper, Job};
use turmite::{DIRS, Rule};

fn rigs() -> &'static Mutex<Vec<GpuSweeper>> {
    static RIGS: OnceLock<Mutex<Vec<GpuSweeper>>> = OnceLock::new();

    RIGS.get_or_init(|| {
        Mutex::new(
            [(5, 64, 997, 256), (3, 100, 4093, 256), (4, 200, 1501, 16)]
                .into_iter()
                .map(|(lanes, grid, slice_steps, pool_tiles)| {
                    GpuSweeper::new(GpuConfig {
                        lanes,
                        grid,
                        slice_steps,
                        pool_tiles,
                        history: 700,
                        max_period: 300,
                        ..GpuConfig::default()
                    })
                    .unwrap()
                })
                .collect(),
        )
    })
}

fn same(got: &RunResult, want: &RunResult) -> Result<(), TestCaseError> {
    prop_assert_eq!(format!("{got:?}"), format!("{want:?}"));
    Ok(())
}

fn oracle(job: &Job, cfg: &GpuConfig) -> RunResult {
    let det = Config {
        max_steps: job.max_steps,
        checkpoint: 1000,
        history: cfg.history,
        max_period: cfg.max_period,
    };

    if job.bg_seed.is_none() {
        return fast::run(&job.rule, &mut Grid::new(cfg.grid), &det);
    }

    let seed = job.bg_seed.unwrap();
    let size = cfg.grid;
    let c = (size / 2) as i32;
    let mut cells = (0..size * size)
        .map(|i| {
            bg_colour(
                seed,
                (i % size) as i64 - c as i64,
                (i / size) as i64 - c as i64,
                job.rule.len(),
            )
        })
        .collect::<Vec<_>>();
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let (mut minx, mut maxx, mut miny, mut maxy) = (c, c, c, c);
    let mut trail = vec![(0, 0)];
    let mut stop = Stop::Budget;
    let mut steps = 0;

    while steps < job.max_steps {
        let idx = y as usize * size + x as usize;
        let col = cells[idx] as usize;
        h = (h + job.rule.0[col].delta()) & 3;
        cells[idx] = ((col + 1) % job.rule.len()) as u8;
        x += DIRS[h as usize].0;
        y += DIRS[h as usize].1;
        steps += 1;

        if x < 0 || y < 0 || x >= size as i32 || y >= size as i32 {
            stop = Stop::Escaped;
            break;
        }

        minx = minx.min(x);
        maxx = maxx.max(x);
        miny = miny.min(y);
        maxy = maxy.max(y);
        trail.push((x - c, y - c));
    }

    let trail = &trail[trail.len().saturating_sub(cfg.history)..];
    let periodic_tail = find_highway(trail, cfg.max_period, MIN_SPAN);
    let highway = if stop == Stop::Escaped {
        periodic_tail
            .or_else(|| find_highway(trail, cfg.max_period, 2000))
            .filter(|&hw| exit_confirms(hw, h))
    } else {
        None
    };

    RunResult {
        steps,
        stop,
        pos: (x - c, y - c),
        heading: h,
        highway,
        periodic_tail,
        extent: ((maxx - minx + 1) as u32, (maxy - miny + 1) as u32),
    }
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(32))]

    #[test]
    fn gpu_equals_cpu_oracle(
        specs in prop::collection::vec((1u32..4096, 2usize..12, 0u64..40_000, prop::option::of(any::<u64>())), 1..10)
    ) {
        let jobs = specs.into_iter().map(|(bits, n, max_steps, bg_seed)| Job {
            rule: Rule::from_bits(bits, n), bg_seed, max_steps,
        }).collect::<Vec<_>>();
        let mut rigs = rigs().lock().unwrap();

        for sw in rigs.iter_mut() {
            let results = sw.run(&jobs, |_| {}).unwrap();

            for (job, got) in jobs.iter().zip(&results) {
                same(got, &oracle(job, sw.config()))?;
            }
        }
    }
}

#[test]
fn results_do_not_depend_on_order_lanes_or_slices() {
    let jobs = [
        "RL",
        "RLR",
        "RRLL",
        "RRLLLRLLLRRR",
        "RLLR",
        "RLRRRLLR",
        "LLRR",
    ]
    .into_iter()
    .map(|r| Job {
        rule: r.parse().unwrap(),
        bg_seed: None,
        max_steps: 60_000,
    })
    .collect::<Vec<_>>();
    let mut reversed = jobs.clone();
    reversed.reverse();
    let mut rigs = rigs().lock().unwrap();

    for sw in rigs.iter_mut() {
        let a = sw.run(&jobs, |_| {}).unwrap();
        let mut b = sw.run(&reversed, |_| {}).unwrap();
        b.reverse();

        for (i, (a, b)) in a.iter().zip(&b).enumerate() {
            same(a, b).unwrap();
            same(a, &oracle(&jobs[i], sw.config())).unwrap();
        }
    }
}

#[test]
fn highways_match_fast() {
    let mut sw = GpuSweeper::new(GpuConfig {
        lanes: 8,
        grid: 512,
        slice_steps: 50_003,
        pool_tiles: 1024,
        ..GpuConfig::default()
    })
    .unwrap();
    let jobs = [
        "RL",
        "RRL",
        "RLRL",
        "RRLL",
        "RLLR",
        "RRLLLRLLLRRR",
        "LLRR",
        "RLR",
    ]
    .into_iter()
    .map(|r| Job {
        rule: r.parse().unwrap(),
        bg_seed: None,
        max_steps: 400_000,
    })
    .collect::<Vec<_>>();
    let got = sw.run(&jobs, |_| {}).unwrap();

    for (job, result) in jobs.iter().zip(&got) {
        same(result, &oracle(job, sw.config())).unwrap();
    }

    assert_eq!(got[0].highway.map(|hw| hw.period), Some(104));
}

#[test]
fn pool_pressure_requeues_and_sweeper_can_be_reused_after_an_error() {
    let mut sw = GpuSweeper::new(GpuConfig {
        lanes: 4,
        grid: 64,
        slice_steps: 1501,
        pool_tiles: 1,
        history: 700,
        max_period: 300,
        ..GpuConfig::default()
    })
    .unwrap();
    let jobs = [
        "RLR",
        "RRLLLRLLLRRR",
        "RRLL",
        "RLLR",
        "RLRRRLLR",
        "RRRLLR",
        "RLLLRRRLLR",
    ]
    .into_iter()
    .map(|r| Job {
        rule: r.parse().unwrap(),
        bg_seed: None,
        max_steps: 60_000,
    })
    .collect::<Vec<_>>();
    let got = sw.run(&jobs, |_| {}).unwrap();
    assert!(sw.stats.oom_requeues > 0);

    for (job, result) in jobs.iter().zip(&got) {
        same(result, &oracle(job, sw.config())).unwrap();
    }

    let mut tiny = GpuSweeper::new(GpuConfig {
        lanes: 2,
        grid: 512,
        slice_steps: 10_000,
        pool_tiles: 2,
        ..GpuConfig::default()
    })
    .unwrap();
    assert!(
        tiny.run(
            &[Job {
                rule: "RL".parse().unwrap(),
                bg_seed: None,
                max_steps: 200_000
            }],
            |_| {}
        )
        .is_err()
    );
    let job = Job {
        rule: "RR".parse().unwrap(),
        bg_seed: None,
        max_steps: 100,
    };
    same(
        &tiny.run(std::slice::from_ref(&job), |_| {}).unwrap()[0],
        &oracle(&job, tiny.config()),
    )
    .unwrap();
}

#[test]
fn zero_budgets_partial_words_and_all_supported_colours() {
    let mut sw = GpuSweeper::new(GpuConfig {
        lanes: 3,
        grid: 65,
        slice_steps: 17,
        pool_tiles: 64,
        history: 19,
        max_period: 7,
        ..GpuConfig::default()
    })
    .unwrap();
    let mut jobs = [0, 1, 15, 16, 17, 31, 32, 33, 257]
        .into_iter()
        .map(|max_steps| Job {
            rule: "RLR".parse().unwrap(),
            bg_seed: Some(u64::MAX),
            max_steps,
        })
        .collect::<Vec<_>>();
    jobs.push(Job {
        rule: Rule(vec![turmite::Turn::R; 128]),
        bg_seed: Some(1 << 63),
        max_steps: 1000,
    });
    let mut progress = Vec::new();
    let got = sw.run(&jobs, |done| progress.push(done)).unwrap();

    for (job, result) in jobs.iter().zip(&got) {
        same(result, &oracle(job, sw.config())).unwrap();
    }

    assert_eq!(progress.last(), Some(&jobs.len()));
    assert!(sw.run(&[], |_| {}).unwrap().is_empty());
    assert!(
        sw.run(
            &[Job {
                rule: Rule(vec![]),
                bg_seed: None,
                max_steps: 1
            }],
            |_| {}
        )
        .is_err()
    );
    assert!(
        sw.run(
            &[Job {
                rule: Rule(vec![turmite::Turn::R; 129]),
                bg_seed: None,
                max_steps: 1
            }],
            |_| {}
        )
        .is_err()
    );
}

#[test]
fn escape_on_the_last_budgeted_step_matches_fast() {
    let mut sw = GpuSweeper::new(GpuConfig {
        lanes: 3,
        grid: 64,
        slice_steps: 31,
        pool_tiles: 32,
        history: 1000,
        max_period: 300,
        ..GpuConfig::default()
    })
    .unwrap();
    let rule = "RL".parse::<Rule>().unwrap();
    let escaped = oracle(
        &Job {
            rule: rule.clone(),
            bg_seed: None,
            max_steps: 100_000,
        },
        sw.config(),
    );
    assert_eq!(escaped.stop, Stop::Escaped);
    let jobs = [
        escaped.steps - 1,
        escaped.steps,
        escaped.steps + 1,
        u64::MAX,
    ]
    .into_iter()
    .map(|max_steps| Job {
        rule: rule.clone(),
        bg_seed: None,
        max_steps,
    })
    .collect::<Vec<_>>();
    let got = sw.run(&jobs, |_| {}).unwrap();

    for (job, result) in jobs.iter().zip(&got) {
        same(result, &oracle(job, sw.config())).unwrap();
    }

    assert_eq!(got[1].stop, Stop::Escaped);
}

#[test]
fn seeded_rules_exercise_every_turn_mask_word() {
    let mut sw = GpuSweeper::new(GpuConfig {
        lanes: 5,
        grid: 65,
        slice_steps: 127,
        pool_tiles: 64,
        history: 1000,
        max_period: 300,
        ..GpuConfig::default()
    })
    .unwrap();
    let jobs = [1, 2, 31, 32, 33, 63, 64, 65, 99, 100, 127, 128]
        .into_iter()
        .map(|n| Job {
            rule: Rule(
                (0..n)
                    .map(|i| {
                        if i % 3 == 0 {
                            turmite::Turn::L
                        } else {
                            turmite::Turn::R
                        }
                    })
                    .collect(),
            ),
            bg_seed: Some(u64::MAX - n as u64),
            max_steps: 10_000,
        })
        .collect::<Vec<_>>();
    let got = sw.run(&jobs, |_| {}).unwrap();

    for (job, result) in jobs.iter().zip(&got) {
        same(result, &oracle(job, sw.config())).unwrap();
    }
}
