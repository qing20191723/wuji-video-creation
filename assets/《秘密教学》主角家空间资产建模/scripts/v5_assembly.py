"""Room-first courtyard assembly, authorized after the V3 / corridor conflict.
Rooms only rotate/translate. No scale or mirror operation is allowed.
"""
import copy
source_objects=copy.deepcopy(D['objects']);source_openings=copy.deepcopy(D['openings'])
module('HOME','全屋拼接 · 采光院方案',26,42,[], '保留 V3 房间；走廊在楼梯后转折。新院落、入口廊和连接处属于补充设计，等待整体检查。')
M['assembly']='proposed_courtyard_assembly';M['height']=6.6
placements=[
 {'source':'KLD','level':1,'pos':[3.8,0,0],'rotation':0},
 {'source':'P','level':1,'pos':[3.8,11.2,0],'rotation':180,'size':[6,5.6]},
 {'source':'LA','level':1,'pos':[13.1,11.4,0],'rotation':0},
 {'source':'E','level':2,'pos':[3.8,0,3.3],'rotation':0},
 {'source':'M','level':2,'pos':[3.8,11.2,3.3],'rotation':0},
 {'source':'Y','level':2,'pos':[12.4,9.4,3.3],'rotation':180,'size':[5,4.8]}]
house_offset=[3.8,15.2,0]
def tr(v,p):
 x,y,z=v
 if p['rotation']==180:x,y=p['size'][0]-x,p['size'][1]-y
 return [round(x+p['pos'][0]+house_offset[0],5),round(y+p['pos'][1]+house_offset[1],5),round(z+p['pos'][2],5)]
def transformed_box(b,p):
 a=tr(b[:3],p);c=tr(b[3:],p);return [min(a[i],c[i]) for i in range(3)]+[max(a[i],c[i]) for i in range(3)]
for p in placements:
 for original in [o for o in source_objects if o['module']==p['source']]:
  # Open the temporary capped bookcase stub to the actual master corridor.
  if p['source']=='KLD' and original['id'].startswith(('KLD_stub_N','KLD_stub_bookcase')):continue
  # The dedicated balcony is extended as a coherent wraparound balcony below.
  if p['source']=='E' and original['role']=='exterior':continue
  o=copy.deepcopy(original);o.update(id='HOME_F'+str(p['level'])+'_'+original['id'],module='HOME',level=p['level'],zone='rooms',source_id=original['id']);o['box']=transformed_box(original['box'],p)
  if o['kind']=='bar':o['a']=tr(original['a'],p);o['b']=tr(original['b'],p)
  if o['kind']=='mesh':o['vertices']=[tr(v,p) for v in original['vertices']]
  D['objects'].append(o)
 for original in [o for o in source_openings if o['module']==p['source']]:
  o=copy.deepcopy(original);o.update(id='HOME_F'+str(p['level'])+'_'+original['id'],module='HOME',level=p['level'],source_id=original['id']);axis=o['axis'];aa=[o['start'],o['plane'],o['sill']] if axis=='x' else [o['plane'],o['start'],o['sill']];bb=[o['start']+o['width'],o['plane'],o['head']] if axis=='x' else [o['plane'],o['start']+o['width'],o['head']];aa=tr(aa,p);bb=tr(bb,p);o['start']=min(aa[0 if axis=='x' else 1],bb[0 if axis=='x' else 1]);o['plane']=aa[1 if axis=='x' else 0];o['sill']=min(aa[2],bb[2]);o['head']=max(aa[2],bb[2]);D['openings'].append(o)

# Helpers operate in HOUSE local coordinates, convert once to world site coordinates.
created_before=len(D['objects'])
def hb(id,b,col='wall',role='wall',level=1):
 q=box(id,[b[0]+3.8,b[1]+15.2,b[2],b[3]+3.8,b[4]+15.2,b[5]],col,role);q.update(level=level,zone='connections');return q
def hw(id,axis,p,start,end,opens=(),z=0,height=3.08,level=1):
 startidx=len(D['objects']);opidx=len(D['openings']);wall(id,axis,p+(15.2 if axis=='x' else 3.8),start+(3.8 if axis=='x' else 15.2),end+(3.8 if axis=='x' else 15.2),[(o+(3.8 if axis=='x' else 15.2),w,s,h,t) for o,w,s,h,t in opens],z=z,height=height)
 for o in D['objects'][startidx:]:o.update(level=level,zone='connections')
 for o in D['openings'][opidx:]:o.update(level=level)
def slab(id,x,y,X,Y,z,level):return hb(id,[x,y,z-.18,X,Y,z],'floor','floor',level)
def roof(id,x,y,X,Y,z,level):return hb(id,[x,y,z+3.08,X,Y,z+3.28],'white','ceiling',level)
def barhouse(id,a,b,r=.03,col='wood',level=2):
 o=line(id,[a[0]+3.8,a[1]+15.2,a[2]],[b[0]+3.8,b[1]+15.2,b[2]],r,col,'rail');o.update(level=level,zone='stairs');return o

# Entry gallery aligns the right-side pedestrian gate with the interior dining door.
slab('F1_entry_gallery',.1,-1.8,16.3,0,0,1);roof('F1_entry_gallery_roof',.1,-1.8,16.3,0,0,1)
hw('F1_front','x',-1.8,.1,16.3,[(.65,3.0,.5,2.6,'window'),(4.1,3.5,.5,2.6,'window'),(8.2,3.6,.5,2.6,'window'),(13.0,1.2,0,2.3,'door'),(14.5,1.1,.4,2.65,'window')]);hw('F1_entry_E','y',16.3,-1.8,0);hw('F1_entry_W','y',.1,-1.8,0)
hb('F1_entry_cabinet',[11.7,-.48,0,12.65,-.05,.85],'wood','furniture');hb('F1_entry_logo',[11.5,-.04,1.4,12.7,0,1.72],'#272a2a','brand')

# Shared straight-flight core. A = front upper landing, B = rear lower landing.
slab('F1_core',.1,0,3.6,11.2,0,1);slab('F2_A_landing',.1,0,3.6,1.8,3.3,2);slab('F2_parallel_hall',1.85,1.8,3.6,11.2,3.3,2);slab('F2_B_end',.1,7.12,1.85,11.2,3.3,2)
roof('F2_core_roof',.1,0,3.6,11.2,3.3,2)
hw('F1_core_W','y',.1,0,11.2,[(7.6,2.0,.65,2.7,'window')]);hw('F2_core_W','y',.1,0,11.2,[(1.95,2.6,1.1,1.75,'window'),(7.65,2.0,.4,2.7,'window')],z=3.3,level=2)
hw('F2_A_front','x',0,.1,3.6,[(.35,2.85,.25,2.8,'window')],z=3.3,level=2)
hb('stair_separating_support',[1.65,1.8,0,1.85,7.12,4.4],'wall','support',2)
for i in range(1,20):
 y=7.12-i*.28;h=i*.165
 hb('tread'+str(i),[.25,y,h-.045,1.55,y+.28,h],'wood','stair',0)
 hb('riser'+str(i),[.25,y+.26,(i-1)*.165,1.55,y+.28,h],'wood','stair',0)
# Sloped concrete waist slab, anchored at both landings. Not merely floating treads.
verts=[[.23,1.8,3.255],[1.57,1.8,3.255],[1.57,7.12,-.045],[.23,7.12,-.045],[.23,1.8,3.02],[1.57,1.8,3.02],[1.57,7.12,-.28],[.23,7.12,-.28]]
o=hb('structural_stair_waist',[.23,1.8,-.28,1.57,7.12,3.255],'#babdbb','stair',0);o.update(kind='mesh',vertices=[[v[0]+3.8,v[1]+15.2,v[2]] for v in verts],faces=[[0,1,2,3],[7,6,5,4],[0,4,5,1],[1,5,6,2],[2,6,7,3],[3,7,4,0]])
hb('stair_upper_connection',[.23,1.57,2.98,1.57,1.8,3.3],'#babdbb','stair',0);hb('stair_lower_connection',[.23,7.12,-.28,1.57,7.4,0],'#babdbb','stair',0)
barhouse('upper_guard_cap',[1.75,1.8,4.43],[1.75,7.12,4.43],.07)
barhouse('flight_wall_handhold',[.2,1.9,4.24],[.2,7.0,1.08],.04,level=0)
hb('F2_corridor_logo',[1.66,7.14,3.85,1.84,7.18,4.18],'#272a2a','brand',2)
slab('F2_E_threshold',3.5,.2,3.9,1.35,3.3,2);slab('F2_Y_threshold',12.2,12.7,12.5,13.95,3.3,2)
hb('F1_core_room_joint',[3.6,0,0,3.8,6,3.08],'wall','wall',1)
hb('F2_core_room_joint',[3.6,1.3,3.3,3.8,6.2,6.38],'wall','wall',2)
for level,z in [(1,0),(2,3.3)]:hw('F'+str(level)+'_court_W','y',3.6,6.2,9.4,[(6.45,2.65,.45,2.7,'window')],z=z,level=level)

# Ground-floor public / master corridor alongside a real open-air courtyard.
slab('F1_north_hall',1.85,9.4,9.5,11.2,0,1);roof('F1_north_hall_roof',1.85,9.4,9.5,11.2,0,1)
slab('F1_master_approach',7.95,7.6,9.5,9.4,0,1);roof('F1_master_approach_roof',7.95,6,9.5,9.4,0,1)
hw('F1_approach_W','y',7.95,7.65,9.4,[(7.85,1.3,.6,2.7,'window')]);hw('F1_approach_E','y',9.5,7.65,9.4)
hw('F1_hall_court_edge','x',9.4,3.6,7.95,[(3.95,3.4,.5,2.7,'window')]);hw('F1_hall_north','x',11.2,1.85,3.8);hw('F1_hall_W','y',1.85,9.4,11.2)
hb('F1_hall_books',[9.15,8.0,0,9.47,9.05,2.3],'wood','furniture');

# East service passage, actual independent laundry and guest bathroom.
slab('F1_service_gallery',16.3,6,18.4,16.0,0,1);roof('F1_service_gallery_roof',16.3,6,18.4,16,0,1)
slab('F1_service_north',15.6,16,18.4,18.9,0,1);roof('F1_service_north_roof',15.6,16,18.4,18.9,0,1)
hw('F1_service_E','y',18.4,6,18.9,[(7.4,2.2,.6,2.7,'window'),(12.2,2.2,.6,2.7,'window'),(16.2,1.8,.6,2.7,'window')]);hw('F1_service_S','x',6,16.3,18.4);hw('F1_service_N','x',18.9,15.6,18.4,[(16.1,1.1,0,2.3,'door')]);hw('F1_service_gap_W','y',16.3,10.2,11.4)
slab('F1_guest_floor',13.1,16,15.6,18.9,0,1);roof('F1_guest_roof',13.1,16,15.6,18.9,0,1)
hw('F1_guest_W','y',13.1,16,18.9);hw('F1_guest_S','x',16,13.1,15.6);hw('F1_guest_N','x',18.9,13.1,15.6,[(13.6,1.3,1.6,2.3,'window')]);hw('F1_guest_E','y',15.6,16,18.9,[(16.2,.9,0,2.2,'door')]);hb('F1_guest_vanity',[13.22,16.3,0,13.82,17.5,.85],'wood','furniture');hb('F1_guest_WC',[14.6,17.7,0,15.3,18.5,.8],'white','furniture')

# Upstairs turns after the straight-flight core; door sequence along the route is E → M → Y.
slab('F2_north_cross_hall',1.85,9.4,12.3,11.2,3.3,2);roof('F2_north_cross_hall_roof',1.85,9.4,12.3,11.2,3.3,2)
slab('F2_east_hall',10.4,11.2,12.3,15.8,3.3,2);roof('F2_east_hall_roof',10.4,11.2,12.3,15.8,3.3,2)
hw('F2_hall_court','x',9.4,3.6,10.4,[(3.95,5.9,.45,2.7,'window')],z=3.3,level=2);hw('F2_hall_north_gap','x',11.2,9.4,10.4,z=3.3,level=2);hw('F2_east_hall_W','y',10.4,11.2,15.8,[(11.6,1.8,.1,2.45,'door')],z=3.3,level=2)
hw('F2_terrace_access','x',15.8,10.4,12.3,[(10.55,1.55,0,2.6,'slider')],z=3.3,level=2);hw('F2_hall_E_gap','y',12.3,14.2,15.8,[(14.5,1.0,.5,2.7,'window')],z=3.3,level=2)
# Linen cabinet is a shallow store, no 10sqm empty room.
hb('F2_linen_cabinet',[9.6,11.6,3.3,10.3,13.4,5.75],'wood','furniture',2)
for i in range(5):hb('F2_linen_shelf'+str(i),[9.62,11.62,3.45+i*.43,10.25,13.37,3.49+i*.43],'white','furniture',2)

# Shared bathroom above a supported ground-floor garden porch, preserving master window daylight.
slab('F2_bath_floor',.1,11.2,3.6,15,3.3,2);roof('F2_bath_roof',.1,11.2,3.6,15,3.3,2)
hw('F2_bath_W','y',.1,11.2,15,[(12.4,1.6,1.3,2.6,'window')],z=3.3,level=2);hw('F2_bath_N','x',15,.1,3.6,z=3.3,level=2);hw('F2_bath_E','y',3.6,11.2,15,z=3.3,level=2);hw('F2_bath_S','x',11.2,.1,3.6,[(2.15,.95,0,2.2,'door')],z=3.3,level=2)
hb('F2_bath_vanity',[.25,11.65,3.3,.85,12.95,4.15],'wood','furniture',2);hb('F2_bath_shower',[.25,13.65,3.3,1.65,14.85,3.38],'white','furniture',2);hb('F2_bath_shower_screen',[1.65,13.65,3.3,1.68,14.85,5.5],'glass','glass',2);hb('F2_bath_WC',[2.5,13.9,3.3,3.25,14.65,4.1],'white','furniture',2)
for i,(x,y) in enumerate([(.25,11.4),(.25,14.8),(3.35,14.8),(12.55,10.7),(17.2,10.7),(17.2,14.1)]):hb('visible_support_column'+str(i),[x-.13,y-.13,0,x+.13,y+.13,3.3],'wall','support',1)

# Outdoor court, wraparound balcony and rear terrace. Guardrails remain physical objects.
slab('F2_front_balcony',.1,-1.8,12.3,0,3.3,2);slab('F2_E_private_balcony',10.2,0,12.3,6.2,3.3,2);slab('F2_court_side_terrace',10.4,6.4,12.3,9.4,3.3,2);slab('F2_rear_terrace',9.6,14.2,17.4,18.4,3.3,2)
def guard(id,a,b):
 for k,z in enumerate([3.7,4.02,4.4]):barhouse(id+str(k),[*a,z],[*b,z],.025,'dark')
 length=math.dist(a,b)
 for i in range(math.ceil(length/1.6)+1):
  t=i/math.ceil(length/1.6);x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;barhouse(id+'_post'+str(i),[x,y,3.3],[x,y,4.43],.03,'dark')
guard('front_rail',[.1,-1.8],[12.3,-1.8]);guard('east_private_rail',[12.3,-1.8],[12.3,6.2]);guard('private_end_rail',[10.2,6.2],[12.3,6.2]);guard('court_edge_rail',[10.4,6.4],[10.4,9.4]);guard('terrace_back',[9.6,18.4],[17.4,18.4]);guard('terrace_E',[17.4,14.2],[17.4,18.4]);guard('terrace_W',[9.6,16.8],[9.6,18.4])
guard('front_W_rail',[.1,-1.8],[.1,0]);guard('court_side_E',[12.3,6.4],[12.3,9.4])
hb('court_ground',[3.8,6.2,-.12,7.95,9.4,-.02],'#a8b995','landscape');hb('court_path',[3.8,6.25,-.02,4.6,9.4,.01],'#c6c5b5','site');
for i,(x,y) in enumerate([(5.1,7.3),(6.55,8.1)]):
 q=ell('courtyard_tree'+str(i),[x+3.8-.45,y+15.2-.45,.2,x+3.8+.45,y+15.2+.45,2.3],'#77926d','landscape');q.update(level=1,zone='court')

# Site remains reference-sized, enlarged to give the new house adequate setbacks.
for original in [o for o in source_objects if o['module']=='SITE']:
 id=original['id']
 if any(id.startswith('SITE_'+p) for p in ['house_','wood_volume','roof_','frontglass','entryglass','backglass','front_mullion','front_balcony','side_terrace','front_rail','front_post','west_walk','east_walk','rear_walk','pedestrian_path']):continue
 o=copy.deepcopy(original);o.update(id='HOME_'+id,module='HOME',level=0,zone='site',source_id=id)
 # Extend the northern boundary only; vehicle / pedestrian geometry stays at the street.
 b=o['box']
 if id=='SITE_ground':b[4]=42.2
 if id=='SITE_side_street':b[4]=43
 if id in ['SITE_boundary_W_end','SITE_boundary_E_end']:b[4]=42
 if id=='SITE_boundary_N_end':b[1]+=8;b[4]+=8
 if 'tree_' in id and b[1]>31:b[1]+=6.5;b[4]+=6.5
 D['objects'].append(o)
box('site_pedestrian_path',[16.8,0,-.08,18.7,13.4,0],'#d5d2c9','site').update(level=0,zone='site')
box('rear_garden_path',[7.5,35.5,-.08,20,37.2,0],'#c8c5ba','site').update(level=0,zone='site')

def hc(id,name,pos,target,lens=24,level_mode='all',cut=False):
 camera(id,name,[pos[0]+3.8,pos[1]+15.2,pos[2]],[target[0]+3.8,target[1]+15.2,target[2]],lens,cut);D['cameras'][-1]['level_mode']=level_mode
hc('floor1','一楼去顶总览',[9,9.2,40],[9,9.2,0],34,'F1',True);hc('floor2','二楼去顶总览',[9,8.3,40],[9,8.3,3.3],34,'F2',True)
hc('A','A端上平台看并排走廊',[2.7,.9,4.95],[2.7,8,4.7],23,'F2');hc('turn','转折走廊：子豪门与舒亚方向',[3.0,10.2,4.95],[11.7,11.2,4.6],23,'F2');hc('stairs_up','B端向上看直跑楼梯',[.9,8.15,1.65],[.9,2.0,3.7],24,'stairs');hc('exterior','全屋、庭院与车库',[34,-40,29],[9,4,2.7],38,'all');hc('court','采光院回看大姐双窗',[6.1,9.0,5.1],[6.8,6.1,4.7],23,'all')
D['placements']=placements;D['house_site_offset']=house_offset
D['walk_routes']=[{'id':'M_to_kitchen','name':'子豪房门→A端→下楼→客餐厨','note':'门扇需开启；仅作路径与净空复核。尚未作为视频漫游终稿。','points':[[x+3.8,y+15.2,z] for x,y,z in [(4.95,11.05,3.3),(4.95,10.3,3.3),(2.7,10.3,3.3),(2.7,1.0,3.3),(.9,1.0,3.3),(.9,1.8,3.3),(.9,7.12,0),(.9,8.2,0),(2.7,8.2,0),(2.7,10.3,0),(8.7,10.3,0),(8.7,6.4,0),(8.7,5.35,0),(10.4,5.35,0),(11,5.6,0),(11,7.2,0)]]}]
D['assembly_decision']={'user_choice':'优先保留V3卧室，允许走廊局部转折或增加采光院','room_operations':'translation + 180-degree rotation only; no scaling or mirroring','corridor_change':'原直线三门改为楼梯后转折；沿主路径仍为薇亚→子豪→舒亚','status':'proposed_model_requires_visual_and_route_review'}
check('主采光院净宽',7.95-3.8,3.0,['HOME_court_ground']);check('主采光院净深',9.4-6.2,3.0,['HOME_court_ground']);check('转折走廊设计宽',11.2-9.4,1.5,['HOME_F2_north_cross_hall']);check('东侧服务通道最窄净距',18.4-.09-(16.6+.09),1.5,['HOME_F1_service_E_end']);check('车库后方至新主屋前缘',13.4-6.84,6.0,['HOME_SITE_garage_N_end']);check('主卧后侧至围墙退距',42-(20.2+15.2),3.0,['HOME_F1_P_bath_floor'])
