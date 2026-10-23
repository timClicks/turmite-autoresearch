# Can an unchanged turn map hide a different boundary return?

## Registered pilot, 2026-10-23 11:37 UTC

Base: `b942a82854b4d61222301959b9895060d2543d3f`. Registration precedes instrument
construction and all new measurements. This is one excluded development pilot,
not a confirmation study or a test of a growth exponent.

The boundary-return shuffle experiment found that long return times depend on
distant colours, but changed both present turns and future colour clocks. We
separate those two pieces. A cell's colour specifies a cyclic sequence of turns.
Two different colours can prescribe the same next turn and different later turns.

**H-map:** the instantaneous left/right map retains most of the return-time
information under field shuffling. Preserving that map should remove most of the
unrestricted shuffle effect. **H-clock (preferred):** hidden phases carry a large
part of the sensitivity of long returns, even with that map held exactly fixed.
This tests causal sufficiency of the map, not a predictive model of occupation.

At each sampled boundary departure, shuffle colours among interior cells grouped
by `(floor(depth/8), next k turns)`, for k = 0, 1, 2, 4 and n (rule length).
Depth is graph distance to the visited boundary. Boundary colours, territory,
position and heading stay fixed. Each arm preserves the colour histogram in each
depth bin. k=0 is unrestricted within depth bins; k=1 fixes the next turn at
**every cell**; k=n fixes the entire future turn sequence (an exact path sham,
even when nonprimitive rules permit colour changes). Four seeded replicas/arm.
Use independent streams keyed by rule, start, band, departure, k and replica.
Fixed points are retained. This is a large field intervention, not a single-cell
or naturally reachable-state claim.

**Exact prefix control:** until the first trajectory difference, the two ants
have identical visit counts at each cell. Preserving k future turns means a
first difference can occur only on visit k+1 or later to some cell. Check this
on every replay. Arrival colour is deliberately excluded from path equality.

## Cohort, sampling and stopping

Rules are the first three distinct rules of the old return-map pilot:
`RLLLLRLLRLRL`, `RLLLRRLRLL`, `RLLRRLLLLLLL`. Four **new** 5x5-patch seeds
2026102301..2026102304. This does not open the c-law renewal main cohort.
Square board 2048, area bands [4096,4352) and [16384,17408).
Live budget 2^27 steps/start. First 16 completed excursions of length >=128 per
band, with departure times at least 64 steps apart; baseline/replay cap 2^18.
Track **every** departure in each band: completed short, eligible long,
overflowed, quota/gap rejected and unfinished at budget/escape. Keep exact total
completed duration, including overflowed episodes. Stop sampling at quota but
continue counting through the band. No overflowing baseline is silently dropped.
Only episodes whose departure lies in a band enter its counters; an episode
keeps its departure band to completion. Initial fragments are not departures.
If the final horizon cuts an episode, record its observed duration separately.

No extension after results. At most 12 x 2^27 live steps and 384 x 20 x 2^18
replay steps (worst case about 3.6 billion steps); stop with an inconclusive
pilot if gates fail. No new rule or larger sweep in this experiment.

## Frozen outcomes and decision

Primary arm effect: mean absolute log2(T_arm/T_base), with T capped at 2^18.
Average replicas and departures within start/band, then average starts equally
within rule/band. Report signed log ratios, factor-two changes, exact path/return
matches, changed-cell fractions and baseline-read exposure separately. Do not
weight every replica as an independent ant. Report seed SD and a paired
start-level bootstrap (10000 draws, seed 2026102300) within each rule/band.

P1: k=1 retains >=50% of k=0's primary effect in **all six** rule/band cells,
with k=1 absolute effect >=0.5 in each. This supports H-clock at pilot scope.
A ratio <=0.2 in all six supports H-map under this intervention. Otherwise the
mechanistic comparison is unresolved. k=2 and 4 are descriptive dose controls;
no monotonicity is assumed, since partitions change intervention support.

Gates: exact live/cropped replay; independent sparse reference agreement on
synthetic fields; exact k=n path sham; prefix theorem holds; deterministic output
at one and three threads. At least 8 sampled long episodes/start/band; <1% of
baseline departures overflow or remain unfinished; <=1% replay censoring per
arm overall; median changed fraction among distinct baseline-read interior cells
>=0.1 for k=1 in each rule/band. A failed gate prevents an uncensored or general
mechanistic claim; report capped effects, not a rescued threshold. A low count
fraction does not bound missing time: report the overflow duration fraction too.

Controls also include nonprimitive `RLRL` on synthetic fields: k=1 can move
colours but cannot change any future turn. A one-interior-cell territory has
return time exactly one. No exponent/tail fit is used. Rotor/random-walk growth
calibration would not calibrate this paired intervention; reference, analytical
and equivalent-phase controls check its actual contract.

## Pruning-index preflight

Index revision: base above. Commands: `rg --files notes/pruning-index/entries`
and `rg -n -i 'clock|phase|same.turn|return|boundary' notes/pruning-index/entries`.
Text search has no matches. Read the sole signature's membership and exclusions:
`NR-20261022-additive-laws-order-blind` covers additive invariant discrimination,
not phase interventions or return dynamics. Decision RUN; no exclusions.
The negative finite-memory c-law pilot concerns repeated forgetting and births;
this test makes one histogram-preserving intervention at an interior departure
and then restores full memory. No duplicate additive-law mining is needed: its
known order-blind laws do not decide the proposed return-time contrast.

Prior evidence: [return map](../2026-10-21-boundary-return-map/README.md),
[gates and eligibility warning](../2026-10-22-single-cell-gates/NOTEBOOK.md),
[current research priorities](../../notes/ACTIVE.md),
[evidence ledger](../../notes/evidence-ledger.md).

## Reproduction and results

To be appended after implementation and measurement. Predictions above stay fixed.
