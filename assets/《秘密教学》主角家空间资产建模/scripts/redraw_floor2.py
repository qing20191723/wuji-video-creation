"""Reference topology only: no metric floor-plan or 3D writes."""
from pathlib import Path
import json, hashlib, html, shutil, sys
import plan_svg as g
R=Path(__file__).resolve().parents[1]; O=R/'平面确认'; RD=O/'走廊原始参考'
REV='P2.4-F4'
REF=Path(sys.argv[1]) if len(sys.argv)>1 else RD
source_notes=[
 ('别墅二楼到楼梯间参考图（俯拍图）.png','① 俯拍下楼','梯段与卧室走廊并排；远端二楼地面下方可见一楼平台。端头木门与其他图不同，不据此新增门。'),
 ('别墅二楼到楼梯间参考图.png','② 平视下楼','舒亚端高窗旁是二楼端部地面；梯段落到其下方附近。玻璃后台阶仅此图出现，不增加第二部楼梯。'),
 ('别墅二楼走廊.png','③ 回看上楼端','卧室在左，护栏与楼梯在右；前方大窗。护栏在窗前结束，上平台需侧向连通走廊。'),
 ('别墅楼梯间参考.png','④ 从楼下向上','直跑上升到大窗前；顶部侧转接二楼走廊。窗口不能被房间或新增木门挡住。'),
 ('楼梯间参考（黄瓜短剧版）.jpg','⑤ 夜间上楼','与④对应同一梯段和顶部大窗，不据此另设楼梯。'),
 ('图片.png','⑥ 舒亚端近景','高落地窗、短端部地面、楼梯洞口收头与玻璃门相邻。横向窄窗是同一侧外墙另一处采光。')]
previous={x['file']:x for x in json.loads((RD/'来源.json').read_text(encoding='utf8'))} if (RD/'来源.json').exists() else {}
refs=[]
for name,label,note in source_notes:
 p=REF/name
 if p.resolve()!=(RD/name).resolve():shutil.copy2(p,RD/name)
 refs.append(dict(file=name,label=label,note=note,source=previous.get(name,{}).get('source',str(p)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(RD/'来源.json').write_text(json.dumps(refs,ensure_ascii=False,indent=2),encoding='utf8')
notes=[
 'F3以缩短护栏为由整体移动楼梯3.90m、收短全屋通道4.00m，均撤回为设计依据。5.42m护栏也不是参考图测得的长度。',
 '本轮先独立校核楼梯间：卧室门墙—二楼走廊—矮护栏—直跑楼梯—外墙窗带依次并列。',
 'A是大窗前的二楼上平台；跨过楼梯口端部侧向接回走廊。',
 'C是舒亚端高窗旁的少量二楼地面及洞口收头；B是一楼下平台，位于C下方附近。C与B不是同一层的两个并列平台。',
 'B与C的精确投影重叠量、梁底和踏步净空无法仅凭图片确定；剖面以虚线标出，不按图示比例建模。',
 '原图俯拍的端头木门、另一图玻璃后台阶互相不一致；本稿保留此前确认的舒亚端玻璃门关系，不新增木门或第二部楼梯。',
 '图纸采用无米制的局部关系坐标；房门间距、踏步数量、护栏长度、窗尺寸均未测定，不改变既有卧室内部。',
 '全屋嵌入、实际楼板边界、辅助房间与一楼公共区接法仍需解决；未形成完整全屋平面，三维冻结。']
D=dict(revision=REV,status='局部关系核对，非比例，禁止直接建模',coordinate_system='schematic_local_nonmetric',notes=notes,references=refs,
 topology={'parallel_bands':['bedroom_doors','level2_corridor','guard','straight_stair','exterior_windows'], 'A':'upper landing at Weiya/window end', 'B':'lower landing near Shuya end', 'C':'upper floor patch above/near B','connections':['A to level2 corridor around guard end','A down straight flight to B','B to level1 public area, exact path unlocated'],'B_C_overlap':'inferred from references; exact overlap unresolved'},
 withdrawn={'F3_stair_shift_m':3.9,'F3_corridor_cut_m':4.0,'F3_guard_length_m':5.42},build_ready=False)
(O/'二楼重绘数据.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')

def sheet(title,sub,size=(2200,1500),scale=220,origin=(180,870)):
 s=g.Sheet(title,sub,[0,0,8,4],scale,origin,size)
 s.p=[x.replace('P2.3-R2 · 2026-10-21 · 走廊空间局部校核 · 同步 P2.3-M1 白模 · 影视参考，非施工图',REV+' · 2026-10-21 · 局部非比例关系图 / 不能按图量尺寸 / 三维未修改') for x in s.p]
 return s

def wall(s,a,b):s.line(a,b,g.WALL,14)
def win(s,a,b):
 s.line(a,b,'#faf9f5',16);s.line(a,b,g.BLUE,6)
def door(s,x):
 s.line((x,2.45),(x+.5,2.45),'#faf9f5',18)
 s.line((x,2.45),(x,2.95),'#91704c',2)
 s.line((x,2.95),(x+.5,2.45),'#baaa96',1,'4 5')
def tag(s,x,y,t):s.wt(x,y,t,23,anchor='middle',weight=700)

s=sheet('《秘密教学》｜二楼楼梯口：局部关系重绘','横向：舒亚端 ← → 薇亚／上平台端。房门只示先后，不表示已确定门距。')
s.rect([0,1.25,7.8,2.45],'#e3eee8','none')
s.rect([0,0,1.25,1.25],'#e3eee8','none');s.rect([6.55,0,7.8,1.25],'#e3eee8','none')
s.rect([1.25,0,6.55,1.25],'#d9e8ef',g.BLUE,1)
for i in range(1,17):s.line((1.25+i*5.3/17,.05),(1.25+i*5.3/17,1.2),'#91a9b3',1)
wall(s,(0,0),(7.8,0));wall(s,(0,0),(0,2.45));wall(s,(7.8,0),(7.8,2.45));wall(s,(0,2.45),(7.8,2.45))
for x,n in [(.45,'舒亚'),(3.25,'子豪'),(6.1,'薇亚')]:door(s,x);tag(s,x+.25,3.16,n+'房门')
win(s,(0,1.4),(0,2.3));win(s,(.3,0),(1.0,0));win(s,(2.0,0),(5.2,0));win(s,(6.8,0),(7.5,0));win(s,(7.8,.1),(7.8,2.3))
s.line((.1,1.5),(.1,2.2),g.TEAL,1.5,arrow=True);s.wt(-.37,1.75,'玻璃门',14,anchor='middle',color=g.BLUE)
s.line((1.25,1.25),(6.55,1.25),'#aa825c',11);s.line((1.25,0),(1.25,1.25),'#aa825c',8)
s.line((7.1,.6),(7.1,1.8),g.TEAL,4,arrow=True);s.line((7.1,1.8),(.7,1.8),g.TEAL,4,arrow=True)
s.line((6.2,.6),(1.6,.6),g.BLUE,4,arrow=True)
tag(s,3.8,2.1,'二楼同层直走廊');tag(s,3.9,.85,'楼梯洞口：由右向左下楼')
s.wt(3.9,1.4,'矮护栏仅沿洞口；两端均有收头',19,anchor='middle',color='#9b6842')
tag(s,.62,.85,'C');s.wt(.62,.55,'二楼端部地面',15,anchor='middle');s.wt(.62,.3,'下方附近是B',15,anchor='middle')
tag(s,7.15,.95,'A');s.wt(7.15,.3,'二楼上平台',16,anchor='middle')
s.wt(.65,-.32,'高落地窗',18,anchor='middle',color=g.BLUE);s.wt(3.6,-.32,'横向窄长采光窗',18,anchor='middle',color=g.BLUE)
s.wt(7.05,-.32,'回看侧窗',18,anchor='middle',color=g.BLUE)
s.wt(8.2,1.5,'大窗',20,anchor='middle',color=g.BLUE)
s.notes(110,1050,[('这次纠正的是上下关系',['C只是窗旁端部地面及洞口收头，不是前稿补出的宽大空场。','B在一楼；平面上与C接近或重叠，应分层画，不能与C当成同层并排。'])],960)
s.notes(1130,1050,[('不再以任意米数迁移楼梯',['撤回F3的西移3.90m及收短4.00m方案；此图不绑定全屋坐标。','端头木门／玻璃后额外台阶有参考差异，不能合并增加房门或梯段。'])],960)
s.finish('11_二楼楼梯口局部关系')

s=sheet('《秘密教学》｜一楼落脚位置：与二楼同向叠合','保持与上一张相同的局部坐标；蓝灰虚线为上方投影，不能作为一楼可走地面。')
s.rect([0,0,1.25,1.25],'#e3eee8',g.WALL,2)
s.rect([1.25,0,6.55,1.25],'#d9e8ef',g.WALL,2)
for i in range(1,17):s.line((1.25+i*5.3/17,.05),(1.25+i*5.3/17,1.2),'#91a9b3',1)
s.rect([0,1.25,7.8,2.45],'none','#a9b8bc',2,'10 7');s.rect([6.55,0,7.8,1.25],'none','#a9b8bc',2,'10 7')
s.rect([0,0,1.25,1.25],'none','#a78461',5,'9 7')
s.line((1.55,.6),(6.2,.6),g.TEAL,4,arrow=True)
s.line((.6,.7),(.6,1.9),g.TEAL,3,'9 7',True)
tag(s,.6,.6,'B');s.wt(.6,.28,'一楼下平台',16,anchor='middle')
tag(s,4,2.0,'二楼走廊投影');s.wt(4,1.65,'一楼用途与外接通路尚未定位',20,anchor='middle')
tag(s,7.15,.6,'A上方');s.wt(3.9,.9,'单一直跑梯段：由左向右上楼',21,anchor='middle')
s.wt(.6,-.3,'C二楼地面在上方附近',17,anchor='middle',color='#9b6842')
s.notes(110,1050,[('落脚后再接一楼',['参考图可看见B及侧向空间，但不能证明它在旧玄关的哪一个坐标。','绿色虚线只表示需有侧向接续，不新画一扇门，也不宣称已接通客厅。'])],960)
s.notes(1130,1050,[('投影与净空必须共同校核',['C下的B、第一批踏步以及梁底要在纵剖中核对净空。','本图未指定一楼房间及家具，不用搬动客厅去补此前任意位移。'])],960)
s.finish('12_一楼下平台与上层投影')

s=sheet('《秘密教学》｜纵剖：C在上，B在下，A在梯顶','沿梯段方向看，左为舒亚端、右为薇亚端。楼层线只表达高低，不给出实测标高。',origin=(180,1010),scale=220)
s.line((-.1,0),(8,0),g.WALL,3);s.wt(8.15,0,'一楼',18)
s.line((0,2.3),(1.25,2.3),g.WALL,9);s.line((6.55,2.3),(7.8,2.3),g.WALL,9)
s.line((1.25,2.3),(6.55,2.3),'#aebec2',2,'9 8');s.wt(8.15,2.3,'二楼',18)
s.rect([0,2.1,1.25,2.3],'#dde1db',g.WALL,1);s.rect([6.55,2.1,7.8,2.3],'#dde1db',g.WALL,1)
for i in range(17):
 x=1.25+i*5.3/17;xx=1.25+(i+1)*5.3/17;z=i*2.3/17;zz=(i+1)*2.3/17
 s.line((x,z),(x,zz),g.WALL,3);s.line((x,zz),(xx,zz),g.WALL,3)
s.line((6.55,3.12),(1.25,3.12),'#aa825c',4,'10 6');s.wt(4,3.3,'侧面矮护栏顶投影',18,anchor='middle',color='#9b6842')
tag(s,.6,2.55,'C 二楼端部地面');tag(s,.6,.25,'B 一楼下平台');tag(s,7.15,2.55,'A 二楼上平台')
s.line((1.25,.2),(1.25,2.1),'#ad7051',2,'5 4');s.wt(1.65,1.5,'梁底／踏步净空待核',19,color='#ad7051')
s.line((.6,1.85),(.6,.55),g.BLUE,2,'7 5',True)
s.wt(3.8,2.55,'洞口上方不能再铺整块二楼楼板',19,anchor='middle',color=g.BLUE)
s.wt(4.4,.3,'踏步数量、坡度、平台尺寸仅示意',19,anchor='middle')
s.notes(110,1160,[('参考①②⑥共同可见',['舒亚端的二楼地面／收头跨在下方空间上方；下楼尽头另见一楼地面。','本稿把它们拆为C与B，精确投影范围仍待尺度校准。'])],960)
s.notes(1130,1160,[('本轮分析的边界',['共识：平行的走廊与直梯、两端接续、上下平台、侧窗类型。','差异：舒亚端木门或玻璃门、玻璃后额外台阶；不混入统一几何。'])],960)
s.finish('13_楼梯纵剖与上下层关系')

names=['11_二楼楼梯口局部关系','12_一楼下平台与上层投影','13_楼梯纵剖与上下层关系']
versions={n:hashlib.sha256((O/(n+'.svg')).read_bytes()).hexdigest()[:12] for n in names}
buttons=''.join('<button data-sheet="'+n+'">'+n[3:]+'</button>' for n in names)
cards=''.join('<section><h2>'+x['label']+'</h2><p>'+html.escape(x['note'])+'</p><img src="走廊原始参考/'+x['file']+'"><p>'+x['file']+'</p></section>' for x in refs)
page='<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>F4 楼梯间上下关系核对</title><style>body{margin:0;background:#eff2ee;font:17px "Microsoft YaHei",sans-serif;color:#233d46}header{padding:24px;background:#253f49;color:white}h1{font-size:27px}p{line-height:1.8}nav,#tools{display:flex;gap:10px;flex-wrap:wrap;padding:14px 24px}a,button{padding:10px;background:white;border:1px solid #aec5be;border-radius:5px;color:#235c64;text-decoration:none;cursor:pointer}button.active{background:#3b887a;color:white}#canvas{padding:0 24px;overflow:auto}#drawing,section img{width:100%;display:block}#canvas.actual #drawing{width:2200px}section{margin:24px;background:white;padding:20px}#location{padding:12px 24px;background:#dcebe6}footer{padding:24px}</style><header><h1>P2.4-F4｜楼梯间上下关系核对</h1><p>先把楼梯间画对：二楼端部地面C、一楼下平台B、梯顶上平台A分别表达。</p><p>撤回上一版3.90m楼梯位移和任意长度。本轮是局部非比例平面＋纵剖，不是已完成的全屋平面；三维冻结。</p></header><nav>BUTTONS</nav><div id="tools"><a id="png">高清PNG</a><a id="svg">可编辑SVG</a><button id="zoom">原尺寸 / 适应页面</button><a href="#refs">六张原图逐项核对 ↓</a><a href="二楼重绘说明.md">错误分析与差异</a></div><div id="canvas"><img id="drawing"></div><div id="location">可直接批注图纸；点击可显示坐标。</div><div id="refs">CARDS</div><footer>本轮没有从透视图臆定米数。全屋嵌入、净空和辅助功能未解决，不以“文件检查通过”代替空间确认。</footer><script>const versions=VERSIONS;let current=\'11_二楼楼梯口局部关系\';function select(n){current=n;const v=\'?v=\'+versions[n];document.querySelector(\'#drawing\').src=n+\'.svg\'+v;document.querySelector(\'#png\').href=n+\'.png\'+v;document.querySelector(\'#svg\').href=n+\'.svg\'+v;document.querySelectorAll(\'[data-sheet]\').forEach(b=>b.classList.toggle(\'active\',b.dataset.sheet===n));}document.querySelectorAll(\'[data-sheet]\').forEach(b=>b.onclick=()=>select(b.dataset.sheet));document.querySelector(\'#zoom\').onclick=()=>document.querySelector(\'#canvas\').classList.toggle(\'actual\');document.querySelector(\'#drawing\').onclick=e=>{const b=e.target.getBoundingClientRect();document.querySelector(\'#location\').textContent=current+\'：x=\'+((e.clientX-b.left)/b.width*100).toFixed(1)+\'%，y=\'+((e.clientY-b.top)/b.height*100).toFixed(1)+\'%。\';};select(current);</script></html>'
page=page.replace('BUTTONS',buttons).replace('CARDS',cards).replace('VERSIONS',json.dumps(versions,ensure_ascii=False))
(O/'打开平面图.html').write_text(page,encoding='utf8')
(O/'二楼重绘说明.md').write_text('# '+REV+' 楼梯间分析\n\n'+'\n'.join('- '+x for x in notes)+'\n\n## 六图核对\n\n'+'\n'.join('- '+x['file']+'：'+x['note'] for x in refs),encoding='utf8')
print('Three nonmetric relationship sheets and six-reference review saved. Models untouched.')
