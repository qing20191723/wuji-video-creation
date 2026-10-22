"""P4 exterior integration from the user-confirmed P3-R2 interiors."""
from pathlib import Path
import ast,copy,csv,hashlib,html,json,math
R=Path(__file__).resolve().parents[1]
BASE=R/'完整平面与品牌_P3_R2_20261022'
OUT=R/'整体平面_P4_20261022'
for name in ['图纸','数据','检查']:(OUT/name).mkdir(parents=True,exist_ok=True)
source=BASE/'数据/空间方案_P3.json'
B=json.loads(source.read_text(encoding='utf8'));D=copy.deepcopy(B)
D.update(revision='P4-20261022',status='P3-R2二楼内部已获用户基本确认；一楼沿用；新增外部设计待验收')
D['acceptance']={'date':'2026-10-22','interior_basis':'P3-R2','user':'二楼的内部布局基本确定无误；一楼暂时没有什么问题','new_request':'公共庭院由上平台向图纸右侧延伸，按用户红色箭头；全家共用','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
# Keep every room, internal furniture item and wall coordinate. Only the indicated
# right-end exterior glazing gets an access door; the Shuya-facing window stays.
old_end=next(o for o in D['openings'] if o['id']=='W_PLATFORM_END')
D['replaced_exterior_openings']=[copy.deepcopy(old_end)]
D['openings']=[o for o in D['openings'] if o['id']!='W_PLATFORM_END']
for oid,start,end,typ in [('W_COURT_SIDE_S',-1.45,-.95,'window'),('D_COURT',-.95,.45,'glassdoor'),('W_COURT_SIDE_N',.45,1.45,'window')]:
 D['openings'].append(dict(id=oid,wall='H_E',level=2,start=start,end=end,type=typ,sill=0 if typ=='glassdoor' else .03,head=2.8,operation='双扇向庭院开启' if typ=='glassdoor' else '固定玻璃'))
T=[15.3,-3.0,23.2,1.6]
furn=[
 dict(id='T01',name='户外三人沙发',box=[18.1,.65,20.5,1.45],kind='sofa'),
 dict(id='T02',name='矮茶几',box=[18.8,.05,19.8,.60],kind='table'),
 dict(id='T03',name='休闲单椅',box=[18,-2.4,18.75,-1.6],kind='chair'),
 dict(id='T04',name='休闲单椅',box=[19.75,-2.4,20.5,-1.6],kind='chair'),
 dict(id='T05',name='东侧轻型花槽',box=[22.6,-2.85,23.05,1.45],kind='planter'),
 dict(id='T06',name='南侧轻型花槽',box=[16.3,-2.85,22.4,-2.4],kind='planter'),
 dict(id='T07',name='入口侧绿植',box=[15.45,-2.8,16.1,-1.6],kind='planter')]
supports=[[15.55,-2.8],[19.2,-2.8],[23,-2.8],[23,1.45]]
D['courtyard']=dict(id='TERRACE_PUBLIC',name='二楼公共露天庭院',level=2,elevation=3.3,box=T,net_area=36.34,furniture=furn,entry_clear=[15.3,-1.25,17.2,.85],main_path=[16.2,-1.35,22.4,-.15],door='D_COURT',route=[[13.9,-.25],[15.2,-.25],[16.3,-.25],[16.3,-.75],[21.9,-.75]],privacy_divider=[[21.1,1.7],[23.3,1.7]],divider_height=1.6,edge_guard_height=1.1,roof='露天，无永久顶棚',materials=['V3浅米色石材','木色户外平台','深灰栏杆','低矮花槽'],drainage=dict(direction='南侧外缘',primary_points=[[17,-2.9],[22.8,-2.9]],overflow='南外侧独立溢流，避开下方主通行线',note='排水坡度、门槛及构造在整模阶段细化'),supports=dict(points=supports,note='仅概念落柱；南侧独立支承、北侧接既有外墙梁线，梁柱截面与基础待工程深化'))
D['ground_exterior']=dict(covered_patio=[15.3,-3,23.2,0],entry_porch=[10.4,-6.3,14.8,-1.7],note='公共庭院下方为室外檐下休闲区；屋顶梯附属体下方为通往既有主入口的雨棚空间，均不增加一楼室内房间')
D['site']=dict(bounds=[-6,-16.8,26,15.4],garage_outer=[2.2,-16.8,10,-10.5],parking_bays=[[2.7,-16.2,5.5,-10.9],[6.2,-16.2,9,-10.9]],pedestrian_gate=[20.1,21.7],vehicle_gate=[2.9,9.3],entry_path=[[20.9,-16.8],[20.9,-7.6],[10.7,-7.6],[10.7,-.1]],path_width=1.6,side_paths=[[-5.3,-10,-4.1,13.6],[24.4,-10,25.6,14.2],[-5.3,13,25.6,14.2]],lawn=[.8,-8.8,9.1,-3.3],trees=[[-2.2,-8.6],[-2.5,10.5],[23.4,13.8]],source='由确认内部+公共庭院+步行和停车功能向外推导；地块32.0×32.2m为本版设计结果')
roof2=[[-.1,-1.7,15.3,1.8],[-3.9,-1.7,0,1.8],[-.1,1.6,7.9,8.2],[7.7,1.6,13.4,9],[13.2,1.6,21.2,8],[10.4,-6.3,14.8,-1.6]]
ground=[[-.1,-1.7,15.3,1.8],[-3.9,-1.7,0,1.8],[-.1,1.8,22,12.2],[0,0,22,1.8]]
D['roof_levels']=dict(main_roof=dict(elevation=6.6,rectangles=roof2),lower_roof=dict(elevation=3.3,base=ground,subtract=roof2+[T,[21.2,1.8,23.2,7.8]],use='仅检修屋面，不自动转成公共露台'),stairhouse=dict(box=[10.6,-6.1,14.6,-1.8],base=6.6,top=9.2,exit=[10.9,11.9],color='深灰',note='非第三层住宅；与P3-R2双跑梯同投影'))
D['roof_outline']=roof2
D['site']['building_bounds']=[-3.9,-6.3,23.35,12.2]
D['site']['garage_net']=[2.4,-16.6,9.8,-10.7]
D['site']['side_paths'].extend([[-4.7,-10.2,25,-9],[8.3,-10.5,9.3,-9]])
D['site']['garage_pedestrian_exit']=[8.3,9.3,-10.5]
D['site']['trees']=[[-2.2,-8.1],[-2.5,10.5],[23.6,14.8]]
D['exterior_brands']=[dict(id='BR_TERRACE_N',carrier='沙发后实体墙面装饰牌',position=[18.5,1.68,5.05],normal=[0,-1,0],size=[.7,.35],variant='normal',master='HG_FULL_normal',domain='hgdju.com',light='none'),dict(id='BR_TERRACE_M',carrier='入口侧花槽外侧小型铭牌',position=[16.11,-2.1,4.1],normal=[1,0,0],size=[.4,.2],variant='mirror',master='HG_FULL_mirror',domain='hgdju.com',light='none')]
for b in D['exterior_brands']:b.update(room='TERRACE_PUBLIC',level=2,kind='plaque',fixed_to_carrier=True,camera_facing=False,main=b['variant']=='normal')
D['brands'].extend(copy.deepcopy(D['exterior_brands']))
for b in D['brands']:
 if b['id']=='BR_EXT_M':b['position'][0]=25.98
 if b['id']=='BR_EXT_N':b['position'][1]=-16.82
D['unresolved']=['本轮只确认了内部基线；庭院、外观组合与地块属于新增设计，待用户审阅。','庭院入口拟将上平台右端玻璃界面改为双扇玻璃门加侧窗；舒亚对面的落地窗不变。','新增平台的落柱位置、梁高、基础、种植荷载、防水和排水为概念设计，尚未工程验算。','一层屋面露出部分只作为检修屋面，未新增卧室入口或公共花园入口。','V3石材、木饰面、深灰栏杆和屋顶小房子沿用视觉语言；旧外立面窗格和外轮廓不作为内部面积约束。','全屋Blend/GLB及实际场景图本轮未更新；新旧品牌在最终机位中的遮挡、反射待整模检查。']
D['authorization_updates'].append('P4：用户确认P3-R2二楼内部基本无误，一楼沿用；公共庭院按箭头从上平台向右延伸。')
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
dump(OUT/'数据/整体空间方案_P4.json',D)
dump(OUT/'数据/室内确认基线.json',D['acceptance'])
# Reuse only the established drawing primitives; never execute the P3 generator.
tree=ast.parse((R/'scripts/build_p3_delivery.py').read_text(encoding='utf8').replace('P3-R2 ·','P4 ·'))
nodes=[n for n in tree.body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['Sheet','drawwalls','drawstairs']]
INK='#243b40';GREEN='#38796c';ORANGE='#b36c31'
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<P3 drawing primitives>','exec'))
def contains(b,x,y):return b[0]<x<b[2] and b[1]<y<b[3]
def tiles_union(rects,subtract=[]):
 xs=sorted(set(v for b in rects+subtract for v in [b[0],b[2]]));ys=sorted(set(v for b in rects+subtract for v in [b[1],b[3]]));cells=[]
 for i in range(len(xs)-1):
  for j in range(len(ys)-1):
   x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2
   if any(contains(b,x,y) for b in rects) and not any(contains(b,x,y) for b in subtract):cells.append([xs[i],ys[j],xs[i+1],ys[j+1]])
 return cells
def roof_fill(s,rects,color,subtract=[]):
 for b in tiles_union(rects,subtract):s.rect(b,color,color,0)
def route(s,pts,color=GREEN,width=3):
 for a,b in zip(pts,pts[1:]):s.line(a,b,color,width)
 if len(pts)>1:
  a,b=pts[-2:];t=math.atan2(b[1]-a[1],b[0]-a[0]);s.line(b,[b[0]-.3*math.cos(t-.45),b[1]-.3*math.sin(t-.45)],color,width);s.line(b,[b[0]-.3*math.cos(t+.45),b[1]-.3*math.sin(t+.45)],color,width)
def label(s,x,y,text,size=13):
 xx,yy=s.xy(x,y);width=len(text)*size*.78+12
 s.p.append(f'<rect x="{xx-width/2:.1f}" y="{yy-size:.1f}" width="{width:.1f}" height="{size+7}" rx="4" fill="#ffffff" fill-opacity=".88"/>');s.text(xx,yy,text,size,anchor='middle')
def interior(s,level,furniture=True,labels=True):
 for r in D['rooms']:
  if r['level']==level:s.rect(r['box'],r['color'])
 if furniture:
  for f in sorted(D['furniture'],key=lambda f:0 if 'rug' in f['kind'] else 1):
   if f['level']==level:s.furniture(f)
 # Render special exterior door explicitly; other opening types use existing logic.
 door=next(o for o in D['openings'] if o['id']=='D_COURT');door['type']='glass';drawwalls(s,level);door['type']='glassdoor'
 drawstairs(s,['ST12'] if level==1 else ['ST12','ST23'])
 if labels:
  for r in D['rooms']:
   if r['level']!=level or r['id'] in ['A','C','B','RS']:continue
   x,y,X,Y=r['box'];obs=[f['box'] for f in D['furniture'] if f['room']==r['id'] and 'rug' not in f['kind']]
   candidates=[(x+(X-x)*i/10,y+(Y-y)*j/10) for i in range(2,9) for j in range(2,9)]
   free=[p for p in candidates if not any(contains([b[0]-.6,b[1]-.2,b[2]+.6,b[3]+.2],*p) for b in obs)]
   px,py=min(free or candidates,key=lambda p:(p[0]-(x+X)/2)**2+(p[1]-(y+Y)/2)**2)
   label(s,px,py,'设备/支承预留' if r['id']=='SUP' else r['name'],12)
def garden(s,detail=False):
 s.rect(T,'#eadfcb');s.rect(D['courtyard']['entry_clear'],'#e2f0e4','#aac6af',1);s.rect(D['courtyard']['main_path'],'#e2f0e4','#aac6af',1)
 for f in furn:
  b=f['box'];s.rect(b,'#71976c' if f['kind']=='planter' else '#cdb494',rx=4);s.world((b[0]+b[2])/2,(b[1]+b[3])/2,f['id'],14 if detail else 10,anchor='middle')
  if f['kind']=='planter':
   x,y,X,Y=b;n=max(1,int(max(X-x,Y-y)/.6))
   for i in range(n):s.circle(x+(X-x)*(i+.5)/n if X-x>Y-y else (x+X)/2,(y+Y)/2 if X-x>Y-y else y+(Y-y)*(i+.5)/n,.14,'#4f7c52')
 for a,b in [([15.2,-3.1],[23.3,-3.1]),([23.3,-3.1],[23.3,1.7]),([15.2,-3.1],[15.2,-1.6])]:s.line(a,b,INK,3)
 s.line([15.2,1.7],[21.1,1.7],INK,4)
 s.line([21.1,1.7],[23.3,1.7],'#9b754c',5)
 for a,b in [(-1.45,-.95),(.45,1.45)]:s.line([15.2,a],[15.2,b],'#319bb1',3)
 s.line([15.2,-.95],[15.9,-.95],'#319bb1',2);s.line([15.2,.45],[15.9,.45],'#319bb1',2)
 route(s,D['courtyard']['route'],GREEN,3)
 if detail:
  s.dim(T);label(s,19.3,-1.05,'连续通路 1.20m',15);label(s,16.2,.8,'入口留空',13)
  s.world(21.15,2.1,'与私人阳台分隔',14)
  for x,y in D['courtyard']['drainage']['primary_points']:s.circle(x,y,.09,'#319bb1')
 else:label(s,19.1,-3.65,'新增公共庭院 36.34㎡',14)
def new(title,sub,bounds,notes):return Sheet(title,sub,bounds,notes)
notes=['室内：P3-R2确认基线','所有原家具坐标保持','庭院从公共上平台进入','沿用户箭头向右延伸','与大姐私人阳台分隔','新增外部仍待用户验收']
s=new('01 / 二楼整体平面 · 向右扩展公共庭院','先确认室内，再安排庭院；庭院净范围7.90×4.60m为布置结果',[-4.7,-7,25,13],notes)
roof_fill(s,ground,'#eeece6',roof2+[T,[21.2,1.8,23.2,7.8]])
interior(s,2);garden(s);label(s,11.2,11.2,'一层露出屋面 / 仅检修',13);s.finish('01_二楼整体平面_公共庭院')
s=new('02 / 公共庭院放大 · 布置与出入口','不借用卧室通行；室内上平台 → 双扇玻璃门 → 公共休闲区',[13.5,-4,24.3,2.7],['庭院净面积 36.34㎡','T01 三人户外沙发','T02 矮茶几','T03 / T04 休闲单椅','T05—T07 轻型花槽','门洞净设计宽 1.40m','通路净设计宽 1.20m','无永久顶棚，保持露天','北东角隔开私人阳台','南侧设排水 / 溢流','种植与栏杆需工程深化'])
s.rect([13.5,-1.5,15.1,1.6],'#edf2e9');garden(s,True);s.world(13.6,1.2,'公共上平台',14);s.finish('02_公共庭院放大')
s=new('03 / 一楼整体平面 · 原内部与新增檐下空间','一楼室内沿用；二楼庭院下方安排室外休闲区，主入口从既有位置进入',[-5,-8.5,26,13.5],['室内家具、门窗不移动','庭院下方：室外檐下区','梯间附属体下：入口雨棚','圆点为概念支承位置','柱位避开室内及入口','不增加一楼封闭房间','结构尺度尚待深化'])
interior(s,1)
s.rect(D['ground_exterior']['covered_patio'],'#e5d5bd');s.rect(D['ground_exterior']['entry_porch'],'#e5d5bd')
for x,y in supports:s.circle(x,y,.16,'#556b65')
label(s,19.4,-1.4,'庭院下方 / 檐下休闲',13);label(s,12.6,-4.6,'入口雨棚',13);route(s,[[10.7,-8],[10.7,-.1]])
for b in [T,[10.4,-6.3,14.8,-1.6]]:
 x,y,X,Y=b
 for a,c in [([x,y],[X,y]),([X,y],[X,Y]),([X,Y],[x,Y]),([x,Y],[x,y])]:s.line(a,c,'#a88e6b',1,'6 4')
s.finish('03_一楼整体平面_檐下空间')
s=new('04 / 屋顶平面 · 高低屋面与出屋面小房子','深灰小房子是楼梯出口；不增设完整第三层住宅',[-4.7,-7,25,13],['+6.60 主屋面','+3.30 一层露出屋面','+3.30 公共庭院与阳台','+9.20 梯间顶部暂定','到屋顶仍走原新增双跑梯','低屋面仅做检修用途','无高大树木或额外住宅'])
roof_fill(s,ground,'#e7e4da');roof_fill(s,roof2,'#cdd9d5');s.rect(T,'#dddbc1');s.rect([21.2,1.8,23.2,7.8],'#dddbc1')
s.rect([10.6,-6.1,14.6,-1.8],'#6b777b');drawstairs(s,['ST23']);s.line([10.9,-1.7],[11.9,-1.7],'#319bb1',5);route(s,[[11.4,-2.1],[11.4,.6],[11.4,4.5]])
label(s,4,4.5,'主屋面 +6.60',16);label(s,10.7,11,'低屋面 +3.30',14);label(s,19.2,-.6,'露天庭院 +3.30',14);s.world(10.6,-6.85,'深灰楼梯小房子',14);s.finish('04_屋顶与高低屋面')
s=new('05 / 上下层对应 · 庭院向外增设','灰色为一楼投影；彩色为二楼空间；外部结构从室内边界向外组织',[-4.7,-7,25,13],['灰色：一楼建筑范围','彩色：二楼确认室内','木色：新增公共庭院','虚线：庭院向下投影','原房间外墙无需内移','新支承避开原室内家具','低屋面不误算二楼房间'])
roof_fill(s,ground,'#dfe2dc')
for r in D['rooms']:
 if r['level']==2:
  s.rect(r['box'],r['color']);x,y,X,Y=r['box']
  if r['id']!='RS':label(s,(x+X)/2,(y+Y)/2,{'C':'端部C','A':'上平台A'}.get(r['id'],r['id']+' '+r['name']),11)
s.rect(T,'#e1caa8');label(s,19.25,-.5,'公共庭院',15)
for x,y in supports:s.circle(x,y,.16,'#52685f')
drawstairs(s,['ST12','ST23']);s.world(10.6,-6.65,'通顶楼梯间',13);s.finish('05_上下层对应')
s=new('06 / 外部总平面 · 入户、停车与庭院','地块32.00×32.20m为本方案向外推导结果，不是室内限制条件',[-7.5,-18,28,17],['二楼公共庭院位于右前侧','下方檐下区接一楼前庭','南侧为临街入口','停车与人行入口分开','入户步道宽1.60m','两侧及后方留检修通路','浅石材 / 木饰面 / 深灰栏杆','外部与地块均为设计提案'])
s.rect(D['site']['bounds'],'#dfe8d4')
for b in D['site']['side_paths']:s.rect(b,'#ece4d3','#d8ceb8')
s.rect(D['site']['lawn'],'#a7c297');roof_fill(s,ground,'#dddeda');roof_fill(s,roof2,'#bdcdc5');s.rect(T,'#d5bc97');s.rect([21.2,1.8,23.2,7.8],'#d5bc97')
s.rect(D['site']['garage_outer'],'#b8c1bd')
for b in D['site']['parking_bays']:s.rect(b,'#e1e7e4');x,y,X,Y=b;s.rect([x+.2,y+.4,X-.2,Y-.4],'#829996',rx=8)
for x,y in D['site']['trees']:s.circle(x,y,.6,'#6c9564')
for a,b in zip(D['site']['entry_path'],D['site']['entry_path'][1:]):s.line(a,b,'#b89d70',1.6*s.scale)
route(s,D['site']['entry_path'],GREEN,2)
s.line([8.3,-10.5],[9.3,-10.5],'#319bb1',3)
s.line([20.1,-16.8],[21.7,-16.8],'#319bb1',5);s.line([2.9,-16.8],[9.3,-16.8],'#6a807a',5)
label(s,6.1,-13.5,'双车位车库',13);label(s,20.8,-17.45,'人行门',13);label(s,6.1,-17.45,'车行门',13);label(s,4.8,-6,'前庭草坪',13);label(s,19.2,-1.5,'二楼庭院投影',12);label(s,11.3,13.5,'后侧检修通路',12)
s.finish('06_外部总平面')
s=new('07 / 南侧体量与庭院剖面示意','示意用于核对空间层次；不作为梁柱、基础或防水施工图',[-4,-1,26,12],['一楼 ±0.00','二楼 / 庭院 +3.30','主屋面 +6.60','梯间顶部 +9.20 暂定','庭院采用外侧支承概念','庭院下方为开放檐下区','室内尺度沿用确认平面'])
s.p=s.p[:-2] # no north arrow on a vertical section
for z in [0,3.3,6.6,9.2]:s.line([-3,z],[24,z],'#9daea3',1,'8 5');s.world(24.2,z,f'+{z:.2f}',13)
s.rect([0,0,21.2,6.6],'#eee5d6');s.rect([10.6,6.6,14.6,9.2],'#69767a');s.rect([15.3,3.08,23.3,3.3],'#b9c6b9')
for x in [15.55,19.2,23]:s.rect([x-.12,0,x+.12,3.08],'#b8c3bb')
s.line([15.3,4.4],[23.3,4.4],INK,3)
for x in [15.3,17.3,19.3,21.3,23.3]:s.line([x,3.3],[x,4.4],INK,1)
s.rect([15.3,0,23.2,3.05],'#f7f4eb','#c0c9bd')
for x in [15.55,19.2,23]:s.rect([x-.12,0,x+.12,3.08],'#b8c3bb')
label(s,19.2,1.5,'檐下室外区',16);label(s,19.2,3.65,'公共庭院',14);label(s,7,4.8,'确认室内空间',18);label(s,12.6,7.6,'屋顶梯间',14)
s.finish('07_体量与庭院剖面示意')
# Scope checks: compare the accepted baseline rather than a newly invented target.
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-6 and min(a[3],b[3])-max(a[1],b[1])>1e-6
checks=[]
def check(name,passed,detail=None):checks.append(dict(name=name,passed=bool(passed),detail=detail))
for key in ['rooms','furniture','walls','stairs']:check('确认基线保持:'+key,D[key]==B[key])
baseline_ops={o['id']:o for o in B['openings']}
for o in D['openings']:
 if o['id'] in baseline_ops:check('原洞口保持:'+o['id'],o==baseline_ops[o['id']])
for r in B['rooms']:
 if r['level']==2:check('庭院不占用:'+r['id'],not overlap(T,r['box']))
for f in furn:
 b=f['box'];check('庭院物件边界:'+f['id'],all([b[0]>=T[0],b[1]>=T[1],b[2]<=T[2],b[3]<=T[3]]))
 for zone in ['entry_clear','main_path']:check(zone+':'+f['id'],not overlap(b,D['courtyard'][zone]))
for i,f in enumerate(furn):
 for g in furn[i+1:]:check('庭院无穿插:'+f['id']+'/'+g['id'],not overlap(f['box'],g['box']))
check('玻璃门接公共平台',next(o for o in D['openings'] if o['id']=='D_COURT')['wall']=='H_E')
check('舒亚对面落地窗未改',next(o for o in D['openings'] if o['id']=='W_SHUYA_OPPOSITE')==baseline_ops['W_SHUYA_OPPOSITE'])
check('公共庭院与私人阳台分隔',D['courtyard']['privacy_divider']==[[21.1,1.7],[23.3,1.7]])
for x,y in supports:
 check('概念支承不占一楼室内:'+str([x,y]),not any(contains(r['box'],x,y) for r in B['rooms'] if r['level']==1))
check('基线文件未改',hashlib.sha256(source.read_bytes()).hexdigest()==D['acceptance']['source_sha256'])
report=dict(revision=D['revision'],checks=checks,passed=all(c['passed'] for c in checks),not_claimed=['结构荷载、梁柱净空及施工合规验算','最终光照、反射及场景机位验收'])
dump(OUT/'检查/范围与通行检查.json',report)
assert report['passed'],[c for c in checks if not c['passed']]
with (OUT/'数据/新增外部尺寸.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['编号','项目','范围或尺寸','状态']);w.writerow(['T','公共庭院','7.90×4.60m / 36.34㎡','新增设计'])
 for o in furn:w.writerow([o['id'],o['name'],o['box'],'新增设计'])
 w.writerows([['D_COURT','庭院双扇玻璃门','1.40m洞口','新增设计'],['SITE','地块','32.00×32.20m','外部推导'],['GARAGE','车库外轮廓','7.80×6.30m','外部设计']])
(OUT/'设计说明.md').write_text('''# P4 整体平面构思

用户已基本确认P3-R2二楼内部；一楼沿用。原房间、家具、墙体、楼梯坐标保持，室内不因庭院或外轮廓压缩。

公共庭院按箭头设在上平台右侧，从公共区直接进入。布置三人沙发、茶几、两把单椅、外缘轻型花槽，留入口净空及1.20m连续通路；据此得到7.90×4.60m净范围。与大姐私人阳台以分隔屏区分，不借用卧室出入。

上平台右端原玻璃界面局部改为1.40m双扇玻璃门并保留侧窗；这是本轮明确列出的新增外部调整。浴室玻璃门、舒亚对面的巨大落地窗以及原直梯、护栏关系保持。

一楼内部不改。新增平台下方为檐下室外休闲区；梯间附属体下方为入口雨棚。概念柱位放在室内范围外；结构和基础尚待工程深化。庭院轻型花槽集中在外缘，不设高大乔木、水池或永久顶棚。

屋顶按真实楼层投影区分：二楼主屋面+6.60m，一楼露出屋面+3.30m，公共庭院与私人阳台+3.30m。灰色小房子仅作屋顶楼梯出口，顶部暂定+9.20m；低屋面只作检修，不额外增加公共花园和房间。

外部总平面由建筑和庭院向外布置：南侧双车位车库、人行门分开；入户步道通到既有入口；前庭草坪、两侧与后侧检修通路补齐。地块32.00×32.20m是本方案结果，并非先设上限。

外观采用V3浅色石材、木色平台、深灰栏杆及灰色屋顶梯间的组合。旧外观比例不反向约束已确认内部。庭院新增两处固定品牌载体，沿用正向/整组镜像含hgdju.com母版，不随机位移动。

本批交付SVG、高清PNG、统一查看页与完整空间数据。全部外部仍属设计提案，未更新全屋Blend/GLB，也未生成实际场景图。原M3、7张认可图及P3-R2文件保留。
''',encoding='utf8')
print(json.dumps(dict(out=str(OUT),checks=len(checks),passed=report['passed']),ensure_ascii=False))
