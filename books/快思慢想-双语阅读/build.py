from pathlib import Path
from zipfile import ZipFile
from bs4 import BeautifulSoup, ProcessingInstruction, Comment
import base64, json, mimetypes, posixpath, re

HERE=Path(__file__).resolve().parent
ROOT=Path('E:/Desktop/LyFiles/Books/Reference')
EN=next(p for p in ROOT.glob('Thinking*epub'))
ZH=next(p for p in ROOT.glob('快思慢想*epub'))
ez,cz=ZipFile(EN),ZipFile(ZH)
ep='OPS/xhtml/chapter001.xhtml'; cp='OEBPS/Text/ch002.xhtml'
es=BeautifulSoup(ez.read(ep),'html.parser')
cs=BeautifulSoup(cz.read(cp),'html.parser').find('section',id='故事中的人物')
ens=es.section.find_all(recursive=False)
zhs=[t for t in cs.find_all(['p','h2','h3','figure','ul','blockquote']) if not t.find_parent(['p','ul','blockquote','figure'])]
cuts=[(3,11,1,8,'Fast and slow','快与慢的初体验'),(11,18,8,15,'Meet the two systems','认识两个系统'),(18,20,15,17,'Automatic skills','自动化技能与注意力'),(20,23,17,20,'Effort and attention','需要努力的系统二'),(23,26,20,23,'The limits of attention','注意力的限度'),(26,30,23,27,'How the systems cooperate','两个系统如何合作'),(30,37,27,33,'Conflict and self-control','冲突与自我控制'),(37,43,33,38,'Seeing and believing','看见与相信'),(43,46,38,41,'Cognitive illusions','认知错觉'),(46,50,41,44,'Useful fictions','有用的拟人叙述'),(50,54,44,50,'Names, characters, and reflection','虚构角色与本章回顾')]
notes=BeautifulSoup(ez.read('OPS/xhtml/notes.xhtml'),'html.parser')

def clean(nodes,z,path):
    s=BeautifulSoup(''.join(map(str,nodes)),'html.parser')
    for t in s.find_all(string=lambda t:isinstance(t,(ProcessingInstruction,Comment))): t.extract()
    for t in s.find_all(['script','style','iframe','object']): t.decompose()
    for t in s.find_all(True):
        old=dict(t.attrs); t.attrs={}
        if t.name=='img':
            src=posixpath.normpath(posixpath.join(posixpath.dirname(path),old['src']))
            mime=mimetypes.guess_type(src)[0] or 'image/png'
            t['src']='data:'+mime+';base64,'+base64.b64encode(z.read(src)).decode()
            t['alt']=old.get('alt','原书插图'); t['loading']='lazy'
        if t.name in ['h5','h3']: t.name='h3'
        if 'strong' in old.get('class',[]): t.name='strong'
        if t.name=='a':
            href=old.get('href','')
            if href.startswith('notes.xhtml#'):
                target=notes.find(id=href.split('#')[1])
                if target:
                    tip=target if target.name in ['p','li'] else target.find_parent(['p','li']) or target.parent
                    t.name='span';t['class']='source-note';t['title']=tip.get_text(' ',strip=True)
                else: t.unwrap()
            else: t.unwrap()
    return str(s)

blocks=[]
for i,(a,b,c,d,title,zhTitle) in enumerate(cuts):
    eng=clean(ens[a:b],ez,ep); zh=clean(zhs[c:d],cz,cp)
    blocks.append(dict(id=f'ch01-b{i+1:02}',title=title,zhTitle=zhTitle,en=eng,zh=zh,words=len(re.findall(r"\b[\w’'-]+\b",BeautifulSoup(eng,'html.parser').get_text(' ',strip=True))),enRange=[a,b],zhRange=[c,d]))
# Guard against missing or duplicate source nodes when manually changing boundaries.
assert [i for a,b,*_ in cuts for i in range(a,b)]==list(range(3,len(ens)))
assert [i for _,_,c,d,*_ in cuts for i in range(c,d)]==list(range(1,len(zhs)))
book=dict(id='thinking-fast-slow-ch1-v1',title='Thinking, Fast and Slow',subtitle='快思慢想 · 第一章',author='Daniel Kahneman · 洪兰译',blocks=blocks)
payload=json.dumps(book,ensure_ascii=False).replace('</','<\\/')
page=(HERE/'template.html').read_text(encoding='utf-8').replace('/*BOOK_DATA*/',payload)
page=page.replace('</html>',(HERE/'eudic-panel.html').read_text(encoding='utf-8')+'\n</html>')
(HERE/'快思慢想-双语阅读样版.html').write_text(page,encoding='utf-8')
(HERE/'alignment.json').write_text(json.dumps([{k:v for k,v in b.items() if k not in ('en','zh')} for b in blocks],ensure_ascii=False,indent=2),encoding='utf-8')
print('Built',len(blocks),'blocks;',sum(b['words'] for b in blocks),'English words')
print('Words per block:',[b['words'] for b in blocks])
