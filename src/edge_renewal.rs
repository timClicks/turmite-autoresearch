//! Ordered boundary events for experiments/active/2026-10-c-law-renewal.
//!
//! A callback keeps full paths optional. Features are sampled before the source
//! read; births belong to that read. No outcome enters a source state.

use crate::edge_trace::{CHC, Layout};
use crate::walkers::Walker;
use crate::{DIRS, Rule};

/// Heading-frame positions, clockwise from forward. Patch digit: fresh=0,
/// visited with initial-turn sign=1, visited with opposite sign=2.
pub const PATCH: [(i32, i32); 8] = [
    (0, 1),
    (1, 1),
    (1, 0),
    (1, -1),
    (0, -1),
    (-1, -1),
    (-1, 0),
    (-1, 1),
];

#[derive(Clone, Copy, Debug, Default, PartialEq, Eq, PartialOrd, Ord)]
pub struct State {
    pub colour: u8,
    /// Bit j: rule[colour+j] has the same turn as rule[0].
    pub next8: u8,
    /// Bits: forward, right, back, left are visited (after reflection if L-first).
    pub visited4: u8,
    /// Two bits per PATCH position; controls without a rule use 1 for visited.
    pub patch: u16,
    /// 0 first read, 1 lag 4, 2 other lag <=16, 3 lag >16.
    pub lag: u8,
    /// Consecutive births immediately preceding this step, capped at 4.
    pub chain_before: u8,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub struct Event {
    pub t: u64,
    /// All-boundary-read clock, including warmup; zero means first source read.
    pub boundary_lag: u64,
    pub state: State,
    pub born: bool,
}

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct Summary {
    pub steps: u64,
    pub start_step: u64,
    pub window_steps: u64,
    pub window_complete: bool,
    pub boundary_reads: u64,
    pub births: u64,
    pub lag: [u64; 4],
    /// Chains clipped to the measurement window, as in edge_trace.
    pub chains: Vec<u64>,
    pub left_chain_censored: bool,
    pub right_chain_censored: bool,
    pub area_t0: u64,
    pub area: u64,
    pub perimeter: u64,
    pub escaped: bool,
}

pub fn lag_class(now: u64, previous: u64) -> u8 {
    match previous {
        0 => 0,
        _ if now - previous == 4 => 1,
        _ if now - previous <= 16 => 2,
        _ => 3,
    }
}

/// `rule` labels features only; it must describe an ant walker when present.
/// `None` permits rotor/random-walk accounting controls without fictitious turns.
pub fn trace<W: Walker>(
    walker: W,
    rule: Option<&Rule>,
    lay: Layout,
    prefill: &dyn Fn(usize, usize) -> Option<u8>,
    start: (usize, usize, u8),
    log2: u32,
    emit: impl FnMut(Event),
) -> Summary {
    trace_clock(
        walker,
        rule,
        lay,
        prefill,
        start,
        Clock::Octave(log2),
        |_, _, _| {},
        emit,
    )
}

#[derive(Clone, Copy, Debug)]
pub enum Clock {
    Octave(u32),
    Boundary {
        warmup: u64,
        reads: u64,
        max_steps: u64,
    },
}

/// The pre-read hook may change the source phase but not geometry or heading.
/// A reset performed in Walker.step would mislabel the recorded source state.
pub fn trace_clock<W: Walker>(
    mut walker: W,
    rule: Option<&Rule>,
    lay: Layout,
    prefill: &dyn Fn(usize, usize) -> Option<u8>,
    start: (usize, usize, u8),
    clock: Clock,
    mut prepare: impl FnMut(&mut W, &mut u8, u8),
    mut emit: impl FnMut(Event),
) -> Summary {
    let (total, fixed_start) = match clock {
        Clock::Octave(log2) => {
            assert!((1..=30).contains(&log2));
            (1u64 << log2, Some(1u64 << (log2 - 1)))
        }
        Clock::Boundary {
            reads, max_steps, ..
        } => {
            assert!(reads > 0 && max_steps > 0 && max_steps <= 1 << 30);
            (max_steps, None)
        }
    };
    let Layout { w, h, wrap } = lay;
    assert!(w >= 8 && h >= 8);
    let norm = |x: i64, y: i64| -> usize {
        if wrap {
            y.rem_euclid(h as i64) as usize * w + x.rem_euclid(w as i64) as usize
        } else {
            assert!(x >= 0 && x < w as i64 && y >= 0 && y < h as i64);
            y as usize * w + x as usize
        }
    };
    let nbr = |i: usize, d: usize| {
        norm(
            (i % w) as i64 + DIRS[d].0 as i64,
            (i / w) as i64 + DIRS[d].1 as i64,
        )
    };
    let mut col = vec![0u8; w * h];
    let mut vis = vec![false; w * h];
    let mut unv = vec![0u8; w * h];
    let mut last = vec![0u32; w * h];
    let mut last_boundary = vec![0u32; w * h];
    let mut out = Summary {
        chains: vec![0; CHC],
        ..Summary::default()
    };
    for y in 0..h {
        for x in 0..w {
            let i = y * w + x;
            let init = if W::RANDOM_INIT {
                walker.initial_cell(x as i64 - (w / 2) as i64, y as i64 - (h / 2) as i64)
            } else {
                0
            };
            let pre = prefill(x, y);
            vis[i] = pre.is_some();
            col[i] = pre.filter(|&c| c != u8::MAX).unwrap_or(init);
            if vis[i] {
                out.area += 1;
                // A non-wrapped prefill must not touch the outermost cells.
                assert!(wrap || (x > 0 && y > 0 && x + 1 < w && y + 1 < h));
            }
        }
    }
    for i in 0..w * h {
        if vis[i] {
            unv[i] = (0..4).filter(|&d| !vis[nbr(i, d)]).count() as u8;
            out.perimeter += u64::from(unv[i] > 0);
        }
    }
    let (mut x, mut y, mut hd) = start;
    assert!(vis[y * w + x]);
    assert!(hd < 4 && (wrap || (x > 2 && y > 2 && x < w - 2 && y < h - 2)));
    let reflected = rule.is_some_and(|r| r.0[0].delta() == 3);
    let mut run = 0usize;
    let mut window_run = 0usize;
    let mut seen_boundary = 0u64;
    let mut started = matches!(clock, Clock::Boundary { warmup: 0, .. });
    if started {
        out.area_t0 = out.area;
    }
    for t in 1..=total {
        let i = y * w + x;
        let on_b = unv[i] > 0;
        let boundary_lag = if on_b {
            let previous = last_boundary[i] as u64;
            let now = seen_boundary + 1;
            last_boundary[i] = now as u32;
            if previous == 0 { 0 } else { now - previous }
        } else {
            0
        };
        let in_window = started;
        prepare(&mut walker, &mut col[i], hd);
        let mut state = State::default();
        if in_window && on_b {
            state.colour = col[i];
            state.lag = lag_class(t, last[i] as u64);
            state.chain_before = run.min(4) as u8;
            if let Some(r) = rule {
                for j in 0..8 {
                    state.next8 |= u8::from(r.0[(col[i] as usize + j) % r.len()] == r.0[0]) << j;
                }
            }
            let f = DIRS[hd as usize];
            let right = DIRS[((hd + 1) & 3) as usize];
            let flip = if reflected { -1 } else { 1 };
            for (k, &(a, b)) in PATCH.iter().enumerate() {
                let p = norm(
                    x as i64 + (a * flip * right.0 + b * f.0) as i64,
                    y as i64 + (a * flip * right.1 + b * f.1) as i64,
                );
                if vis[p] {
                    let digit = if let Some(r) = rule {
                        if r.0[col[p] as usize] == r.0[0] { 1 } else { 2 }
                    } else {
                        1
                    };
                    state.patch |= digit << (2 * k);
                    if k % 2 == 0 {
                        state.visited4 |= 1 << (k / 2);
                    }
                }
            }
        }
        last[i] = t as u32;
        walker.step(&mut col[i], &mut hd);
        let j = nbr(i, hd as usize);
        x = j % w;
        y = j / w;
        let born = !vis[j];
        if born {
            vis[j] = true;
            out.area += 1;
            for d in 0..4 {
                let k = nbr(j, d);
                if vis[k] {
                    unv[k] -= 1;
                    out.perimeter -= u64::from(unv[k] == 0);
                } else {
                    unv[j] += 1;
                }
            }
            out.perimeter += u64::from(unv[j] > 0);
        }
        if on_b {
            seen_boundary += 1;
        }
        let opens = fixed_start == Some(t)
            || matches!(clock, Clock::Boundary { warmup, .. } if !started && seen_boundary == warmup);
        if opens {
            out.area_t0 = out.area;
            out.start_step = t;
            started = true;
        }
        if in_window {
            if t == out.start_step + 1 {
                out.left_chain_censored = run > 0 && born;
            }
            if on_b {
                out.boundary_reads += 1;
                out.lag[state.lag as usize] += 1;
                emit(Event {
                    t,
                    boundary_lag,
                    state,
                    born,
                });
            }
            assert!(!born || on_b);
            out.births += u64::from(born);
            if born {
                window_run += 1;
            } else if window_run > 0 {
                out.chains[window_run.min(CHC - 1)] += 1;
                window_run = 0;
            }
        }
        run = if born { run + 1 } else { 0 };
        out.steps = t;
        if in_window {
            out.window_steps += 1;
        }
        if !wrap && (x <= 2 || y <= 2 || x >= w - 2 || y >= h - 2) {
            out.escaped = true;
            break;
        }
        if matches!(clock, Clock::Boundary { reads, .. } if out.boundary_reads == reads) {
            out.window_complete = true;
            break;
        }
    }
    if fixed_start.is_some() && !out.escaped && out.steps == total {
        out.window_complete = true;
    }
    if window_run > 0 {
        out.chains[window_run.min(CHC - 1)] += 1;
        out.right_chain_censored = true;
    }
    out
}
