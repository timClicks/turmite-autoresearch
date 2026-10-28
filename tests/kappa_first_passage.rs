//! SUPERSEDED (2026-10-20): prototype oracle only. Its geometry flag cannot fire, it drops skipped milestones and runs a full BFS per step;
//! the instrument is src/first_passage.rs, tested in tests/first_passage.rs. See the correction in the experiment NOTEBOOK.
//! Tests and prototype oracle verification for `experiments/archive/2026-10-kappa-first-passage`.
//! Implements:
//! 1. From-scratch full BFS depth oracle from boundary cells.
//! 2. Step-by-step evolving depth tracking at ant location.
//! 3. Milestone crossing accountant (milestones 0, 1, 2, 4, 8, 16, 32, 64).
//! 4. Property test fixtures checking B + I = S, adjacent milestone invariants,
//!    geometry-induced vs physical crossings, and time-budget conservation.

use proptest::prelude::*;
use std::collections::{HashMap, HashSet, VecDeque};
use turmite::{DIRS, reference, Rule};
use turmite::walkers::{PatchedAnt, Walker};

pub const MILESTONES: [u32; 8] = [0, 1, 2, 4, 8, 16, 32, 64];

pub type P = (i32, i32);

/// Full from-scratch BFS depth oracle over visited cells.
/// A cell is on the boundary (depth 0) iff it is visited and has >= 1 unvisited 4-neighbour.
/// Other visited cells have depth = shortest 4-neighbour distance through visited cells to boundary.
pub fn full_depth(visited: &HashSet<P>) -> HashMap<P, u32> {
    let mut depth = HashMap::new();
    let mut q = VecDeque::new();
    for &p in visited {
        if DIRS.iter().any(|&(dx, dy)| !visited.contains(&(p.0 + dx, p.1 + dy))) {
            depth.insert(p, 0);
            q.push_back(p);
        }
    }
    while let Some(p) = q.pop_front() {
        let d = depth[&p];
        for &(dx, dy) in &DIRS {
            let n = (p.0 + dx, p.1 + dy);
            if visited.contains(&n) && !depth.contains_key(&n) {
                depth.insert(n, d + 1);
                q.push_back(n);
            }
        }
    }
    depth
}

/// Check if depth matches a milestone.
pub fn milestone_idx(depth: u32) -> Option<usize> {
    MILESTONES.iter().position(|&m| m == depth)
}

/// Are two milestones adjacent in the milestone hierarchy?
pub fn are_milestones_adjacent(m1: usize, m2: usize) -> bool {
    (m1 as isize - m2 as isize).abs() == 1
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MilestoneSegment {
    pub from_m: u32,
    pub to_m: u32,
    pub t_start: u64,
    pub t_end: u64,
    pub elapsed: u64,
    pub is_geometry_induced: bool,
}

#[derive(Debug, Clone, Default)]
pub struct FirstPassageTallies {
    pub total_steps: u64,
    pub boundary_steps: u64,
    pub interior_steps: u64,
    pub segments: Vec<MilestoneSegment>,
    pub unresolved_elapsed: u64,
}

/// State observed before each departure, after marking current cell visited.
pub struct FirstPassageTracker {
    pub visited: HashSet<P>,
    pub pos: P,
    pub t: u64,
    pub boundary_steps: u64,
    pub interior_steps: u64,
    pub current_depth: u32,
    pub current_milestone: usize,
    pub milestone_dep_t: u64,
    pub segments: Vec<MilestoneSegment>,
}

impl FirstPassageTracker {
    pub fn new(start_pos: P) -> Self {
        let mut visited = HashSet::new();
        visited.insert(start_pos);
        let depth_map = full_depth(&visited);
        let current_depth = depth_map[&start_pos];
        let current_milestone = milestone_idx(current_depth).unwrap_or(0);
        Self {
            visited,
            pos: start_pos,
            t: 0,
            boundary_steps: 0,
            interior_steps: 0,
            current_depth,
            current_milestone,
            milestone_dep_t: 0,
            segments: Vec::new(),
        }
    }

    /// Step from current cell to next_pos.
    pub fn step(&mut self, next_pos: P) {
        // Record departure from self.pos
        if self.current_depth == 0 {
            self.boundary_steps += 1;
        } else {
            self.interior_steps += 1;
        }
        self.t += 1;

        // Depth of next_pos before birth in the current territory
        let prev_depth_of_next = if self.visited.contains(&next_pos) {
            let map = full_depth(&self.visited);
            Some(map[&next_pos])
        } else {
            None
        };

        // Mark next_pos visited
        self.visited.insert(next_pos);
        self.pos = next_pos;

        // Compute new depth map
        let new_depth_map = full_depth(&self.visited);
        let new_depth = new_depth_map[&self.pos];

        // Did geometry reclassification change next_pos's depth?
        let is_geometry_induced = match prev_depth_of_next {
            Some(d_prev) => d_prev != new_depth,
            None => false, // fresh birth
        };

        self.current_depth = new_depth;

        // Check if next_pos reached a different adjacent milestone
        if let Some(m_new) = milestone_idx(new_depth) {
            if are_milestones_adjacent(self.current_milestone, m_new) {
                let elapsed = self.t - self.milestone_dep_t;
                self.segments.push(MilestoneSegment {
                    from_m: MILESTONES[self.current_milestone],
                    to_m: MILESTONES[m_new],
                    t_start: self.milestone_dep_t,
                    t_end: self.t,
                    elapsed,
                    is_geometry_induced,
                });
                self.current_milestone = m_new;
                self.milestone_dep_t = self.t;
            }
        }
    }

    pub fn finish(self) -> FirstPassageTallies {
        let unresolved_elapsed = self.t - self.milestone_dep_t;
        FirstPassageTallies {
            total_steps: self.t,
            boundary_steps: self.boundary_steps,
            interior_steps: self.interior_steps,
            segments: self.segments,
            unresolved_elapsed,
        }
    }
}

// ------------------- Tests -------------------

#[test]
fn test_empty_or_one_cell_territory() {
    let tracker = FirstPassageTracker::new((0, 0));
    assert_eq!(tracker.visited.len(), 1);
    assert_eq!(tracker.current_depth, 0);
    let tallies = tracker.finish();
    assert_eq!(tallies.total_steps, 0);
    assert_eq!(tallies.boundary_steps, 0);
    assert_eq!(tallies.interior_steps, 0);
}

#[test]
fn test_straight_line_no_interior() {
    let mut tracker = FirstPassageTracker::new((0, 0));
    for i in 1..=50 {
        tracker.step((i, 0));
    }
    let tallies = tracker.finish();
    assert_eq!(tallies.total_steps, 50);
    assert_eq!(tallies.boundary_steps, 50);
    assert_eq!(tallies.interior_steps, 0);
    assert_eq!(tallies.boundary_steps + tallies.interior_steps, tallies.total_steps);
    // Straight line has all cells on boundary (depth 0), so no segments to depth 1
    assert_eq!(tallies.segments.len(), 0);
}

#[test]
fn test_square_loop_creates_depth_1_interior() {
    // 3x3 filled square: center cell (1, 1) has depth 1!
    // Outline: (0,0)->(1,0)->(2,0)->(2,1)->(2,2)->(1,2)->(0,2)->(0,1)->(1,1)
    let path = [
        (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2), (0, 1), (1, 1)
    ];
    let mut tracker = FirstPassageTracker::new((0, 0));
    for &p in &path {
        tracker.step(p);
    }
    assert_eq!(tracker.visited.len(), 9);
    assert_eq!(tracker.current_depth, 1);

    // Now step back from (1, 1) to (1, 2) (boundary):
    tracker.step((1, 2));
    assert_eq!(tracker.current_depth, 0);
    let tallies = tracker.finish();
    assert_eq!(tallies.total_steps, path.len() as u64 + 1);
    assert_eq!(tallies.boundary_steps + tallies.interior_steps, tallies.total_steps);
    // Must have crossed milestone 0 -> 1 and then 1 -> 0
    let m_crossings: Vec<(u32, u32)> = tallies.segments.iter().map(|s| (s.from_m, s.to_m)).collect();
    assert_eq!(m_crossings, vec![(0, 1), (1, 0)]);
}

proptest! {
    #![proptest_config(ProptestConfig::with_cases(25))]
    #[test]
    fn property_ant_budget_conservation_and_valid_milestones(
        bits in prop::collection::vec(any::<bool>(), 2..10),
        seed in any::<u64>(),
        steps in 50u64..250u64,
    ) {
        let rule_str: String = bits.iter().map(|&b| if b { 'R' } else { 'L' }).collect();
        let rule: Rule = rule_str.parse().unwrap();
        let mut ant = reference::Ant::new(rule.clone());
        let init = PatchedAnt::new(&rule, seed, 2);
        for y in -2..=2 {
            for x in -2..=2 {
                let c = init.initial_cell(x, y);
                if c != 0 {
                    ant.cells.insert((x as i32, y as i32), c);
                }
            }
        }

        let mut tracker = FirstPassageTracker::new(ant.pos);
        for _ in 0..steps {
            ant.step();
            tracker.step(ant.pos);
        }

        let tallies = tracker.finish();

        // 1. Conservation: Boundary + Interior = Total steps
        prop_assert_eq!(tallies.boundary_steps + tallies.interior_steps, tallies.total_steps);
        prop_assert_eq!(tallies.total_steps, steps);

        // 2. All milestone segments must be between adjacent milestones
        for seg in &tallies.segments {
            let from_idx = milestone_idx(seg.from_m).unwrap();
            let to_idx = milestone_idx(seg.to_m).unwrap();
            prop_assert!(are_milestones_adjacent(from_idx, to_idx));
            prop_assert_eq!(seg.elapsed, seg.t_end - seg.t_start);
            prop_assert!(seg.elapsed > 0);
        }

        // 3. Segment chain continuity: each segment ends when next starts
        for i in 1..tallies.segments.len() {
            prop_assert_eq!(tallies.segments[i-1].t_end, tallies.segments[i].t_start);
            prop_assert_eq!(tallies.segments[i-1].to_m, tallies.segments[i].from_m);
        }

        // 4. Time sum: completed segment times + unresolved time = total time
        let completed_time: u64 = tallies.segments.iter().map(|s| s.elapsed).sum();
        prop_assert_eq!(completed_time + tallies.unresolved_elapsed, tallies.total_steps);
    }
}
