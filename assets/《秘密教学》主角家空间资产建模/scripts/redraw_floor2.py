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
D=copy.deepcopy(BASE);D['revision']='P2.4-F2_20261021';D['status']='仅二楼关系重绘；未批准建模；楼板和辅助空间待解'
D['rooms']=[r for r in D['rooms'] if r['level']==2 and r['id'] in ['B1','B2','B3','WT','AB','A','H2']]
for r in D['rooms']:
    if r['id']=='H2':r['box']=[.2,2.6,18.6,4.2];r['net_area']=round(18.4*1.6,2)
    if r['id']=='A':r['box']=[16.72,1.1,18.6,2.6];r['net_area']=round(1.88*1.5,2)
D['furniture']=[f for f in D['furniture'] if f['room'] in ['B1','B2','B3']]
keep=['2-N','2-B1N','2-W','2-B3S','2-B3E','2-B2S','2-B12','2-B1S','2-B1E','2-PAR','2-STB','2-STS']
D['walls']=[w for w in D['walls'] if w['id'] in keep]
D['openings']=[o for o in D['openings'] if o['wall'] in keep]
# A clear glazed end at the landing, plus a tall side window. No door symbols.
D['walls'] += [dict(id='F2-END',level=2,a=[18.7,1],b=[18.7,4.3],thickness=.2),dict(id='F2-AS',level=2,a=[16.72,1],b=[18.7,1],thickness=.2)]
D['openings'] += [dict(id='W-A-END',wall='F2-END',level=2,start=1.15,end=4.1,type='window',sill=.1,head=2.8,fixed=True),dict(id='W-A-SIDE',wall='F2-AS',level=2,start=16.95,end=18.35,type='window',sill=.1,head=2.8,fixed=True)]
D['architecture']={'status':'unresolved; do not build','stair_opening_provisional':[11.3,1,16.72,2.5],'unresolved_floor_band':[1.8,1,11.3,2.5],'note':'撤销R2整段14.92m挑空的定案；栏外西段楼板关系尚未确定。护栏连续关系来自原图，长度沿用旧房间坐标仅用于揭示冲突。'}
D['unplaced_functions']=['二楼公卫','布草收纳'];D['references']=references
D['routes']=[];D['clearances']=[c for c in BASE['clearances'] if c['id']=='H-width']
D['notes']=['卧室内部与三门原坐标暂保留；这是用户已认可部分，不代表门距已由照片测准。','A平台向东临时延至18.60m，与卧室东立面平齐；原终点18.32m，差0.28m。','平台端必须为外窗；其外侧不能再排公卫、布草或封闭房间。','未定位辅助功能不等于取消功能；本稿不是完整闭合的可建模平面。','回看图在子豪门附近取景，不能据此要求同框出现舒亚门。','较早俯拍参考出现端头木门、另图玻璃后有楼梯，与本次指定回看图不一致，不叠加其门洞或额外楼梯。']
(O/'二楼重绘数据.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
g.OPEN=D['openings']

def sheet(title,sub,scale,offset,size):
    s=g.Sheet(title,sub,[0,0,22,11],scale,offset,size)
    s.p=[x.replace('P2.3-R2 · 2026-10-21 · 走廊空间局部校核 · 同步 P2.3-M1 白模 · 影视参考，非施工图','P2.4-F2 · 2026-10-21 · 二维关系重绘，未写入三维 · 尺寸待校准，非施工图') for x in s.p]
    return s

def hatch(s,b):
    s.rect(b,'#fbf0d9','#b69154',1,'6 5')
    x,y,X,Y=b
    for i in range(int((X-x)/.32)):
        xx=x+i*.32;s.line((xx,y),(min(xx+.65,X),min(y+.65,Y)),'#dcc798',1)

def corridor(s,full=False):
    s.rect([.2,2.6,18.6,4.2],'#e3f0e9','none')
    s.rect([.2,1.1,1.7,2.6],'#e3f0e9','none');s.rect([16.72,1.1,18.6,2.6],'#e3f0e9','none')
    hatch(s,[1.8,1,11.3,2.5]);s.rect([11.3,1,16.72,2.5],'#dce8ef','#66899b',1)
    for i in range(20):s.line((11.4+i*.28,1.1),(11.4+i*.28,2.4),'#849ca9',1)
    s.line((16.4,1.7),(11.7,1.7),g.TEAL,3,arrow=True)
    for w in D['walls']:
        if not full and w['id'] not in ['2-B3S','2-B2S','2-B1S','2-PAR','2-STB','2-STS','F2-END','F2-AS']:continue
        g.wall_draw(s,w,False)
        if w['id'] in ['2-PAR','2-STB']:s.line(w['a'],w['b'],'#af8b62',5)
    if not full:
        west=copy.deepcopy(next(w for w in D['walls'] if w['id']=='2-W'))
        west['a']=[.1,1];west['b']=[.1,4.3]
        g.wall_draw(s,west,False)
    s.line((16.8,3.6),(1,3.6),'#3b887a',2,'7 5',True)
    s.wt(7.5,3.8,'直走廊 / 不插入横墙或辅助房门',17,anchor='middle',weight=700)
    s.wt(6.5,1.6,'栏外楼板待核对，不默认整段挑空',16,anchor='middle',color='#97722c')
    s.wt(14,1.25,'A → B 下楼（旧梯段暂留）',14,anchor='middle')
    s.wt(17.6,1.8,'A 上平台',15,anchor='middle',weight=700)
    s.wt(17.6,1.4,'无房门',14,anchor='middle',color='#277f91')
    # Evidence-linked viewing directions; the latest reverse camera is near Zihao.
    for x,y,xx,yy,label,col in [(7.7,3.15,11.5,3.15,'② 回看 → 大窗','#377ca0'),(17.5,2.9,14.4,2.9,'① 正向 → 舒亚','#9b6842')]:
        s.circ(x,y,.11,col,'none');s.line((x,y),(xx,yy),col,2.2,arrow=True);s.wt(x,y-.28,label,14,anchor='middle',color=col)

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
s.wt(20.4,3.6,'窗外 / 室外',17,anchor='middle',color=g.BLUE);s.wt(20.4,3.15,'不放公卫、布草',16,anchor='middle',color=g.BLUE)
s.line((18.8,3.4),(20.1,3.4),g.BLUE,2,arrow=True)
s.wt(9,.25,'临街阳台与外轮廓沿用虚线投影；公共出入口尚未重新确定',16,anchor='middle',color='#76877c')
for a,b,t in [(.2,6.4,'舒亚 6.20 × 5.80m（暂用）'),(6.6,13,'子豪 6.40 × 5.80m（暂用）'),(13.2,18.6,'薇亚 5.40 × 5.00m（暂用）')]:s.dim((a,10.95),(b,10.95),t)
s.txt(2040,180,'项目北 ↑',23,weight=700)
s.notes(1930,260,[('本次纠正',['尽头落地大窗，无公卫门。','侧面高窗＋横向窗。','卧室仍为连续三门。','楼梯靠护栏，不增横墙。']),('未强行补齐',['公卫、布草暂不落位。','整段挑空不再视为定案。','A平台向东延0.28m待核。','完整楼板接法仍需闭合。'])],400)
s.notes(100,1185,[('颜色与线型',['绿色：通行区域；蓝灰：暂沿用的真实梯段；棕色：参考图中的矮护栏关系。','浅黄斜线：尚未确定的楼板范围；虚线：未重新确认的外围关系，不是新建房间。'])],1050)
s.notes(1230,1185,[('为什么这次先停在二维',['旧三门跨度与5.32m梯段存在尺度冲突，不能靠加长挑空掩盖。','当前图保留卧室内部并把冲突画出；未解决部分不下发三维。'])],1050)
s.finish('03_二楼家具平面图')

s=sheet('《秘密教学》｜走廊—楼梯关系放大','房门、外窗、护栏分开表达；图中米数沿用旧平面以便定位，不能当作照片实测。',104,(155,850),(2400,1420))
corridor(s)
for x,name in [(.95,'舒亚の窝'),(8.5,'子豪の窝'),(13.75,'薇亚的窝')]:s.wt(x,4.65,name,22,anchor='middle',weight=700)
s.wt(19.9,3.3,'大面积落地窗',19,anchor='middle',color=g.BLUE);s.wt(19.9,2.92,'不是房门',19,anchor='middle',color=g.BLUE)
s.wt(13.8,.5,'横向低窗',17,anchor='middle',color=g.BLUE);s.wt(17.6,.5,'侧面高窗',17,anchor='middle',color=g.BLUE)
s.wt(3.05,.5,'外墙高窗',17,anchor='middle',color=g.BLUE)
s.dim((8,4.95),(9,4.95),'子豪门位暂沿用');s.dim((13.3,4.95),(14.2,4.95),'大姐门位暂沿用')
s.notes(100,995,[('正向看舒亚端：参考①',['右侧近到远为薇亚、子豪、舒亚；左侧为楼梯和矮护栏。','舒亚端玻璃门沿用前次确认；早期资料中相互矛盾的端门不叠加。'])],1050)
s.notes(1230,995,[('从子豪附近回看：参考②',['左侧近处子豪、远处薇亚；舒亚在镜头后，不必挤入画面。','尽头是落地大窗；右侧外墙为高窗及横向窗，没有公卫、布草门。'])],1050)
s.finish('09_二楼走廊关系放大图')

names=['03_二楼家具平面图','09_二楼走廊关系放大图'];versions={n:hashlib.sha256((O/(n+'.svg')).read_bytes()).hexdigest()[:12] for n in names}
cards=''.join('<section><h2>'+html.escape(x['use'])+'</h2><img src="走廊原始参考/'+x['file']+'"><p>'+html.escape(x['file'])+'</p></section>' for x in references)
buttons=''.join('<button data-sheet="'+n+'">'+n[3:]+'</button>' for n in names)
doc='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P2.4 二楼平面重绘</title><style>
body{margin:0;background:#eff2ee;font:17px "Microsoft YaHei",sans-serif;color:#233d46}header{padding:24px;background:#253f49;color:white}h1{font-size:27px}p{line-height:1.8}nav,#tools{display:flex;gap:10px;flex-wrap:wrap;padding:14px 24px}a,button{padding:10px;background:white;border:1px solid #aec5be;border-radius:5px;color:#235c64;text-decoration:none;cursor:pointer}button.active{background:#3b887a;color:white}#canvas{padding:0 24px;overflow:auto}#drawing{width:100%;display:block;cursor:crosshair}#canvas.actual #drawing{width:2400px}section{margin:24px;background:white;padding:20px}section img{width:100%;display:block}#location{padding:12px 24px;background:#dcebe6}h2{font-size:21px}footer{padding:24px}</style>
<header><h1>P2.4-F2｜二楼平面重绘</h1><p>按已有正反向参考核对：上平台尽头是大窗，没有新增房门。只更新二维图；R2白模已暂停使用。</p><p>公卫、布草位置与栏外楼板关系尚未确定，图中明确留空或标注，不能据此直接建模。</p></header><nav>BUTTONS</nav><div id="tools"><a id="png">高清PNG</a><a id="svg">可编辑SVG</a><button id="zoom">原尺寸 / 适应页面</button><a href="#refs">正反向原图 ↓</a><a href="二楼重绘说明.md">变更与未决项</a></div><div id="canvas"><img id="drawing" alt="二楼重绘"></div><div id="location">点击平面可取得百分比位置，也可以直接使用浏览器图片批注。</div><div id="refs">CARDS</div><footer>当前仅这两张图为二楼重绘稿。尺寸由用户校准；其余全屋图暂不作为本轮二楼连接依据。模型未改。</footer><script>
const versions=VERSIONS;let current='03_二楼家具平面图';function select(n){current=n;const v='?v='+versions[n];document.querySelector('#drawing').src=n+'.svg'+v;document.querySelector('#png').href=n+'.png'+v;document.querySelector('#svg').href=n+'.svg'+v;document.querySelectorAll('[data-sheet]').forEach(b=>b.classList.toggle('active',b.dataset.sheet===n));}document.querySelectorAll('[data-sheet]').forEach(b=>b.onclick=()=>select(b.dataset.sheet));document.querySelector('#zoom').onclick=()=>document.querySelector('#canvas').classList.toggle('actual');document.querySelector('#drawing').onclick=e=>{const b=e.target.getBoundingClientRect();document.querySelector('#location').textContent=current+'：x='+((e.clientX-b.left)/b.width*100).toFixed(1)+'%，y='+((e.clientY-b.top)/b.height*100).toFixed(1)+'%。';};select(current);</script></html>'''.replace('BUTTONS',buttons).replace('CARDS',cards).replace('VERSIONS',json.dumps(versions,ensure_ascii=False))
(O/'打开平面图.html').write_text(doc,encoding='utf8')
md='# P2.4-F2 二楼平面重绘\n\n本轮仅二维，三维冻结。\n\n'+ '\n'.join('- '+x for x in D['notes'])+'\n\n## 参考依据\n\n'+'\n'.join('- '+x['file']+'：'+x['use'] for x in references)
(O/'二楼重绘说明.md').write_text(md,encoding='utf8')
print('Two SVG sheets, review HTML and separate draft data saved; no model files modified.')
