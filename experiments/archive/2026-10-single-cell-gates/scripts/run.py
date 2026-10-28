from pathlib import Path
import subprocess,hashlib,json,os,datetime
root=Path(__file__).resolve().parents[4]
exp=root/'experiments/archive/2026-10-single-cell-gates'
os.chdir(root)
env=os.environ.copy();env['CARGO_TARGET_DIR']='/tmp/turmite-single-cell-20261022';env['PROPTEST_RNG_SEED']='20261019'
subprocess.run(['cargo','test','--release','--locked','--example','single_cell_gates'],env=env,check=True)
subprocess.run(['cargo','build','--release','--locked','--example','single_cell_gates'],env=env,check=True)
binary=Path(env['CARGO_TARGET_DIR'])/'release/examples/single_cell_gates'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rules=['RLLLLRLLRLRL','RLLLRRLRLL','RLLRRLLLLLLL']
specs=[f'{r}@{s}' for r in rules for s in range(202610208001,202610208005)]+['rotor:301','rotor:302','rw:301','rw:302']
(exp/'results/specs.txt').write_text('\n'.join(specs)+'\n')
args=[str(binary),str(exp/'results/raw'),'1048576','4096','12','64','1','0','32768,131072',sha(binary),'2']
recipe={'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'binary_sha256':sha(binary),'command':args,'specs':specs,'source_sha256':sha(root/'examples/single_cell_gates.rs')}
(exp/'results/recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
with (exp/'results/run.log').open('a') as log:
 subprocess.run(args,input='\n'.join(specs)+'\n',text=True,stderr=log,stdout=log,env=env,check=True)
recipe['output_sha256']={p.name:sha(p) for p in sorted((exp/'results/raw').glob('*'))}
(exp/'results/recipe.json').write_text(json.dumps(recipe,indent=2)+'\n')
