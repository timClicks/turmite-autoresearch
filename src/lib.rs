// Style lints kept off crate-wide, with the reason: the many-argument and
// complex-type signatures are plain parameter lists of tested kernels (a struct
// per call would obscure the oracle comparison), and indexed loops mirror the
// lattice arithmetic they implement.
#![allow(
    clippy::too_many_arguments,
    clippy::type_complexity,
    clippy::needless_range_loop
)]
//! Generalised Langton's ants ("turmites" with one internal state).
//!
//! A rule is a string over {L, R}. Each cell holds a colour `0..n`. On every
//! step the ant reads the colour `c` under it, turns according to `rule[c]`,
//! advances the cell to colour `(c + 1) % n`, then moves one cell forward.
//! Classic Langton's ant is the rule "RL".
//!
//! Two implementations live here: [`reference`] favours obviousness and is the
//! oracle; [`fast`] is what the sweep uses and is tested against the oracle.

pub mod bulk;
pub mod colourflux;
pub mod colours;
pub mod detect;
pub mod edge_renewal;
pub mod edge_trace;
pub mod ext;
pub mod falsify;
pub mod fast;
pub mod field_age;
pub mod first_passage;
pub mod fixed_area;
#[cfg(feature = "cuda")]
pub mod gpu;
pub mod lattice_probe;
pub mod invariants;
pub mod lattice_trace;
pub mod lean;
pub mod local_memory;
pub mod onset;
pub mod prefix_exposure;
pub mod probe;
pub mod reference;
pub mod return_gates;
pub mod seed;
pub mod snap;
pub mod rule;
pub mod synth;
pub mod tiled;
pub mod walkers;

pub use rule::{Rule, Turn};

/// Headings: 0 = north, 1 = east, 2 = south, 3 = west. Screen coordinates,
/// so north is -y.
pub const DIRS: [(i32, i32); 4] = [(0, -1), (1, 0), (0, 1), (-1, 0)];
