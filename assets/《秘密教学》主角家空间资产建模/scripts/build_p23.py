"""Current build: Blender -b --python this_file -- --f4 [--render].
F4 uses the authorized M2 metric realization; all dimensions remain provisional.
Legacy mode is retained only for historical reproducibility, never current delivery.
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
P=R/('白模当前/模型/建模方案.json' if '--f4' in sys.argv else '平面确认/平面方案数据.json')
D=json.loads(P.read_text(encoding='utf8'))
OUT=R/'白模当前'; OUT.mkdir(exist_ok=True)
for sub in ['模型','检查记录','空间']: (OUT/sub).mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
s=bpy.context.scene; s.unit_settings.system='METRIC'; s.render.engine='CYCLES'
s.cycles.samples=16;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type=='OPTIX'
 if any(d.use for d in p.devices):s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.85,.85,.85,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.4
COL={}; GEO=[]; MAT={}; CAM=[]; MOT=[]
def material(name,value):
 if name not in MAT:
  m=bpy.data.materials.new(name);m.diffuse_color=(value,value,value,1);m.use_nodes=True
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(value,value,value,1);p.inputs['Roughness'].default_value=.75
  MAT[name]=m
 return MAT[name]
for n,v in [('wall',.82),('floor',.56),('frame',.22),('furniture',.68),('fabric',.47),('detail',.32),('garden',.38),('glass',.7)]:material(n,v)
MAT['glass'].diffuse_color=(.7,.7,.7,.08)
MAT['glass'].node_tree.nodes['Principled BSDF'].inputs['Alpha'].default_value=.08
MAT['glass'].surface_render_method='DITHERED'
def register(o,id,level,category,source='',mat='wall'):
 o.name=id;o.data.materials.append(MAT[mat]);key=f'F{level}_{category}'
 if key not in COL:COL[key]=bpy.data.collections.new(key);s.collection.children.link(COL[key])
 for c in list(o.users_collection):c.objects.unlink(o)
 COL[key].objects.link(o);o['source_id']=source;o['category']=category;o['level']=level
 bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(v) for v in o.bound_box]
 b=[min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)]
 GEO.append(dict(id=id,source=source,level=level,category=category,box=b,material=mat,vertices=[list(o.matrix_world@v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons]))
 return o
def box(id,b,l=0,cat='wall',src='',mat='wall'):
 if any(b[i+3]-b[i]<=.00001 for i in range(3)):return
 bpy.ops.mesh.primitive_cube_add(size=1,location=[(b[i]+b[i+3])/2 for i in range(3)])
 o=bpy.context.object;o.dimensions=[b[i+3]-b[i] for i in range(3)];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return register(o,id,l,cat,src,mat)
def cyl(id,c,r,h,l=0,cat='furniture',src='',mat='detail',axis=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=h,location=c);o=bpy.context.object
 if axis:o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
 bpy.context.view_layer.update();return register(o,id,l,cat,src,mat)
def bar(id,a,b,r,l,src=''):
 return cyl(id,(Vector(a)+Vector(b))/2,r,(Vector(b)-Vector(a)).length,l,'furniture',src,axis=Vector(b)-Vector(a))
def slab(id,b,z,l,cat='slab'):return box(id,[b[0],b[1],z-.22,b[2],b[3],z],l,cat,id,'floor')
slab('F1_floor',[0,0,22,10.4],0,1)
for r in D['rooms']:
 if r['id']=='WT':slab('west_public_terrace',r['box'],3.3,2)
# Floor openings and roof use the selected source, never patched display geometry.
for i,b in enumerate(D['architecture']['floor2_rects']):slab('F2_slab_'+str(i),b,3.3,2)
roofrects=D['architecture']['roof_rects']
for i,b in enumerate(roofrects):slab('roof_'+str(i),b,6.6,2,'roof')
# True wall apertures, frame and separately switchable door leaves.
for w in D['walls']:
 l=w['level'];z=(l-1)*3.3;h=w['a'][1]==w['b'][1];t=w['thickness']/2;v=w['a'][1] if h else w['a'][0]
 lo=w['a'][0] if h else w['a'][1];end=w['b'][0] if h else w['b'][1]
 height=1.1 if w['id'] in ['2-PAR','2-STB'] else 3.08
 def part(tag,a,b,z0,z1,mat='wall',cat='wall',th=t):
  bb=[a,v-th,z+z0,b,v+th,z+z1] if h else [v-th,a,z+z0,v+th,b,z+z1]
  return box(w['id']+'_'+tag,bb,l,cat,w['id'],mat)
 ops=sorted([o for o in D['openings'] if o['wall']==w['id']],key=lambda o:o['start'])
 for op in ops+[dict(start=end,end=end,type='end')]:
  a,b=op['start'],op['end'];part('pier_'+str(lo),lo,a,0,height)
  if op['type']=='end':break
  sill=op.get('sill',0);head=op['head'];oid=op['id']
  part(oid+'_below',a,b,0,sill);part(oid+'_lintel',a,b,head,height)
  for tag,u,uu,k,kk in [('left',a,a+.045,sill,head),('right',b-.045,b,sill,head),('head',a,b,head-.045,head)]+([] if op['type']=='door' else [('sill',a,b,sill,sill+.045)]):part(oid+'_'+tag,u,uu,k,kk,'frame','frame',t+.01)
  if op['type']=='door':
   leaf=part(oid+'_leaf',a+.045,b-.045,.02,head-.045,'furniture','door',.021)
   pivot=[a+.045,v,z] if h else [v,a+.045,z];angle=(1 if h else -1)*op.get('side',1)*math.pi/2
   leaf['motion_pivot']=pivot;leaf['motion_angle']=angle
   MOT.append(dict(id=leaf.name,pivot=pivot,angle=angle))
   handle=part(oid+'_handle',b-.22,b-.08,.96,1,'detail','door',.065)
   MOT.append(dict(id=handle.name,pivot=pivot,angle=angle))
  else:
   # Boundary markers and center mullion; non-reflective clear inspection glazing.
   if op.get('panes',2)>1:part(oid+'_mullion',(a+b)/2-.025,(a+b)/2+.025,sill,head,'frame','frame',.03)
   pane=part(oid+'_glass',a+.045,b-.045,sill+.045,head-.045,'glass','glass',.005)
   pane.hide_render=True;pane['inspection_clear_glass']=True
  lo=b
 if height<2:part('cap',w['a'][0] if h else w['a'][1],end,height,height+.06,'frame','guard',t+.025)
# Stair steps are parameterized; final rise joins A at 3.3m.
st=D['stairs'];sx,sy,ex,ey=st['footprint']
for i in range(st['treads']):
 x=sx+i*st['tread'];top=(i+1)*st['rise']
 box(f'STAIR_{i+1:02}',[x,sy,0,x+st['tread'],ey,top],1,'stairs','stairs','floor')
bar('stair_handrail',[sx,sy+.05,st['rise']+.9],[ex,sy+.05,3.3+.9],.035,1,'stairs')
# Balcony perimeter rails, no rail across an indoor entry.
for i,(a,b) in enumerate(D.get('exterior_rails',[((0,-1.4),(22,-1.4)),((0,-1.4),(0,1)),((22,-1.4),(22,10.4)),((18.8,10.4),(22,10.4)),((18.8,4.4),(22,4.4)),((18.8,9.6),(18.8,10.4))])):
 length=math.dist(a,b)
 for j in range(math.ceil(length/.9)+1):
  u=j/math.ceil(length/.9);x=a[0]+(b[0]-a[0])*u;y=a[1]+(b[1]-a[1])*u
  cyl(f'rail_{i}_{j}',[x,y,3.85],.025,1.1,2,'guard',mat='frame')
 bar(f'rail_top_{i}',[*a,4.4],[*b,4.4],.035,2)
# Named furniture; dimensions are exact plan footprints. Heights are provisional.
for i,(a,b) in enumerate([] if '--f4' in sys.argv else [((-1.5,1.3),(-1.5,4.5)),((-1.5,1.3),(0,1.3)),((-1.5,4.5),(0,4.5))]):
 length=math.dist(a,b)
 for j in range(math.ceil(length/.8)+1):
  u=j/math.ceil(length/.8);x=a[0]+(b[0]-a[0])*u;y=a[1]+(b[1]-a[1])*u
  cyl(f'west_rail_{i}_{j}',[x,y,3.85],.025,1.1,2,'guard',mat='frame')
 bar(f'west_rail_top_{i}',[*a,4.4],[*b,4.4],.035,2)
for f in D['furniture']:
 id=f['id'];x,y,X,Y=f['box'];w=X-x;d=Y-y;l=f['level'];z=(l-1)*3.3;k=f['kind'];name=f['name'];n=0
 def B(tag,a,b,c,e,g,j,mat='furniture'):
  return box(id+'_'+tag,[x+a*w,y+b*d,z+c,x+e*w,y+g*d,z+j],l,'furniture',id,mat)
 def C(tag,a,b,c,r,h,mat='detail',axis=None):return cyl(id+'_'+tag,[x+a*w,y+b*d,z+c],r,h,l,'furniture',id,mat,axis)
 def legs(top):
  for a,b in [(.08,.08),(.92,.08),(.08,.92),(.92,.92)]:C('leg_'+str(a)+str(b),a,b,top/2,.025,top)
 if k=='bed':
  B('frame',0,0,.08,1,1,.32);B('mattress',.025,.025,.32,.975,.975,.56,'fabric')
  hd=f['head'];a,b,e,g={'W':(0,0,.07,1),'E':(.93,0,1,1),'N':(0,.93,1,1),'S':(0,0,1,.07)}[hd]
  B('headboard',a,b,.25,e,g,1.05)
  for j in range(2 if min(w,d)>1.6 else 1):
   if hd in ['W','E']:B('pillow'+str(j),.08 if hd=='W' else .72,.08+j*.44,.56,.28 if hd=='W' else .92,.46+j*.44,.68,'wall')
   else:B('pillow'+str(j),.1+j*.44,.73 if hd=='N' else .07,.56,.48+j*.44,.93 if hd=='N' else .27,.68,'wall')
 elif 'rug' in k:
  if k=='roundrug':C('rug',.5,.5,.012,min(w,d)/2,.02,'fabric')
  else:B('rug',0,0,.005,1,1,.018,'fabric')
 elif k in ['desk','table']:
  ht=.45 if id in ['B11','L04'] else .75;B('top',0,0,ht-.055,1,1,ht);legs(ht-.05)
  if '电脑' in name:
   if w>=d:B('monitor',.35,.65,.82,.7,.72,1.25,'detail');B('keyboard',.35,.25,.76,.65,.45,.79,'detail')
   else:B('monitor',.25,.35,.82,.32,.75,1.25,'detail')
  if '梳妆' in name:
   if w<d:B('mirror',.94,.15,.8,1,.85,1.5,'detail')
   else:B('mirror',.2,.02,.8,.8,.08,1.5,'detail')
 elif k=='chair':
  B('seat',0,0,.42,1,1,.49,'fabric');B('back',0,0,.49,1,.1,.95);legs(.42)
 elif k=='sofa':
  B('base',0,0,.12,1,1,.4);B('cushion',.03,.12,.4,.97,.97,.54,'fabric');B('back',0,0,.4,1,.16,.88,'fabric')
 elif k=='circle':
  if '球' in name:
   bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=min(w,d)/2,location=((x+X)/2,(y+Y)/2,z+min(w,d)/2));register(bpy.context.object,id+'_ball',l,'furniture',id,'fabric')
  else:C('round',.5,.5,.23,min(w,d)/2,.46,'fabric')
 elif k=='trampoline':C('rim',.5,.5,.24,min(w,d)/2,.08);C('mat',.5,.5,.29,min(w,d)*.44,.025,'fabric');legs(.22)
 elif k in ['bike','scope','rack']:
  if k=='bike':
   B('base',0,0,.01,1,1,.06,'detail');C('wheel',.5,.7,.4,.29,.12,'detail',[1,0,0]);bar(id+'_frame',[x+w*.5,y+d*.2,z+.1],[x+w*.5,y+d*.65,z+1.05],.045,l,id);B('seat',.2,.15,.94,.8,.4,1.02);bar(id+'_handle',[x+w*.1,y+d*.9,z+1.13],[x+w*.9,y+d*.9,z+1.13],.035,l,id)
  elif k=='scope':
   for a,b in [(0,0),(1,0),(.5,1)]:bar(id+'_tripod'+str(a),[x+a*w,y+b*d,z],[x+w/2,y+d/2,z+1.15],.02,l,id)
   cyl(id+'_tube',[x+w/2,y+d/2,z+1.25],.1,.6,l,'furniture',id,'detail',[0,1,.4])
  else:
   B('base',0,0,0,1,1,.4);B('post1',0,0,.4,.07,1,1.75);B('post2',.93,0,.4,1,1,1.75);B('top',0,0,1.7,1,1,1.75)
 elif k=='mirror':B('mirror',0,0,.08,1,1,1.8,'detail')
 elif k=='hob':
  B('hob',0,0,.9,1,1,.94,'detail');B('hood',0,0,1.65,1,1,1.8);B('flue',.3,.3,1.8,.7,.7,2.75)
  for a,b in [(.25,.25),(.75,.75)]:C('burner'+str(a),a,b,.945,.12,.015)
 elif k in ['sink','tub','wc']:
  ht=.88 if k=='sink' else .48;B('body',0,0,.05,1,1,ht);B('bowl',.15,.15,ht,.85,.85,ht+.015,'detail')
  if k=='sink':bar(id+'_tap',[x+w*.75,y+d*.8,z+ht],[x+w*.75,y+d*.8,z+ht+.3],.025,l,id)
  if k=='wc':B('tank',.05,.8,.4,.95,1,.85)
 elif k=='washer':
  for j in range(2):
   B('machine'+str(j),0,j*.5,0,1,(j+1)*.5,.87);cyl(id+'_drum'+str(j),[x-.006,y+d*(.25+j*.5),z+.45],.22,.025,l,'furniture',id,'detail',[1,0,0])
 else:
  tall='衣柜' in name or k=='fridge';shelf='书架' in name or '层架' in name;ht=2.25 if tall else 1.9 if shelf else .88 if f['room']=='K' else .7
  if shelf:
   B('side1',0,0,0,.045,1,ht);B('side2',.955,0,0,1,1,ht)
   for j in range(6):B('shelf'+str(j),0,0,j*ht/5,1,1,j*ht/5+.025)
  else:
   B('body',0,0,.04,1,1,ht)
   # Front seams make cabinets/appliances distinguishable from placeholders.
   if w>=d:
    for a in [.25,.75]:B('handle'+str(a),a,.0,ht*.65,a+.04,.025,ht*.8,'detail')
   else:
    for b in [.25,.75]:B('handle'+str(b),0,b,ht*.65,.025,b+.04,ht*.8,'detail')
# Site: confirmed driveway/garage and 4.5m front garden.
T=D['site'];slab('site',T['bounds'],-.08,0,'ground')
for i,b in enumerate(D['garden']['paths']):box('path'+str(i),[b[0],b[1],-.075,b[2],b[3],-.015],0,'garden',mat='floor')
for i,b in enumerate(D['garden']['beds']):
 box('flowerbed'+str(i),[b[0],b[1],-.075,b[2],b[3],.08],0,'garden',mat='garden')
 for j in range(int((b[2]-b[0])/.55)):cyl(f'plant{i}_{j}',[b[0]+.3+j*.55,(b[1]+b[3])/2,.22],.17,.28,0,'garden',mat='garden')
for i,b in enumerate([[-1.8,-10.3,-1.6,13.4],[24,-10.3,24.2,13.4],[-1.8,13.2,24.2,13.4],[-1.8,-10.3,6,-10.1],[14,-10.3,20.5,-10.1],[22.1,-10.3,24.2,-10.1],[5,-10.1,5.2,-4.5],[5,-4.7,17,-4.5],[16.8,-10.1,17,-6.3],[16.8,-5.3,17,-4.5]]):box('boundary'+str(i),[b[0],b[1],0,b[2],b[3],2.1],0,'sitewall')
slab('garage_roof',[5,-10.3,17,-4.5],2.8,0,'roof')
box('car_body',[10.4,-8.15,.3,15.2,-6.25,1.05],0,'vehicle',mat='fabric');box('car_cabin',[11.3,-8.05,1.05,14.2,-6.35,1.5],0,'vehicle',mat='frame')
for x in [11.2,14.4]:
 for y in [-8.15,-6.25]:cyl('wheel'+str(x)+str(y),[x,y,.4],.34,.17,0,'vehicle',mat='detail',axis=[0,1,0])
def camera(id,rid,pos,target,lens=28,kind='真实机位'):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=id;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.05
 CAM.append(dict(id=id,room=rid,pos=pos,target=target,lens=lens,kind=kind));return o
# Camera seeds are provisional until collision/visibility audit.
for r in D['rooms']:
 if r['id'] in ['A','B','C','H2','WT','FB','AB'] and '--f4' in sys.argv:continue
 if r['id'] in ['A','FB','AB']:continue
 x,y,X,Y=r['box'];cx=(x+X)/2;cy=(y+Y)/2;z=(r['level']-1)*3.3
 seeds=[(x+.35,y+.35),(X-.35,Y-.35),(x+.35,Y-.35),(X-.35,y+.35)]
 count=6 if r['id'] in ['B1','B2','B3','MB','L','K','D'] else 4
 # Keep camera XY out of all furniture footprints; select nearest free grid point.
 obs=[f['box'] for f in D['furniture'] if f['room']==r['id'] and 'rug' not in f['kind']]
 def free(px,py):return all(not (b[0]-.18<px<b[2]+.18 and b[1]-.18<py<b[3]+.18) for b in obs)
 candidates=[(x+.3+i*(X-x-.6)/25,y+.3+j*(Y-y-.6)/25) for i in range(26) for j in range(26)]
 candidates=[v for v in candidates if free(*v)]
 for i in range(count):
  p=seeds[i%4];p=min(candidates,key=lambda v:math.dist(p,v)) if candidates else p
  camera(r['id']+f'_{i+1:02}',r['id'],[*p,z+(2.65 if i>=4 else 1.6)],[cx,cy,z+.95],28)
 camera(r['id']+'_TOP',r['id'],[cx,cy,z+12],[cx,cy,z],kind='顶视检查')
 CAM[-1]['ortho_scale']=max(X-x,(Y-y)*16/9)+.6
 bpy.context.object.data.type='ORTHO';bpy.context.object.data.ortho_scale=max(X-x,(Y-y)*16/9)+.6
if '--f4' in sys.argv:
 for c in D['cameras_override']:
  ob=camera(c['id'],c['room'],c['pos'],c['target'],c['lens'],c['kind'])
  if 'ortho_scale' in c:CAM[-1]['ortho_scale']=c['ortho_scale']
  if c['kind']=='顶视检查':ob.data.type='ORTHO';ob.data.ortho_scale=c.get('ortho_scale',19.4)
else:
 camera('EXT_01','外部',[31,-30,20],[11,2,2.5],35)
 camera('STAIR_UP','楼梯',[10.5,1.75,1.6],[17.3,1.75,4.4],24)
 camera('STAIR_DOWN','楼梯',[17.5,1.75,4.9],[10.5,1.75,1],24)
 camera('H2_END_W','H2',[17.6,3.4,4.9],[.1,3.4,4.5],28)
 camera('H2_END_E','H2',[.65,3.4,4.9],[18.1,3.4,4.5],28)
 camera('H2_MID_W','H2',[8.9,3.1,4.9],[.1,3.4,4.6],28)
 camera('H2_REFERENCE','H2',[17.9,2.1,4.9],[3,3.3,2.5],24)
 camera('H2_VOID_CHECK','H2',[16.7,3.8,5.65],[5.5,1.8,3.4],28)
 camera('H2_PLAN','H2',[10.5,4.5,22],[10.5,4.5,0],kind='顶视检查')
 bpy.context.object.data.type='ORTHO';bpy.context.object.data.ortho_scale=25
 camera('WT_ENTRY','WT',[-1.15,3.4,4.9],[3,3.4,4.6],24)
for r in D['rooms']:
 if r['id'] in ['A','FB','AB']:continue
 x,y,X,Y=r['box'];z=(r['level']-1)*3.3
 bpy.ops.object.light_add(type='AREA',location=((x+X)/2,(y+Y)/2,z+2.98));o=bpy.context.object;o.data.energy=55*math.sqrt((X-x)*(Y-y));o.data.shape='DISK';o.data.size=min(3,X-x,Y-y)
for pos in [[10,-12,18],[-12,5,15],[29,8,15]]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=2500;o.data.size=10;o.rotation_euler=(Vector((11,4,2))-o.location).to_track_quat('-Z','Y').to_euler()
revision=D['revision'] if '--f4' in sys.argv else 'P2.3-M1-R2'
s['model_revision']=revision;s['status']='F4关系重建；尺寸暂定；全屋覆盖待核验';s['source_sha256']=hashlib.sha256(P.read_bytes()).hexdigest()
bpy.context.preferences.filepaths.save_version=0;s.camera=bpy.data.objects['EXT_01']
data=dict(revision=revision,change='依据已确认F4重建楼梯间及调整二楼比例',status=s['status'],source_sha256=s['source_sha256'],plan=D,objects=GEO,cameras=CAM,motions=MOT)
(OUT/'模型/空间数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
txt=bpy.data.texts.new('空间数据.json');txt.write(json.dumps(data,ensure_ascii=False))
stem='秘密教学_'+D['revision'] if '--f4' in sys.argv else '秘密教学_P2.3-M1'
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'模型'/(stem+'.blend')))
bpy.ops.export_scene.gltf(filepath=str(OUT/'模型'/(stem+'.glb')),export_format='GLB',export_cameras=True,export_extras=True)
if '--render' in sys.argv:
 selected=(sys.argv[sys.argv.index('--cameras')+1].split(',') if '--cameras' in sys.argv else [c['id'] for c in CAM] if '--all' in sys.argv else ['F4_DOWN','F4_REVERSE','F4_UP','F4_PLAN','EXT_01'] if '--f4' in sys.argv else ['EXT_01','B1_01','B3_02','K_02','STAIR_UP','STAIR_DOWN'])
 for cid in selected:
  c=next(c for c in CAM if c['id']==cid);p=OUT/'空间'/c['room']/'白模视角';p.mkdir(parents=True,exist_ok=True)
  hidden=[]
  if c['kind']=='顶视检查':
   p=OUT/'空间'/c['room']/'方位检查';p.mkdir(parents=True,exist_ok=True)
   level=next(r['level'] for r in D['rooms'] if r['id']==c['room'])
   for ob in bpy.data.objects:
    if ob.type=='MESH' and not ob.hide_render and (ob.get('category')=='roof' or ob.get('level',0)>level):ob.hide_render=True;hidden.append(ob)
  s.camera=bpy.data.objects[cid];s.render.filepath=str(p/(cid+'_'+D['revision'].split('-')[-1]+'.png'));bpy.ops.render.render(write_still=True)
  for ob in hidden:ob.hide_render=False
print('P23_BUILD_COMPLETE',len(GEO),len(CAM))
