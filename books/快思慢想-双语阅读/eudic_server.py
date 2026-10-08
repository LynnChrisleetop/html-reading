"""Loopback-only reader bridge, with Windows current-user DPAPI credentials."""
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
from collections import deque
import json, secrets, time, re, webbrowser, sys, ssl, socket
import credential_store

ROOT=Path(__file__).resolve().parent
HOST='127.0.0.1'; PORT=18746
ORIGIN=f'http://{HOST}:{PORT}'
CSRF=secrets.token_urlsafe(32)
AUTH=''; TARGET=None; CATEGORIES=[]; CALLS=deque()

class APIError(Exception): pass
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): return None

def remote(method,path,body=None,auth=None):
    now=time.monotonic()
    while CALLS and CALLS[0]<now-1800: CALLS.popleft()
    if sum(t>now-60 for t in CALLS)>=25 or len(CALLS)>=450:
        raise APIError('请求较多，请稍后再试。未自动重试，以免触发欧路限流。')
    CALLS.append(now)
    req=Request('https://api.frdic.com/api/open/v1/studylist/'+path,
        data=json.dumps(body).encode() if body is not None else None,
        method=method,headers={'Authorization':auth or AUTH,'Content-Type':'application/json','User-Agent':'SlowReadingLocal/1.0'})
    try:
        with build_opener(NoRedirect()).open(req,timeout=20) as res:
            if res.status != (201 if method=='POST' else 200):
                raise APIError('欧路未返回文档约定的成功状态，请在词典中核对操作结果。')
            return json.loads(res.read(2_000_000))
    except HTTPError as e:
        messages={401:'授权无效或已过期，请重新连接。',403:'欧路拒绝了请求，可能触发限流，请稍后再试。',429:'欧路请求限流，请稍后再试。'}
        raise APIError(messages.get(e.code,f'欧路返回 HTTP {e.code}，请核对授权和生词本。')) from None
    except (URLError,TimeoutError,OSError) as e:
        reason=e.reason if isinstance(e,URLError) else e
        if isinstance(reason,ssl.SSLError): detail='HTTPS 证书或加密连接失败，请检查系统时间、代理或证书配置。'
        elif isinstance(reason,socket.gaierror): detail='无法解析欧路域名，请检查网络或 DNS。'
        elif isinstance(reason,(TimeoutError,socket.timeout)): detail='连接欧路超时，请检查网络或代理后重试。'
        else: detail='连接欧路失败（'+type(reason).__name__+'），请检查网络或代理后重试。'
        if method=='POST':detail+=' 未确认写入结果；操作可能已生效，请先检查生词本，重复词会去重。'
        else:detail+=' 此次是读取请求，没有添加单词。'
        raise APIError(detail) from None
    except (ValueError,TypeError): raise APIError('欧路响应格式无法识别。') from None

def categories(auth):
    result=remote('GET','category?language=en',auth=auth)
    data=result.get('data')
    if not isinstance(data,list): raise APIError('未能读取生词本列表，请检查授权信息。')
    return [{'id':str(c['id']),'name':str(c['name'])} for c in data if isinstance(c,dict) and 'id' in c and 'name' in c]

def dispatch(path,data):
    global AUTH,TARGET,CATEGORIES
    if path=='/api/connect':
        token=str(data.get('token','')).strip()
        if not token or len(token)>4096 or '\n' in token or '\r' in token: raise APIError('请粘贴完整的欧路 API 授权信息。')
        cs=categories(token)
        AUTH=token;TARGET=None;CATEGORIES=cs
        credential_store.save(AUTH,TARGET)
        return {'categories':cs,'connected':True}
    if path=='/api/disconnect':
        AUTH='';TARGET=None;CATEGORIES=[]
        credential_store.forget()
        return {'connected':False}
    if not AUTH: raise APIError('请先连接欧路账号。')
    if path=='/api/target':
        ident=str(data.get('id',''))
        match=next((c for c in CATEGORIES if c['id']==ident),None)
        if not match: raise APIError('请选择列表中的生词本。')
        TARGET=match
        credential_store.save(AUTH,TARGET)
        return {'target':TARGET}
    if path=='/api/create':
        name=str(data.get('name','')).strip()
        if not name or len(name)>80: raise APIError('生词本名称需要 1～80 个字符。')
        CATEGORIES=categories(AUTH)
        existing=[c for c in CATEGORIES if c['name']==name]
        if len(existing)>1: raise APIError('有多个同名生词本，请从已有列表选择。')
        if existing: TARGET=existing[0]
        else:
            result=remote('POST','category',{'language':'en','name':name})
            obj=result.get('data')
            if not isinstance(obj,dict) or not obj.get('id'): raise APIError('欧路未确认新生词本 ID，请重新连接后检查列表。')
            TARGET={'id':str(obj['id']),'name':str(obj.get('name',name))}
            CATEGORIES.append(TARGET)
        credential_store.save(AUTH,TARGET)
        return {'target':TARGET,'categories':CATEGORIES}
    if path=='/api/collect':
        if not TARGET: raise APIError('请先选择或创建专用生词本。')
        word=str(data.get('word','')).strip().replace('’',"'")
        if not re.fullmatch(r"[A-Za-z]+(?:[' -][A-Za-z]+){0,5}",word) or len(word)>80:
            raise APIError('请选择一个英文单词或简短词组。')
        result=remote('POST','words',{'language':'en','category_id':TARGET['id'],'words':[word]})
        # Only a successful HTTP response reaches this point; failures never masquerade as saved.
        return {'word':word,'target':TARGET,'message':str(result.get('message','欧路已确认添加请求'))}
    raise APIError('未知操作。')

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass
    def valid_host(self): return self.headers.get('Host')==f'{HOST}:{PORT}'
    def send(self,code,body,ctype='application/json; charset=utf-8'):
        if not isinstance(body,bytes): body=json.dumps(body,ensure_ascii=False).encode('utf-8')
        self.send_response(code);self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(body)));self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','no-referrer')
        self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'")
        self.end_headers();self.wfile.write(body)
    def do_GET(self):
        if not self.valid_host(): self.send(403,{'error':'Host rejected'});return
        if self.path=='/': self.send(200,(ROOT/'快思慢想-双语阅读样版.html').read_bytes(),'text/html; charset=utf-8')
        elif self.path=='/api/status': self.send(200,{'csrf':CSRF,'connected':bool(AUTH),'target':TARGET,'categories':CATEGORIES})
        else:self.send(404,{'error':'Not found'})
    def do_POST(self):
        if not self.valid_host() or self.headers.get('Origin')!=ORIGIN or not secrets.compare_digest(self.headers.get('X-Reader-Key',''),CSRF):
            self.send(403,{'error':'请从本机阅读器页面操作。'});return
        if self.headers.get('Content-Type','').split(';')[0]!='application/json':self.send(400,{'error':'Expected JSON'});return
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<16000: raise APIError('请求大小不正确。')
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict):raise APIError('请求格式不正确。')
            self.send(200,dispatch(self.path,data))
        except APIError as e:self.send(400,{'error':str(e)})
        except (ValueError,KeyError,TypeError):self.send(400,{'error':'请求或响应格式不正确。'})

if __name__=='__main__':
    try:
        saved=credential_store.load()
        if saved.get('token'):
            CATEGORIES=categories(saved['token']);AUTH=saved['token']
            wanted=saved.get('target') or {}
            TARGET=next((c for c in CATEGORIES if c['id']==wanted.get('id')),None)
    except Exception:
        print('Saved authorization could not be verified. Reconnect in reader settings; saved credential is retained.')
    try: server=HTTPServer((HOST,PORT),Handler)
    except OSError:
        print('Port 18746 is in use. Open http://127.0.0.1:18746 if the reader is already running.');sys.exit(1)
    print('Reader: '+ORIGIN+'\nClose this window or press Ctrl+C to stop. Authorization is encrypted for the current Windows user.')
    if '--no-browser' not in sys.argv: webbrowser.open(ORIGIN)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:AUTH='';server.server_close()
