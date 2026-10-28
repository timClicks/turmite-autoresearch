# Lab notebook: formal check of the exposure classifier

Append-only. Newest entry last. Never edit an old entry; correct it with a new one
(`corrects: <timestamp>`). Tags: intent, assumption, observation, interpretation,
surprise, decision, dead-end, question, deviation. See `experiments/README.md`.

### 2026-10-25 09:12 (+00:00) · 8a073b7 · intent
Close off the "instrument bug" explanation for the failed P3/P4 of 2026-10-kappa-exposure-classes
with a checker written separately from the Rust (proof-track architecture rule). Plan: a Rust
example that calls the instrument's own `Region` / `run` code on every 3x3 pattern and every visit
order and on scripted walks, dumps the tables to `results/`; a PEP 723 z3 script that proves the
documentation-level spec and checks the dumped tables against it.

### 2026-10-25 09:13 (+00:00) · 8a073b7 · decision
Pruning preflight at `8a073b75aab339e492863eaa6303a7d035906162`: `rg --files notes/pruning-index/entries`
(one entry); `rg -n -i -e exposure -e classifier -e "exposure class" -e z3 -e formal notes/pruning-index/entries`:
no matches. Decision RUN (finite check, seconds of compute).

### 2026-10-25 09:14 (+00:00) · 66b8ddb · deviation
The registration text says "09:14 UTC"; the registration commit `66b8ddb` is stamped 09:13:37 UTC.
Both precede any harness or checker code. No other change.

### 2026-10-25 09:15 (+00:00) · 66b8ddb · assumption
The instrument's private `Region` and `run` cannot be reached from another example: `include!` rejects
the file's `//!` header and a `#[path]` module hides private items from the parent. The harness
therefore carries a byte-for-byte copy of lines 20-248 of `examples/kappa_exposure_classes.rs`
(everything except the doc header and `main`) and asserts at runtime that the instrument source
(`include_str!`) contains that copy verbatim, so the code exercised is the code that ran.
Status: enforced by the harness; would fail loudly if the instrument changed.

### 2026-10-25 09:16 (+00:00) · 52bcd60 · result
Harness run (`scripts/run_dump.sh`, fresh target dir, binary sha256 bade9373...5dc4, identical to the
earlier fresh build). 512 table rows, every pattern one outcome over all orders, scan_ok everywhere;
224 walks, 576 windows. CSVs committed with the harness in `52bcd60` (same bytes as the logged run).

### 2026-10-25 09:31 (+00:00) · 99d0a3c · decision
z3 pinned to `z3-solver==4.13.4.0` to match PR #15's `prove_prefix.py` (not the newest PyPI release),
same `check(name, premises, goal, expect)` / "ok|FAIL name verdict" layout, single script with the
controls at the end. Added N6 (mutant `visit()`) as an extra control for P5; noted as beyond the
registration.

### 2026-10-25 09:31 (+00:00) · 99d0a3c · result
65/65 as expected (results/check.txt, 6m46s). P1-P7 held; N1-N6 rejected. P7 holds on all 6,154
rows of the 2026-10-20 classes.csv. Impact on the 2026-10-20 P3/P4: verdicts stand; only the
"corners, bays, tips" wording is qualified (README Results). Registered predictions not edited.

### 2026-10-25 09:32 (+00:00) · 99d0a3c · correction
Timestamps of the 09:14 and 09:15 entries were written from memory and are approximate (both written
between 09:13:37 and 09:16 UTC); from here on each heading uses `date -u`. No content changes.

### 2026-10-25 09:39 (+00:00) · 05de7b2 · observation
Merged into the onboarding branch (`05de7b2`). The verbatim guard now fails there, because `0a010ff`
changed the instrument (Shadow check, clippy). Scratch re-dump with the post-review instrument body:
table/walks/paths byte-identical to the committed dumps. Recorded in README ("Reproduction on later
revisions"); reproduce the committed dumps at `421d477`.
