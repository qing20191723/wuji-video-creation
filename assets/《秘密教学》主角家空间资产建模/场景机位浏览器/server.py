"""Loopback-only scene camera workbench. Python standard library; no AI calls."""
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlsplit, unquote
import argparse, base64, datetime, hashlib, json, math, mimetypes, os, re, secrets, struct, threading, uuid, webbrowser

APP = Path(__file__).resolve().parent
MODEL = APP.parent / '全屋模型_P4-M2_20261022' / '模型' / '秘密教学_P4-M2.glb'
REVISION = 'P4-M2'
LOCK = threading.Lock()
TOKEN = secrets.token_urlsafe(32)
SHOT_ID = re.compile(r'^shot-[0-9a-f]{12}$')
DATA = APP / '我的镜头'
MODEL_SHA = ''

def atomic(path, data):
    temp = path.with_suffix(path.suffix + '.pending')
    temp.write_bytes(data)
    os.replace(temp, path)

def json_bytes(data):
    return json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')

def shots():
    result = []
    for p in DATA.glob('shot-*.json'):
        if not SHOT_ID.fullmatch(p.stem):
            continue
        result.append(json.loads(p.read_text('utf-8')))
    return sorted(result, key=lambda s: s['updated_at'], reverse=True)

def vector(value):
    if not isinstance(value, list) or len(value) != 3 or any(type(v) not in (int, float) or not math.isfinite(v) or abs(v) > 500 for v in value):
        raise ValueError('相机坐标无效')
    return value

def validate(body):
    if body.get('revision') != REVISION or body.get('model_sha256') != MODEL_SHA:
        raise ValueError('模型版本已变化，请重新打开页面')
    sid = body.get('id') or 'shot-' + uuid.uuid4().hex[:12]
    if not isinstance(sid, str) or not SHOT_ID.fullmatch(sid):
        raise ValueError('机位编号无效')
    if body.get('aspect') not in ('9:16', '16:9', '1:1'):
        raise ValueError('画幅无效')
    cam = body['camera']
    position, target, up = vector(cam['position']), vector(cam['target']), vector(cam['up'])
    fov = cam['fov_vertical']
    if type(fov) not in (int, float) or not 25 <= fov <= 95 or sum((a-b)**2 for a,b in zip(position,target)) < .0001:
        raise ValueError('视角或目标无效')
    if up != [0, 0, 1]:
        raise ValueError('本工作台使用Z向上坐标')
    name, notes = body.get('name', ''), body.get('notes', '')
    if not isinstance(name, str) or not 1 <= len(name) <= 80 or not isinstance(notes, str) or len(notes) > 1000:
        raise ValueError('镜头名称或备注过长')
    preset_ids = {p['id']:p for p in json.loads((APP/'presets.json').read_text('utf-8'))['shots']}
    if body.get('preset_id') not in preset_ids:
        raise ValueError('预设编号不存在')
    raw = body['png']
    if not isinstance(raw, str) or not raw.startswith('data:image/png;base64,'):
        raise ValueError('需要PNG截图')
    png = base64.b64decode(raw.split(',', 1)[1], validate=True)
    if len(png) > 8_000_000 or png[:8] != b'\x89PNG\r\n\x1a\n' or png[12:16] != b'IHDR':
        raise ValueError('预览图无效')
    w,h = struct.unpack('>II', png[16:24])
    expected = {'9:16':(720,1280), '16:9':(1280,720), '1:1':(1080,1080)}[body['aspect']]
    if (w,h) != expected:
        raise ValueError('预览画幅与相机不一致')
    now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(timespec='seconds')
    old = json.loads((DATA/(sid+'.json')).read_text('utf-8')) if (DATA/(sid+'.json')).exists() else {}
    result = dict(id=sid, name=name, notes=notes, preset_id=body['preset_id'], room=preset_ids[body['preset_id']]['room'], aspect=body['aspect'], revision=REVISION, model_sha256=MODEL_SHA, created_at=old.get('created_at', now), updated_at=now, requested=bool(body.get('requested')) or old.get('requested', False), generation_status='待助手读取后生图' if body.get('requested') or old.get('requested') else '仅保存机位', camera=dict(position=position,target=target,up=up,fov_vertical=fov,near=.025,far=300,projection='perspective',coordinate_system='Blender Z-up, metres'), preview=dict(file=sid+'.png',width=w,height=h,mirrored=False), constraints=['保持P4-M2几何和家具固定关系','门牌保持正常阅读方向','品牌含hgdju.com，镜像为整组水平翻转','预览为基础材质，相机截图不能视为最终写实图','用户未发出生图指令前不自动生成'])
    return result, png

class Handler(BaseHTTPRequestHandler):
    server_version = 'SceneStudio/1.0'
    def log_message(self, *_): pass
    def send(self, status, data, ctype='application/json; charset=utf-8'):
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Cross-Origin-Resource-Policy', 'same-origin')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' blob: data:; connect-src 'self' blob:; worker-src 'self' blob:; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(data)
    def allowed(self):
        return self.headers.get('Host') == f'127.0.0.1:{self.server.server_port}'
    def do_GET(self):
        if not self.allowed(): return self.send(403,b'{}')
        path = unquote(urlsplit(self.path).path)
        if path == '/api/health': return self.send(200,json_bytes(dict(ok=True,app=str(APP),revision=REVISION)))
        if path == '/api/state':
            with LOCK: value = shots()
            return self.send(200,json_bytes(dict(revision=REVISION,model_sha256=MODEL_SHA,token=TOKEN,shots=value)))
        if path.startswith('/shots/'):
            name = path[len('/shots/'):]
            if not name.endswith('.png') or not SHOT_ID.fullmatch(name[:-4]): return self.send(404,b'{}')
            file = DATA/name
        elif path == '/model/秘密教学_P4-M2.glb': file=MODEL
        else:
            relative = path.lstrip('/') or 'index.html'
            file = (APP/relative).resolve()
            if not file.is_relative_to(APP) or not (relative in ('index.html','app.js','style.css','presets.json') or (relative.startswith('vendor/') and file.is_relative_to(APP/'vendor'))):
                return self.send(404,b'{}')
        if not file.is_file(): return self.send(404,b'{}')
        ctype = {'.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.glb':'model/gltf-binary'}.get(file.suffix, mimetypes.guess_type(file.name)[0] or 'application/octet-stream')
        return self.send(200,file.read_bytes(),ctype)
    def do_POST(self):
        expected = f'http://127.0.0.1:{self.server.server_port}'
        if not self.allowed() or self.headers.get('Origin') != expected or self.headers.get('X-Session-Token') != TOKEN:
            return self.send(403,json_bytes({'error':'请求来源不匹配，请从本地工作台保存'}))
        if self.path != '/api/shots': return self.send(404,b'{}')
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0 < length <= 12_000_000: raise ValueError('请求大小无效')
            body=json.loads(self.rfile.read(length))
            with LOCK:
                shot,png=validate(body)
                atomic(DATA/(shot['id']+'.png'),png)
                atomic(DATA/(shot['id']+'.json'),json_bytes(shot))
                current=shots()
                atomic(DATA/'待生图清单.json',json_bytes(dict(revision=REVISION,shots=[s['id'] for s in current if s['requested']],note='仅记录选择，不自动触发生图；先读取每个镜头JSON与PNG。')))
            self.send(200,json_bytes(dict(shot=shot,shots=current)))
        except (ValueError,KeyError,TypeError,IndexError) as e:
            self.send(400,json_bytes({'error':str(e)}))

def main():
    global DATA, MODEL_SHA
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8765);parser.add_argument('--no-browser',action='store_true');parser.add_argument('--data-dir',type=Path)
    args=parser.parse_args()
    if args.data_dir: DATA=args.data_dir.resolve()
    DATA.mkdir(parents=True,exist_ok=True)
    content=MODEL.read_bytes()
    if content[:4] != b'glTF': raise SystemExit('缺少GLB实体模型；不能使用Git LFS指针。')
    MODEL_SHA=hashlib.sha256(content).hexdigest()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    url=f'http://127.0.0.1:{args.port}'
    print(url,flush=True)
    if not args.no_browser: webbrowser.open(url)
    server.serve_forever()

if __name__ == '__main__': main()
