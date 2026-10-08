import sys,json,shutil,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if (ROOT/'.deps').exists():sys.path.insert(0,str(ROOT/'.deps'))
import pymupdf
source=next(ROOT.parent.glob('*3 Student*.pdf'))
(ROOT/'public/pages').mkdir(parents=True,exist_ok=True)
(ROOT/'public/audio').mkdir(parents=True,exist_ok=True)
manifest=ROOT/'public/book.json'
old=json.loads(manifest.read_text(encoding='utf-8-sig')) if manifest.exists() else {}
doc=pymupdf.open(source)
shutil.copy2(source,ROOT/'public/book.pdf')
pages=[]
for i,p in enumerate(doc):
 dest=ROOT/f'public/pages/{i+1:03}.jpg'
 p.get_pixmap(matrix=pymupdf.Matrix(2,2)).save(str(dest),jpg_quality=88)
 prior=next((x for x in old.get('pages',[]) if x['page']==i+1),{})
 pages.append({'page':i+1,'image':f'pages/{i+1:03}.jpg','width':p.rect.width,'height':p.rect.height,'hotspots':prior.get('hotspots',[])})
tracks={}
for folder in sorted(ROOT.parent.glob('oxford-phonics-world-level3-disc*')):
 for f in folder.glob('*.mp3'):
  m=re.search(r'Disc(\d)_Track(\d+)',f.name,re.I)
  if m:
   disc,track=map(int,m.groups());key=f'{disc}-{track:02}'
   if key not in tracks:shutil.copy2(f,ROOT/f'public/audio/{key}.mp3')
   tracks[key]=f'audio/{key}.mp3'
manifest.write_text(json.dumps({'title':'Oxford Phonics World 3','pages':pages,'tracks':tracks},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Imported {len(pages)} pages and {len(tracks)} tracks. Existing hotspots preserved.')
