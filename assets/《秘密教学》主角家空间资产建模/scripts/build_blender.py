import bpy,json,math,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'模型/空间主数据_v4.json').read_text(encoding='utf8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='CYCLES';s.cycles.samples=20;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for dev in p.devices:dev.use=dev.type!='CPU'
 if any(dev.use for dev in p.devices):s.cycles.device='GPU'
except Exception:pass
s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX'
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.84,.91,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.35
coll={};mats={};obs={}
def put(o,g):
 if g not in coll:
  coll[g]=bpy.data.collections.new(g);s.collection.children.link(coll[g])
 for c in list(o.users_collection):c.objects.unlink(o)
 coll[g].objects.link(o)
def mat(hex,glass=False):
 key=hex+str(glass)
 if key in mats:return mats[key]
 c=tuple(int(hex[i:i+2],16)/255 for i in (1,3,5));m=bpy.data.materials.new('中性_'+key);m.diffuse_color=(*c,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in c),1);p.inputs['Roughness'].default_value=.6
 if glass:
  nt=m.node_tree;nt.nodes.clear();out=nt.nodes.new('ShaderNodeOutputMaterial');tr=nt.nodes.new('ShaderNodeBsdfTransparent');nt.links.new(tr.outputs[0],out.inputs[0])
 mats[key]=m;return m
for d in D['objects']:
 b=d['box'];kind=d['kind']
 if kind=='mesh':
  me=bpy.data.meshes.new(d['id']);me.from_pydata(d['vertices'],[],d['faces']);me.update();o=bpy.data.objects.new(d['id'],me);s.collection.objects.link(o)
 elif kind=='bar':
  a,c=Vector(d['a']),Vector(d['b']);bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=d['radius'],depth=(c-a).length,location=(a+c)/2);o=bpy.context.object;o.rotation_euler=(c-a).to_track_quat('Z','Y').to_euler()
 else:
  bpy.ops.mesh.primitive_cube_add(size=1,location=[(b[k]+b[k+3])/2 for k in range(3)]);o=bpy.context.object;o.dimensions=[max(.001,b[k+3]-b[k]) for k in range(3)];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.name=d['id'];o.data.materials.append(mat(d['color'],'glass' in d['group']));put(o,d['group']);obs[d['id']]=o;o['source_group']=d['group'];o['solid_for_check']=d['solid']
 if d.get('label'):o['label']=d['label']
 if kind=='box' and 'glass' not in d['group']:
  be=o.modifiers.new('边缘可读性','BEVEL');be.width=.007;be.segments=1
for r in D['rooms']:
 e=bpy.data.objects.new(r['id']+'_'+r['name'],None);put(e,'房间标记');b=r['box'];e.location=((b[0]+b[2])/2,(b[1]+b[3])/2,(r['level']-1)*3.3+.05);e.empty_display_size=.15;e['source']=r['source'];e['reference_dimensions_only']=True
for c in D['cameras']:
 bpy.ops.object.camera_add(location=c['pos']);o=bpy.context.object;o.name=c['id']+'_'+c['name'];o.rotation_euler=(Vector(c['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=c['lens'];o.data.clip_start=.03;o.data.clip_end=250;put(o,'Cameras');obs[c['id']]=o
def area(name,pos,power,size,target):
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.name=name;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();put(o,'Lighting')
area('外部柔光',[3,-7,14],4000,10,[6,6,0]);area('西侧柔光',[-7,6,10],3500,10,[5,6,2]);area('东侧柔光',[20,8,12],3500,10,[6,8,2])
for r in D['rooms']:
 if r['id'] in ['R209','R210','R211']:continue
 b=r['box'];x=(b[0]+b[2])/2;y=(b[1]+b[3])/2;z=(r['level']-1)*3.3
 area('检查光_'+r['id'],[x,y,z+2.9],55*math.sqrt((b[2]-b[0])*(b[3]-b[1])),2,[x,y,z])
def visible(d,mode):
 g=d['group'];b=d['box'];id=d['id']
 if mode=='floor1':return (g.startswith('F1') or g=='Stairs') and not id.startswith(('STAIR_handhold','RAIL_')) and 'brands' not in g
 if mode=='floor2':return (g.startswith('F2') or g=='Stairs') and 'brands' not in g
 if mode=='stairs':return (g=='Stairs' or g=='F2_guard' or g in ['F1_slabs','F2_slabs'] or ((g.startswith('F1') or g.startswith('F2')) and b[0]>=.12 and b[0]<3.45 and b[1]<13 and 'furniture' not in g and 'brands' not in g)) and not id.startswith(('STAIR_handhold_0.14','RAIL_bracket_0.14'))
 return True
def mode(m):
 for d in D['objects']:
  o=obs[d['id']];o.hide_render=not visible(d,m);o.hide_set(o.hide_render)
 # Cut walls to 1.15 m for overhead plan inspection, keeping original mesh untouched.
 for d in D['objects']:
  o=obs[d['id']];o.scale=(1,1,1)
  if d['kind']=='box':o.location=[(d['box'][k]+d['box'][k+3])/2 for k in range(3)]
  if m=='stairs' and d['group'] in ['F1_slabs','F2_slabs']:
   b=d['box'];bb=[max(b[0],.1),max(b[1],0),b[2],min(b[3],3.5),min(b[4],9.2),b[5]]
   if bb[0]>=bb[3] or bb[1]>=bb[4]:o.hide_render=True;o.hide_set(True)
   else:
    o.scale=[(bb[k+3]-bb[k])/(b[k+3]-b[k]) for k in range(3)];o.location=[(bb[k]+bb[k+3])/2 for k in range(3)]
  if m in ['floor1','floor2'] and ('walls' in d['group'] or 'doors' in d['group'] or 'glass' in d['group']):
   z=0 if d['group'].startswith('F1') else 3.3;b=d['box'];top=z+1.15
   if b[2]>=top:o.hide_render=True;o.hide_set(True)
   else:
    h=min(b[5],top)-b[2];o.scale.z=h/(b[5]-b[2]);o.location.z=b[2]+h/2
mode('all');s.camera=obs['C01']
s['说明']='全屋中性空间模型。A端上平台→B端下楼；影视参考尺寸。正式场景生成等待用户验收。'
txt=bpy.data.texts.new('空间主数据_v4.json');txt.write(json.dumps(D,ensure_ascii=False,indent=2))
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'模型/秘密教学_全屋空间_v4.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'模型/秘密教学_全屋空间_v4.glb'),export_format='GLB',export_cameras=True,export_extras=True)
for c in D['cameras']:
 mode(c['mode']);s.camera=obs[c['id']];s.render.filepath=str(R/'预览'/f"{c['id']}.png");bpy.ops.render.render(write_still=True)
print('ALL_RENDERS_COMPLETE')
