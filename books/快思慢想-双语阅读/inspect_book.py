from pathlib import Path
from zipfile import ZipFile
from bs4 import BeautifulSoup
import sys
sys.stdout.reconfigure(encoding='utf-8')
root=Path('E:/Desktop/LyFiles/Books/Reference')
for f in root.glob('*Thinking*epub'):
    z=ZipFile(f)
    print('\nBOOK',f.name)
    names=['OPS/xhtml/chapter001.xhtml'] if f.name.startswith('Thinking') else [n for n in z.namelist() if '/Text/ch' in n]
    for n in names:
        s=BeautifulSoup(z.read(n),'html.parser')
        print('FILE',n)
        tags=s.find_all(['h1','h2','h3','p'])
        for i,t in enumerate(tags):
            text=t.get_text(' ',strip=True)
            if f.name.startswith('Thinking') or t.name!='p' or i<8:
                print(i,t.name,t.get('id',''),text[:230])
