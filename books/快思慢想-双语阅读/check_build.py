from pathlib import Path
from bs4 import BeautifulSoup
import json, re, base64, subprocess

root=Path(__file__).resolve().parent
page=(root/'快思慢想-双语阅读样版.html').read_text(encoding='utf-8')
soup=BeautifulSoup(page,'html.parser')
script=soup.script.string
book=json.loads(script.split('const BOOK=',1)[1].split(';\nconst $=',1)[0])
assert len(book['blocks'])==11
assert len({b['id'] for b in book['blocks']})==11
ids=[t['id'] for t in soup.find_all(id=True)]
assert len(ids)==len(set(ids))
assert set(re.findall(r"\$\('([^']+)'\)",script)).issubset(ids)
for b in book['blocks']:
    assert 250<=b['words']<=600
    for lang in ['en','zh']:
        content=BeautifulSoup(b[lang],'html.parser')
        assert content.get_text(strip=True)
        assert not content.find(['script','iframe','object'])
        for img in content.find_all('img'):
            assert img['src'].startswith('data:image/')
            assert len(base64.b64decode(img['src'].split(',',1)[1]))>100
assert sum(len(BeautifulSoup(b['en'],'html.parser').find_all('img')) for b in book['blocks'])==3
assert sum(len(BeautifulSoup(b['zh'],'html.parser').find_all('img')) for b in book['blocks'])==3
# Parse actual embedded JavaScript with Node; this does not claim browser UI testing.
result=subprocess.run(['node','-e','const fs=require("fs"),vm=require("vm");const p=fs.readFileSync(process.argv[1],"utf8");for(const m of p.matchAll(/<script>([\\s\\S]*?)<\\/script>/g))new vm.Script(m[1]);console.log("All embedded JavaScript syntax OK");',str(root/'快思慢想-双语阅读样版.html')],capture_output=True,text=True)
assert result.returncode==0,result.stderr
print(result.stdout.strip())
print('PASS: 11 unique blocks, all required controls present, word lengths, 6 embedded images, no external content dependencies.')
