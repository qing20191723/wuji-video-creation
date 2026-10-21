"""Reference-led second-floor review only; never writes Blender or model source."""
from pathlib import Path
import json, copy, hashlib, shutil, html, sys
import plan_svg as g
R=Path(__file__).resolve().parents[1];O=R/'平面确认'
BASE=json.loads((O/'平面方案数据.json').read_text(encoding='utf8'))
RD=O/'走廊原始参考';RD.mkdir(exist_ok=True)
REF=Path(sys.argv[1]) if len(sys.argv)>1 else RD
previous={x['file']:x for x in json.loads((RD/'来源.json').read_text(encoding='utf8'))} if (RD/'来源.json').exists() else {}
references=[]
for name,use in [('别墅二楼走廊.png','最新用户指定回看：上平台端大窗，无辅助房门'),('二楼走廊夜景后视图.jpg','夜间回看交叉印证'),('二楼走廊夜景正视图.jpg','反向：三卧室门序、楼梯和舒亚端玻璃门'),('别墅楼梯间参考.png','由下向上：梯顶大窗、平台连接')]:
    p=REF/name
    if p.resolve()!=(RD/name).resolve():shutil.copy2(p,RD/name)
    references.append(dict(file=name,source=previous.get(name,{}).get('source',str(p)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),use=use))
(RD/'来源.json').write_text(json.dumps(references,ensure_ascii=False,indent=2),encoding='utf8')
D=copy.deepcopy(BASE);D['revision']='P2.4-F3_20261021';D['status']='二维短护栏与窗位修订；楼梯位移未批准建模'
D['rooms']=[r for r in D['rooms'] if r['level']==2 and r['id'] in ['B1','B2','B3','WT','AB','A','H2']]
for r in D['rooms']:
    if r['id']=='H2':r['box']=[.2,2.6,14.6,4.2];r['net_area']=round(14.4*1.6,2)
    if r['id']=='A':r['box']=[12.82,1.1,14.6,2.6];r['net_area']=round(1.78*1.5,2)
D['furniture']=[f for f in D['furniture'] if f['room'] in ['B1','B2','B3']]
keep=['2-N','2-B1N','2-W','2-B3S','2-B3E','2-B2S','2-B12','2-B1S','2-B1E','2-PAR','2-STB','2-STS']
D['walls']=[w for w in D['walls'] if w['id'] in keep]
D['openings']=[o for o in D['openings'] if o['wall'] in keep]
for w in D['walls']:
    if w['id']=='2-PAR':w['a']=[7.4,2.5];w['b']=[12.82,2.5];w['height']=1.1
    if w['id']=='2-STB':w['a']=[7.4,1];w['b']=[7.4,2.5];w['height']=1.1
    if w['id']=='2-STS':w['b']=[12.82,1]
D['openings']=[o for o in D['openings'] if o['wall']!='2-STS']
D['openings'] += [dict(id='W-TALL',wall='2-STS',level=2,start=5.8,end=7.1,type='window',sill=0,head=2.85,fixed=True,evidence='用户标注②/⑤：高落地窗'),dict(id='W-SLOT',wall='2-STS',level=2,start=8.4,end=11.4,type='window',sill=.75,head=1.35,fixed=True,evidence='用户标注③/④：横向窄长采光窗，保留原图玻璃，不是通道')]
# A clear glazed end at the landing, plus a tall side window. No door symbols.
D['walls'] += [dict(id='F2-END',level=2,a=[14.7,1],b=[14.7,4.3],thickness=.2),dict(id='F2-AS',level=2,a=[12.82,1],b=[14.7,1],thickness=.2)]
D['openings'] += [dict(id='W-A-END',wall='F2-END',level=2,start=1.15,end=4.1,type='window',sill=0,head=2.85,fixed=True),dict(id='W-A-SIDE',wall='F2-AS',level=2,start=13.05,end=14.35,type='window',sill=0,head=2.85,fixed=True)]
D['stairs']['footprint']=[7.5,1.1,12.82,2.4];D['stairs']['A']=[12.82,1.1,14.6,2.6];D['stairs']['B']=[5.9,1.1,7.5,2.4]
D['stairs']['status']='proposal only; old first-floor connection not updated'
D['architecture']={'status':'proposal; do not build','stair_opening_provisional':[7.4,1,12.82,2.5],'solid_floor_proposal':[.2,1.1,7.3,2.6],'guard_length':5.42,'previous_guard_length':14.92,'stairs_translation':[-3.9,0,0],'old_stairs':BASE['stairs'],'note':'护栏只覆盖梯段；舒亚侧恢复平层通行。楼梯整体向西移3.90m为本轮补充设计，会改变一楼落点；未写入一楼或三维。'}
D['unplaced_functions']=['二楼公卫','布草收纳'];D['references']=references
D['routes']=[];D['clearances']=[c for c in BASE['clearances'] if c['id']=='H-width']
D['notes']=['用户①：原14.92m长护栏取消，改为仅沿梯段的5.42m短护栏（比例试排，非测量）。','用户②/⑤：在图中X约6.45m处安排高落地窗；窗台0、窗顶2.85m均为暂定示意。','用户③/④：在图中X约9.90m处安排横向窄长采光窗，暂宽3.00m、高0.60m，窗下保留实体墙；按原图保留玻璃。','端部通道由18.40m缩至14.40m；保留已认可的卧室家具和三门坐标，不能凭单张照片宣称总门距准确。','为使短护栏、高窗及横窗与梯段对位，楼梯暂整体西移3.90m；一楼新落点需要重新校核，不能直接建模。','舒亚侧多余挑空取消，改为平层地面，不新造房间；公卫及布草仍待另行定位。','窗位来源于用户标注；开口宽高、短护栏长度、楼梯位移为本次设计试值，具体尺寸由用户校准。']
D['notes'].append('一楼冲突：拟移梯段经过原玄关通路X10.0—11.2m上方，净高尚不满足原直接通行假设；新B平台与客厅地毯L03重叠0.42㎡。一楼旧梯间墙也尚未同步。')
(O/'二楼重绘数据.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
g.OPEN=D['openings']

def sheet(title,sub,scale,offset,size):
    s=g.Sheet(title,sub,[0,0,22,11],scale,offset,size)
    s.p=[x.replace('P2.3-R2 · 2026-10-21 · 走廊空间局部校核 · 同步 P2.3-M1 白模 · 影视参考，非施工图','P2.4-F3 · 2026-10-21 · 二维关系重绘，未写入三维 · 尺寸待校准，非施工图') for x in s.p]
    return s

def hatch(s,b):
    s.rect(b,'#fbf0d9','#b69154',1,'6 5')
    x,y,X,Y=b
    for i in range(int((X-x)/.32)):
        xx=x+i*.32;s.line((xx,y),(min(xx+.65,X),min(y+.65,Y)),'#dcc798',1)

def corridor(s,full=False):
    s.rect([.2,2.6,14.6,4.2],'#e3f0e9','none')
    s.rect([.2,1.1,7.3,2.6],'#e3f0e9','none');s.rect([12.82,1.1,14.6,2.6],'#e3f0e9','none')
    s.rect([7.4,1,12.82,2.5],'#dce8ef','#66899b',1)
    for i in range(20):s.line((7.5+i*.28,1.1),(7.5+i*.28,2.4),'#849ca9',1)
    s.line((12.4,1.7),(7.7,1.7),g.TEAL,3,arrow=True)
    for w in D['walls']:
        if not full and w['id'] not in ['2-B3S','2-B2S','2-B1S','2-PAR','2-STB','2-STS','F2-END','F2-AS']:continue
        if not full and w['id']=='2-B1S':
            w=copy.deepcopy(w);w['b']=[14.7,4.3]
        g.wall_draw(s,w,False)
        if w['id'] in ['2-PAR','2-STB']:s.line(w['a'],w['b'],'#af8b62',5)
    if not full:
        west=copy.deepcopy(next(w for w in D['walls'] if w['id']=='2-W'))
        west['a']=[.1,1];west['b']=[.1,4.3];g.wall_draw(s,west,False)
    s.line((14,3.6),(1,3.6),'#3b887a',2,'7 5',True)
    s.wt(6.3,3.8,'直走廊；端部向内收短4.00m（试排）',17,anchor='middle',weight=700)
    s.wt(3.5,1.8,'平层地面 / 原多余挑空取消',16,anchor='middle',color=g.TEAL)
    s.wt(10,1.25,'A → B 下楼',14,anchor='middle')
    s.wt(13.6,1.8,'A 上平台',15,anchor='middle',weight=700)
    s.wt(13.6,1.4,'无房门',14,anchor='middle',color='#277f91')
    s.wt(10.1,2.72,'① 短护栏5.42m（原14.92m）',16,anchor='middle',color='#9b6842')
    for x,y,xx,yy,label,col in [(7.7,3.15,10.1,3.15,'回看 → 大窗','#377ca0'),(14.1,3.15,11.5,3.15,'正向 → 舒亚','#9b6842')]:
        s.circ(x,y,.09,col,'none');s.line((x,y),(xx,yy),col,2,arrow=True);s.wt(x,y-.25,label,12,anchor='middle',color=col)

s=sheet('《秘密教学》｜二楼平面重绘','以正向、回看及上楼参考交叉核对；本轮只画二维，不修改白模。',77,(180,1060),(2400,1570))
s.rect([0,0,22,10.4],'#f3f3ef','#cad1cc',1,'8 6')
for r in D['rooms']:
    if r['id'] in ['B1','B2','B3','AB','WT']:
        if r['polygon']:s.poly(r['polygon'],r['color'],'#b2beb7',1)
        else:s.rect(r['box'],r['color'],'none')
for f in sorted(D['furniture'],key=lambda f:0 if 'rug' in f['kind'] else 1):g.furniture(s,f)
corridor(s,True)
for x,y,label in [(3.3,8.8,'舒亚 / 二姐'),(9.7,8.6,'子豪'),(16.1,6.6,'薇亚 / 大姐')]:s.wt(x,y,label,22,anchor='middle',weight=700)
s.wt(20.3,6.7,'大姐阳台',17,anchor='middle');s.wt(-.75,4.8,'舒亚端露台',14,anchor='middle')
s.wt(17.4,3.6,'窗外 / 室外',17,anchor='middle',color=g.BLUE);s.wt(17.4,3.15,'原端部通道取消',16,anchor='middle',color=g.BLUE)
s.line((14.8,3.4),(16.6,3.4),g.BLUE,2,arrow=True)
s.wt(6.45,.45,'② 高落地窗',16,anchor='middle',color=g.BLUE);s.wt(9.9,.45,'③ 横向采光窗',16,anchor='middle',color=g.BLUE)
for a,b,t in [(.2,6.4,'舒亚 6.20 × 5.80m（暂用）'),(6.6,13,'子豪 6.40 × 5.80m（暂用）'),(13.2,18.6,'薇亚 5.40 × 5.00m（暂用）')]:s.dim((a,10.95),(b,10.95),t)
s.txt(2040,180,'项目北 ↑',23,weight=700)
s.notes(1930,260,[('对应你的标注',['① 护栏14.92 → 5.42m。','② 高落地窗在标注处。','③ 横向窄长采光窗。','窗下留墙，不是门洞。']),('本次试排的影响',['楼梯整体向西移3.90m。','一楼落点尚未同步。','卧室家具与房门未动。','公卫、布草未定。'])],400)
s.notes(100,1185,[('本次实际缩短',['护栏只覆盖梯段，取消左侧多余护栏及长条挑空，恢复平层地面。','上平台及端窗向内收，走廊净长暂从18.40m减至14.40m。'])],1050)
s.notes(1230,1185,[('二维试排 / 不是建模定稿',['楼梯西移3.90m是本次补充设计，一楼落点必须重新校核。','②③位置据用户标注；尺寸、窗台窗顶及楼梯位置仍为设计试值。'])],1050)
s.finish('03_二楼家具平面图')

s=sheet('《秘密教学》｜短护栏与两类采光窗','对应用户①②③标注；整体位置与二楼总图一致。几何为二维试排，三维冻结。',125,(155,850),(2400,1420))
corridor(s)
for x,name in [(.95,'舒亚の窝'),(8.5,'子豪の窝'),(13.75,'薇亚的窝')]:s.wt(x,4.65,name,22,anchor='middle',weight=700)
s.wt(16.3,3.3,'回看端头大窗',19,anchor='middle',color=g.BLUE);s.wt(16.3,2.92,'无房门',19,anchor='middle',color=g.BLUE)
s.wt(9.9,.5,'③ 横向窄长采光窗',17,anchor='middle',color=g.BLUE);s.wt(13.7,.5,'回看侧窗',17,anchor='middle',color=g.BLUE)
s.wt(6.45,.5,'② 高落地窗',17,anchor='middle',color=g.BLUE)
s.dim((7.4,5.25),(12.82,5.25),'① 护栏长度5.42m，按比例暂定')
s.notes(100,995,[('原图④与⑤是两种开口',['② / 原图⑤：竖向落地高窗，接近顶面；在短护栏收头附近。','③ / 原图④：横向窄长窗洞，保留窗台和上方墙面，沿梯段采光。'])],1050)
s.notes(1230,995,[('缩短的代价已显式标出',['取消9.50m多余护栏；走廊端部收短4.00m。','楼梯整体西移3.90m，需核对一楼，不将位移悄悄写入三维。'])],1050)
s.finish('09_二楼走廊关系放大图')

s=sheet('《秘密教学》｜窗墙立面与楼梯位移检查','从室内看南侧窗墙：横坐标与平面一致。高度为示意；高落地窗不擅自解释为跨两层。',115,(180,700),(2400,1500))
s.rect([.1,0,14.7,3.08],'#edece7',g.WALL,2)
for x,X,z,Z,label in [(5.8,7.1,0,2.85,'② 高落地窗'),(8.4,11.4,.75,1.35,'③ 横向采光窗'),(13.05,14.35,0,2.85,'回看侧窗')]:
    s.rect([x,z,X,Z],'#dbeef5',g.BLUE,4);s.rect([x+.05,z+.05,X-.05,Z-.05],'none',g.BLUE,1)
    s.wt((x+X)/2,3.45,label,21,anchor='middle',weight=700)
s.dim((5.35,0),(5.35,2.85),'高2.85m（暂定）')
s.dim((8.4,1.65),(11.4,1.65),'宽3.00m / 高0.60m（暂定）')
s.line((7.4,1.1),(12.82,1.1),'#af8b62',3,'9 6')
s.wt(10,2.25,'虚线：近侧护栏顶投影，非窗横框',17,anchor='middle',color='#9b6842')
s.wt(9.9,.35,'窗下实体墙 / 窗台暂高0.75m',16,anchor='middle')
s.wt(3,1.5,'②已移至用户标注处',19,anchor='middle');s.wt(3,1.05,'不再复制为两扇等高小窗',17,anchor='middle')
s.wt(7,-.45,'二楼完成面 ±0.00；净高暂3.08m；本页高度不是照片实测',17,anchor='middle')
s.txt(100,860,'楼梯平面位移：需同步核对一楼的影响',25,weight=700)
# Explicit plan overlay uses the same x coordinate and does not pretend first-floor alignment passed.
s.rect([11.4,-3.3,16.72,-2],'none','#a6a5a0',2,'8 5')
s.wt(14.1,-1.8,'灰虚线：一楼原梯段位置',16,anchor='middle')
s.rect([7.5,-3.3,12.82,-2],'#dce8ef',g.BLUE,2)
s.rect([10,-3.3,11.2,-2],'#f5d6d0','#aa5b4c',2,'5 4')
s.wt(8.6,-2.65,'拟移梯段',16,anchor='middle')
s.wt(10.6,-3.55,'红区：原玄关通路交叠',14,anchor='middle',color='#aa5b4c')
s.line((14.5,-3.7),(10.6,-3.7),g.ORANGE,2,arrow=True)
s.wt(12.55,-4.05,'向西位移3.90m；踏步尺寸不变；一楼尚未修改',17,anchor='middle',color=g.ORANGE)
s.notes(100,1290,[('检查结论：已发现一楼连带冲突',['红区是原玄关通路X10.0—11.2m；拟移楼梯经过其上方，不能继续假定原通路净高足够。','拟移B平台另与客厅地毯L03重叠0.42㎡。本轮只供窗位与比例核对，上下楼连接尚未通过。'])],2150)
s.finish('10_走廊窗墙立面与楼梯位移')

names=['03_二楼家具平面图','09_二楼走廊关系放大图','10_走廊窗墙立面与楼梯位移'];versions={n:hashlib.sha256((O/(n+'.svg')).read_bytes()).hexdigest()[:12] for n in names}
cards=''.join('<section><h2>'+html.escape(x['use'])+'</h2><img src="走廊原始参考/'+x['file']+'"><p>'+html.escape(x['file'])+'</p></section>' for x in references)
buttons=''.join('<button data-sheet="'+n+'">'+n[3:]+'</button>' for n in names)
doc='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P2.4 二楼平面重绘</title><style>
body{margin:0;background:#eff2ee;font:17px "Microsoft YaHei",sans-serif;color:#233d46}header{padding:24px;background:#253f49;color:white}h1{font-size:27px}p{line-height:1.8}nav,#tools{display:flex;gap:10px;flex-wrap:wrap;padding:14px 24px}a,button{padding:10px;background:white;border:1px solid #aec5be;border-radius:5px;color:#235c64;text-decoration:none;cursor:pointer}button.active{background:#3b887a;color:white}#canvas{padding:0 24px;overflow:auto}#drawing{width:100%;display:block;cursor:crosshair}#canvas.actual #drawing{width:2400px}section{margin:24px;background:white;padding:20px}section img{width:100%;display:block}#location{padding:12px 24px;background:#dcebe6}h2{font-size:21px}footer{padding:24px}</style>
<header><h1>P2.4-F3｜二楼平面重绘</h1><p>按你的①②③标注修改：短护栏、高落地窗、横向窄长采光窗；新增窗墙立面方便核对。</p><p>本轮护栏14.92→5.42m，端部通道缩短4.00m。楼梯拟西移3.90m，需核对一楼；三维未改，尺寸为暂定试值。</p></header><nav>BUTTONS</nav><div id="tools"><a id="png">高清PNG</a><a id="svg">可编辑SVG</a><button id="zoom">原尺寸 / 适应页面</button><a href="#refs">正反向原图 ↓</a><a href="二楼重绘说明.md">变更与未决项</a></div><div id="canvas"><img id="drawing" alt="二楼重绘"></div><div id="location">点击平面可取得百分比位置，也可以直接使用浏览器图片批注。</div><div id="refs">CARDS</div><footer>当前仅这三张图为二楼重绘稿。尺寸由用户校准；其余全屋图暂不作为本轮二楼连接依据。模型未改。</footer><script>
const versions=VERSIONS;let current='03_二楼家具平面图';function select(n){current=n;const v='?v='+versions[n];document.querySelector('#drawing').src=n+'.svg'+v;document.querySelector('#png').href=n+'.png'+v;document.querySelector('#svg').href=n+'.svg'+v;document.querySelectorAll('[data-sheet]').forEach(b=>b.classList.toggle('active',b.dataset.sheet===n));}document.querySelectorAll('[data-sheet]').forEach(b=>b.onclick=()=>select(b.dataset.sheet));document.querySelector('#zoom').onclick=()=>document.querySelector('#canvas').classList.toggle('actual');document.querySelector('#drawing').onclick=e=>{const b=e.target.getBoundingClientRect();document.querySelector('#location').textContent=current+'：x='+((e.clientX-b.left)/b.width*100).toFixed(1)+'%，y='+((e.clientY-b.top)/b.height*100).toFixed(1)+'%。';};select(current);</script></html>'''.replace('BUTTONS',buttons).replace('CARDS',cards).replace('VERSIONS',json.dumps(versions,ensure_ascii=False))
(O/'打开平面图.html').write_text(doc,encoding='utf8')
md='# P2.4-F3 二楼平面重绘\n\n本轮仅二维，三维冻结。\n\n'+ '\n'.join('- '+x for x in D['notes'])+'\n\n## 参考依据\n\n'+'\n'.join('- '+x['file']+'：'+x['use'] for x in references)
(O/'二楼重绘说明.md').write_text(md,encoding='utf8')
print('Three SVG sheets, review HTML and separate draft data saved; no model files modified.')
