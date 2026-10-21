"""Validate and publish only the current corridor review, not whole-house approval."""
from pathlib import Path
import json, hashlib, sys, math
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1];O=R/'白模当前'
P=json.loads((R/'平面确认/平面方案数据.json').read_text(encoding='utf8'))
M=json.loads((O/'模型/空间数据.json').read_text(encoding='utf8'))
before=json.loads(Path(sys.argv[1]).read_text(encoding='utf8'))
checks=[]
def check(name,passed,detail=''):
    checks.append(dict(name=name,passed=bool(passed),detail=detail))
def area_intersection(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
def same(key,pred):return [x for x in before[key] if pred(x)]==[x for x in P[key] if pred(x)]
check('四卧室家具占地、朝向与编号不变',same('furniture',lambda x:x['room'] in ['B1','B2','B3','MB']))
check('三卧室房门位置不变',same('openings',lambda x:x['id'] in ['D203','D204','D205']))
check('三卧室室内边界不变',same('rooms',lambda x:x['id'] in ['B1','B2','B3']))
check('楼梯踏步、上下口不变',P['stairs']==before['stairs'])
check('车库与花园数据不变',P['site']==before['site'] and P['garden']==before['garden'])
check('平面与模型来源一致',M['source_sha256']==hashlib.sha256((R/'平面确认/平面方案数据.json').read_bytes()).hexdigest())
check('旧走廊侧高墙确实不存在',not any(w['id']=='2-HS' for w in P['walls']) and not any(o['source']=='2-HS' for o in M['objects']))
v=P['architecture']['void']
check('延长挑空中没有二楼楼板',all(area_intersection(v,b)<1e-8 for b in P['architecture']['floor2_rects']))
guards=[o for o in M['objects'] if o['source']=='2-PAR']
check('沿走廊护栏实际高度1.16m',abs(max(o['box'][5] for o in guards)-3.3-1.16)<1e-5)
check('护栏从舒亚端平台连续到A平台',abs(min(o['box'][0] for o in guards)-v[0])<1e-5 and abs(max(o['box'][3] for o in guards)-v[2])<1e-5)
rooms={r['id']:r for r in P['rooms']}
check('公卫、布草不占露台或挑空',all(area_intersection(rooms[a]['box'],rooms[b]['box'])<1e-8 for a,b in [('WB','AB'),('LC','AB'),('WB','LC')]) and all(area_intersection(rooms[a]['box'],v)<1e-8 for a in ['WB','LC']))
# Door sweeps sampled against named furniture in the destination rooms.
for oid,rid in [('D207','WB'),('D208','LC')]:
    op=next(o for o in P['openings'] if o['id']==oid);w=next(w for w in P['walls'] if w['id']==op['wall'])
    hits=[]
    for i in range(91):
        a=math.radians(i)
        for j in range(21):
            length=(op['end']-op['start']-.09)*j/20
            x=w['a'][0]+math.sin(a)*length;y=op['start']+.045+math.cos(a)*length
            for f in P['furniture']:
                b=f['box']
                if f['room']==rid and b[0]-.025<x<b[2]+.025 and b[1]-.025<y<b[3]+.025:hits.append(f['id'])
    check(oid+'门扇开启不碰固定家具',not hits,','.join(sorted(set(hits))))
cams=['H2_REFERENCE','H2_END_W','H2_END_E','H2_MID_W','H2_VOID_CHECK','H2_PLAN','STAIR_UP','STAIR_DOWN']
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',27)
small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
titles=['上平台看舒亚端：楼梯在左、卧室在右','走廊东端向西：连续矮护栏','舒亚端回看上平台','中段看舒亚端平台','室内高位看护栏与挑空','二楼顶视检查：隐藏屋顶，墙体未截矮','B端看上楼及A平台','A端看下楼及B平台']
manifest=[]
for cid,title in zip(cams,titles):
    c=next(c for c in M['cameras'] if c['id']==cid);kind='方位检查' if c['kind']=='顶视检查' else '白模视角'
    p=O/'空间'/c['room']/kind/(cid+'.png')
    im=Image.open(p).convert('RGB');check(cid+'图像可读取',im.size==(1920,1080))
    out=Image.new('RGB',(1920,1176),'#edf1f1');out.paste(im,(0,96));d=ImageDraw.Draw(out)
    d.text((28,12),'P2.3-M1-R2  |  '+cid+'  |  '+title,font=font,fill='#233d46')
    d.text((28,52),'机位 '+str(c['pos'])+' m  →  '+str(c['target'])+'  |  '+('顶视检查；不作为真实摄影图' if kind=='方位检查' else '完整墙高；无剖切；'+str(c['lens'])+'mm'),font=small,fill='#485f65')
    if cid=='H2_PLAN':
        for x,y,label in [(2.8,9.7,'舒亚'),(9.1,9.7,'子豪'),(16,9.1,'薇亚'),(7.6,3.5,'连续直走廊'),(5.1,1.7,'新增挑空 / 下方客厅'),(13.7,1.7,'原梯段'),(17.4,2,'A上平台'),(20.1,.9,'公卫'),(20.6,3.4,'布草')]:
            px=(x+2)*76.8;py=(11.53125-y)*76.8+96;b=d.textbbox((px,py),label,font=small)
            d.rectangle((b[0]-6,b[1]-4,b[2]+6,b[3]+4),fill='#edf1f1');d.text((px,py),label,font=small,fill='#234b56')
    q=O/'空间'/c['room']/'方位检查'/(cid+'_标注.png');q.parent.mkdir(parents=True,exist_ok=True);out.save(q)
    manifest.append(dict(id=cid,title=title,file=p.relative_to(O).as_posix(),annotated=q.relative_to(O).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),size=list(im.size)))
report=dict(revision=M['revision'],checks=checks,passed=all(c['passed'] for c in checks),current_images=manifest,limitations=['连续挑空14.92m长，大于5.32m实际梯段；系保持卧室间距的补充设计，不是从照片测出的尺寸。','下方一楼公共区出现额外挑空；承重梁、楼板支承及声学未设计。','公卫、布草后移占用部分原东南露台；外立面与排水尚待核对。','局部机位已视检；全屋覆盖、人物碰撞与连续漫游未验收。','旧批次图片不在当前对照入口展示，备份验证后再回收。'])
(O/'检查记录/走廊空间复核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
cards=''.join('<section><h2>'+x['title']+'</h2><img class="markable" src="'+x['annotated']+'?v='+x['sha256'][:12]+'" alt="'+x['id']+'"><p><a href="'+x['file']+'">干净 PNG</a> · <a href="'+x['annotated']+'">标注 PNG</a></p></section>' for x in manifest)
doc='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>走廊 R2 原图与白模对照</title><style>
body{margin:0;background:#edf1f1;color:#233d46;font:17px "Microsoft YaHei",sans-serif}header,main{max-width:1440px;margin:auto;padding:24px}h1{font-size:27px}h2{font-size:21px}p,li{line-height:1.8}section{background:white;margin:22px 0;padding:18px}img{display:block;width:100%;height:auto}a{color:#176d75}button{padding:10px;margin:5px}#mark{position:fixed;right:14px;bottom:14px;background:#fff;padding:12px;border:2px solid #3a787d;max-width:320px;z-index:5}.markable{cursor:crosshair}#pin{position:absolute;border:4px solid #e54033;border-radius:50%;width:30px;height:30px;pointer-events:none;display:none;z-index:4}</style>
<header><h1>走廊 R2：撤除高墙，恢复连续矮护栏</h1><p>三卧室内部、门位和楼梯上下口保持不变；公卫与布草移至上平台后侧。此页仅展示本次重新渲染的8个机位。</p><p><a href="查看白模.html?rev=corridor-r2&cam=H2_REFERENCE">打开可旋转白模</a> · <a href="../平面确认/打开平面图.html?rev=corridor-r2">平面图</a></p><p>点击任意检查图，可得到机位编号与百分比位置；也可直接使用浏览器图片批注。</p></header><main><section><h2>用户参考原图</h2><img src="空间/H2/原始参考/二楼走廊夜景正视图.jpg"><p>右侧近至远：薇亚、子豪、舒亚；左侧为楼梯和矮护栏，采光窗在对侧外墙。</p></section>CARDS<section><h2>这次仍需注意的差异</h2><ul>LIMITS</ul></section></main><div id="pin"></div><div id="mark">点击检查图定位；结果显示在这里。</div><script>
document.querySelectorAll('.markable').forEach(im=>im.addEventListener('click',e=>{const b=im.getBoundingClientRect(),x=(e.clientX-b.left)/b.width*100,y=(e.clientY-b.top)/b.height*100;document.querySelector('#mark').textContent='机位 '+im.alt+'；图上位置 x='+x.toFixed(1)+'%，y='+y.toFixed(1)+'%。可复制此文字说明问题。';const p=document.querySelector('#pin');p.style.display='block';p.style.left=(e.pageX-19)+'px';p.style.top=(e.pageY-19)+'px';}));</script></html>'''.replace('CARDS',cards).replace('LIMITS',''.join('<li>'+x+'</li>' for x in report['limitations']))
(O/'走廊修订对照.html').write_text(doc,encoding='utf8')
print(json.dumps({'passed':report['passed'],'checks':len(checks),'images':len(manifest)},ensure_ascii=False))
if not report['passed']:raise SystemExit(1)
