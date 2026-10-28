"""Extract supplied Meng1994 PDF locally; copyrighted outputs stay in ignored scratch.
Run: uv run --with pypdf --with pypdfium2 --with rapidocr-onnxruntime scripts/meng_extract.py (full repo-relative path).
"""
from pathlib import Path
import hashlib,json
from pypdf import PdfReader
import pypdfium2 as pdfium
from rapidocr_onnxruntime import RapidOCR
import numpy as np
root=Path(__file__).resolve().parents[4]
work=root/'experiments/archive/2026-10-literature-review/scratch/meng1994'
source=work/'source.pdf'
r=PdfReader(source)
text='\n\f\n'.join(p.extract_text() or '' for p in r.pages)
(work/'text-layer.txt').write_text(text)
print('pages',len(r.pages),'text layer characters',len(text),flush=True)
pdf=pdfium.PdfDocument(source)
ocr=RapidOCR()
for i,page in enumerate(pdf):
    im=page.render(scale=2.5).to_pil().convert('RGB')
    im.save(work/f'page-{i+1}.png')
    arr=np.asarray(im)
    blocks=[]
    # The article is two-column. OCR each half so paragraph order is retained.
    for half in (arr[:,:arr.shape[1]//2],arr[:,arr.shape[1]//2:]):
        result,_=ocr(half)
        blocks.append('\n'.join(x[1] for x in result or []))
    (work/f'ocr-{i+1}.txt').write_text('\n\nRIGHT COLUMN\n\n'.join(blocks))
    print('finished page',i+1,flush=True)
(work/'provenance.json').write_text(json.dumps({'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'pages':len(r.pages),'render_scale':2.5,'ocr':'RapidOCR default models, two vertical half-page crops'},indent=2))
