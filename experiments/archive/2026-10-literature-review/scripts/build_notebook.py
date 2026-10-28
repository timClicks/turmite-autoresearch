from pathlib import Path
import json, hashlib
ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / 'experiments/archive/2026-10-literature-review'
report = BASE / 'reports/Cube root growth literature.md'
text = report.read_text(encoding='utf-8-sig')
audit = text.split('| Manuscript contribution/claim |', 1)[1].split('\n\n', 1)[0]
rows = []
for line in audit.splitlines()[2:]:
    fields = [v.strip() for v in line.strip('|').split('|')]
    if len(fields) == 4:
        rows.append(dict(zip(['claim', 'comparator', 'distinction', 'action'], fields)))
summary = {'source': str(report.relative_to(ROOT)), 'source_sha256': hashlib.sha256(report.read_bytes()).hexdigest(), 'kind': 'documentary claim extraction, not measured data', 'claims': rows}
(BASE / 'results/claim_audit.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')

def md(s): return {'cell_type':'markdown','metadata':{},'source':s.splitlines(True)}
def code(s): return {'cell_type':'code','metadata':{},'execution_count':None,'outputs':[],'source':s.splitlines(True)}
cells = [md('''# Question and why it matters
Has non-highway territory growth already been measured, which mechanisms constrain occupation, and what boundary comparisons are justified? This documentary review implements the [README](README.md) and [plan](../../../notes/literature-review-plan-2026-10-15.md). The complete report contains the model table and annotated bibliography; this notebook is a reproducible compact audit, not a new numerical experiment.

## Assumptions and definitions
Full-text verification applies only to explicitly recorded sections; abstract-only and inaccessible sources cannot establish technical exponents. Displacement, range, width and accumulated local time differ. All material is a working-tree snapshot: the user did not authorize commits. **Deviation:** these newly produced `results/` inputs are uncommitted, so the normal committed-input-only notebook rule cannot yet be met. The provenance output identifies this explicitly; commit and rerun before archival sharing.

## Provenance
No simulation or fit is run and no random seed is used (fixed documentary seed recorded as 0 for deterministic tooling).'''), code('''from pathlib import Path
import hashlib, json, subprocess, random
SEED = 0
random.seed(SEED)
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "Cargo.toml").exists() and (p / "experiments").is_dir())
BASE = ROOT / "experiments/archive/2026-10-literature-review"
inputs = [BASE / "results" / name for name in ["claim_audit.json", "novelty-search-log.md", "mechanisms-search.md", "boundary-search.md"]]
print("Review date: 2026-10-15 NZDT; documentary seed:", SEED)
print("HEAD:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip())
for p in inputs:
    assert p.exists(), str(p)
    rel = p.relative_to(ROOT).as_posix()
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", rel], cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    modified = bool(subprocess.check_output(["git", "status", "--porcelain", "--", rel], cwd=ROOT, text=True).strip())
    print(rel, hashlib.sha256(p.read_bytes()).hexdigest(), "committed-clean" if tracked and not modified else "UNCOMMITTED WORKING INPUT")
'''), md('''## Data and method
Researchers recorded exact queries, versions, access limits and locators in the three search logs. The requested search-service succeeded for novelty but failed on mechanism/boundary attempts; fallback web retrieval is recorded. The producing script `scripts/build_notebook.py` extracts the claim-audit table from the report into `results/claim_audit.json`. No heavy computation, network or raw dumps are used here.

## Results'''),code('''data = json.loads(inputs[0].read_text())
print(data["kind"])
print("Report:", data["source"], data["source_sha256"])
for row in data["claims"]:
    print(row["claim"] + " -> " + row["action"])
'''),md('''The table shows which literature comparisons require manuscript wording changes. It does not establish exhaustive novelty or prove an ant asymptotic law.

## Caveats and controls
No numerical estimates were regenerated; previously failed controls remain failed. Rotor calibration does not establish equal ant estimator bias. A displacement exponent cannot substitute for area or width. Surface centring and ensemble conventions differ. Mixed wavelength results and the failed high-band prediction do not establish persistent lobes. Latest source-access status is in the report; Eq.5 in Mishra remains ambiguous and citation tracing is selective.

## What this changes / next steps
Remove the broad first-measurement assertion, retain the calibrated multicolour census and explicit horizons, and distinguish conditional cone arguments from rotor theorems. Prioritize fixed-area censor-complete transport accounting and the already registered hull checks over another broad sweep. Open questions: what sets rule-specific kappa, whether old-site increments balance on a meaningful ant cycle clock, and how persistent shape separates from local interface fluctuations. No simulations are launched by this review.''')]
for i, cell in enumerate(cells): cell['id'] = f'review-{i:02d}'
nb={'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'cells':cells}
(BASE/'notebook.ipynb').write_text(json.dumps(nb,ensure_ascii=False,indent=1)+'\n')
