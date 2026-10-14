from pathlib import Path
import json,math,csv,shutil
R=Path(__file__).resolve().parents[1]
D={'version':'v4_全屋空间模型_待用户验收','units':'m','axis':'x向项目东，y向项目北；临街南立面在平面图下方。非实测朝向。',
'floor_height':3.3,'door_height':2.2,'notice':'影视场景参考尺寸；中性空间模型，不是施工图。','objects':[],'rooms':[],'walls':[],'openings':[],'furniture':[],'cameras':[],'routes':{},'brands':[]}
COL={'wall':'#e5e8e8','floor':'#acb4b8','wood':'#9c9690','furniture':'#7e8c92','fabric':'#adb5bc','frame':'#384952','glass':'#aac6ce','plant':'#748d85','brand':'#697b89','marker':'#b67f3f'}
def obj(id,box,group,mat='wall',solid=True,kind='box',**kw):
 x,y,z,X,Y,Z=box
 d=dict(id=id,box=box,group=group,color=COL[mat],solid=solid,kind=kind,**kw);D['objects'].append(d);return d
def prism(id,x0,x1,profile,group,mat='wall'):
 n=len(profile);verts=[[x,y,z] for x in [x0,x1] for y,z in profile]
 faces=[list(reversed(range(n))),list(range(n,n*2))]+[[k,(k+1)%n,(k+1)%n+n,k+n] for k in range(n)]
 return obj(id,[x0,min(p[0] for p in profile),min(p[1] for p in profile),x1,max(p[0] for p in profile),max(p[1] for p in profile)],group,mat,kind='mesh',vertices=verts,faces=faces)
def room(id,name,level,box,source,new=False):
 D['rooms'].append(dict(id=id,name=name,level=level,box=box,source=source,new=new))
def wall(id,level,a,b,ops=(),th=.2,height=3.08,base=None,group=None):
 z=(level-1)*3.3 if base is None else base;group=group or f'F{level}_walls';hori=a[1]==b[1];axis=0 if hori else 1
 w=dict(id=id,level=level,a=a,b=b,thickness=th,height=height,z=z,group=group);D['walls'].append(w)
 def segment(s,e,z0,h,suffix,mat='wall'):
  if e-s<.001 or h<.001:return
  bb=[s,a[1]-th/2,z+z0,e,a[1]+th/2,z+z0+h] if hori else [a[0]-th/2,s,z+z0,a[0]+th/2,e,z+z0+h]
  obj(id+'_'+suffix,bb,group,mat)
 cursor=a[axis]
 for j,o in enumerate(sorted(ops,key=lambda o:o['s'])):
  s=o['s'];e=s+o['w'];bottom=o.get('sill',0);top=o.get('head',2.2)
  assert s>=cursor-.001 and e<=b[axis]+.001,(id,o)
  segment(cursor,s,0,height,f'seg{j}')
  segment(s,e,0,bottom,f'{o["id"]}_below')
  segment(s,e,top,height-top,f'{o["id"]}_above')
  rec=dict(o,wall=id,level=level,a=([s,a[1]] if hori else [a[0],s]),b=([e,a[1]] if hori else [a[0],e]),z=z,axis=axis)
  D['openings'].append(rec)
  if o['type']!='open':
   for t in [s,e]:segment(t-.027,t+.027,bottom,top-bottom,o['id']+'_jamb'+str(t),'frame')
   segment(s,e,top-.04,.04,o['id']+'_top','frame')
  if o['type']=='window':
   if o['type']=='window':segment(s,e,bottom,.04,o['id']+'_bottom','frame')
   for k in range(1,o.get('panes',2)):segment(s+(e-s)*k/o.get('panes',2)-.018,s+(e-s)*k/o.get('panes',2)+.018,bottom,top-bottom,o['id']+'_mullion'+str(k),'frame')
   bb=[s,a[1]-.009,z+bottom,e,a[1]+.009,z+top] if hori else [a[0]-.009,s,z+bottom,a[0]+.009,e,z+top]
   obj(o['id']+'_glass',bb,f'F{level}_glass','glass',False,opening=o['id'],opacity=.16 if o['type']=='window' else .1)
  elif o['type']=='slide':
   rec['state']='pocket_open';rec['note']='双向入墙滑门开启；玻璃扇收入墙内，开口不设固定中梃。'
   segment(s,e,top+.01,.035,o['id']+'_track','frame')
  elif o['type']=='door':
   side=o.get('side',1)
   hinge=[s,a[1],z] if hori else [a[0],s,z]
   # Doors are shown at 90 degrees, with a closed-plane and swing arc on the plan.
   bb=[s-.023,a[1]+min(0,side*o['w']),z,s+.023,a[1]+max(0,side*o['w']),z+top-.04] if hori else [a[0]+min(0,side*o['w']),s-.023,z,a[0]+max(0,side*o['w']),s+.023,z+top-.04]
   obj(o['id']+'_leaf',bb,f'F{level}_doors','wood',False,opening=o['id'])
   rec['hinge']=hinge;rec['swing_side']=side
  cursor=e
 segment(cursor,b[axis],0,height,'end')
def op(id,s,w,type='door',**kw):return dict(id=id,s=s,w=w,type=type,**kw)
def furn(id,label,l,b,h=.8,kind='cabinet',rot=0):
 x,y,X,Y=b;z=(l-1)*3.3;g=f'F{l}_furniture'
 D['furniture'].append(dict(id=id,label=label,level=l,box=b,height=h,kind=kind,rotation=rot))
 if kind=='bed':
  obj(id+'_frame',[x,y,z+.15,X,Y,z+.4],g,'wood')
  obj(id+'_mattress',[x+.04,y+.04,z+.4,X-.04,Y-.06,z+.64],g,'fabric')
  head=[x,Y-.12,z+.35,X,Y,z+1.15] if rot==0 else ([x,y,z+.35,X,y+.12,z+1.15] if rot==180 else [x,y,z+.35,x+.12,Y,z+1.15])
  obj(id+'_head',head,g,'wood')
  for i in range(2):
   pillow=[x+.1+i*(X-x)/2,Y-.58,z+.64,x+(i+1)*(X-x)/2-.07,Y-.15,z+.78] if rot==0 else ([x+.1+i*(X-x)/2,y+.15,z+.64,x+(i+1)*(X-x)/2-.07,y+.58,z+.78] if rot==180 else [x+.15,y+.08+i*(Y-y)/2,z+.64,x+.58,y+(i+1)*(Y-y)/2-.07,z+.78])
   obj(id+'_pillow'+str(i),pillow,g,'fabric',False)
 elif kind in ['table','desk','vanity']:
  obj(id+'_top',[x,y,z+h-.07,X,Y,z+h],g,'wood')
  for xx in [x+.07,X-.13]:
   for yy in [y+.07,Y-.13]:obj(id+'_leg'+str(xx)+str(yy),[xx,yy,z,xx+.06,yy+.06,z+h-.07],g,'frame')
 elif kind in ['chair','sofa']:
  obj(id+'_seat',[x,y,z+.33,X,Y,z+.49],g,'fabric')
  obj(id+'_back',[x,Y-.15,z+.49,X,Y,z+.95],g,'fabric')
  for xx in [x+.08,X-.13]:
   for yy in [y+.08,Y-.13]:obj(id+'_leg'+str(xx)+str(yy),[xx,yy,z,xx+.05,yy+.05,z+.35],g,'wood')
 elif kind=='tub':
  obj(id+'_base',[x,y,z+.05,X,Y,z+.18],g,'fabric')
  for suf,bb in [('L',[x,y,z+.18,x+.13,Y,z+.62]),('R',[X-.13,y,z+.18,X,Y,z+.62]),('F',[x,y,z+.18,X,y+.13,z+.62]),('B',[x,Y-.13,z+.18,X,Y,z+.62])]:obj(id+suf,bb,g,'fabric')
 elif kind=='wc':
  obj(id+'_bowl',[x,y,z+.05,X,Y-.22,z+.43],g,'fabric');obj(id+'_tank',[x,Y-.22,z+.2,X,Y,z+.8],g,'fabric')
 elif kind=='plant':
  obj(id+'_pot',[x,y,z,X,Y,z+.4],g,'furniture');obj(id+'_leaves',[x-.05,y-.05,z+.4,X+.05,Y+.05,z+h],g,'plant',False)
 elif kind in ['guitar','telescope','exercise']:
  obj(id+'_identity',[x,y,z,X,Y,z+h],g,'frame')
 else:obj(id,[x,y,z,X,Y,z+h],g,'furniture')
def brand(id,l,b,carrier):
 z=(l-1)*3.3
 obj(id,[b[0],b[1],z+1.55,b[2],b[3],z+1.88],f'F{l}_brands','brand',False,label='黄瓜短剧·位置占位')
 D['brands'].append(dict(id=id,level=l,carrier=carrier,box=b,center_height=1.715,width=max(b[2]-b[0],b[3]-b[1])))
# FLOOR SURFACES: same footprints are used by drawings, render, and route checks.
slabs={1:[[0,0,10.8,5.5],[0,5.5,11,6],[0,6,14.2,16]],2:[[0,0,10.8,1.7],[1.8,1.7,10.8,7.02],[0,7.02,10.8,12.9],[10.8,11.4,14.2,12.9],[7.4,12.9,14.2,16],[10.8,5.5,11,6]]}
D['slabs']=slabs;D['outdoor_slabs']=[[0,-1.6,10.8,0],[0,12.9,7.4,16],[10.8,6,14.2,11.4]]
for l,arr in slabs.items():
 for i,b in enumerate(arr):obj(f'F{l}_SLAB_{i}',[b[0],b[1],(l-1)*3.3-.22,b[2],b[3],(l-1)*3.3],f'F{l}_slabs','floor')
for i,b in enumerate(D['outdoor_slabs']):obj('F2_OUTDOOR_'+str(i),[b[0],b[1],3.08,b[2],b[3],3.3],'F2_slabs','floor')
obj('SITE_ground',[-2,-6,-.45,16.2,18,-.25],'Site','floor',False)
# FIRST FLOOR ROOMS
for a in [
('R101','客厅',[3.4,0,10.8,5.5],'客厅/客厅_前视图.png',False),
('R102','餐厅',[3.4,5.5,7.6,9.2],'餐厅/餐厅_前视图.png',False),
('R103','厨房',[3.4,12.3,7.6,16],'厨房/厨房_俯拍图.png',False),
('R104','洗衣房',[0,12.3,3.4,16],'周家洗衣房.jpeg',False),
('R105','餐厨前厅与家政',[3.4,9.2,7.6,12.3],'补充连接',True),
('R106','主卧独立走廊',[7.6,9.2,9.2,16],'阿姨卧室/一楼走廊到主卧（正面视角）.png',False),
('R107','主卧',[9.2,9.2,14.2,14.4],'阿姨卧室/主卧与浴室_联合俯视_门洞对齐.png',False),
('R108','主卫',[11,6,14.2,9.2],'阿姨卧室/浴室/主卧浴室_俯拍.png',False),
('R109','客卫',[0,9,1.8,11.3],'新增功能',True),
('R110','公共走廊',[1.8,1.7,3.4,12.3],'漫画动线',True),
('R111','玄关',[0,0,3.4,1.7],'别墅玄关/别墅玄关.png',False),
('R112','楼梯B端落地平台',[0,7.02,1.8,9],'漫画下楼',True),
('R113','阅读角',[7.6,5.5,11,9.2],'公共区补充',True),
('R114','主卧门前廊',[9.2,14.4,14.2,16],'门前转接',True)]:
 room(a[0],a[1],1,a[2],a[3],a[4])
# 1F shell
wall('F1_WEST',1,[0,0],[0,16],[op('W101',7.45,1.1,'window',sill=.8,head=2.6),op('W102',13.3,1.9,'window',sill=1.05,head=2.65)])
wall('F1_SOUTH',1,[0,0],[10.8,0],[op('D101',2.05,1.1,side=1),op('W103',4.5,4.9,'window',sill=.45,head=2.8)])
wall('F1_EAST_FRONT',1,[10.8,0],[10.8,5.5],[op('W104',1.2,3.0,'window',sill=.45,head=2.8)])
wall('F1_READING_FRONT',1,[7.6,5.5],[11,5.5],[op('O110',8.3,1.7,'open',head=2.8)])
wall('F1_READING_E',1,[11,5.5],[11,9.2])
wall('F1_BATH_S',1,[11,6],[14.2,6],[op('W107',11.7,1.8,'window',sill=1.45,head=2.1)])
wall('F1_EAST_REAR',1,[14.2,6],[14.2,16],[op('W108',10.0,3.9,'window',sill=.45,head=2.75)])
wall('F1_NORTH',1,[0,16],[14.2,16],[op('W109',.6,2.0,'window',sill=1.05,head=2.65),op('W110',4.3,1.8,'window',sill=1.1,head=2.6)])
# Walls separating circulation from rooms
wall('F1_HALL_E',1,[3.4,0],[3.4,12.3],[op('O101',.2,1.4,'open',head=2.8),op('O102',3.4,1.7,'open',head=2.8),op('O103',7.15,1.65,'open',head=2.8),op('O104',10.55,1.4,'open',head=2.8)])
wall('F1_TV_DIVIDER',1,[3.4,5.5],[7.6,5.5],[op('O105',3.65,1.0,'open',head=2.8),op('O106',6.35,1.0,'open',head=2.8)])
wall('F1_DIN_KIT',1,[3.4,9.2],[7.6,9.2],[op('O107',4.0,2.8,'open',head=2.8)])
wall('F1_DIN_READING',1,[7.6,5.5],[7.6,9.2],[op('O108',6.8,1.7,'open',head=2.8)])
wall('F1_KIT_PRIVATE',1,[7.6,9.2],[7.6,16])
wall('F1_KIT_UTILITY',1,[3.4,12.3],[7.6,12.3],[op('D103',5.3,1.1,'slide')])
wall('F1_LAUNDRY_S',1,[0,12.3],[3.4,12.3],[op('D104',2.1,1.0,side=1)])
wall('F1_LAUNDRY_E',1,[3.4,12.3],[3.4,16])
wall('F1_GWC_E',1,[1.8,9],[1.8,11.3],[op('D105',9.7,.9,side=-1)])
wall('F1_GWC_S',1,[0,9],[1.8,9]);wall('F1_GWC_N',1,[0,11.3],[1.8,11.3])
wall('F1_MASTER_W',1,[9.2,9.2],[9.2,14.4])
wall('F1_MASTER_N',1,[9.2,14.4],[14.2,14.4],[op('D106',9.4,.95,side=-1)])
wall('F1_MASTER_S',1,[9.2,9.2],[14.2,9.2],[op('D107',12.4,.95,side=-1)])
# 2F room list
for a in [
('R201','大姐卧室',[3.4,0,10.8,3.8],'大姐卧室/大姐卧室_俯拍视角.png',False),
('R202','男主卧室',[3.4,3.8,10.8,7.6],'男主卧室/男主卧室俯拍视角.png',False),
('R203','二姐卧室',[3.4,7.6,10.8,11.4],'二姐卧室/二姐房间_正视图.png',False),
('R204','公用浴室',[10.7,12.9,14.2,16],'新增功能',True),
('R205','布草储物',[7.4,12.9,10.7,16],'新增功能',True),
('R206','二楼并排走廊',[1.8,1.7,3.4,12.9],'别墅楼道和楼梯间参考/别墅二楼到楼梯间参考图.png',False),
('R207','A端上平台',[0,0,3.4,1.7],'别墅楼道和楼梯间参考/别墅楼梯间参考.png',False),
('R208','二楼服务过厅',[3.4,11.4,14.2,12.9],'补充公共卫浴通路',True),
('R209','后露台',[0,12.9,7.4,16],'尽头玻璃门去掉额外台阶',False),
('R210','侧露台',[10.8,6,14.2,11.4],'别墅外景参考/别墅俯拍视角.png',False),
('R211','临街阳台',[0,-1.6,10.8,0],'别墅外景参考/别墅正面视角.png',False)]:
 room(a[0],a[1],2,a[2],a[3],a[4])
# 2F shell, tight stair opening only
wall('F2_SOUTH',2,[0,0],[10.8,0],[op('W201',.2,1.3,'window',sill=.15,head=2.8),op('D201',1.95,1.15,'slide',head=2.8),op('D202',5.1,2.4,'slide',head=2.8)])
wall('F2_WEST',2,[0,0],[0,12.9],[op('W202',2.2,2.8,'window',sill=.45,head=1.02,panes=1),op('W203',7.3,.9,'window',sill=.15,head=2.8,panes=1),op('W204',10.9,1.0,'window',sill=.85,head=2.6)])
wall('F2_EAST_MAIN',2,[10.8,0],[10.8,11.4],[op('W205',.9,2.0,'window',sill=.7,head=2.7),op('W206',4.1,2.9,'window',sill=.65,head=2.7),op('W207',8.0,2.8,'window',sill=.65,head=2.7)])
wall('F2_BEDROOM_W',2,[3.4,0],[3.4,12.9],[op('D203',2.55,.95,side=1),op('D204',5.35,.95,side=1),op('D205',10.25,.95,side=1),op('O201',11.5,1.3,'open',head=2.8)])
wall('F2_BED_SPLIT1',2,[3.4,3.8],[10.8,3.8]);wall('F2_BED_SPLIT2',2,[3.4,7.6],[10.8,7.6]);wall('F2_BED_N',2,[3.4,11.4],[10.8,11.4])
wall('F2_TERRACE_DOOR',2,[0,12.9],[7.4,12.9],[op('D206',1.95,1.2,'slide',head=2.6),op('W208',4.1,2.3,'window',sill=.6,head=2.6)])
wall('F2_SERVICE_S',2,[10.8,11.4],[14.2,11.4],[op('D207',11.6,1.5,'slide',head=2.6)])
wall('F2_SERVICE_E',2,[14.2,11.4],[14.2,16],[op('W209',13.8,1.3,'window',sill=1.5,head=2.6)])
wall('F2_SERVICE_N',2,[7.4,16],[14.2,16],[op('W210',11.2,2.2,'window',sill=1.4,head=2.5)])
wall('F2_SERVICE_W',2,[7.4,12.9],[7.4,16])
wall('F2_UTILITY_ENTRY',2,[7.4,12.9],[14.2,12.9],[op('D208',8.0,.9,side=1),op('D209',11.25,.95,side=1)])
wall('F2_BATH_LINEN',2,[10.7,12.9],[10.7,16])
# Structural stair: A SOUTH HIGH -> B NORTH LOW.
D['stairs']={'id':'STAIR01','A':[.85,.9,3.3],'B':[.85,7.9,0],'flight':[.2,1.7,1.5,7.02],'rise':.165,'tread':.28,'risers':20,'treads':19,'upper_void':[0,1.7,1.8,7.02],'clear_width':1.3,'direction_down':'A→B，+y'}
profile=[(1.7,3.3)]
for k in range(19):
 y=1.7+k*.28;h=3.3-(k+1)*.165
 profile.extend([(y,h-.03),(y+.28,h-.03)])
 obj(f'STAIR_tread_{k+1:02d}',[.2,y,h-.03,1.5,y+.28,h],'Stairs','wood')
profile.extend([(7.02,0),(7.02,-.20),(1.7,2.91)])
prism('STAIR_continuous_concrete_slab',.2,1.5,profile,'Stairs')
obj('STAIR_upper_bearing',[.1,1.48,2.86,1.8,1.72,3.08],'Stairs')
obj('STAIR_lower_bearing',[.1,7.0,-.22,1.8,7.3,0],'Stairs')
wall('STAIR_corridor_support',1,[1.65,1.7],[1.65,7.02],th=.3,height=3.3,group='Stairs')
wall('STAIR_F2_guard',2,[1.65,1.7],[1.65,7.02],th=.3,height=1.1,group='F2_guard')
obj('STAIR_guard_woodcap',[1.48,1.7,4.4,1.82,7.02,4.46],'F2_guard','wood')
# Guard across B edge of floor opening; this is NOT another stair entrance.
wall('STAIR_B_void_guard',2,[0,7.12],[1.65,7.12],th=.2,height=1.1,group='F2_guard')
obj('STAIR_B_guard_cap',[-.03,7.0,4.4,1.82,7.24,4.46],'F2_guard','wood')
# Wall-mounted handrails with real brackets, continuous diagonal supports.
for x in [.14,1.47]:
 o=obj('STAIR_handhold_'+str(x),[x-.03,1.7,.92,x+.03,7.02,4.115],'Stairs','wood',False,kind='bar',a=[x,1.7,4.085],b=[x,7.02,.95],radius=.03)
 for k in range(0,19,4):
  y=1.7+k*.28;z=4.085-(.165/.28)*(y-1.7)
  obj(f'RAIL_bracket_{x}_{k}',[x-.05,y-.025,z-.12,x+.05,y+.025,z],'Stairs','frame',False)
# Roof and service screen; no additional staircase.
for i,b in enumerate([[0,0,10.8,12.9],[10.8,11.4,14.2,12.9],[7.4,12.9,14.2,16]]):
 obj('ROOF_'+str(i),[b[0],b[1],6.38,b[2],b[3],6.62],'Roof','floor')
obj('ROOF_equipment_screen',[7.7,9,6.62,10,11,7.35],'Roof','frame')
# Balcony / terrace rails are independent of staircase.
def railing(id,a,b):
 z=3.3;dx=b[0]-a[0];dy=b[1]-a[1];n=max(1,math.ceil(math.hypot(dx,dy)/1.2))
 for k in range(n+1):
  x=a[0]+dx*k/n;y=a[1]+dy*k/n
  obj(id+'_post'+str(k),[x-.03,y-.03,z,x+.03,y+.03,z+1.1],'F2_rails','frame')
 for k in range(5):
  zz=z+.15+k*.23
  obj(id+'_rail'+str(k),[min(a[0],b[0])-.02,min(a[1],b[1])-.02,zz,max(a[0],b[0])+.02,max(a[1],b[1])+.02,zz+.04],'F2_rails','frame')
for i,(a,b) in enumerate([([0,-1.6],[10.8,-1.6]),([0,-1.6],[0,0]),([10.8,-1.6],[10.8,0]),([0,12.9],[0,16]),([0,16],[7.4,16]),([10.8,6],[14.2,6]),([14.2,6],[14.2,11.4])]):railing('OUT_R'+str(i),a,b)
# Furniture and room identities (geometry only).
furn('F101','浅灰L沙发',1,[6.0,.6,9.7,1.5],kind='sofa')
furn('F102','沙发贵妃位',1,[8.8,1.45,9.7,2.8],kind='sofa')
furn('F103','玻璃茶几占位',1,[6.2,2.3,8.3,3.3],h=.43,kind='table')
furn('F104','白色电视隔断',1,[4.7,5.26,6.25,5.47],h=2.1)
furn('F105','客厅地毯',1,[5.7,1.7,9.1,4.5],h=.015)
furn('F106','客厅绿植',1,[9.95,.45,10.4,.9],h=1.3,kind='plant')
furn('F107','餐桌',1,[4.75,6.45,6.75,7.45],h=.76,kind='table')
for k,(x,y) in enumerate([(4.8,5.8),(6.1,5.8),(4.8,7.65),(6.1,7.65),(4.05,6.68),(6.95,6.68)]):furn('DIN_C'+str(k),'餐椅',1,[x,y,x+.48,y+.5],kind='chair')
for i,b in enumerate([[3.6,15.3,7.35,15.85],[3.6,13.5,4.2,15.3],[6.75,13.5,7.35,15.3],[6.2,12.7,7.35,13.3]]):furn('K_COUNTER'+str(i),'厨房围合台面',1,b,h=.9)
furn('K_FRIDGE','冰箱',1,[3.6,12.55,4.35,13.4],h=1.85)
furn('K_SINK','水槽·对外窗下',1,[4.6,15.34,5.8,15.78],h=.93)
furn('L_WASHER','洗衣机',1,[.25,14.6,1.0,15.4],h=.85)
furn('L_DRYER','烘干机',1,[.25,13.65,1.0,14.45],h=.85)
furn('L_COUNTER','洗衣收纳台',1,[1.25,15.25,3.1,15.8],h=.9)
furn('L_BASKET','洗衣篮',1,[1.4,13.8,2.0,14.4],h=.6)
furn('L_STORAGE','家政收纳柜',1,[3.65,9.5,4.3,10.5],h=2.25)
furn('L_FOLD','家政整理台',1,[6.5,10.7,7.35,11.8],h=.9,kind='table')
furn('G_WC','客卫坐便',1,[.2,9.15,.75,9.8],kind='wc')
furn('G_SINK','客卫台盆',1,[.25,10.65,1.15,11.1],h=.85)
furn('MASTER_BED','主卧床·酒红床品身份',1,[11.0,11.2,13.15,13.6],kind='bed')
furn('M_BEDSIDE1','主卧床头柜',1,[10.45,13,10.95,13.65],h=.62)
furn('M_BEDSIDE2','主卧床头柜',1,[13.25,13,13.8,13.65],h=.62)
furn('M_WARDROBE','主卧原衣柜',1,[9.35,11.1,9.85,12.8],h=2.2)
furn('M_VANITY','深木梳妆台',1,[9.35,9.5,10.65,10.05],h=.78,kind='vanity')
furn('M_TUB','主卫浴缸',1,[11.3,6.25,13.5,7.0],kind='tub')
furn('M_WC','主卫坐便',1,[13.35,7.15,14.0,7.95],kind='wc')
furn('M_SINK','主卫木台盆柜',1,[11.15,7.55,11.7,8.55],h=.85)
furn('READ_C','阅读椅',1,[9.4,6.1,10.2,6.9],kind='chair')
furn('READ_BOOK','阅读书架',1,[10.4,7.2,10.85,8.7],h=2.0)
furn('ENTRY_C','玄关柜',1,[.2,.3,1.5,.7],h=.9)
for l,id,name,bed in [(2,'E','大姐',[6.3,1.15,8.4,3.45]),(2,'M','男主',[6.0,4.05,8.0,6.35]),(2,'Y','二姐',[3.65,7.8,5.95,8.95])]:
 furn(id+'_BED',name+'床位',l,bed,kind='bed',rot={'E':0,'M':180,'Y':90}[id])
furn('E_WARD','大姐衣柜',2,[3.65,.2,4.35,1.8],h=2.25)
furn('E_VANITY','大姐梳妆区',2,[8.4,.15,9.65,.7],h=.78,kind='vanity')
furn('E_BIKE','大姐运动器材',2,[9.8,.2,10.5,1.4],h=1.25,kind='exercise')
furn('E_DESK','大姐窗边工作区',2,[9.95,1.65,10.55,3.5],h=.76,kind='desk')
furn('E_BOOK','大姐书架',2,[4.6,3.15,6.0,3.65],h=1.6)
furn('E_RUG','粉色圆毯范围占位',2,[6.0,.8,7.5,2.3],h=.02)
furn('M_DESK','男主工作区',2,[8.2,6.9,10.2,7.45],h=.76,kind='desk')
furn('M_WARD','男主衣柜',2,[9.65,4.05,10.4,5.1],h=2.25)
furn('M_TELESCOPE','望远镜',2,[10.0,5.8,10.5,6.3],h=1.3,kind='telescope')
furn('M_GUITAR','吉他',2,[8.15,4.05,8.4,4.35],h=1.05,kind='guitar')
furn('M_TV','男主电视柜',2,[5.8,7.18,7.8,7.5],h=.75)
furn('M_COFFEE','男主矮茶几',2,[6.25,6.55,7.4,6.95],h=.38,kind='table')
furn('Y_DESK','二姐电脑工作区·与床头和房门同墙',2,[3.65,9.0,4.25,10.2],h=.76,kind='desk')
furn('Y_DRAWERS','二姐衣物柜',2,[6.0,10.65,8.0,11.2],h=.85)
furn('Y_COLLECTION','二姐窗下收藏柜',2,[10.1,8.3,10.65,10.8],h=.8)
furn('Y_RUG','星形图案地毯范围',2,[6.1,9.1,7.6,10.6],h=.02)
furn('U_SINK','公用浴室台盆',2,[10.9,14.2,11.55,15.4],h=.85)
furn('U_WC','公用浴室坐便',2,[13.2,13.2,13.9,14],kind='wc')
furn('U_SHOWER','公用浴室淋浴底盘',2,[12.4,14.65,14.0,15.8],h=.08)
furn('LIN_SHELF1','布草架',2,[7.6,14.1,8.1,15.8],h=2.2)
furn('LIN_SHELF2','布草架',2,[9.9,13.3,10.5,15.8],h=2.2)
furn('BAL_C','阳台藤椅',2,[8.6,-1.3,9.25,-.6],kind='chair')
furn('BAL_P','阳台盆栽',2,[9.7,-1.2,10.2,-.7],h=1.2,kind='plant')
furn('TER_SOFA','后露台沙发',2,[1.0,14.85,3.8,15.75],kind='sofa')
furn('TER_C','后露台单椅',2,[4.5,14.85,5.4,15.75],kind='chair')
furn('TER_TABLE','后露台茶几',2,[1.8,13.7,3.6,14.4],h=.45,kind='table')
furn('TER_P','后露台盆栽',2,[6.2,15.1,6.8,15.7],h=1.3,kind='plant')
furn('SIDE_P','侧露台盆栽',2,[13.3,6.4,13.8,6.9],h=1.3,kind='plant')
# Brand carriers are only placeholders in this neutral review.
for a in [('BR_ENTRY',1,[.3,.105,1.3,.13],'玄关墙'),('BR_LIVING',1,[4.85,5.23,6.05,5.26],'电视隔断'),
('BR_DIN',1,[7.46,5.8,7.49,6.7],'餐厅侧墙'),('BR_KIT',1,[6.2,15.87,7.2,15.9],'厨房柜上墙'),
('BR_LAUNDRY',1,[3.26,14.0,3.29,15.5],'洗衣房东侧实墙'),('BR_MASTER',1,[10.6,14.26,11.8,14.29],'床头墙'),
('BR_MBA',1,[14.07,7.2,14.1,8.0],'主卫干区'),('BR_GWC',1,[.105,10.1,.13,10.7],'客卫干区'),
('BR_STAIR',1,[.3,8.87,1.35,8.9],'一楼B端落地墙'),('BR_HALL',2,[3.26,4.1,3.29,5.1],'大姐与男主门间'),
('BR_ELDER',2,[5.1,3.67,6.2,3.7],'梳妆区墙'),('BR_MALE',2,[4.8,7.47,5.9,7.5],'衣柜旁墙'),
('BR_YOUNGER',2,[3.51,9.3,3.54,10.05],'电脑区墙'),('BR_UBA',2,[14.06,13.0,14.09,13.7],'公用浴室干区实墙'),
('BR_LIN',2,[10.56,14.3,10.59,15.1],'布草柜端'),('BR_BAL',2,[8.0,-.13,9,-.105],'阳台实体墙'),
('BR_TER',2,[7.27,14,7.3,15.2],'后露台侧墙'),('BR_SIDE',2,[10.91,7.25,10.94,7.95],'侧露台窗间实墙'),
('BR_PRIVATE',1,[9.06,10.2,9.09,11.4],'主卧独立走廊墙'),('BR_PUBLIC',1,[3.26,5.65,3.29,6.8],'一楼公共走廊墙'),
('BR_HOUSEKEEP',1,[7.46,10.1,7.49,11.2],'家政前厅墙'),('BR_READING',1,[10.86,5.75,10.89,6.8],'阅读角侧墙'),
('BR_EXTERIOR',1,[.45,-.13,1.65,-.105],'室外入户门旁墙')]:brand(*a)
# Cameras explicitly defined in the same coordinates. Source images are comparisons only.
def cam(id,name,pos,target,lens=24,mode='all',ref=None):
 D['cameras'].append(dict(id=id,name=name,pos=pos,target=target,lens=lens,mode=mode,ref=ref))
cam('C01','参考图4：A端看卧室走廊与下楼口',[1.0,.4,4.9],[2.2,7.0,3.0],20,'all','别墅二楼到楼梯间参考图.png')
cam('C02','参考图5：B端回看A端大窗',[2.65,10.1,4.95],[2.05,.5,4.7],24,'all','别墅二楼走廊.png')
cam('C03','参考图6：B端楼梯向上看A平台',[.85,7.85,1.62],[.85,.65,4.0],22,'all','别墅楼梯间参考.png')
cam('C04','一楼B端落地与餐厨出口',[.9,7.85,1.62],[5.2,7.6,1.35],22)
cam('C05','餐厅回看楼梯落地',[6.75,8.3,1.62],[.8,7.75,1.2],24)
cam('C06','一楼主卧套房',[13.7,9.75,1.7],[10.8,13.3,1.0],24)
cam('C07','厨房：水槽对外窗与围合台面',[5.6,12.7,1.62],[5.5,15.5,1.1],24)
cam('C08','洗衣房：独立房间与设备占地',[2.6,12.75,1.62],[1.4,15.3,1.1],24)
cam('C09','男主卧室：床位与工作区',[4.4,6.0,4.92],[8.5,5.5,4.2],24)
cam('C10','大姐卧室：床位与梳妆运动区',[4.4,2.9,4.92],[8.5,2,4.2],24)
cam('C11','二姐卧室：床头、书桌与房门',[6.4,10.1,4.92],[3.85,8.95,4.2],24)
cam('AX1','一楼俯视剖切',[20,-18,23],[6.5,7,0],42,'floor1')
cam('AX2','二楼俯视剖切',[20,-18,27],[6.5,7,3.3],42,'floor2')
cam('AXS','楼梯纵向剖切·剖去西侧外墙',[-12,4.3,7.8],[1.5,4.3,2.4],38,'stairs')
cam('EXT','建筑体量核对',[22,-24,14],[6,7,2.7],42,'exterior')
cam('EXT_E','建筑侧面开口核对',[29,5,12],[7,8,2.8],42,'exterior')
cam('EXT_N','建筑后侧与露台核对',[22,30,16],[7,8,2.8],42,'exterior')
cam('EXT_TOP','建筑屋顶及平台边界',[17,-5,34],[7,8,0],42,'exterior')
# Continuous walking eye path: on the same built floor, no jump cuts.
route=[[4.4,5.82,4.92],[3.95,5.82,4.92],[2.6,5.82,4.92],[2.6,.85,4.92],[.85,.85,4.92],[.85,1.56,4.92]]
for k in range(19):route.append([.85,1.7+(k+.5)*.28,3.3-(k+1)*.165+1.62])
route.extend([[.85,7.62,1.62],[2.6,7.62,1.62],[4.35,7.62,1.62],[4.35,8.5,1.62],[5.15,8.5,1.62],[5.15,10.65,1.62],[5.85,11.5,1.62],[5.85,14.3,1.62]])
D['routes']={'forward':route,'reverse':list(reversed(route))}
D['review_required']=['已确定：走廊尽头玻璃门直通露台，取消额外台阶。','外立面保留浅墙、黑框、平屋顶和栏杆的体量语言；原外景与楼梯外窗不能同时逐窗复原，开口映射需用户核对。','主卧套房采用联合俯视图的入口床头侧/主卫床尾侧关系。','原始楼梯向上图的斜向木压顶与二楼走廊水平实体护栏存在表达差异，本模型采用水平实体护栏加梯段侧墙扶手。','新空间布局改变了旧露台与阳台家具的世界坐标；现有图片不自动作为本模型的反向视角证明。']
(R/'模型/空间主数据_v4.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
for key in ['rooms','openings','furniture','cameras','brands']:
 arr=D[key];keys=sorted(set(k for r in arr for k in r))
 with (R/'校验'/f'{key}.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows({k:json.dumps(v,ensure_ascii=False) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in arr)
print('SCENE',len(D['objects']),'objects',len(D['rooms']),'rooms',len(D['openings']),'openings')
