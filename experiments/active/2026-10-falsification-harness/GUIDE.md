# Using the falsification harness

For anyone (human or agent) about to write "rule R is chaotic", "R forms a stable highway", or "highway type X is robust". The
harness attacks the claim instead of re-running it for longer. Its record is in `README.md` (design, registered predictions, what
failed); this file is how to use it. Code: `src/falsify.rs`, `src/bin/falsify.rs`; search comparison: `src/bin/falsify_search.rs`.

## When to use it
Use it before a claim of the form *about every start* or *no highway ever* goes into `notes/`, the blog or the paper. Do not use it for
growth exponents (t^(1/3) fits), mixing statistics or anything that is not about highways: there is no attack for those yet.
A blank-board horizon run is one trial of this harness (`blank`), not a substitute for it.

## Workflow (the order matters: AGENTS.md rule 8)
1. **Write the claim line and your prediction first**, in your experiment's `claims.txt` and README, with a timestamp. State what outcome
   would surprise you. Claims can only be registered, never tuned after seeing a run.
2. **Commit the claims file.** `falsify` refuses a claims file with uncommitted changes. (`--allow-dirty` exists for harness development;
   the header then says `DIRTY: not a registered run`, and such output must not be cited.)
3. **Build and run from a clean checkout of a commit** so the provenance header is true:
   ```
   git worktree add --detach /tmp/wt HEAD && cd /tmp/wt
   CARGO_TARGET_DIR=/tmp/wt-target cargo build --release --locked --bin falsify
   /tmp/wt-target/release/falsify experiments/<slug>/claims.txt /abs/path/to/experiments/<slug>/results
   git worktree remove --force /tmp/wt
   ```
   Log the binary's sha256. Output is identical for any `RAYON_NUM_THREADS`; check once with 1 thread.
4. **Read `results/<id>.verdict.txt`**, then append the outcome to your README *below* the unedited predictions, including every miss, and add a
   notebook entry. Commit `*.counterexamples.txt` (they are the harness's regression cases).
5. **Replay** a counterexample at any time: `falsify --replay results/<id>.counterexamples.txt`.

## Claim line (one per line, `key=value`, `#` comments)
`id=C1-RL-highway kind=highway rule=RL same_canon=true horizon=2000000 ladder=0 size=2048 trials=64 seed=101 registered=2026-10-22T21:35+13:00`

| key | meaning | default |
|---|---|---|
| `id` | letters, digits, `-`, `_` (it names the output files) | required |
| `kind` | `highway` (every start ends in a highway) or `chaotic` (no start ever does) | required |
| `rule` | `L`/`R` string | required |
| `registered` | ISO timestamp of the prediction; refused if absent | required |
| `same_canon` | highway claims: a different highway type counts as a counterexample | `true` |
| `horizon` | the horizon **the claim's author looked at** | 1000000 |
| `ladder` | attack to `horizon * 4^ladder`; the report lists escapes by `horizon * 4^k` | 2 |
| `size` | board side; see pitfalls | 2048 |
| `trials` | per generator class | 64 |
| `attacks` | `all` or a comma list of: blank, heading, boundary, patch, mono, half, stripe, sparse, obstacle, adaptive (blank and the two controls always run) | `all` |
| `chains`, `evals` | the evolutionary search: chains x evaluations per chain | 4 x 200 |
| `seed` | every trial is a function of (seed, rule, class, index) | 1 |
| `quantifier` | `universal` or `probabilistic` (the latter is always reported `Unsupported`: no valid interval exists for pooled adaptive attacks) | `universal` |

## Reading a verdict
| verdict | meaning | what you may write |
|---|---|---|
| `Falsified` | a reproduced counterexample (shrunk, re-run on a second board geometry) | "refuted by this start", cite the replay line |
| `Invalid` | a control failed (headings are rotations; a blank start near an edge must behave like the centred one) or the counterexample did not reproduce | nothing about the rule: fix the detector first |
| `Unsupported` | a highway claim with starts that never ended in a highway by the horizon | "not supported at this horizon". Never "refuted": a start that has not escaped yet is not a counterexample |
| `Survived` | no counterexample among the attacks at this horizon | "no counterexample in N attacks of these classes at this horizon". Never "proved" or "holds for all starts" |

`horizon-sensitive` in the notes means the blank-board highway starts after the stated horizon (exact onset): the original claim was a
horizon artefact. Escape counts by horizon lag the onset by the board-crossing time, so they are conservative.

## What it asymmetrically can and cannot do
- A confirmed highway is a finite witness, so it kills "no highway" claims. Nothing finite kills "highway from every start".
- Only finite perturbations in a blank far field are valid (the detector assumes the highway ends in blank cells). Dense random backgrounds
  are out of scope.
- The `chaotic` adaptive objective (smallest bounding box) is an unvalidated heuristic.
- The adaptive search beats random sampling at hunting long transients (RL, RRL; p ~ 1e-5 to 1e-8) but not at finding the one rare
  counterexample (RRRL: 27/30 vs random 30/30); keep random draws in the mix. See `../../archive/2026-10-falsify-adaptive-search/`.
- Survival is evidence only against the generators it tried. Add an attack when you suspect a blind spot.

## Pitfalls we hit
- **Board too small for the highway.** `size/2` divided by drift-per-step must fit inside the horizon, or every start is `Unresolved`.
  RRLR (drift 4 per 384 steps) needs about 98k steps just to cross 1024 cells.
- **Too small a board for the chaotic pattern** makes the heading control disagree; raise `size`.
- **Seeding leaks.** `fast::Grid::reset` only clears the old bounding box, so never reuse a grid for seeded starts; `falsify::simulate` allocates fresh.
- **`fast::highway_onset` replays from a blank board**: wrong for any perturbed start. Use it only for the baseline.
- **`git add -A` in a shared tree** once swept another contributor's files into a commit; add paths explicitly.

## Extending it
New attack = a `Class` variant, a branch in `make_trial`, and a line in `plan`. Any change to `simulate` or a generator needs the oracle
tests in `tests/falsify.rs` (step-for-step against `reference::Ant`, the mid-run obstacle, the two symmetries) and a mutation check that
the test can fail. A new search strategy goes through `falsify_search` as an equal-budget, replicated, paired comparison with its
predictions registered first.
