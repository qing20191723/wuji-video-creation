"""blender -b --python scripts/production_blender.py -- --font <CJK.ttf>"""
import bpy,json,math,os,sys,argparse
from pathlib import Path
from mathutils import Vector,Matrix
R=Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser();ap.add_argument('--font',default=os.environ.get('HOME_ASSETS_FONT'));ap.add_argument('--render',default='H2_PAN,H2_ELEV,LIV_MAIN,YOU_MAIN');a=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
if not a.font or not Path(a.font).is_file():raise RuntimeError('Pass --font with a CJK font supporting 舒亚の窝 / 子豪の窝 / 薇亚的窝. Fonts are converted to meshes, not redistributed.')
D=json.loads((R/'模型/空间制作配置_v4.1.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_全屋空间_v4.blend'))
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for dev in p.devices:dev.use=dev.type!='CPU'
 if any(dev.use for dev in p.devices):s.cycles.device='GPU'
except Exception:pass
font=bpy.data.fonts.load(a.font)
def material(name,c):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*c,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.55;return m
wood=material('牌与门_淡橡木',(.55,.39,.23));white=material('浅色墙',(.79,.80,.79));floor=material('浅木地板',(.49,.36,.24));ink=material('深棕手写字',(.07,.036,.016))
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 g=ob.get('source_group','')
 if 'walls' in g or g=='F2_guard':ob.data.materials.clear();ob.data.materials.append(white)
 elif 'slabs' in g:ob.data.materials.clear();ob.data.materials.append(floor)
 elif 'doors' in g:ob.data.materials.clear();ob.data.materials.append(wood)
def cube(name,loc,dim,mat,bevel=0):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:m=o.modifiers.new('圆润边缘','BEVEL');m.width=bevel;m.segments=5;o.modifiers.new('法线','WEIGHTED_NORMAL')
 return o
# Mesh glyphs ensure exact plaque text without a system-font dependency in saved models.
orient=Matrix(((0,0,-1),(-1,0,0),(0,1,0))).to_4x4()
for plaque in D['door_plaques']:
 op=next(p for p in D['openings'] if p['id']==plaque['door']);leaf=bpy.data.objects[plaque['door']+'_leaf'];leaf.location=(3.4,op['s']+op['w']/2,3.3+1.08);leaf.dimensions=(.046,op['w'],2.16)
 plaque['door_state']='closed';x,y,z=plaque['center'];o=cube('PLAQUE_'+plaque['door'],(x,y,z),(.034,.46,.23),wood,.045)
 bpy.ops.object.text_add(location=(x-.02,y,z));t=bpy.context.object;t.name='TEXT_'+plaque['door'];t.data.body=plaque['text'];t.data.font=font;t.data.align_x='CENTER';t.data.align_y='CENTER';t.data.size=.105;t.data.extrude=.0007;t.rotation_euler=orient.to_euler();t.data.materials.append(ink);t['exact_text']=plaque['text'];bpy.ops.object.convert(target='MESH')
 # handle on closed leaf, away from hinge; no extra signage.
 cube('HANDLE_'+plaque['door'],(3.355,op['s']+op['w']-.14,4.32),(.07,.19,.032),ink,.01)
img=bpy.data.images.load(str(R/'品牌/黄瓜短剧_无域名_透明底.png'));img.pack()
brandmat=bpy.data.materials.new('黄瓜短剧_图标金白文字_无域名');brandmat.use_nodes=True
nt=brandmat.node_tree;p=nt.nodes.get('Principled BSDF');tx=nt.nodes.new('ShaderNodeTexImage');tx.image=img;nt.links.new(tx.outputs['Color'],p.inputs['Base Color']);nt.links.new(tx.outputs['Alpha'],p.inputs['Alpha']);p.inputs['Roughness'].default_value=.5
for brand in D['brands']:
 ob=bpy.data.objects.get(brand['id']);ob.hide_render=True;ob.hide_set(True)
 b=brand['box'];cx=(b[0]+b[2])/2;cy=(b[1]+b[3])/2;cz=(brand['level']-1)*3.3+brand['center_height'];w=brand['width'];h=w/3
 # Face the room: choose the side of each carrier that faces occupied space.
 if b[2]-b[0] > b[3]-b[1]:
  sign=1 if brand['id']=='BR_ENTRY' else -1
  yy=cy+sign*.023;verts=[(cx-w/2,yy,cz-h/2),(cx+w/2,yy,cz-h/2),(cx+w/2,yy,cz+h/2),(cx-w/2,yy,cz+h/2)]
 else:
  sign=1 if brand['id'] in ['BR_GWC','BR_YOUNGER','BR_SIDE'] else -1;xx=cx+sign*.023
  ys=[cy+w/2,cy-w/2] if sign==-1 else [cy-w/2,cy+w/2]
  verts=[(xx,ys[0],cz-h/2),(xx,ys[1],cz-h/2),(xx,ys[1],cz+h/2),(xx,ys[0],cz+h/2)]
 me=bpy.data.meshes.new(brand['id']+'_decal');me.from_pydata(verts,[],[(0,1,2,3)]);me.update();uv=me.uv_layers.new();
 for j,co in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[j].uv=co
 ob=bpy.data.objects.new(brand['id']+'_ART',me);s.collection.objects.link(ob);me.materials.append(brandmat);ob['carrier_id']=brand['id']
cams={}
for c in D['production_cameras']:
 bpy.ops.object.camera_add(location=c['pos']);o=bpy.context.object;o.name=c['id'];o.rotation_euler=(Vector(c['target'])-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=c['lens'];o.data.type=c['projection'];o.data.clip_start=.03
 if c['projection']=='ORTHO':o.data.ortho_scale=c['ortho_scale']
 cams[c['id']]=o
def lighting(state):
 s.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.88,1,1) if state=='day' else (.1,.14,.23,1)
 s.world.node_tree.nodes['Background'].inputs[1].default_value=.5 if state=='day' else .06
 for o in bpy.data.objects:
  if o.type!='LIGHT':continue
  if '外部' in o.name or '侧柔光' in o.name:o.data.energy=4500 if state=='day' else 80;o.data.size=12
  else:o.data.energy=170 if state=='day' else 300;o.data.size=2.5
  o.data.color=(1,1,1) if state=='day' else (1,.84,.68)
 s['lighting_state']=state
s['说明']='2026-10-14用户已认可v4空间。v4.1仅新增机位、柔光预设、木制姓名牌与品牌。三扇卧室门为关闭状态。'
s['baseline_geometry']='空间主数据_v4.json';s.camera=cams['H2_PAN'];lighting('day');bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'模型/秘密教学_主角家_v4.1.blend'))
bpy.ops.export_scene.gltf(filepath=str(R/'模型/秘密教学_主角家_v4.1.glb'),export_format='GLB',export_cameras=True,export_extras=True)
basehidden={o.name:o.hide_render for o in bpy.data.objects}
for c in D['production_cameras']:
 if c['id'] not in a.render.split(','):continue
 for state in ['day','night']:
  for o in bpy.data.objects:o.hide_render=basehidden[o.name]
  if c['id']=='H2_ELEV':
   for o in bpy.data.objects:
    if o.type=='LIGHT' or o.type=='CAMERA':continue
    o.hide_render=not (o.name.startswith('F2_BEDROOM_W') or o.name.startswith(('PLAQUE_','TEXT_','HANDLE_')) or o.name in ['D203_leaf','D204_leaf','D205_leaf','BR_HALL_ART'])
  lighting(state);s.camera=cams[c['id']];s.render.resolution_x=c['resolution'][0];s.render.resolution_y=c['resolution'][1];s.render.resolution_percentage=100;s.render.filepath=str(R/'预览'/f'{c["id"]}_{state}.png');bpy.ops.render.render(write_still=True)
print('PRODUCTION_GUIDES_DONE')
