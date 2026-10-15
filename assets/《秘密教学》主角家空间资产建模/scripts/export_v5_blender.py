"""Blender adapter: no independent room coordinates permitted here."""
import bpy,json,sys,math,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--render',default='E_side,E_reverse,E_cut,KLD_K_front,KLD_K_reverse,KLD_cut,M_front,M_cut,Y_front,Y_cut,P_front,P_cut,LA_front,LA_cut,SITE_front,SITE_garden,HOME_floor1,HOME_floor2,HOME_A,HOME_turn,HOME_stairs_up,HOME_exterior,HOME_court');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.unit_settings.system='METRIC';s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=1600;s.render.resolution_y=1000;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
s.display.shading.light='STUDIO';s.display.shading.studio_light='paint.sl';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.show_object_outline=True;s.display.shading.background_type='WORLD';s.world.color=(.76,.79,.80)
s.view_settings.view_transform='Standard';s.view_settings.look='None'
offsets={m['id']:Vector((i*32,0,0)) for i,m in enumerate(D['modules'])};colls={};objs={};mats={}
def put(o,g):
 if g not in colls:
  colls[g]=bpy.data.collections.new(g);s.collection.children.link(colls[g])
 for c in list(o.users_collection):c.objects.unlink(o)
 colls[g].objects.link(o)
def material(c):
 if c in mats:return mats[c]
 rgb=[int(c[i:i+2],16)/255 for i in [1,3,5]];m=bpy.data.materials.new(c);m.diffuse_color=(*rgb,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*rgb,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.65;mats[c]=m;return m
for d in D['objects']:
 b=d['box'];mid=Vector([(b[k]+b[k+3])/2 for k in range(3)]);dims=Vector([b[k+3]-b[k] for k in range(3)]);off=offsets[d['module']]
 if d['kind']=='mesh':
  me=bpy.data.meshes.new(d['id']);me.from_pydata(d['vertices'],[],d['faces']);me.update();o=bpy.data.objects.new(d['id'],me);s.collection.objects.link(o);o.location=off
 elif d['kind']=='bar':
  av,bv=Vector(d['a']),Vector(d['b']);bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=d['radius'],depth=(bv-av).length,location=(av+bv)/2+off);o=bpy.context.object;o.rotation_euler=(bv-av).to_track_quat('Z','Y').to_euler()
 elif d['kind']=='cylinder':bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=d['radius'],depth=dims.z,location=mid+off);o=bpy.context.object
 elif d['kind']=='ellipsoid':bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=mid+off);o=bpy.context.object;o.scale=dims/2
 else:bpy.ops.mesh.primitive_cube_add(size=1,location=mid+off);o=bpy.context.object;o.dimensions=dims
 o.name=d['id'];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(material(d['color']));put(o,d['module']+'/'+d['role']);o['role']=d['role'];o['reference_module']=d['module'];o['design_reference_only']=True;objs[d['id']]=o
 if d['role']=='glass':o.display_type='WIRE';o.hide_render=True
 if d['role']=='ceiling':o.hide_render=True;o.hide_set(True)
 for k in ['note','label','text']:
  if k in d:o[k]=d[k]
 if d['kind']=='box' and d['role'] not in ['massing','floor','site','wall','glass','ceiling']:
  mod=o.modifiers.new('边缘','BEVEL');mod.width=.012;mod.segments=2
cams={}
for c in D['cameras']:
 off=offsets[c['module']];bpy.ops.object.camera_add(location=Vector(c['pos'])+off);o=bpy.context.object;o.name=c['id'];o.rotation_euler=(Vector(c['target'])+off-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=c['lens'];o.data.clip_start=.02;o.data.clip_end=250;o['cutaway']=c['cutaway'];put(o,c['module']+'/cameras');cams[c['id']]=o
t=bpy.data.texts.new('空间校准主数据_v5.json');t.write(json.dumps(D,ensure_ascii=False,indent=2));s['status']='V3房间校准与采光院全屋拼接提案，待整体复核，不可作为正式出图基线';s['module_offsets']=json.dumps({k:list(v) for k,v in offsets.items()});s.camera=cams['E_side']
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'模型/秘密教学_V3校准模块_v5.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'模型/秘密教学_V3校准模块_v5.glb'),export_format='GLB',export_cameras=True,export_extras=True)
out=R/'预览/v5';out.mkdir(parents=True,exist_ok=True)
for cid in a.render.split(','):
 if cid not in cams:continue
 c=next(c for c in D['cameras'] if c['id']==cid)
 for d in D['objects']:
  hide=d['module']!=c['module'] or d['role']=='glass' or (c['cutaway'] and d['role']=='ceiling')
  if c['module']=='HOME':
   lm=c.get('level_mode','all')
   shared=d['role']=='stair' or d['id']=='HOME_stair_separating_support'
   if lm=='F1' and ((d.get('level')==2 and not shared) or d.get('zone')=='site'):hide=True
   if lm=='F2' and d.get('level')!=2 and not shared:hide=True
  o=objs[d['id']];o.hide_render=hide
 s.camera=cams[cid];s.render.filepath=str(out/(cid+'.png'));bpy.ops.render.render(write_still=True)
print('V5_EXPORT_COMPLETE')
