from pathlib import Path
import subprocess, json, hashlib
from PIL import Image, ImageOps, ImageDraw
import pypdfium2 as pdfium
root=Path(__file__).resolve().parents[4]
base=root/'experiments/archive/2026-10-literature-review'
out=base/'scratch/review-pages';out.mkdir(parents=True,exist_ok=True)
pdf=pdfium.PdfDocument(root/'research-outputs/cube-root-growth-paper/main.pdf')
indices=[]
for i in range(len(pdf)):
    text=pdf[i].get_textpage().get_text_range()
    if i==0 or any(x in text for x in ['Introduction','Width against radius','Conclusion','References']): indices.append(i)
images=[]
for i in indices:
    im=pdf[i].render(scale=0.9).to_pil().convert('RGB')
    im.thumbnail((430,610))
    tile=Image.new('RGB',(450,640),'#dddddd');tile.paste(im,((450-im.width)//2,20));ImageDraw.Draw(tile).text((15,620),f'Page {i+1}',fill='black');images.append(tile)
sheet=Image.new('RGB',(450*3,640*((len(images)+2)//3)),'white')
for j,im in enumerate(images):sheet.paste(im,((j%3)*450,(j//3)*640))
sheet.save(out/'contact.png')
files=[root/'research-outputs/cube-root-growth-paper/main.typ',root/'research-outputs/cube-root-growth-paper/refs.bib',root/'research-outputs/cube-root-growth-paper/main.pdf',base/'reports/Cube root growth literature.md',base/'notebook.ipynb',base/'results/claim_audit.json']
manifest={'review_date':'2026-10-15 NZDT','base_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'status':'uncommitted working-tree outputs, no commit authorized','pdf_pages':len(pdf),'rendered_pages':[i+1 for i in indices],'files':{p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},'verification':{'notebook':'nbconvert clean-kernel execution succeeded','typst':'compiled without diagnostics','simulations':'none','rust_release_tests':'not rerun for documentary/editorial change; no simulator or estimator modifications'}}
(base/'results/verification.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'pages':len(pdf),'rendered':[i+1 for i in indices]}))
