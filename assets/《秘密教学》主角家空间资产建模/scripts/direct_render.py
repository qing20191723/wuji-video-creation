"""Deterministic Cycles pilot: one physical model, multiple cameras, no image synthesis."""
import bpy,math,json,random,sys,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];random.seed(42)
ap=argparse.ArgumentParser();ap.add_argument('--samples',type=int,default=80);ap.add_argument('--only',default='');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_主角家_v4.1.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for d in p.devices:d.use=d.type!='CPU'
 if any(d.use for d in p.devices):s.cycles.device='GPU'
except Exception:pass
D=json.loads((R/'模型/空间制作配置_v4.1.json').read_text(encoding='utf8'))
def mat(name,c,rough=.5,metal=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*c,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;return m
white=mat('白色烤漆与陶器',(.8,.81,.8));wall=mat('自然白墙',(.8,.81,.81),.84);black=mat('黑色金属',(.023,.025,.028),.35,.55);silver=mat('银色五金',(.5,.53,.56),.27,.8)
pink=mat('柔粉',(.62,.31,.4),.88);blue=mat('灰蓝布艺',(.19,.26,.36),.95);leafmat=mat('绿叶',(.06,.19,.09),.56);soil=mat('盆土',(.04,.027,.015));paper=mat('纸张',(.78,.75,.69));purple=mat('紫灰',(.28,.23,.34),.9)
def wood(name,c1,c2,plank=False):
 m=mat(name,c1,.42);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY';v.inputs[1].default_value=(45,3,8);l.new(tc.outputs['Object'],v.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2;noise.inputs['Detail'].default_value=3;l.new(v.outputs[0],noise.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(*c1,1);r.color_ramp.elements[1].color=(*c2,1);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.13;b.inputs['Distance'].default_value=.007;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 if plank:
  brick=n.new('ShaderNodeTexBrick');brick.inputs['Scale'].default_value=1;brick.inputs['Brick Width'].default_value=.18;brick.inputs['Row Height'].default_value=1.4;brick.inputs['Mortar Size'].default_value=.002;brick.inputs['Mortar Smooth'].default_value=.001;l.new(tc.outputs['Object'],brick.inputs['Vector']);bb=n.new('ShaderNodeBump');bb.inputs['Strength'].default_value=.18;bb.inputs['Distance'].default_value=.012;l.new(brick.outputs['Fac'],bb.inputs['Height']);l.new(b.outputs[0],bb.inputs['Normal']);l.new(bb.outputs[0],p.inputs['Normal'])
 return m
oak=wood('浅橡木_细木纹',(.32,.20,.11),(.6,.43,.26));floor=wood('浅木地板_细拼缝',(.36,.27,.17),(.59,.46,.32),True);darkwood=wood('深木家具',(.011,.006,.003),(.046,.022,.01))
def fabric(name,c1,c2,plaid=False):
 m=mat(name,c1,.92);n=m.node_tree.nodes;l=m.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=180;l.new(tc.outputs['Generated'],noise.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.3;b.inputs['Distance'].default_value=.004;l.new(noise.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 if plaid:
  wx=n.new('ShaderNodeTexWave');wy=n.new('ShaderNodeTexWave');wx.bands_direction='X';wy.bands_direction='Y'
  for w in [wx,wy]:w.inputs['Scale'].default_value=5;w.inputs['Distortion'].default_value=0;l.new(tc.outputs['Generated'],w.inputs['Vector'])
  mx=n.new('ShaderNodeMath');mx.operation='MAXIMUM';l.new(wx.outputs['Fac'],mx.inputs[0]);l.new(wy.outputs['Fac'],mx.inputs[1]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.98;ramp.color_ramp.elements[0].color=(*c1,1);ramp.color_ramp.elements[1].position=.998;ramp.color_ramp.elements[1].color=(*c2,1);l.new(mx.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color'])
 return m
quilt=fabric('二姐_灰蓝格子床品',(.17,.23,.32),(.3,.37,.46),True);cushion=fabric('淡灰棉织物',(.54,.56,.6),(.6,.61,.63));rug=fabric('星形地毯_灰紫短绒',(.37,.35,.41),(.3,.3,.3));star=fabric('星形图案',(.115,.12,.18),(.15,.15,.18))
def assign(o,m):o.data.materials.clear();o.data.materials.append(m)
def box(name,loc,dim,m,bevel=.01):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,m)
 if bevel:b=o.modifiers.new('柔和边缘','BEVEL');b.width=bevel;b.segments=4;o.modifiers.new('表面法线','WEIGHTED_NORMAL')
 return o
def sphere(name,loc,dim,m):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);assign(o,m)
 for p in o.data.polygons:p.use_smooth=True
 return o
def rod(name,start,end,r,m):
 a,b=Vector(start),Vector(end);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=(a-b).length,location=(a+b)/2);o=bpy.context.object;o.name=name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();assign(o,m);return o
def cyl(name,loc,r,h,m):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=r,depth=h,location=loc);o=bpy.context.object;o.name=name;assign(o,m);b=o.modifiers.new('圆边','BEVEL');b.width=.005;b.segments=3;o.modifiers.new('法线','WEIGHTED_NORMAL');return o
def remove_prefix(prefix):
 for o in list(bpy.data.objects):
  if o.name==prefix or o.name.startswith(prefix+'_'):bpy.data.objects.remove(o,do_unlink=True)
for o in list(bpy.data.objects):
 if o.type!='MESH' or o.name.endswith('_ART'):continue
 g=o.get('source_group','');source=next((v for v in D['objects'] if v['id']==o.name),None)
 if 'walls' in g:
  assign(o,black if source and source['color']=='#384952' else wall)
  for mod in list(o.modifiers):o.modifiers.remove(mod)
 elif 'slabs' in g:
  assign(o,floor);o.data.materials.append(wall)
  for polygon in o.data.polygons:polygon.material_index=0 if polygon.normal.z>.5 else 1
 elif 'doors' in g or o.name.startswith('PLAQUE_'):assign(o,oak)
 elif 'furniture' in g:assign(o,white)
 if 'cap' in o.name.lower() or 'handhold' in o.name:assign(o,oak)
 if o.name.startswith('F2_BEDROOM_W_D20') and '_above' not in o.name:assign(o,oak)
# Add baseboards on solid wall segments. Door openings remain real and unchanged.
for v in D['objects']:
 if 'walls' not in v['group'] or v['kind']!='box' or v['color']=='#384952':continue
 b=v['box'];z=3.3 if v['group'].startswith('F2') else 0
 if abs(b[2]-z)>.001:continue
 dx,dy=b[3]-b[0],b[4]-b[1]
 if max(dx,dy)<.15:continue
 box('TRIM_'+v['id'],((b[0]+b[3])/2,(b[1]+b[4])/2,z+.045),(dx+.012,dy+.012,.09),oak,.003)
# The full bedroom is dressed within its accepted furniture footprints.
for key in ['Y_BED','Y_DESK','Y_DRAWERS','Y_COLLECTION','Y_RUG']:remove_prefix(key)
z=3.3
box('Y_BED_frame',(4.8,8.375,z+.26),(2.3,1.15,.3),oak,.04)
box('Y_BED_head',(3.72,8.375,z+.77),(.1,1.15,.91),oak,.045)
box('Y_BED_mattress',(4.8,8.375,z+.49),(2.24,1.10,.22),white,.09)
for yy in [8.08,8.65]:sphere('Y_BED_pillow',(4.03,yy,z+.68),(.53,.5,.17),cushion)
# Soft quilt with a real draped perimeter, no image repainting.
verts=[];faces=[];nx,ny=52,36
for i in range(nx+1):
 for j in range(ny+1):
  u=i/nx;v=j/ny;xx=4.2+u*1.8;yy=7.735+v*1.28;edge=max(0,(abs(v-.5)-.4)/.1);end=max(0,(u-.95)/.05)
  zz=z+.64-.30*edge**1.4-.17*end**1.4+.009*math.sin(u*31+v*14)+.006*math.sin(v*52+u*8)
  verts.append((xx,yy,zz))
for i in range(nx):
 for j in range(ny):k=i*(ny+1)+j;faces.append((k,k+1,k+ny+2,k+ny+1))
me=bpy.data.meshes.new('quilt');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Y_BED_quilt',me);s.collection.objects.link(o);assign(o,quilt)
for p in me.polygons:p.use_smooth=True
o.modifiers.new('织物厚度','SOLIDIFY').thickness=.006
# Desk runs along the same west wall as bed head and entry.
box('Y_DESK_top',(3.95,9.6,z+.76),(.6,1.2,.045),oak,.012)
for xx in [3.71,4.2]:
 for yy in [9.08,10.12]:rod('Y_DESK_leg',(xx,yy,z+.02),(xx,yy,z+.74),.022,white)
box('Y_BEDSIDE',(3.96,8.98,z+.31),(.5,.25,.6),oak,.015)
for zz in [.2,.4]:rod('Y_bedside_handle',(4.217,8.91,z+zz),(4.217,9.04,z+zz),.008,silver)
box('Y_LAPTOP_base',(3.94,9.64,z+.795),(.28,.36,.022),black,.005)
box('Y_LAPTOP_lid',(3.79,9.64,z+.94),(.015,.36,.28),black,.008)
screen=mat('电脑屏幕_微蓝紫',(.075,.09,.24),.3);p=screen.node_tree.nodes.get('Principled BSDF');p.inputs['Emission Color'].default_value=(.07,.06,.24,1);p.inputs['Emission Strength'].default_value=.3
box('Y_LAPTOP_display',(3.80,9.64,z+.94),(.002,.33,.25),screen,.003)
for i in range(4):
 for j in range(9):box('key',(3.87+i*.028,9.5+j*.031,z+.808),(.022,.023,.002),silver,.001)
# White chair, oriented toward west-facing desk.
box('Y_CHAIR_seat',(4.52,9.61,z+.46),(.43,.47,.075),white,.06)
box('Y_CHAIR_back',(4.73,9.61,z+.73),(.065,.46,.47),white,.07)
for yy in [9.43,9.79]:
 for xx in [4.35,4.67]:rod('Y_CHAIR_leg',(xx,yy,z+.06),(xx,yy,z+.44),.014,black)
cork=mat('软木板',(.32,.17,.09));box('Y_BOARD_frame',(3.54,9.58,z+1.33),(.042,.88,.6),oak,.012);box('Y_BOARD',(3.565,9.58,z+1.33),(.008,.84,.56),cork,.003)
for j in range(8):
 yy=9.25+(j%4)*.2;zz=z+1.19+(j//4)*.25
 note=box('Y_BOARD_note',(3.576,yy,zz),(.003,.14,.18),paper if j%2 else pink,.001);note.rotation_euler.x=(j%3-1)*.13
 cyl('Y_pin',(3.585,yy,zz+.065),.008,.012,black).rotation_euler.y=math.pi/2
# Move no furniture: actual drawer and collection cabinets use their recorded boxes.
for id,b in [('Y_DRAWERS',[6,10.65,8,11.2]),('Y_COLLECTION',[10.1,8.3,10.65,10.8])]:
 x,y,X,Y=b;h=.85 if id=='Y_DRAWERS' else .8;box(id,((x+X)/2,(y+Y)/2,z+h/2),(X-x,Y-y,h),white,.018)
 if id=='Y_DRAWERS':
  for xx in [6.5,7.5]:
   for j in range(3):
    zz=z+.14+j*.26;box(id+'_front',(xx,y-.007,zz),(.97,.015,.235),white,.007);rod('Y_handle',(xx-.12,y-.025,zz+.07),(xx+.12,y-.025,zz+.07),.007,silver)
 else:
  for yy in [8.65,9.4,10.15]:
   box(id+'_door',(x-.01,yy,z+.4),(.02,.71,.72),white,.008)
   rod('Y_handle',(x-.028,yy+.21,z+.3),(x-.028,yy+.21,z+.5),.007,silver)
# Star rug, literal geometry and textured fabric.
box('Y_RUG',(6.85,9.85,z+.015),(1.5,1.5,.03),rug,.025)
vs=[(6.85,9.85,z+.032)]
for i in range(10):ang=math.pi/2+i*math.pi/5;r=.64 if i%2==0 else .285;vs.append((6.85+r*math.cos(ang),9.85+r*math.sin(ang),z+.033))
me=bpy.data.meshes.new('rugstar');me.from_pydata(vs,[],[(0,i+1,(i+1)%10+1) for i in range(10)]);me.update();o=bpy.data.objects.new('Y_RUG_STAR',me);s.collection.objects.link(o);assign(o,star)
# Desk lamp, mug, books, figurines and plants are fixed mesh objects.
cyl('Y_LAMP_base',(4.0,10.04,z+.80),.085,.025,black);rod('Y_LAMP_arm',(4,10.04,z+.82),(3.82,10.02,z+1.15),.012,black);rod('Y_LAMP_neck',(3.82,10.02,z+1.15),(3.99,9.97,z+1.25),.012,black)
bpy.ops.mesh.primitive_cone_add(vertices=40,radius1=.07,radius2=.032,depth=.1,location=(4.01,9.97,z+1.19));shade=bpy.context.object;shade.name='Y_LAMP_shade';assign(shade,black)
cyl('Y_MUG',(4.08,9.3,z+.83),.035,.1,white)
for i in range(3):box('Y_BOOK',(6.35,10.9,z+.87+i*.033),(.26,.18,.028),[pink,blue,paper][i],.003)
def plant(name,loc,scale):
 x,y,zz=loc;cyl(name+'_pot',(x,y,zz+.08*scale),.085*scale,.16*scale,white);cyl(name+'_soil',(x,y,zz+.159*scale),.075*scale,.008*scale,soil)
 for k in range(11):
  ang=k*2.4;end=(x+.13*scale*math.cos(ang),y+.13*scale*math.sin(ang),zz+scale*(.26+.13*(k%3)/2));rod(name+'_stem',(x,y,zz+.14*scale),end,.003*scale,leafmat);o=sphere(name+'_leaf',end,(.11*scale,.045*scale,.018*scale),leafmat);o.rotation_euler=(.3,ang*.2,ang)
plant('Y_DESK_PLANT',(3.99,9.16,z+.79),.55);plant('Y_COLLECTION_PLANT',(10.37,10.48,z+.8),1.1)
for k in range(7):
 x=10.36;y=8.5+k*.24;zz=z+.8;m=[pink,purple,blue,white][k%4]
 sphere('Y_FIGURE_body',(x,y,zz+.08),(.09,.08,.13),m);sphere('Y_FIGURE_head',(x,y,zz+.18),(.10,.10,.10),m)
 for yy in [y-.029,y+.029]:sphere('Y_FIGURE_eye',(x-.048,yy,zz+.19),(.011,.01,.011),black)
# Cow plush on the bed, all spots actual geometry.
sphere('Y_COW_body',(4.37,8.45,z+.81),(.43,.23,.24),white);sphere('Y_COW_head',(4.19,8.45,z+.94),(.24,.23,.24),white)
sphere('Y_COW_muzzle',(4.31,8.45,z+.90),(.12,.19,.11),white)
for yy in [8.375,8.525]:sphere('Y_COW_eye',(4.29,yy,z+.99),(.013,.015,.018),black)
for yy in [8.31,8.59]:sphere('Y_COW_ear',(4.18,yy,z+1.00),(.13,.1,.048),white)
for xx in [4.23,4.52]:
 for yy in [8.34,8.56]:sphere('Y_COW_foot',(xx,yy,z+.72),(.11,.075,.13),black)
for xx,yy,zz in [(4.49,8.53,z+.85),(4.42,8.34,z+.81),(4.18,8.55,z+.99)]:sphere('Y_COW_spot',(xx,yy,zz),(.09,.015,.066),black)
# Black frames and curtains on the existing east window, no change to opening size.
for op in D['openings']:
 if op['type']!='window' or op['level']!=2:continue
 if op['axis']!=1 or abs(op['a'][0]-10.8)>.01:continue
 if not (7.6<=op['s']<=11.4):continue
 for edge in [op['s']+.08,op['s']+op['w']-.3]:
  vv=[];ff=[]
  for i in range(25):
   for j in range(2):vv.append((10.6+.045*math.sin(i*math.pi/3),edge+i*.015,3.45+j*2.5))
  for i in range(24):ff.append((2*i,2*i+1,2*i+3,2*i+2))
  me=bpy.data.meshes.new('curtain');me.from_pydata(vv,[],ff);me.update();o=bpy.data.objects.new('Y_CURTAIN',me);s.collection.objects.link(o);assign(o,cushion);o.modifiers.new('帘布厚度','SOLIDIFY').thickness=.004
# Soft outdoor foliage is real geometry outside the building.
green2=mat('树叶浅绿',(.12,.23,.07),.9)
for x,y in [(-3,3),(-3,9),(-2,15),(16,8),(16,12),(8,19),(3,-4)]:
 rod('TREE_trunk',(x,y,-.2),(x,y,5),.12,darkwood)
 verts=[];faces=[]
 for k in range(4500):
  az=random.uniform(0,math.tau);h=random.uniform(-1,1);r=random.random()**(1/3)*1.6;v=Vector((math.sqrt(1-h*h)*math.cos(az),math.sqrt(1-h*h)*math.sin(az),h));center=Vector((x,y,4.8))+v*r;up=v.cross(Vector((0,0,1))).normalized();side=v.cross(up).normalized();size=random.uniform(.075,.15);start=len(verts)
  for u,w in [(0,-1),(.4,-.35),(.45,.25),(0,1),(-.45,.25),(-.4,-.35)]:verts.append(tuple(center+up*u*size+side*w*size))
  faces.append(tuple(range(start,start+6)))
 me=bpy.data.meshes.new('foliage');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('TREE_foliage',me);s.collection.objects.link(o);me.materials.append(leafmat);me.materials.append(green2)
 for face in me.polygons:face.material_index=random.randrange(2)
# Dress remaining principal rooms without editing any structural object.
exec(compile((R/'scripts/detail_rooms.py').read_text(encoding='utf8'),str(R/'scripts/detail_rooms.py'),'exec'))
# Lights are fixed; only exposure/intensity/color switches between time presets.
for o in bpy.data.objects:
 if o.type=='LIGHT':
  o['base_energy']=o.data.energy
  if o.data.type=='AREA':
   if '检查光' in o.name:
    room=next((r for r in D['rooms'] if r['id'] in o.name),None)
    b=room['box'] if room else [0,0,3,3];o['room_area']=(b[2]-b[0])*(b[3]-b[1]);o.data.size=max(.35,min(2.5,b[2]-b[0]-.5,b[3]-b[1]-.5))
   else:o.data.size=12
def time_state(night):
 sys.path.insert(0,str(R/'scripts'))
 from lighting import set_time
 set_time(s,bpy.data.objects,night)
jobs=[]
for id,pos,target,lens in [
 ('二姐卧室_前视图',[8.3,9.65,4.92],[3.7,9.65,4.92],22),
 ('二姐卧室_侧视图',[9.75,10.55,4.92],[4.5,8.7,4.2],22),
 ('二姐卧室_后视图',[4.7,9.8,4.92],[10.5,9.65,4.7],22),
 ('二姐卧室_俯拍图',[7.1,10.35,6.25],[6.55,9.35,3.65],16)]:
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name='DIRECT_'+id;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.04;jobs.append((id,o))
jobs.extend([('二楼走廊_三门同框平视全景',bpy.data.objects['H2_PAN']),('二楼走廊_三门正面关系图',bpy.data.objects['H2_ELEV'])])
jobs.extend(extra_jobs)
s['render_method']='Cycles direct render only. No imagegen repaint. Main-room furniture development; service spaces still require refinement.'
s['user_update']='2026-10-14 改用同一模型多机位直接渲染；AI试图不作终稿。'
time_state(False);s.camera=jobs[0][1];bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'模型/秘密教学_主角家_直接渲染_v4.3.blend'))
basehidden={o.name:o.hide_render for o in bpy.data.objects};out=R/'预览/直接渲染';out.mkdir(parents=True,exist_ok=True);records=[]
for name,cam in jobs:
 if a.only and a.only not in name:continue
 for night in [False,True]:
  for o in bpy.data.objects:o.hide_render=basehidden[o.name]
  elev='关系图' in name
  if elev:
   for o in bpy.data.objects:
    if o.type not in ['LIGHT','CAMERA']:o.hide_render=not(o.name.startswith(('F2_BEDROOM_W','PLAQUE_','TEXT_','HANDLE_')) or o.name in ['D203_leaf','D204_leaf','D205_leaf','BR_HALL_ART'])
  time_state(night);s.camera=cam;s.render.resolution_x=3000 if elev else 1920;s.render.resolution_y=1000 if elev else 1080
  fn=name+('（夜间）' if night else '（日景）')+'.png';s.render.filepath=str(out/fn);bpy.ops.render.render(write_still=True)
  records.append({'file':fn,'camera':cam.name,'pos':list(cam.location),'rotation':list(cam.rotation_euler),'lens':cam.data.lens,'time':'night' if night else 'day','method':'Blender Cycles deterministic direct render','geometry_changes_between_views':False,'status':'pilot_requires_visual_review'})
(R/'制作记录/直接渲染首批.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
print('DIRECT_PILOT_DONE',len(records))
