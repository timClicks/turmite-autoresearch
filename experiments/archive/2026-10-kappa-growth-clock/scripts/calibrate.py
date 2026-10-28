"""Run only synthetic calibration, before loading ant outcomes."""
import json
from pathlib import Path
from analyse import calibration

out=calibration()
(Path(__file__).resolve().parents[1]/'results/calibration.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
