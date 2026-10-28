from pathlib import Path
import subprocess,json,hashlib
root=Path(__file__).resolve().parents[4];exp=root/'experiments/archive/2026-10-single-cell-gates';b='/tmp/turmite-single-cell-20261022/release/examples/single_cell_gates'
recipe=json.loads((exp/'results/recipe.json').read_text());args=recipe['command'].copy();args[1]=str(exp/'scratch/thread3');args[-1]='3'
subprocess.run(args,input='\n'.join(recipe['specs'])+'\n',text=True,check=True)
files=sorted((exp/'results/raw').glob('*'))
for p in files: assert p.read_bytes()==(Path(args[1])/p.name).read_bytes(),p.name
(exp/'results/thread_check.json').write_text(json.dumps({'threads':[2,3],'files_compared':len(files),'identical':True},indent=2)+'\n')
