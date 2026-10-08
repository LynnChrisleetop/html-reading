const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');
const root = path.join(__dirname, 'public');
const types = {'.html':'text/html; charset=utf-8','.css':'text/css','.js':'text/javascript','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.mp3':'audio/mpeg','.pdf':'application/pdf'};
function handler(req,res) {
  let name;
  try { name = decodeURIComponent(new URL(req.url,'http://localhost').pathname); } catch { res.writeHead(400).end(); return; }
  const file = path.resolve(root, '.' + (name === '/' ? '/index.html' : name));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.stat(file,(err,st)=>{
    if(err || !st.isFile()){res.writeHead(404).end('Not found');return;}
    const headers={'Content-Type':types[path.extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'};
    let start=0,end=st.size-1,status=200;
    if(req.headers.range){
      const m=/^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if(!m || (!m[1]&&!m[2])) {res.writeHead(416,{'Content-Range':`bytes */${st.size}`}).end();return;}
      start=m[1]?Number(m[1]):Math.max(0,st.size-Number(m[2]));
      end=m[1]&&m[2]?Math.min(Number(m[2]),st.size-1):st.size-1;
      if(start>end || start>=st.size){res.writeHead(416,{'Content-Range':`bytes */${st.size}`}).end();return;}
      status=206;headers['Content-Range']=`bytes ${start}-${end}/${st.size}`;
    }
    headers['Content-Length']=end-start+1;
    res.writeHead(status,headers);
    if(req.method==='HEAD'){res.end();return;}
    const stream=fs.createReadStream(file,{start,end});stream.on('error',()=>res.destroy());stream.pipe(res);
  });
}
if(require.main===module){const port=Number(process.env.PORT)||4173;http.createServer(handler).listen(port,'127.0.0.1',()=>console.log(`Reader: http://127.0.0.1:${port}`));}
module.exports=handler;
