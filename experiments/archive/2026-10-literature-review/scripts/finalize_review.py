from pathlib import Path
root=Path(__file__).resolve().parents[4]
p=root/'experiments/archive/2026-10-literature-review/reports/Cube root growth literature.md'
s=p.read_text()
s=s.replace('Assume compactness A~R², boundary cardinality B~R^d, and a mean time between relevant boundary growth opportunities τ~A/B~R^(2−d), with an order-one new-area gain per opportunity.', 'Assume compactness A~R², boundary cardinality B~R^d and a scale-independent mean pocket area. Their rectangular-pocket construction has B~hR/w, outside-pocket probability ~w/h and conditional bulk-return time ~R; assuming this term dominates the pocket-internal contribution gives mean boundary-collision interval τ~Rw/h~R^(2−d)~A/B. These are heuristic geometric and first-passage assumptions, supported by their numerical consistency checks rather than a general stationary-occupation theorem.')
s=s.replace('three configurations; no between-seed uncertainty reported;', 'three configurations among13 symmetry-distinct3×3 media,36 initial position/heading phases; phase-averaged transient lengths are not independent growth replicates; growth uncertainty/phase spread and exact fit upper endpoint NR;')
s=s.replace('This review supplies conservative revisions and two discriminating mechanism candidates;', 'This review supplies conservative revisions and two discriminating mechanism candidates, explicitly crediting the earlier boundary-access argument;')
p.write_text(s)
p=root/'research-outputs/scholarly-articles/cube-root-growth/main.typ';s=p.read_text();s=s.replace('and the edge does not match: the ants\' surface width grows about twice as fast as the rotor\'s.', 'and the examined ant cohorts have a larger finite-window surface-width exponent than the rotor controls.')
s=s.replace('Meng and Cohen\'s earlier argument assumes $A tilde R^2$, $B tilde R^d$ and return time $tau tilde A/B$,', 'Meng and Cohen\'s earlier pocket/return argument assumes $A tilde R^2$, $B tilde R^d$, scale-independent mean pocket gain and a bulk-return-dominated collision interval $tau tilde A/B$,')
p.write_text(s)
