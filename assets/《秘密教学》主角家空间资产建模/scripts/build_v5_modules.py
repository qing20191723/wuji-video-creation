"""V3-driven room calibration with a provisional courtyard whole-house assembly.
All geometry, previews and dimension checks consume this one JSON.
Lengths are film-design estimates in metres, not survey/construction data.
"""
import json, math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
D={'version':'v5.0-reference-calibration','status':'room_modules_and_site_study_not_assembled',
   'units':'metres; 影视场景设计参考尺寸', 'modules':[], 'objects':[], 'openings':[], 'cameras':[], 'checks':[]}
M=None; serial=0
C={'wall':'#eee9e5','wood':'#c8ae8c','white':'#eeeef0','dark':'#34363b','glass':'#9dc5d0','floor':'#d4bea1','cloth':'#9c9da1'}
def module(id,name,w,h,refs,note=''):
 global M
 M={'id':id,'name':name,'width':w,'depth':h,'height':3.08,'references':refs,'note':note,'assembly':'independent_local_coordinates'}
 D['modules'].append(M)
def box(id,b,color='white',role='furniture',label=None):
 global serial
 serial+=1; col=C.get(color,color)
 o={'id':M['id']+'_'+id,'module':M['id'],'kind':'box','box':b,'color':col,'role':role,'label':label or id}
 D['objects'].append(o);return o
def cyl(id,x,y,z,r,h,color='wood',role='furniture'):
 o=box(id,[x-r,y-r,z,x+r,y+r,z+h],color,role);o.update(kind='cylinder',radius=r);return o
def ell(id,b,color='cloth',role='furniture'):
 o=box(id,b,color,role);o['kind']='ellipsoid';return o
def line(id,a,b,r=.025,color='dark',role='furniture'):
 o=box(id,[min(a[k],b[k])-r for k in range(3)]+[max(a[k],b[k])+r for k in range(3)],color,role);o.update(kind='bar',a=a,b=b,radius=r);return o
def camera(id,name,pos,target,lens=24,cut=False):
 D['cameras'].append({'id':M['id']+'_'+id,'module':M['id'],'name':name,'pos':pos,'target':target,'lens':lens,'cutaway':cut})
def wall(id,axis,p,start,end,opens=(),z=0,height=3.08,thick=.18,color='wall'):
 # Openings: offset, width, sill, head, type. Wall height is never truncated.
 opens=sorted(opens,key=lambda a:a[0]);cur=start
 def segment(n,lo,hi,bottom,top,clr=color,role='wall'):
  if hi-lo<.001 or top-bottom<.001:return
  b=[lo,p-thick/2,bottom,hi,p+thick/2,top] if axis=='x' else [p-thick/2,lo,bottom,p+thick/2,hi,top]
  return box(id+'_'+n,b,clr,role)
 for i,(off,width,sill,head,typ) in enumerate(opens):
  assert off>=cur-1e-6 and off+width<=end+1e-6,(id,off,cur,end)
  segment(str(i)+'solid',cur,off,z,z+height);segment(str(i)+'below',off,off+width,z,z+sill);segment(str(i)+'above',off,off+width,z+head,z+height)
  oid=M['id']+'_'+id+'_O'+str(i)
  D['openings'].append({'id':oid,'module':M['id'],'axis':axis,'plane':p,'start':off,'width':width,'sill':z+sill,'head':z+head,'type':typ})
  if typ in ('window','slider'):
   segment(str(i)+'glass',off,off+width,z+sill,z+head,'glass','glass')
   for j,s in enumerate([off,off+width/2,off+width-.045]):segment(str(i)+'mull'+str(j),s,s+.045,z+sill,z+head,'dark','frame')
   segment(str(i)+'bottom',off,off+width,z+sill,z+sill+.045,'dark','frame');segment(str(i)+'top',off,off+width,z+head-.045,z+head,'dark','frame')
  elif typ=='door':
   segment(str(i)+'door',off+.025,off+width-.025,z+.025,z+head-.025,'wood','door')
   for j,s in enumerate([off-.05,off+width]):segment(str(i)+'jamb'+str(j),s,s+.05,z,z+head+.05,'wood','frame')
   segment(str(i)+'lintel',off-.05,off+width+.05,z+head,z+head+.06,'wood','frame')
  cur=off+width
 segment('end',cur,end,z,z+height)
def room(w,h,opens=None,wallcolor='wall'):
 opens=opens or {};box('floor',[-.1,-.1,-.18,w+.1,h+.1,0],'floor','floor')
 for side,axis,p,end in [('S','x',0,w),('N','x',h,w),('W','y',0,h),('E','y',w,h)]:wall(side,axis,p,0,end,opens.get(side,()),color=wallcolor)
 box('ceiling',[-.1,-.1,3.08,w+.1,h+.1,3.26],'white','ceiling')
def table(id,x,y,w,d,h=.75,glass=False):
 box(id+'_top',[x,y,h-.05,x+w,y+d,h],'glass' if glass else 'wood','table')
 for i,(a,b) in enumerate([(x+.07,y+.07),(x+w-.12,y+.07),(x+.07,y+d-.12),(x+w-.12,y+d-.12)]):box(id+'_leg'+str(i),[a,b,0,a+.05,b+.05,h-.05],'wood')
def plant(id,x,y,z=.0,scale=1):
 cyl(id+'_pot',x,y,z,.13*scale,.22*scale,'#d8d2c9');ell(id+'_leaves',[x-.25*scale,y-.25*scale,z+.2*scale,x+.25*scale,y+.25*scale,z+.65*scale],'#71926d','decor')
def chair(id,x,y,angle=0,color='white'):
 box(id+'_seat',[x-.25,y-.25,.43,x+.25,y+.25,.49],color)
 # Back on +Y, or -Y / X as needed.
 if angle==90:box(id+'_back',[x+.2,y-.25,.49,x+.25,y+.25,.95],color)
 elif angle==-90:box(id+'_back',[x-.25,y-.25,.49,x-.2,y+.25,.95],color)
 else:box(id+'_back',[x-.25,y+(.2 if angle==0 else -.25),.49,x+.25,y+(.25 if angle==0 else -.2),.95],color)
 for i,(dx,dy) in enumerate([(-.2,-.2),(.2,-.2),(-.2,.2),(.2,.2)]):line(id+'_leg'+str(i),[x+dx,y+dy,0],[x+dx,y+dy,.43],.025)
def shelf(id,x,y,w,d,h=2.45):
 box(id+'_back',[x,y+d-.03,0,x+w,y+d,h]);box(id+'_L',[x,y,0,x+.04,y+d,h]);box(id+'_R',[x+w-.04,y,0,x+w,y+d,h])
 for k in range(6):
  z=k*(h-.04)/5;box(id+'_shelf'+str(k),[x,y,z,x+w,y+d,z+.035])
  if k<5:
   for j in range(4):box(id+f'_book{k}_{j}',[x+.09+j*.085,y+.07,z+.035,x+.14+j*.085,y+d-.08,z+.28],['#e3d7c4','#8d9899','#ab9c8b','#d7c6b4'][j],'decor')
def plaque(id,b,text='黄瓜短剧'):
 o=box(id,b,'#272a2a','brand',text);o['text']=text;o['note']='文字位置载体；正式金白图标尚未作为此中性模型材质'
def check(name,actual,minimum,ids,note=''):
 D['checks'].append({'module':M['id'],'name':name,'actual_m':round(actual,3),'design_minimum_m':minimum,'pass':actual>=minimum,'objects':ids,'note':note,'scope':'design_clearance_not_building_code'})

# Elder bedroom: source overhead image top = local +Y. No mirrored layout.
module('E','大姐卧室 · 原图独立校准',6.4,6.2,['V3_042','V3_043','V3_045','V3_047'],'窗墙与旧串联卧室拼接冲突；本模块不挪窗迁就旧外壳。')
room(6.4,6.2,{'W':[(.25,1.0,0,2.2,'door')],'N':[(.55,2.35,.85,2.65,'window'),(3.5,2.4,.85,2.65,'window')],'E':[(1.15,1.9,0,2.65,'slider')]},'#e6d9d5')
box('bed_base',[.23,3.8,.08,2.46,5.8,.32]);box('mattress',[.27,3.83,.32,2.43,5.77,.57],'cloth','bed');box('head_ledge',[.1,3.73,0,.29,5.88,1.02]);box('duvet',[.7,3.81,.57,2.47,5.81,.64],'#a3a4a9','bed')
for i,y in enumerate([3.85,4.85]):ell('green_pillow'+str(i),[.3,y,.62,.88,y+.86,.86],'#446665')
ell('pink_pillow',[.65,4.4,.67,1.04,5.1,.87],'#be7c8b')
box('bedside',[.1,3.1,0,.65,3.65,.56],'wood');plant('bedside_plant',.39,3.4,.56,.55)
# Bookcase faces +X, physically constructed with horizontal shelves and books.
box('bookcase_back',[.02,1.83,0,.06,3.02,2.5]);box('bookcase_side1',[.02,1.83,0,.37,1.87,2.5]);box('bookcase_side2',[.02,2.98,0,.37,3.02,2.5])
for k in range(6):
 z=k*.49;box('bookcase_shelf'+str(k),[.02,1.83,z,.37,3.02,z+.04])
 if k<5:
  for j in range(7):box(f'book_{k}_{j}',[.07,1.9+j*.12,z+.04,.3,1.97+j*.12,z+.31],['#c2b3a0','#e1d6c8','#9ba3a2'][j%3],'decor')
plant('bookcase_trailing',.2,2.7,2.5,.65)
table('desk',3.45,5.5,2.4,.65);box('desk_drawers',[5.27,5.54,0,5.81,6.1,.7]);box('monitor',[4.15,5.94,.88,5.05,6.02,1.43],'dark');box('monitor_foot',[4.42,5.71,.75,4.78,5.96,.8],'dark');box('keyboard',[4.12,5.57,.75,4.91,5.79,.78]);box('pc',[3.54,5.63,0,3.83,6.1,.58],'dark');chair('desk_chair',4.58,4.91,180);plant('desk_plant',3.7,5.8,.75,.6)
box('vanity_top',[5.85,3.82,.71,6.35,4.95,.77]);box('vanity_drawers',[5.89,3.86,.57,6.29,4.9,.71]);box('vanity_leg1',[5.87,3.84,0,5.93,3.9,.71]);box('vanity_leg2',[5.87,4.84,0,5.93,4.91,.71]);box('vanity_mirror',[6.27,4.15,.8,6.32,4.64,1.4],'#b7c5c7');cyl('pink_stool',5.36,4.36,0,.26,.47,'#c7a0a5');box('tall_mirror',[6.27,3.1,.08,6.33,3.7,1.9],'#b7c5c7');plant('vanity_flower',6.08,4.8,.77,.55)
for i in range(5):cyl('cosmetic'+str(i),6.05,3.97+i*.09,.77,.025,.12,'#b59d8e','decor')
cyl('pink_rug',3.47,2.17,.008,1.35,.014,'#c195a0','rug');ell('yoga_ball',[.42,2.65,0,1.16,3.39,.74],'#bd7488');cyl('trampoline',.95,1.93,.2,.5,.08,'dark');
for i in range(12):
 a=i*math.tau/12;line('trampoline_rim'+str(i),[.95+.44*math.cos(a),1.93+.44*math.sin(a),.28],[.95+.51*math.cos(a),1.93+.51*math.sin(a),.28],.018,'#c6ad45')
box('bike_mat',[5.08,.12,.005,6.22,1.1,.018],'dark');line('bike_base',[5.35,.35,.1],[5.95,.85,.1],.055);line('bike_frame',[5.4,.4,.18],[5.85,.78,.78],.05);line('bike_post',[5.5,.5,.2],[5.5,.5,.95],.035);ell('bike_saddle',[5.35,.35,.93,5.65,.62,1.0],'dark');line('bike_handle',[5.95,.85,.45],[5.95,.85,1.2],.035);line('bike_handlebar',[5.76,.85,1.2],[6.1,.85,1.2],.035);ell('bike_flywheel',[5.6,.55,.08,5.98,.91,.56],'dark')
box('wardrobe',[1.8,.02,0,4.85,.62,2.6]);
for x in [2.55,3.3,4.05]:box('wardrobe_joint'+str(x),[x,.62,.05,x+.012,.63,2.55],'#c9c6c0')
for i in range(6):box('head_photo'+str(i),[.095,4+i*.22,1.3+(i%2)*.3,.12,4.16+i*.22,1.51+(i%2)*.3],'#9da6a0','decor')
plaque('logo',[6.265,4.0,1.83,6.29,4.93,2.12]);
box('balcony_floor',[6.4,1.05,-.18,8.3,3.2,0],'#d8d6ce','exterior');
for i in range(3):line('balcony_rail'+str(i),[8.18,1.05,.45+i*.31],[8.18,3.2,.45+i*.31],.025,'dark','exterior')
for y in [1.05,3.2]:line('balcony_post'+str(y),[8.18,y,0],[8.18,y,1.1],.035,'dark','exterior')
plant('balcony_plant',7.8,2.85,0,1.2)
camera('front','床尾看床头',[4.1,4.7,1.55],[.2,4.7,1.03],26);camera('reverse','床头看书桌梳妆区',[.65,4.7,1.55],[5.9,4.0,1.05],22);camera('side','入口侧看双窗与床',[3.2,.72,1.7],[3.2,4.4,1.1],18);camera('high','室内真实高位',[1.0,.75,2.88],[3.4,3.6,.3],17);camera('cut','去顶俯视关系检查',[3.2,3.1,13],[3.2,3.1,0],40,True)
check('床尾至桌前工作区水平余量',3.45-2.47,.85,['E_duvet','E_desk_top'],'不把椅子收入桌下后的空位算成日常通路');check('衣柜前至地毯中心通路',2.17-.62,.9,['E_wardrobe','E_pink_rug'],'地毯可行走，检查柜门前地面，不视作障碍');check('床与地毯不重叠',3.8-(2.17+1.35),0,['E_bed_base','E_pink_rug']);check('桌前椅后至中央活动区',4.66-3.52,.9,['E_desk_chair','E_pink_rug'])

# Connected module uses its own sole coordinate specification.
exec((R/'scripts/v5_social.py').read_text(encoding='utf8'), globals())
exec((R/'scripts/v5_other_rooms.py').read_text(encoding='utf8'), globals())

# Exterior is a site study, deliberately not falsely connected to the room modules.
module('SITE','院墙、车库、庭院 · 总图研究',26,34,['V3_023','V3_024','V3_026','V3_027','V3_029','V3_031'],'主屋为外形体量占位，不代表房间已经拼接。车库增设后部车行开口，车头方向按真实进出路径修正。')
box('ground',[-.2,-.2,-.35,26.2,34.2,-.15],'#a4b290','site');box('street',[-3,-8,-.25,29,-1.6,-.08],'#838a8c','site');box('sidewalk',[-3,-1.6,-.15,29,0,-.05],'#bfc0b9','site');box('side_street',[26,-1.6,-.2,31,35,-.08],'#838a8c','site')
wall('boundary_W','y',0,0,34,height=1.8,color='#d7d2c7');wall('boundary_E','y',26,0,34,height=1.8,color='#d7d2c7');wall('boundary_N','x',34,0,26,height=1.8,color='#d7d2c7');wall('boundary_S','x',0,0,26,[(2.4,6.8,0,2.5,'open'),(17,1.5,0,2.3,'open')],height=2.7,color='#d7d2c7')
box('driveway',[1.7,0,-.1,12.5,13.65,0],'#b9bbb5','site');box('pedestrian_path',[16.8,0,-.08,18.7,14,0],'#d5d2c9','site');box('garage_slab',[1.9,.15,-.15,9.7,6.75,0],'#b2b4b0','site')
wall('garage_W','y',1.9,.15,6.75,height=2.75);wall('garage_E','y',9.7,.15,6.75,height=2.75);wall('garage_N','x',6.75,1.9,9.7,[(2.4,6.8,0,2.5,'open')],height=2.75);box('garage_roof',[1.7,0,2.75,9.9,6.95,2.95],'#a3a8a5','ceiling');box('garage_shutter_roll',[2.4,.08,2.5,9.2,.35,2.72],'dark','fixture')
for x in [2.4,9.2]:box('garage_track'+str(x),[x,.06,0,x+.06,.16,2.5],'dark','fixture')
box('garage_center_line',[5.75,.4,.005,5.8,6.4,.01],'#dedfcd','marking');
for i,x in enumerate([3.75,7.55]):
 box('car'+str(i)+'_body',[x-.92,.95,.25,x+.92,5.75,1.08],'#dce0df' if i==0 else '#89949a','vehicle');ell('car'+str(i)+'_cabin',[x-.76,2.1,.9,x+.76,4.7,1.55],'#98afb7','vehicle')
 for j,(xx,yy) in enumerate([(x-.94,1.85),(x+.94,1.85),(x-.94,4.9),(x+.94,4.9)]):ell('car'+str(i)+'_wheel'+str(j),[xx-.08,yy-.32,.05,xx+.08,yy+.32,.69],'dark','vehicle')
# Real-sized 6.7m reversing apron between garage and house; path is separate.
for i in range(8):box('vehicle_route'+str(i),[5.63,7.2+i*.75,.01,5.83,7.6+i*.75,.02],'#d6c589','marking')
for x in [16.8,18.7]:box('gate_pier'+str(x),[x-.15,-.12,0,x+.15,.38,2.35],'#d1cbbb','exterior')
box('gate_canopy',[16.6,-.3,2.35,18.9,.8,2.48],'dark','exterior');
for i in range(12):box('gate_slat'+str(i),[17.04+i*.118,.1,.08,17.10+i*.118,.16,2.12],'wood','door')
plaque('entry_logo',[15.0,-.13,1.2,16.3,-.09,1.57]);
# Visual mass only, not a misleading fully solved floorplan.
box('house_F1',[5.6,14,0,20.4,30,3.3],'#dedbd2','massing');box('house_F2',[5.6,14,3.3,18.4,29,6.6],'#e5e2d8','massing');box('wood_volume',[18.4,19,3.3,20.4,28,6.6],'#b9a084','massing');box('roof_cap',[5.5,13.9,6.6,18.5,29.1,6.82],'#777d7d','massing');box('roof_service',[14.3,24.2,6.82,17.7,27.8,8.3],'#777d7d','massing')
for id,b in [('frontglass1',[6.8,13.94,.6,13.2,13.99,2.7]),('entryglass',[16.9,13.94,0,18.4,13.99,2.5]),('frontglass2',[6.8,13.94,3.35,16.6,13.99,5.95]),('backglass',[7.0,30.01,.6,12.0,30.04,2.65])]:box(id,b,'glass','facade_glass')
for x in [6.8,9.1,11.4,13.7,16.6]:box('front_mullion'+str(x),[x,13.88,3.35,x+.06,14,5.95],'dark','frame')
box('front_balcony',[5.7,12.1,3.12,18.4,14,3.3],'#d0cabe','exterior');box('side_terrace',[18.4,14,3.12,20.4,19,3.3],'wood','exterior')
for z in [3.65,3.97,4.36]:line('front_rail'+str(z),[5.7,12.12,z],[18.4,12.12,z],.025,'dark','exterior')
for x in [5.7,8.2,10.7,13.2,15.7,18.4]:line('front_post'+str(x),[x,12.12,3.3],[x,12.12,4.4],.03,'dark','exterior')
for id,b in [('west_walk',[3.7,14,-.08,5.5,30,0]),('east_walk',[20.5,14,-.08,22.3,30,0]),('rear_walk',[5.6,30.1,-.08,20.4,31.9,0])]:box(id,b,'#c8c5ba','site')
for i,(x,y) in enumerate([(1.2,10),(2.5,18),(2.5,26),(23.7,9),(23.7,19),(23.7,28),(8,32.7),(16,32.7)]):
 cyl('tree_trunk'+str(i),x,y,0,.13,2.4,'wood','landscape');ell('tree_crown'+str(i),[x-.9,y-.9,1.7,x+.9,y+.9,4.0],'#789274','landscape')
for i in range(9):plant('hedge'+str(i),10.8+i*.56,1.2,0,1.1)
camera('front','临街围墙与车库',[31,-24,16],[13,13,2],43);camera('garden','院内回看车库与通道',[20,11,5],[7,4,1],30);camera('top','总图俯视检查',[30,-18,39],[13,17,0],42,True)
check('车库内部净宽',(9.7-.09)-(1.9+.09),7.0,['SITE_garage_W_end','SITE_garage_E_end']);check('车库内部净深',(6.75-.09)-.15,6.0,['SITE_garage_N_end']);check('车辆长向剩余',6.51-4.8,1.2,['SITE_car0_body']);check('车库后方至主屋退车场',14-(6.75+.09),6.0,['SITE_garage_N_end','SITE_house_F1']);check('独立人行路净宽',18.7-16.8,1.5,['SITE_pedestrian_path']);check('后院可用深度',34-.09-30,3.0,['SITE_house_F1','SITE_boundary_N_end'])

exec((R/'scripts/v5_assembly.py').read_text(encoding='utf8'), globals())
D['status']='proposed_courtyard_whole_house_plus_independent_modules'
D['assembly_conflicts']=[
 {'id':'C01','severity':'review','fact':'大姐原图双窗墙与阳台门分属相邻外墙；旧模型把该窗墙贴住男主卧室。','decision':'用户选择保留V3卧室并允许转折/采光院。全屋提案留4.15×3.2m主采光院，卧室不缩放、不镜像；走廊在楼梯后转折。'},
 {'id':'C02','severity':'review','fact':'客餐厨原图直接连接，旧模型插入3.1m餐厨前厅。','decision':'独立连续模块取消前厅；房屋总图需据此回调。'},
 {'id':'C03','severity':'review','fact':'V3车库车身呈侧向，而正面门、内部转向空间不明确。','decision':'总图研究用实际车长4.8m、车宽1.84m，车位纵向；前后开口形成可进出路径。后开口是新增设计。'},
 {'id':'C04','severity':'review','fact':'部分V3品牌牌在不同镜头换墙。','decision':'各独立空间固定一个载体，模型标注位置，不复制。'},
 {'id':'C05','severity':'review','fact':'V3没有可用楼梯走廊图，先前整体认可不能证明生活主环境保真。','decision':'全屋提案保留A前端上口→B后端下口的直跑核心；三门改为沿转折路径薇亚→子豪→舒亚，不再承诺普通镜头三门同框。'},
 {'id':'C06','severity':'review','fact':'原外景紧凑长方体不能直接容纳所有原房间窗墙与新院落。','decision':'HOME显示实际室内拼接后的外形，SITE仍作为旧体量研究对照。新增入口玻璃廊、采光院、后部套房体量和受支撑露台，外立面需整体复核。'}]
out=R/'模型';out.mkdir(exist_ok=True)
(out/'空间校准主数据_v5.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),encoding='utf8')
(R/'校验/v5_参考尺寸与净距.json').write_text(json.dumps({'checks':D['checks'],'limitations':['尺寸为影视设计假设，不是实测','只检查列出的局部净距，不能替代门扇转动或车辆转弯轨迹验证','全屋采光院拼接是待审提案；不应恢复正式生图']},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'modules':len(D['modules']),'objects':len(D['objects']),'cameras':len(D['cameras']),'checks':len(D['checks']),'failed':[x for x in D['checks'] if not x['pass']]},ensure_ascii=False))
