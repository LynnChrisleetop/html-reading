const test=require('node:test');const assert=require('node:assert/strict');const http=require('node:http');const fs=require('node:fs');const path=require('node:path');const handler=require('../server');
const book=JSON.parse(fs.readFileSync(path.join(__dirname,'../public/book.json'),'utf8').replace(/^\uFEFF/,''));
test('all book pages, audio targets and normalized hotspots are valid',()=>{
 assert.equal(book.pages.length,105);let count=0;
 for(const p of book.pages){assert.ok(fs.existsSync(path.join(__dirname,'../public',p.image)));for(const h of p.hotspots){count++;assert.ok(h.x>=0&&h.y>=0&&h.w>0&&h.h>0&&h.x+h.w<=1&&h.y+h.h<=1);const key=`${h.disc}-${String(h.track).padStart(2,'0')}`;assert.ok(book.tracks[key],key);}}
 assert.equal(count,133); assert.equal(Object.keys(book.tracks).length,136); const mapped=new Set(book.pages.flatMap(p=>p.hotspots.map(h=>`${h.disc}-${h.track}`))); for(let t=3;t<=68;t++)assert.ok(mapped.has(`1-${t}`));for(let t=2;t<=68;t++)assert.ok(mapped.has(`2-${t}`));for(const src of Object.values(book.tracks))assert.ok(fs.existsSync(path.join(__dirname,'../public',src)));
});
test('audio seeking serves byte ranges and rejects invalid ranges',async()=>{
 const s=http.createServer(handler);await new Promise(r=>s.listen(0,'127.0.0.1',r));const base=`http://127.0.0.1:${s.address().port}`;
 try{let r=await fetch(base+'/audio/1-03.mp3',{headers:{Range:'bytes=100-199'}});assert.equal(r.status,206);assert.match(r.headers.get('content-range'),/^bytes 100-199\//);assert.equal((await r.arrayBuffer()).byteLength,100);
 r=await fetch(base+'/audio/1-03.mp3',{headers:{Range:'bytes=999999999-'}});assert.equal(r.status,416);await r.text();
 r=await fetch(base+'/audio/1-03.mp3',{headers:{Range:'bytes=-64'}});assert.equal(r.status,206);assert.equal((await r.arrayBuffer()).byteLength,64);
 r=await fetch(base+'/book.json');assert.equal(r.status,200);await r.text();
 r=await fetch(base+'/%2e%2e%5cpackage.json');assert.equal(r.status,403);await r.text();
 }finally{s.closeAllConnections();await new Promise(r=>s.close(r));}
});

