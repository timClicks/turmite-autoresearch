//! Registered pilot: experiments/2026-10-23-hidden-phase-return/README.md.
//! Usage: hidden_phase_return OUT THREADS [BUDGET]. No input files are required.

use rayon::prelude::*;
use std::collections::{BTreeMap, VecDeque};
use std::fmt::Write as _;
use std::path::Path;
use turmite::walkers::{PatchedAnt, Walker, splitmix_next};
use turmite::{DIRS, Rule};

const BOARD: usize = 2048;
const CAP: usize = 1 << 18;
const BANDS: [usize; 2] = [4096, 16384];
const RULES: [&str; 3] = ["RLLLLRLLRLRL", "RLLLRRLRLL", "RLLRRLLLLLLL"];

#[derive(Clone)]
struct Field {
    width: usize,
    colours: Vec<u8>,
    inner: Vec<bool>,
    depth: Vec<usize>,
    pos: usize,
    heading: u8,
}

impl Field {
    fn offsets(&self) -> [isize; 4] {
        DIRS.map(|(x, y)| x as isize + y as isize * self.width as isize)
    }
}

#[derive(Debug, PartialEq)]
struct Episode {
    duration: usize,
    pos: usize,
    heading: u8,
    censored: bool,
    path: Vec<(usize, u8)>,
}

fn replay(field: &Field, rule: &Rule, cap: usize) -> Episode {
    let mut colours = field.colours.clone();
    let mut pos = field.pos;
    let mut heading = field.heading;
    let offsets = field.offsets();
    let mut path = Vec::new();

    for duration in 1..=cap {
        let colour = colours[pos] as usize;
        heading = (heading + rule.0[colour].delta()) % 4;
        colours[pos] = ((colour + 1) % rule.len()) as u8;
        pos = pos.wrapping_add_signed(offsets[heading as usize]);
        path.push((pos, heading));

        if !field.inner[pos] {
            return Episode {
                duration,
                pos,
                heading,
                censored: false,
                path,
            };
        }
    }

    Episode {
        duration: cap,
        pos,
        heading,
        censored: true,
        path,
    }
}

fn prefix(rule: &Rule, colour: u8, k: usize) -> Vec<u8> {
    (0..k)
        .map(|j| rule.0[(colour as usize + j) % rule.len()].delta())
        .collect()
}

fn shuffle(field: &Field, rule: &Rule, k: usize, mut seed: u64) -> Field {
    let mut groups: BTreeMap<(usize, Vec<u8>), Vec<usize>> = BTreeMap::new();

    for (i, &inner) in field.inner.iter().enumerate() {
        if inner {
            groups
                .entry((field.depth[i] / 8, prefix(rule, field.colours[i], k)))
                .or_default()
                .push(i);
        }
    }

    let mut result = field.clone();

    for indices in groups.values() {
        for j in (1..indices.len()).rev() {
            // Rejection sampling avoids bias for group sizes that do not divide 2^64.
            let size = (j + 1) as u64;
            let threshold = size.wrapping_neg() % size;
            let ticket = loop {
                let value = splitmix_next(&mut seed);
                if value >= threshold {
                    break (value % size) as usize;
                }
            };
            result.colours.swap(indices[j], indices[ticket]);
        }
    }

    result
}

fn keyed_seed(
    rule: &str,
    seed: u64,
    band: usize,
    departure: usize,
    k: usize,
    replica: usize,
) -> u64 {
    let mut value = rule.bytes().fold(0xcbf2_9ce4_8422_2325u64, |v, b| {
        (v ^ b as u64).wrapping_mul(0x100_0000_01b3)
    });

    for part in [
        seed,
        band as u64,
        departure as u64,
        k as u64,
        replica as u64,
    ] {
        value ^= part;
        value = splitmix_next(&mut value);
    }

    value
}

/// Compare steps, not arrival colours: equivalent phases can have different labels.
fn first_difference(field: &Field, baseline: &Episode, arm: &Episode, k: usize) -> (usize, usize) {
    let mut visits = vec![0usize; field.colours.len()];
    let mut pos = field.pos;

    for (step, (&expected, &actual)) in baseline.path.iter().zip(&arm.path).enumerate() {
        visits[pos] += 1;

        if expected != actual {
            assert!(visits[pos] > k, "turn-prefix guarantee failed");
            return (step + 1, visits[pos]);
        }

        pos = expected.0;
    }

    assert_eq!(
        baseline.path.len(),
        arm.path.len(),
        "paths ended differently without a first difference"
    );
    (0, 0)
}

struct Record {
    band: usize,
    start: u64,
    pos: usize,
    heading: u8,
    undo: Vec<(usize, u8)>,
}

#[derive(Default)]
struct Counts {
    departures: u64,
    short: u64,
    eligible_long: u64,
    overflow: u64,
    sampled: u64,
    gap_or_quota: u64,
    unfinished: u64,
    completed_time: u64,
    overflow_time: u64,
    unfinished_time: u64,
    last_sample: u64,
}

fn crop(
    colours: &[u8],
    visited: &[bool],
    bounds: (usize, usize, usize, usize),
    rec: &Record,
) -> Field {
    let (xmin, xmax, ymin, ymax) = bounds;
    let width = xmax - xmin + 3;
    let height = ymax - ymin + 3;
    let local = |i: usize| (i / BOARD - ymin + 1) * width + i % BOARD - xmin + 1;
    let mut field = Field {
        width,
        colours: vec![0; width * height],
        inner: vec![false; width * height],
        depth: vec![usize::MAX; width * height],
        pos: local(rec.pos),
        heading: rec.heading,
    };
    let mut mask = vec![false; width * height];

    for y in ymin..=ymax {
        for x in xmin..=xmax {
            let global = y * BOARD + x;
            let i = local(global);
            mask[i] = visited[global];
            field.colours[i] = colours[global];
        }
    }

    for &(i, old) in rec.undo.iter().rev() {
        field.colours[local(i)] = old;
    }

    let offsets = field.offsets();
    let mut queue = VecDeque::new();

    for i in 0..mask.len() {
        if mask[i] {
            field.inner[i] = offsets.iter().all(|&d| mask[i.wrapping_add_signed(d)]);

            if !field.inner[i] {
                field.depth[i] = 0;
                queue.push_back(i);
            }
        }
    }

    while let Some(i) = queue.pop_front() {
        for d in offsets {
            let j = i.wrapping_add_signed(d);

            if mask[j] && field.depth[j] == usize::MAX {
                field.depth[j] = field.depth[i] + 1;
                queue.push_back(j);
            }
        }
    }

    field
}

fn interventions(
    field: &Field,
    rule: &Rule,
    seed: u64,
    rec: &Record,
    dep: usize,
    baseline: &Episode,
    rows: &mut String,
) {
    let mut read = vec![false; field.colours.len()];
    read[field.pos] = true;

    for &(pos, _) in &baseline.path {
        if field.inner[pos] {
            read[pos] = true;
        }
    }

    let read_count = read.iter().filter(|&&v| v).count();
    let inner_count = field.inner.iter().filter(|&&v| v).count();

    for k in [0, 1, 2, 4, rule.len()] {
        for replica in 0..4 {
            let arm_field = shuffle(
                field,
                rule,
                k,
                keyed_seed(&rule.to_string(), seed, rec.band, dep, k, replica),
            );
            let arm = replay(&arm_field, rule, CAP);
            let (split_step, split_visit) = first_difference(field, baseline, &arm, k);
            let changed = (0..read.len())
                .filter(|&i| field.inner[i] && field.colours[i] != arm_field.colours[i])
                .count();
            let read_changed = (0..read.len())
                .filter(|&i| read[i] && field.colours[i] != arm_field.colours[i])
                .count();
            let exact_return = !arm.censored
                && arm.duration == baseline.duration
                && arm.pos == baseline.pos
                && arm.heading == baseline.heading;

            if k == rule.len() {
                assert_eq!(baseline, &arm, "equivalent-phase sham changed the path");
            }

            writeln!(rows, "{rule},{seed},{},{dep},{},{},{k},{replica},{},{},{},{},{},{split_step},{split_visit},{changed},{inner_count},{read_changed},{read_count}",
                rec.band, rec.start, baseline.duration, arm.duration, arm.censored as u8,
                exact_return as u8, (split_step == 0) as u8, arm.pos).unwrap();
        }
    }
}

fn run(rule_text: &str, seed: u64, budget: u64, out: &Path) -> Result<(), String> {
    let rule: Rule = rule_text.parse().map_err(|e| format!("{e}"))?;
    let mut walker = PatchedAnt::new(&rule, seed, 2);
    let mut colours = vec![0u8; BOARD * BOARD];
    let mut visited = vec![false; BOARD * BOARD];
    let offsets = DIRS.map(|(x, y)| x as isize + y as isize * BOARD as isize);
    let mut pos = (BOARD / 2) * (BOARD + 1);
    let mut heading = 0;
    let mut area = 0;
    let mut bounds = (BOARD, 0, BOARD, 0);
    let mut previous_boundary = true;
    let mut record: Option<Record> = None;
    let mut counts: [Counts; 2] = std::array::from_fn(|_| Counts::default());
    let mut rows = String::from(
        "rule,seed,band,departure,t0,base_t,k,replica,arm_t,censored,return_equal,path_equal,arrival,split_step,split_visit,changed,interior,read_changed,read_cells\n",
    );
    let mut time = 0;
    let status;

    loop {
        let x = pos % BOARD;
        let y = pos / BOARD;

        if x == 0 || y == 0 || x + 1 == BOARD || y + 1 == BOARD {
            status = "board_escape";
            break;
        }

        if !visited[pos] {
            visited[pos] = true;
            colours[pos] =
                walker.initial_cell(x as i64 - BOARD as i64 / 2, y as i64 - BOARD as i64 / 2);
            area += 1;
            bounds = (
                bounds.0.min(x),
                bounds.1.max(x),
                bounds.2.min(y),
                bounds.3.max(y),
            );
        }

        let boundary = offsets
            .iter()
            .any(|&d| !visited[pos.wrapping_add_signed(d)]);

        if boundary {
            if let Some(rec) = record.take() {
                let duration = time - rec.start;
                let c = &mut counts[rec.band];
                c.completed_time += duration;

                if duration > CAP as u64 {
                    c.overflow += 1;
                    c.overflow_time += duration;
                } else if duration < 128 {
                    c.short += 1;
                } else {
                    c.eligible_long += 1;

                    if c.sampled < 16 && (c.sampled == 0 || rec.start - c.last_sample >= 64) {
                        let field = crop(&colours, &visited, bounds, &rec);
                        let baseline = replay(&field, &rule, CAP);
                        let local = |i: usize| {
                            (i / BOARD - bounds.2 + 1) * field.width + i % BOARD - bounds.0 + 1
                        };
                        assert_eq!(
                            (
                                baseline.duration as u64,
                                baseline.pos,
                                baseline.heading,
                                baseline.censored
                            ),
                            (duration, local(pos), heading, false),
                            "live replay mismatch"
                        );
                        interventions(
                            &field,
                            &rule,
                            seed,
                            &rec,
                            c.sampled as usize,
                            &baseline,
                            &mut rows,
                        );
                        c.sampled += 1;
                        c.last_sample = rec.start;
                    } else {
                        c.gap_or_quota += 1;
                    }
                }
            }
        }

        // Resolve an arrival exactly at the horizon, but do not open a zero-step episode.
        if time >= budget {
            status = "budget";
            break;
        }

        if area >= BANDS[1] * 17 / 16 && record.is_none() {
            status = "complete";
            break;
        }

        if !boundary && previous_boundary && record.is_none() {
            if let Some(band) = BANDS
                .iter()
                .position(|&lower| area >= lower && area < lower * 17 / 16)
            {
                counts[band].departures += 1;
                record = Some(Record {
                    band,
                    start: time,
                    pos,
                    heading,
                    undo: Vec::new(),
                });
            }
        }

        previous_boundary = boundary;

        if let Some(rec) = record.as_mut() {
            if rec.undo.len() < CAP {
                rec.undo.push((pos, colours[pos]));
            }
        }

        walker.step(&mut colours[pos], &mut heading);
        pos = pos.wrapping_add_signed(offsets[heading as usize]);
        time += 1;
    }

    if let Some(rec) = record {
        counts[rec.band].unfinished += 1;
        counts[rec.band].unfinished_time += time - rec.start;
    }

    let mut audit = String::from(
        "rule,seed,band,status,steps,area,departures,short,eligible_long,overflow,sampled,gap_or_quota,unfinished,completed_time,overflow_time,unfinished_time\n",
    );

    for (band, c) in counts.iter().enumerate() {
        assert_eq!(
            c.departures,
            c.short + c.eligible_long + c.overflow + c.unfinished
        );
        assert_eq!(c.eligible_long, c.sampled + c.gap_or_quota);
        writeln!(
            audit,
            "{rule},{seed},{band},{status},{time},{area},{},{},{},{},{},{},{},{},{},{}",
            c.departures,
            c.short,
            c.eligible_long,
            c.overflow,
            c.sampled,
            c.gap_or_quota,
            c.unfinished,
            c.completed_time,
            c.overflow_time,
            c.unfinished_time
        )
        .unwrap();
    }

    let stem = format!("{rule}_{seed}");
    std::fs::write(out.join(format!("{stem}.csv")), rows).map_err(|e| e.to_string())?;
    std::fs::write(out.join(format!("{stem}.audit.csv")), audit).map_err(|e| e.to_string())?;
    eprintln!("{stem}: {status}, {time} steps, {area} cells");
    Ok(())
}

fn main() -> Result<(), String> {
    let args: Vec<_> = std::env::args().collect();
    if !(3..=4).contains(&args.len()) {
        return Err("usage: hidden_phase_return OUT THREADS [BUDGET]".into());
    }
    let threads: usize = args[2].parse().map_err(|_| "invalid thread count")?;
    let budget = args
        .get(3)
        .map(|v| v.parse())
        .transpose()
        .map_err(|_| "invalid budget")?
        .unwrap_or(1 << 27);
    let out = Path::new(&args[1]);
    std::fs::create_dir_all(out).map_err(|e| e.to_string())?;
    let specs: Vec<_> = RULES
        .into_iter()
        .flat_map(|rule| (2026102301..=2026102304).map(move |seed| (rule, seed)))
        .collect();
    let pool = rayon::ThreadPoolBuilder::new()
        .num_threads(threads)
        .build()
        .map_err(|e| e.to_string())?;
    pool.install(|| {
        specs
            .par_iter()
            .try_for_each(|&(rule, seed)| run(rule, seed, budget, out))
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use turmite::reference::Ant;

    fn synthetic(rule: &Rule, seed: u64) -> Field {
        let width = 13;
        let mut state = seed;
        let mut field = Field {
            width,
            colours: vec![0; width * width],
            inner: vec![false; width * width],
            depth: vec![0; width * width],
            pos: 6 * width + 6,
            heading: 0,
        };

        for y in 1..width - 1 {
            for x in 1..width - 1 {
                let i = y * width + x;
                field.colours[i] = (splitmix_next(&mut state) % rule.len() as u64) as u8;
                field.inner[i] = x > 1 && y > 1 && x < width - 2 && y < width - 2;
                field.depth[i] = (x - 1).min(y - 1).min(width - 2 - x).min(width - 2 - y);
            }
        }

        field
    }

    fn oracle(field: &Field, rule: &Rule, cap: usize) -> Episode {
        let mut ant = Ant::new(rule.clone());
        ant.pos = (
            (field.pos % field.width) as i32,
            (field.pos / field.width) as i32,
        );
        ant.heading = field.heading;

        for (i, &colour) in field.colours.iter().enumerate() {
            if colour != 0 {
                ant.cells
                    .insert(((i % field.width) as i32, (i / field.width) as i32), colour);
            }
        }

        let mut path = Vec::new();
        for duration in 1..=cap {
            ant.step();
            let pos = ant.pos.1 as usize * field.width + ant.pos.0 as usize;
            path.push((pos, ant.heading));
            if !field.inner[pos] || duration == cap {
                return Episode {
                    duration,
                    pos,
                    heading: ant.heading,
                    censored: field.inner[pos],
                    path,
                };
            }
        }
        unreachable!()
    }

    #[test]
    fn shuffled_replays_match_sparse_oracle_and_preserve_prefixes() {
        for text in RULES.into_iter().chain(["RL", "RLRL", "RRLL"]) {
            let rule: Rule = text.parse().unwrap();
            for seed in 0..24 {
                let field = synthetic(&rule, seed);
                let baseline = replay(&field, &rule, 2048);
                assert_eq!(baseline, oracle(&field, &rule, 2048));
                for k in [0, 1, 2, 4, rule.len()] {
                    let arm = shuffle(&field, &rule, k, seed + 100);
                    let result = replay(&arm, &rule, 2048);
                    assert_eq!(result, oracle(&arm, &rule, 2048));
                    first_difference(&field, &baseline, &result, k);
                    for i in 0..field.colours.len() {
                        assert_eq!(
                            prefix(&rule, field.colours[i], k),
                            prefix(&rule, arm.colours[i], k)
                        );
                        if !field.inner[i] {
                            assert_eq!(field.colours[i], arm.colours[i]);
                        }
                    }
                    let histogram = |f: &Field| {
                        let mut h = BTreeMap::new();
                        for (i, &inside) in f.inner.iter().enumerate() {
                            if inside {
                                *h.entry((f.depth[i] / 8, f.colours[i])).or_insert(0) += 1;
                            }
                        }
                        h
                    };
                    assert_eq!(histogram(&field), histogram(&arm));
                    if k >= rule.len() {
                        assert_eq!(baseline, result);
                    }
                }
            }
        }
    }

    #[test]
    fn equivalent_nonprimitive_phases_change_colours_but_not_paths() {
        let rule: Rule = "RLRL".parse().unwrap();
        let field = synthetic(&rule, 17);
        let arm = shuffle(&field, &rule, 1, 42);
        assert_ne!(field.colours, arm.colours);
        assert_eq!(replay(&field, &rule, 4096), replay(&arm, &rule, 4096));
    }

    #[test]
    fn one_interior_cell_returns_in_one_step_including_at_cap() {
        let rule: Rule = "RL".parse().unwrap();
        let mut field = synthetic(&rule, 1);
        field.inner.fill(false);
        field.inner[field.pos] = true;
        let episode = replay(&field, &rule, 1);
        assert_eq!(episode.duration, 1);
        assert!(!episode.censored);
    }

    #[test]
    fn first_difference_is_detected_on_a_revisit_not_on_first_read() {
        let rule: Rule = "RRLL".parse().unwrap();
        let mut found = false;
        for seed in 0..100 {
            let field = synthetic(&rule, seed);
            let arm = shuffle(&field, &rule, 1, seed + 100);
            let (step, visit) = first_difference(
                &field,
                &replay(&field, &rule, 2048),
                &replay(&arm, &rule, 2048),
                1,
            );
            if step != 0 {
                assert!(visit >= 2);
                found = true;
            }
        }
        assert!(found, "negative control did not exercise a path difference");
    }
}
