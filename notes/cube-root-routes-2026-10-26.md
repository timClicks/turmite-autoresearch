# Routes to explaining the cube root: proposals from a literature survey

**STATUS: PROPOSALS, NOT RESULTS.** Written 2026-10-26 23:05 NZDT by the Turmite Research Agent (AI research agent), on
branch `survey/cube-root-routes` from `5b96f680ba25ff898fc5ed91d2c33a43d6713233`. No experiment was run and no measurement
was made for this note. Nothing here is registered: each proposal states a prediction and a kill criterion so that it
*could* be registered, in an experiment README and before any measurement, if a maintainer chooses it. The ranking is a
suggestion, not a decision, and it does not change the priorities in [ACTIVE.md](ACTIVE.md). Every number quoted below
comes from an existing, linked record; none is new.

Companion blog post: `blog/_posts/2026-10-26-four-constants-that-came-before-their-theories.md`. Open questions: Q34-Q37
in [open-questions-hypotheses.md](open-questions-hypotheses.md) (section "Added 2026-10-26").

## 1. Why this note exists

Two threads from a conversation with the maintainer on 2026-10-26 are recorded here so they are not lost:

1. a reframing of what the cube-root explanation has to explain (Kac's return-time lemma, and what the *shape* of the
   ant's excursions away from its edge would say), and
2. a survey of other fields where a constant or exponent was measured, or guessed correctly, long before anyone could
   say why, and what each of those stories suggests for this project.

## 2. Where the explanation stands (existing record only)

- The growth identity `dA/dt = c * kappa * P/A` is bookkeeping: with c and kappa constant and `P ~ A^(1/2)` it gives
  `A ~ t^(2/3)` and width `~ t^(1/3)` ([cube-root-hypothesis.md](cube-root-hypothesis.md)). P5's formula
  `a = (1 + gamma_c + gamma_kappa) / (2 - beta)` is a fit-consistency check, not an independent test (correction of
  2026-10-16 in the same note).
- Boundary dwell is flat over L = A/P, so constant kappa is *equivalent* to the mean interior excursion E[T] tracking L
  (renewal identity `f = E[D]/(E[D] + E[T])`, `kappa = L f`). Why E[T] tracks L is open. The tail fit meant to answer it
  failed calibration (C6), so its theta and z are not findings
  ([first-passage README](../experiments/2026-10-20-kappa-first-passage/README.md), "Correction after review").
- The typical boundary excursion is local (median `r*/L` 0.096 and 0.053), but time-weighted reach is about 1.16 L
  ([boundary-return map](../experiments/2026-10-21-boundary-return-map/README.md), "Confirmation results"). The typical
  excursion in the earlier tomography is a one-step return
  ([excursion tomography](excursion-tomography-2026-10-13.md)).
- Known failure modes of the cube root in this repo: log-growers with kappa near 0 and falling, including tethered rules
  held by exact home cells ([summary-2026-10-13.md](summary-2026-10-13.md), "Tethered ("hard") rules"); the sqrt(t)
  turmite cluster, which builds 1D structures (area/extent^2 0.001 against 0.54 for compact blobs;
  [frontier-2026-10-13-results.md](frontier-2026-10-13-results.md), D1); highways; and the square-ring board fillers,
  whose edge is a crawler with a *proved* c ([square-ring fillers](../experiments/2026-10-25-square-ring-fillers/README.md),
  [crawler cost](../experiments/2026-10-25-crawler-cost-chaotic-edge/README.md)).

## 3. Thread 1: what the cube root reduces to

### 3a. Kac's lemma as the target (prior art: Meng and Cohen 1994; this repo)

Kac's lemma: for a stationary ergodic process, the mean return time to a set S, starting from S, equals 1/Pr(S). If the ant occupied its
territory uniformly, the boundary would carry probability P/A and the mean return time would be A/P = L. The repo's
finding "constant kappa iff E[T] tracks L" therefore says: **the ant returns to its own edge on Kac's schedule for a
uniform occupant, up to a rule-specific constant** (the census median is about 0.81 of each rule's uniform reference;
[uniform baseline](../experiments/2026-10-16-kappa-uniform-baseline/README.md)). The ant is neither stationary nor
Markov and its territory grows, so this is an analogy that names the target, not a theorem that applies.

This is **not new**. Meng and Cohen (1994) already used a boundary-return argument with a return time of order area over
boundary to get territory exponents in a Lorentz lattice gas; the repo's
[literature review](literature-review-2026-10-15.md) records it as direct prior art. The renewal identity in the
first-passage experiment is the same bookkeeping.

### 3b. The mean cannot tell two stories apart; the shape can

At least two excursion laws give `E[T] ~ L`:

- **Diffusive (D).** Excursions behave like a random walk leaving a wall: `Pr(T > s) ~ s^(-1/2)` for `1 << s << L^2`,
  cut off near `L^2`. The mean is of order `integral of s^(-1/2) up to L^2`, i.e. of order L. Durations collapse in
  `s/L^2` after multiplying by `s^(1/2)`, and the intermediate tail does not depend on L.
- **Sweep (S).** Long excursions are traversals with length proportional to L (plus an atom of short returns).
  Durations collapse in `s/L` and there is no L-independent intermediate range.

Both give `z(1 - theta) = 1` in the first-passage scaffold `Pr(T > t) ~ a t^(-theta) F(t / (b L^z))`: (theta, z) =
(1/2, 2) for D and (0, 1) for S. The first-passage README already noted that fits are pushed toward `z(1 - theta) ~ 1`.
That is what `E[T] ~ L` forces, so the mean constrains only the product, and a free fit of theta and z is badly
conditioned along this line. Deciding between D and S (or "neither") needs a test of the *shape*, not a better fit of
the mean.

The boundary-return map does not decide it: local typical excursions with time-weighted reach of order L fit D (a
heavy tail) and S with an atom of short returns.

### 3c. What the rotor proofs actually use

Read in full for this note (the 2026-10-12 entry under "Items 29 and 28" in [frontier-results.md](frontier-results.md) read abstracts only).

- **Florescu, Levine and Peres (2016), "The range of a rotor walk".** Lemma 2.1: on an Eulerian graph, during one
  excursion from the origin each vertex is visited at most deg(x) times (this needs in-degree = out-degree). Lemma 2.4:
  the (n+1)th excursion traverses every edge out of the set A_n visited by the first n excursions. Corollary 2.5: the
  ball of radius n lies inside A_n. So each excursion costs at most a constant times the current territory and is forced
  to add a whole layer. Counting gives range `>= c t^(2/3)` on Z^2 for *every* rotor mechanism and initial configuration
  (Theorem 3.1 gives `W(r) ~ (8/3) r^3`, the diamond case of Remark 3.2). Theorem 1.2: an infinite rotor path pointing to
  the origin gives linear range. They credit the `t^(2/3)` heuristic to Priezzhev, Dhar, Dhar and Krishnamurthy (1996)
  and Povolotsky, Priezzhev and Shcherbakov (1998).
- **Bou-Rabee and Peres (2026), "Eulerian walkers on Z^2 have range exponent 2/3".** For i.i.d. uniform initial rotors
  (clockwise on Z^2, and doubly periodic graphs of maximum degree 3) they prove recurrence, convergence of the rescaled
  territory to a convex deterministic body, and `|R_t| t^(-2/3)` converging to a deterministic constant. The proof has
  three parts: a monotone circuit map (from the abelian property) gives passage times with a triangle inequality and
  the subadditive ergodic theorem; fast growth would force long, almost-live rotor paths in the initial configuration;
  such paths are rare, by comparison with critical percolation (square lattice) or Galton-Watson trees (degree 3).
  **Randomness of the initial rotors is essential.** Counterexamples they give: a graph with attached leaves is
  transient; on the F-lattice the shape degenerates and `log|R_t| / log t -> 1`; the tetrakis lattice with another
  rotor order appears linear. Whether the limit body is a disc (Kapri and Dhar's numerics) is their open Problem 3.
  The 1/3 is therefore proved for the random rotor; the constant exists but is not computed.

Why none of this transfers directly (credited, not new): the ant's exit depends on its incoming heading and the shared
cell colour, so it is not a rotor walk (frontier-results, items 29 and 28: "the rotor router's monotone/abelian structure ... does
not apply directly"; item 6's pilot found no exact rotor reduction;
[kappa-mechanisms-2026-10-15.md](kappa-mechanisms-2026-10-15.md): "a rotor-style Eulerian identity cannot be
assumed"; the [literature review](literature-review-2026-10-15.md): "Rotor results supply conditional comparisons, not
an ant theorem"). Two further obstacles this reading adds: (i) on the (cell, heading) state graph, the four incoming
headings share one colour state, so Lemma 2.1's "use every out-edge before reusing one" fails; (ii) a blank-board ant
has no random initial configuration, so Bou-Rabee and Peres's rarity step has nothing to average over. Existing
deterministic results for Langton's ant (Bunimovich and Troubetzkoy 1992, cited in
[proof-track-2026-10-20.md](proof-track-2026-10-20.md), not yet through the literature-review process) give
unboundedness, not a rate.

## 4. Thread 2: constants before theories (verified sources only)

| Field | Empirical or heuristic value | Later theory | Lesson for this project |
|---|---|---|---|
| Period doubling | Feigenbaum (1978) found universal constants; his abstract says "At present our treatment is heuristic" | Lanford (1982), a computer-assisted proof | Find the operator whose fixed point is the constant; a computer can check a fixed point that no one can compute by hand |
| Polymers | Flory's formula `nu = 3/(d+2)` (1949) gives 3/4 in 2D | Nienhuis (1982) derived exact O(n) exponents, giving 3/4 for 2D self-avoiding walks | A right number can come from a wrong argument (des Cloizeaux 1976 showed Flory's argument incorrect, as recounted by Redner and Reynolds 1981). Agreement of the growth identity with data is not evidence for its story |
| Growing interfaces | Kardar, Parisi and Zhang (1986) predicted exponent 1/3 for 1D interface fluctuations | Johansson (2000) proved `N^(1/3)` fluctuations for an exactly solvable model and identified the limit law as Tracy and Widom's (1994) | The sharp universal object was the fluctuation *distribution*, and the proof came from one exactly solvable member of the class |
| Rotor walks | Priezzhev et al. (1996) conjectured radius `t^(1/3)` from numerics and a heuristic | Florescu, Levine and Peres (2016) lower bound; Bou-Rabee and Peres (2026) full result for random rotors | A one-sided bound (arXiv 2014) came more than a decade before the theorem and was cheap; the full proof needed randomness |
| Return times | Kac (1947) | Exact for any stationary ergodic process | A mean can be exact without a model of the dynamics; it then carries no mechanism |

The 1/3 in KPZ is a fluctuation exponent of a growing interface; ours is the growth exponent of a radius. The shared
value is not evidence of a connection, and the repo's own walker comparisons already warn that matching edge numbers
"neither ... proves KPZ" ([walker-comparisons-2026-10-13.md](walker-comparisons-2026-10-13.md)).

## 5. Proposals (ranked suggestion)

### P-A (Q34). Excursion lemma, adapted: a one-sided bound and its failure in tethered rules

**Idea.** Split FLP's argument into two properties that can be measured on ant trajectories, rule by rule:
- *(M) bounded multiplicity:* between consecutive visits to a reference set (first choice: the origin cell, any
  heading), no cell is visited more than M times, with M independent of territory size;
- *(B) boundary coverage:* each such excursion that lasts longer than a size-independent cutoff visits at least a
  fraction m of the current boundary cells.
If (M) and (B) held with c bounded below, the same counting as FLP gives a lower bound `A >~ t^(2/3)` (excursion cost
`<= M A`, gain `>~ c m P ~ A^(1/2)`). A proof target would be a rule-restricted version of (M) and (B); the measurement
would only say whether the target is plausible.

**Step zero (cheap, before anything else).** FLP's excursions are from the origin, and nothing in the repo shows that a
blank-board chaotic ant revisits its origin cell often, or at all. Count origin returns on a few census rules first. If
returns are sparse, replace the origin with a territory-relative reference set (for example the current boundary), which
leaves only the Kac reading of 3a.

**Scope of (B).** A measured coverage fraction is a necessary condition only. FLP get "each excursion adds a whole layer"
from the abelian property and Eulerian structure, which the ant lacks; a rule passing (M) and (B) is consistent with the
counting argument, not covered by it.

**Prediction (if registered).** Blob rules satisfy (M) and (B) with constants that do not drift with L; tethered
log-growers fail (B) (their excursions from home do not reach the edge); the sqrt(t) cluster is excluded because it is
not compact; highways are excluded because the origin is not revisited.

**Kill criterion.** In blob rules the per-excursion maximum visit count grows with L, or origin returns stop, or (B)'s
coverage fraction falls with L. Any of these kills the origin-based adaptation; only the territory-relative Kac reading
(3a) would remain. Calibration first: the rotor must satisfy (M) and (B) exactly, and a random walk on a growing
cluster must fail (M).

### P-B (Q35). Fluctuation-shape collapse across chaotic rules versus the rotor

**Idea.** The KPZ lesson: classes are told apart by fluctuation distributions, not exponents. The repo already finds
the ants' boundary-width exponent at 0.22-0.25 against about 0.12 for the rotor through 2^34, and says "the universality
class isn't decided" ([summary-2026-10-13.md](summary-2026-10-13.md), "Edge width"). The atlas's edge-roughness topic
now records that at the longest windows (to 2^36, `experiments/2026-10-13-w4-edge-exponent-2e36/`) both registered
decision rules are inconclusive, so exponents may not separate the classes; distributions might.

**Prediction (conjecture).** After centring and scaling each rule's edge fluctuations by its own spread, chaotic blob
rules share one distribution that differs from the rotor's.

**Kill criterion.** The between-rule spread of standardised shape statistics is as large as the ant-rotor difference,
judged against the rotor's seed-to-seed spread. Then the ants share an exponent but no fluctuation class, which would
weaken any single-mechanism story.

**Data.** `experiments/2026-10-13-a4-boundary-width/results/a4_shape_{ants,rotor}.csv` hold moments only (rbar, rsd,
harmonics h2/h4/h8, Wsurf). A first look at standardised moment ratios could use them. A distribution test needs saved
radial profiles, which means a new (small) run.

### P-C (Q36). Excursion-duration collapse: diffusive or sweep?

**Idea.** Test 3b's two readings directly, without fitting theta and z. Builds on the dynamic-scaling item in
[kappa-mechanisms-2026-10-15.md](kappa-mechanisms-2026-10-15.md) and the calibration list under "First-passage closure"
in [ACTIVE.md](ACTIVE.md) (rotor, random walk on a growing cluster, mean-field walker, synthetic streams).

**Prediction (two-sided).** D: at fixed s with `1 << s << L^2` the survival `Pr(T > s)` does not depend on L, and
`s^(1/2) Pr(T > s)` collapses in `s/L^2`. S: `Pr(T > s)` beyond the short-return atom collapses in `s/L`. Fix the
collapse-quality metric and the margin needed to prefer one before looking.

**Gate and kill criterion.** The random walk must come out D. The rotor and mean-field walker are measured as
calibrators, not given a guessed answer. If the calibrators cannot be told apart at accessible L with the fixed metric,
the test is uninformative and stops (as C6 did). For the ants, the reading whose collapse fails by the margin is
rejected; if both fail, report "neither". Censoring must use the tail-budget sampler's bounds.

### P-D (Q37). Universality conjecture: what produces stationary access

The identity makes "compact + stationary kappa + bounded c => cube root" automatic, so that statement has no content
on its own. The conjecture with content is:

> **Stationary boundary access holds for any walker whose territory is compact and which has neither a tether (a
> fixed region it keeps returning to) nor an edge lock (a structure that keeps it on the boundary), whatever the
> walker class.**

The known failures each break one condition: tethered log-growers (tether, kappa falls), crawler and ring fillers (edge
lock, faster than a cube root), sqrt(t) cluster and highways (not compact). The rotor examples line up: an infinite
rotor path toward the origin gives linear range (FLP Theorem 1.2), the leaf graph is transient, and the F-lattice shape
degenerates (Bou-Rabee and Peres).

**Prediction (if registered).** With tether and edge-lock defined operationally and decided on early windows, walkers
classified "compact, untethered, unlocked" have stationary kappa on later, separate windows, and beat persistence at
predicting late kappa drift (the priority-1 criterion in ACTIVE.md).

**Kill criterion.** A compact walker with neither tether nor edge lock, by the frozen definitions, whose kappa drifts;
or a cube-root grower that breaks one condition. P5 agreement must not be used as support (2026-10-16 correction).

## 5b. Before any of these is registered

Each proposal that becomes a sweep or a variation on a failed test needs the negative-result pruning-index check first
(`notes/pruning-index/README.md`): record the index revision, search terms, matching signature IDs and the
run/skip/reopen decision in the experiment README and NOTEBOOK, including a no-match search. P-B and P-C are the likeliest
to touch existing signatures (edge-width and first-passage dead ends). The cheapest start is P-B on the existing a4 moment
files, before any new run.

## 6. What would change my mind about the ranking

If P-C's calibration shows that the random walk and the rotor cannot be told apart at sizes we can reach, then P-C
drops out and P-A becomes the only route that says anything about E[T]. If the a4 moment ratios already spread widely
between rules, P-B is weak before it starts. P-D is the most ambitious and the easiest to make circular. Its value
depends entirely on defining tether and edge lock without using kappa.

## 7. References

Verified 2026-10-26 against arXiv abstract pages, publisher pages or Crossref metadata (bibliographic details; claims
about content were checked against abstracts or full text as noted).

- Bou-Rabee, A., and Peres, Y. (2026). Eulerian walkers on Z^2 have range exponent 2/3. arXiv:2608.23545. Full text read.
  No journal reference listed. Flagged 2026-10-27 for a manual re-check of the arXiv identifier; not independently re-verified in this revision.
- Florescu, L., Levine, L., and Peres, Y. (2016). The range of a rotor walk. Amer. Math. Monthly 123(7), 627-642.
  doi:10.4169/amer.math.monthly.123.7.627; arXiv:1408.5533. Full text read.
- Priezzhev, V. B., Dhar, D., Dhar, A., and Krishnamurthy, S. (1996). Eulerian walkers as a model of self-organised
  criticality. Phys. Rev. Lett. 77, 5079; arXiv:cond-mat/9611019.
- Povolotsky, A. M., Priezzhev, V. B., and Shcherbakov, R. R. (1998). Dynamics of Eulerian walkers. Phys. Rev. E 58,
  5449; arXiv:cond-mat/9802070.
- Kapri, R., and Dhar, D. (2009). Asymptotic shape of the region visited by an Eulerian walker. Phys. Rev. E 80, 051118;
  arXiv:0906.5506.
- Meng, H.-F., and Cohen, E. G. D. (1994). Growth, self-randomization, and propagation in a Lorentz lattice gas. Phys.
  Rev. E 50, 2482-2487. doi:10.1103/PhysRevE.50.2482 (content as recorded in the repo's literature review).
- Kac, M. (1947). On the notion of recurrence in discrete stochastic processes. Bull. Amer. Math. Soc. 53, 1002-1010.
  doi:10.1090/S0002-9904-1947-08927-8 (Crossref metadata; the article page could not be fetched).
- Feigenbaum, M. J. (1978). Quantitative universality for a class of nonlinear transformations. J. Stat. Phys. 19,
  25-52. doi:10.1007/BF01020332.
- Lanford, O. E. (1982). A computer-assisted proof of the Feigenbaum conjectures. Bull. Amer. Math. Soc. 6, 427-434.
  doi:10.1090/S0273-0979-1982-15008-X.
- Flory, P. J. (1949). The configuration of real polymer chains. J. Chem. Phys. 17, 303-310. doi:10.1063/1.1747243
  (Crossref metadata only).
- Redner, S., and Reynolds, P. J. (1981). Position-space renormalisation group for isolated polymer chains. J. Phys. A
  14, 2679-2703. doi:10.1088/0305-4470/14/10/022 (source for the formula's history and for des Cloizeaux's 1976
  criticism; read from indexed full text).
- Nienhuis, B. (1982). Exact critical point and critical exponents of O(n) models in two dimensions. Phys. Rev. Lett.
  49, 1062.
- Kardar, M., Parisi, G., and Zhang, Y.-C. (1986). Dynamic scaling of growing interfaces. Phys. Rev. Lett. 56, 889.
- Johansson, K. (2000). Shape fluctuations and random matrices. Commun. Math. Phys. 209, 437-476.
  doi:10.1007/s002200050027; arXiv:math/9903134.
- Tracy, C. A., and Widom, H. (1994). Level-spacing distributions and the Airy kernel. Commun. Math. Phys. 159, 151-174.
  doi:10.1007/BF02100489; arXiv:hep-th/9211141.

Not cited (unverified): Gale, Propp, Sutherland and Troubetzkoy (1995), listed "from memory" in proof-track; any claim
about the current status of a rigorous proof of the 2D self-avoiding-walk exponent; experimental KPZ confirmations.
