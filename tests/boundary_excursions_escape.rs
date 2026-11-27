//! Rev5 review S7: `boundary_excursions --check` must not panic on a run that escapes the board.
//! The instrument keeps the partial escape window; `probe_walker` drops it. Only completed windows are compared.
//! `RL` (Langton's ant) builds its highway and leaves a 512 board during window k = 14 (README, amendment A1).

#[path = "../examples/boundary_excursions.rs"]
#[allow(dead_code)]
mod be;

#[test]
fn check_tolerates_escaping_run_on_small_board() {
    // Before the fix this panicked with `window count` 5 vs 6.
    assert!(be::check_spec("RL@7", 512, 14), "RL@7 must escape the 512 board");
}

#[test]
fn check_still_strict_without_escape() {
    assert!(!be::check_spec("RL@7", 8192, 14), "RL@7 must stay on the 8192 board");
    assert!(!be::check_spec("LLRR@7", 512, 14), "LLRR@7 stays on the 512 board");
}
