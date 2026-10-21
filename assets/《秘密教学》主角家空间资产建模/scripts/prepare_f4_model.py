"""Metric realization of user-approved F4 topology; all dimensions provisional.
Preserves the approved F4 sheets and the historical P2.3 source unchanged.
"""
from pathlib import Path
import copy, json, hashlib
R=Path(__file__).resolve().parents[1]
O=R/'白模当前'; (O/'模型').mkdir(parents=True,exist_ok=True)
src=R/'平面确认/平面方案数据.json'
D=json.loads(src.read_text(encoding='utf8'))
old=copy.deepcopy(D)
D['revision']='P2.4-M2'
D['status']='F4关系已确认；本次尺寸与二楼家具重新布置为暂定实现'
D['authorization']={'topology':'这版平面图是正确的','rebuild':'现在基于这个确定平面图，重新生成建模','proportions':'允许调整房间比例，以F4关系为准','date':'2026-10-21'}
D['source']={'legacy_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'approval':'平面确认/F4用户确认记录.json'}
names={'B3':'舒亚卧室','B2':'子豪卧室','B1':'薇亚卧室','MB':'主卧','H2':'二楼直走廊','L':'客厅','K':'厨房','D':'餐厅','LA':'洗衣房','E':'玄关','R':'阅读与公共通路','MH':'主卧通道','MW':'主卫','WC':'客卫','ST':'储物'}
rooms=[r for r in D['rooms'] if r['level']==1 or r['id'] in ['B1','B2','B3']]
boxes={'B3':[7.8,4.4,11,10.2],'B2':[11.2,4.4,14.5,10.2],'B1':[14.7,4.4,18.6,10.2]}
for r in rooms:
 r['name']=names.get(r['id'],r['name'])
 if r['id'] in boxes:r['box']=boxes[r['id']];r['net_area']=round((r['box'][2]-r['box'][0])*(r['box'][3]-r['box'][1]),2)
for id,name,b in [('H2','二楼直走廊',[7.8,2.6,18.6,4.2]),('A','A二楼上平台',[16.96,1.1,18.6,2.6]),('C','C二楼端部地面',[7.8,1.1,9.4,2.6]),('B','B一楼下平台',[7.8,1.1,9.4,2.4]),('WT','西侧屋面露台',[.2,.2,7.6,10.2]),('AB','东侧阳台',[18.8,4.4,21.8,10.2])]:
 rooms.append(dict(id=id,name=name,level=1 if id=='B' else 2,box=b,color='#e2eae6',net_area=round((b[2]-b[0])*(b[3]-b[1]),2)))
D['rooms']=rooms
D['walls']=[w for w in D['walls'] if w['level']==1 and w['id'] not in ['1-STN','1-STS','1-STA']]
D['openings']=[o for o in D['openings'] if o['level']==1]
def wall(id,l,a,b,t=.2):D['walls'].append(dict(id=id,level=l,a=a,b=b,thickness=t))
def opening(id,w,l,a,b,type='window',sill=0,head=2.8,**kw):D['openings'].append(dict(id=id,wall=w,level=l,start=a,end=b,type=type,sill=sill,head=head,**kw))
wall('1-STN',1,[9.4,2.5],[16.96,2.5]);wall('1-STS',1,[9.4,1],[16.96,1]);wall('1-STA',1,[16.96,1],[16.96,2.5])
wall('2-N',2,[7.7,10.3],[18.7,10.3]);wall('2-W',2,[7.7,1],[7.7,10.3]);wall('2-E',2,[18.7,1],[18.7,10.3])
for id,a,b in [('2-B3S',7.7,11.1),('2-B2S',11.1,14.6),('2-B1S',14.6,18.7)]:wall(id,2,[a,4.3],[b,4.3])
wall('2-B3E',2,[11.1,4.3],[11.1,10.3]);wall('2-B12',2,[14.6,4.3],[14.6,10.3])
wall('2-PAR',2,[9.4,2.5],[16.96,2.5],.16);wall('2-STB',2,[9.4,1],[9.4,2.5],.16)
wall('2-STS',2,[7.7,1],[18.7,1])
opening('D205','2-B3S',2,7.95,8.85,'door',head=2.2,side=1)
opening('D204','2-B2S',2,11.85,12.85,'door',head=2.2,side=1)
opening('D203','2-B1S',2,14.95,15.85,'door',head=2.2,side=1)
opening('G202','2-W',2,2.8,4,'glass')
opening('W_C_HIGH','2-STS',2,7.95,9.15,sill=.03)
opening('W_STRIP','2-STS',2,10.05,15.9,sill=.65,head=1.25,panes=1)
opening('W_A_SIDE','2-STS',2,17.2,18.4,sill=.03)
opening('W_A_END','2-E',2,1.15,4.05,sill=.03,head=2.95,panes=1)
opening('G201','2-E',2,5.25,6.45,'glass')
for id,a,b in [('W207',8.6,10.5),('W206',12,14),('W205a',15.1,16.95),('W205b',17.2,18.4)]:opening(id,'2-N',2,a,b,sill=.6)
D['stairs']=dict(footprint=[9.4,1.1,16.96,2.4],A=[16.96,1.1,18.6,2.6],B=[7.8,1.1,9.4,2.4],C=[7.8,1.1,9.4,2.5],rises=22,rise=.15,treads=21,tread=.36)
D['architecture']=dict(void=[9.4,1,16.96,2.5],floor2_rects=[[0,0,9.4,10.4],[16.96,0,22,10.4],[9.4,0,16.96,1],[9.4,2.5,16.96,10.4],[0,-1.4,22,0]],roof_rects=[[7.7,1,18.8,10.4]],guard_height=1.1,guard_cap=.06)
D['exterior_rails']=[[[0,-1.4],[22,-1.4]],[[0,-1.4],[0,10.4]],[[22,-1.4],[22,10.4]],[[18.8,10.4],[22,10.4]],[[18.8,4.4],[22,4.4]],[[18.8,9.6],[18.8,10.4]],[[0,10.4],[7.7,10.4]]]
# Furniture remains recognizable and physical sizes are explicitly chosen, not mesh-scaled.
fboxes={
'A01':[14.8,8,17.05,10.1],'A02':[14.8,7.35,15.4,7.95],'A03':[14.7,5.5,15.1,6.9],
'A04':[17.2,9.55,18.6,10.2],'A05':[17.5,8.8,18.1,9.4],'A06':[18,7.25,18.6,8.55],
'A07':[17.35,7.55,17.9,8.1],'A08':[18.4,6.5,18.6,7.2],'A09':[16,4.4,17.4,5],
'A10':[15.7,5.4,17.9,7.6],'A11':[17.65,4.55,18.4,5.85],'A12':[16.3,7.2,17,7.9],'A13':[15.2,6,16.3,7.1],
'B01':[12.3,5.4,14.5,7.2],'B02':[11.2,5.5,11.65,7.45],'B03':[11.2,8.2,11.85,9.85],
'B04':[12.15,8.6,12.75,9.2],'B05':[13.8,8.9,14.45,10.2],'B06':[14.35,8.25,14.5,8.8],
'B07':[13.9,7.7,14.5,8.1],'B08':[13.4,7.7,13.8,8.15],'B09':[12.9,9.25,13.75,10.15],
'B10':[11.7,7.4,13.7,9.1],'B11':[12.1,7.6,13.3,8.3],'B12':[11.2,4.4,11.7,4.95],'B13':[13.2,4.4,14.4,4.8],
'C01':[9.5,4.4,11,6.6],'C02':[10.3,6.75,11,7.35],'C03':[7.8,7.8,8.45,9.8],
'C04':[8.7,8.4,9.3,9],'C05':[8.6,9.75,10.9,10.2],'C06':[7.8,6.05,8.45,7.6],
'C07':[7.8,5.35,7.98,5.95],'C08':[8.6,7,10.9,9.3],'C09':[8.9,4.4,9.35,5]}
D['furniture']=[f for f in D['furniture'] if f['level']==1 or f['room'] in ['B1','B2','B3']]
changes=[]
for f in D['furniture']:
 if f['id'] in fboxes:
  changes.append(dict(id=f['id'],before=f['box'],after=fboxes[f['id']]))
  f['box']=fboxes[f['id']]
D['furniture_changes']=changes
D['provisional_dimensions']=['层高3.30m，板厚0.22m','22级高差，每级0.15m；21个踏面，每步0.36m，梯段7.56m','走廊净宽1.60m，梯段净宽1.30m','二楼卧室净宽3.20/3.30/3.90m，净深均5.80m；面积18.56/19.14/22.62㎡','护栏沿7.56m洞口布置；大姐床保持2.25×2.10m','二楼体量横向缩短，原西侧空间改为空屋面露台；外景体量需后续校准']
D['unresolved']=['公卫、布草在F4没有已确认位置，本版不新增其房门或补造房间；一楼客卫保留','全套机位覆盖、柜门抽屉状态和正式1080p漫游尚未完成','外立面与屋顶体量受二楼比例调整影响，需后续核对；本版不声称与旧外景尺寸一致']
# Deterministic walk route, camera follows tread elevation, then connects into F1 public area.
D['walk_route']=[dict(pos=p,target=t) for p,t in [([12.35,5,4.9],[12.35,4.3,4.8]),([12.35,3.4,4.9],[16.9,3.4,4.9]),([17.7,3.4,4.9],[17.7,1.75,4.9]),([17.7,1.75,4.9],[9,1.75,2]),([16.96,1.75,4.9],[9,1.75,2])]]
for i in range(21,-1,-1):
 x=9.4+i*.36;z=1.6+(.15*i if i<22 else 3.3)
 D['walk_route'].append(dict(pos=[x,1.75,z],target=[x-1,1.75,z-.3]))
D['walk_route'] += [dict(pos=p,target=t) for p,t in [([8.6,1.75,1.6],[8.6,3.3,1.6]),([8.6,3.4,1.6],[6,4,1.6]),([7.8,4,1.6],[5,4,1.6]),([7.8,6.5,1.6],[7.3,8,1.2]),([4.1,6.5,1.6],[2,8,1.4])]]
D['cameras_override']=[
dict(id='F4_DOWN',room='H2',pos=[17.7,2.05,4.9],target=[8.4,2.7,3.5],lens=26,kind='真实机位'),
dict(id='F4_REVERSE',room='H2',pos=[8.35,3.35,4.9],target=[18.7,3.25,4.9],lens=28,kind='真实机位'),
dict(id='F4_C',room='H2',pos=[11.5,3.4,4.9],target=[7.8,2,4.65],lens=28,kind='真实机位'),
dict(id='F4_UP',room='B',pos=[11.4,1.75,2.5],target=[18.7,1.75,5.1],lens=28,kind='真实机位'),
dict(id='F4_STAIR_DOWN',room='A',pos=[17.7,1.75,4.9],target=[8.6,1.75,1.6],lens=28,kind='真实机位'),
dict(id='F4_B_CONNECT',room='B',pos=[8.6,1.75,1.6],target=[6.8,4.4,1.3],lens=28,kind='真实机位'),
dict(id='F4_PLAN',room='H2',pos=[13.2,5.65,23],target=[13.2,5.65,0],lens=28,kind='顶视检查'),
dict(id='EXT_01',room='外部',pos=[31,-30,23],target=[11,3,2.8],lens=35,kind='真实机位')]
from restore_bedrooms import apply
D=apply(D,old)
(O/'模型/建模方案.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
print('P2.4-M3 source prepared; approved corridor unchanged; bedrooms expanded.')
