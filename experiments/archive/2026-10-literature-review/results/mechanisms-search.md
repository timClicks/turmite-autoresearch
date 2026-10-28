# Mechanism source-search record

Date: 2026-10-15 NZDT. Base HEAD da88e61b690507526ba4e2a2c017d9c7941beb91; dirty tree. No simulation. Queries had no date/domain filters. Explicitly requested connector `mcp__codex_apps__search_service_web_run` was attempted twice: (1) batched queries `Priezzhev Dhar Dhar Krishnamurthy 1996 Eulerian walkers`, `arxiv 0906.5506`, `arxiv 2608.23545`; (2) `Kapri Dhar 0906.5506`. Both returned empty content with isError:true. Fallback service was `web__run`.

Exact fallback discovery queries, in order:

1. `Priezzhev Dhar 1996 Eulerian walkers`
2. `arxiv 0906.5506`
3. `arxiv 2608.23545`
4. `Florescu Levine Peres range rotor walk 2016`
5. `Holroyd Propp Rotor walks Markov chains 2010 hitting frequencies`
6. `Lawler Bramson Griffeath internal diffusion limited aggregation shape 1992`
7. `"Eulerian walkers" "Bou-Rabee" "Peres" 2026 publication`
8. `"Kapri" "Dhar" "Toth" "Veto" 2009 Eulerian`

Direct primary retrieval and screening:

| Source | Access and extraction | Direction / decision |
|---|---|---|
| cond-mat/9611019, DOI 10.1103/PhysRevLett.77.5079 | Accessible original arXiv PDF, 8 PDF pages; argument/model and eqs.1–5 inspected; publisher metadata accessible | Plan seed, included: distinction between finite Euler circuit theorem, infinite-growth heuristic and driven-sink ensemble |
| 0906.5506v2, 17 Sep 2009, DOI 10.1103/PhysRevE.80.051118 | Accessible complete seven-page PDF text; relevant §§II–IV, eqs.1–10 inspected; metadata journal reference has typo 1051118, use DOI's 051118 | Plan seed; included for local-time balancing/cone and exact dynamic-noise convention; boundary specialist handles width |
| 2608.23545v1, 24 Aug 2026 | Accessible arXiv metadata and 29-page HTML; Theorem1.1/Prop1.2, §§1.2–1.3/2–3 and open problems inspected; only v1 currently listed | Plan seed; included theorem scope/proof assumptions; no journal reference listed; refereeing status unverified |
| 1408.5533, DOI 10.4169/amer.math.monthly.123.7.627 | Accessible 15-page original PDF, selected §§1–3 and Lemma2.4 read | Backward from 2026 and forward from Priezzhev/Kapri; included exact excursions and general lower bound |
| 0904.4507, DOI 10.1090/conm/520/10256 | Accessible 32-page original PDF; selected §§1.1–1.3, occupation and stationary theorems checked; not a whole-paper audit | Backward from 2026/Kapri; included finite-chain limitation, fixed transition stacks |
| Lawler–Bramson–Griffeath 1992, DOI 10.1214/aop/1176989542 | Publisher full endpoint returned no substantive text; aggregator abstract screened only, no original theorem extracted | Backward from 2026 §1.3; retained only clock/model caution; full-text gap |
| Povolotsky–Priezzhev–Shcherbakov 1998, cond-mat/9802070 / DOI 10.1103/PhysRevE.58.5449 | Abstract and author-posted search hit screened; not original full-text verified | Forward from Priezzhev / backward from 2026; exclude quantitative use: critical-state MSD/avalanches is a different ensemble |
| Angel–Holroyd tree paper 1009.4802; Toth–Veto 1D references | Abstract/reference screen only | Backward from 2026/Kapri; exclude extrapolation: trees/1D not an ant kappa result |
| “Locally Markov Walks on Finite Graphs” (2026) | Search result screened | Exclude: finite-graph scope, no closer expanding ant-boundary mechanism identified |
| Author homepage nitromannitol.github.io | Retrieved: publications JS-only; snippet says submitted but live extracted body does not corroborate this | Publication-status discovery only, not evidence of peer-review state |
| ResearchGate, Qwen Councils, arxivdesk, Academus, arxivlens, papers.cool, gallery, rotor-23 Lean repository | Search hits screened | Exclude technical reliance: mirrors/discovery aids or formalization rather than a new occupation result |

Trace stopping rule: one selective backward/forward round on rotor seeds, following exact excursions, occupation discrepancy, and aggregation clock comparison. Latest preprint's backward citations already connect the original heuristic to the range theorem and distinguish aggregation. The forward publication query found mirrors/formalization rather than a newer journal record. No exhaustive citing-paper database export was available; this log does not claim an exhaustive forward citation audit. IDLA original access and one-dimensional self-interacting originals remain explicit gaps. Expansion stopped because neither introduced an established ant kappa formula and this review's assigned scope is a short falsifiable mechanism shortlist.

Local sources read: literature-review-plan; cube-root-hypothesis; paper-gaps-research-avenues; cutoff-research-avenues; excursion-tomography including retraction/verdict; walker-comparisons including pilot; kappa-rule-space README corrected W5 and W3c; independent-area README; relevant manuscript abstract/introduction/occupation/limitations passages. Source evidence and candidate tests are in `../research_notes/Cube root growth literature/mechanisms.md`. No shared README, NOTEBOOK, manuscript or existing result was edited by this researcher.

## Same-session full-text recovery addendum

Coordinator/novelty researcher recovered Meng–Cohen1994 original publisher PDF locally in ignored `scratch/meng1994/source.pdf`, with OCR and rendered pages. No further search query was issued. Independently read printed p.2486 (PDF p.5) visually using `view_image` of `page-5.png`, alongside `ocr-5.txt`; equations verified from rendered image. PDF skill read-only workflow applied. Source DOI10.1103/PhysRevE.50.2482. Backward tracing from Mishra thus resolves a previously inaccessible mechanistic antecedent: pocket growth, boundary collision interval, and exponent relation. Novelty agent handles full-paper growth measurements and provenance hashes. Mechanism addendum records mapping to our c/kappa/P bookkeeping, distinguishes notation, and sharpens Candidate B rather than adding a third mechanism. Earlier log entries report the initial access situation; this addendum supersedes any impression that Meng remains inaccessible. IDLA original full-text gap remains.
