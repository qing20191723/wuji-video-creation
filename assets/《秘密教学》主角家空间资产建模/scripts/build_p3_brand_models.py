"""Blender 4.5: independent named signs, complete normal/mirror brands and icon sculpture."""
import bpy,math,json,sys,hashlib,bmesh
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]/'完整平面与品牌_P3_20261022';O=R/'独立模型';T=R/'品牌贴图'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.name='P3_brand_asset_library';S.unit_settings.system='METRIC';S.render.engine='CYCLES';S.cycles.samples=12;S.cycles.use_denoising=True
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
 for dev in prefs.devices:dev.use=dev.type=='OPTIX'
 if any(dev.use for dev in prefs.devices):S.cycles.device='GPU'
except Exception:pass
S.render.resolution_x=1200;S.render.resolution_y=650;S.render.resolution_percentage=100;S.render.image_settings.file_format='PNG';S.render.film_transparent=True
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.79,.82,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.5
S.view_settings.view_transform='Standard';S.view_settings.look='Medium High Contrast' if False else 'None'
font=bpy.data.fonts.load('C:/Windows/Fonts/msyhbd.ttc');latin=bpy.data.fonts.load('C:/Windows/Fonts/arial.ttf')
def material(name,color,metal=0,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=.32
 if emit:p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m
gold=material('金色边缘',(.63,.40,.06),.65);black=material('黑色牌体',(.009,.012,.009));ivory=material('门牌暖白',(.82,.79,.70));ink=material('门牌黑字',(.008,.012,.009));white=material('白色字',(.92,.92,.88));green=material('品牌绿色',(.22,.43,.01),.1)
neongold=material('文字本体自发光_金',(.8,.55,.06),.2,2);neonwhite=material('文字本体自发光_白',(.92,.94,.92),0,1.4);backmat=material('背光_不等于文字自发光',(.8,.55,.1),0,1.2)
assets=[];glyphchecks=[]
def coll(name):
 c=bpy.data.collections.new(name);S.collection.children.link(c);return c
def move(o,c):
 for old in list(o.users_collection):old.objects.unlink(o)
 c.objects.link(o);return o
def cube(name,loc,dims,mat,c,bevel=.015):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=move(bpy.context.object,c);o.name=name;o.dimensions=dims;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
 if bevel:
  mod=o.modifiers.new('真实圆角','BEVEL');mod.width=bevel;mod.segments=4;bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
 return o
def glyph(text,loc,width,height,mat,c,name):
 cu=bpy.data.curves.new(name,'FONT');cu.body=text;cu.font=latin if text.isascii() else font;cu.align_x='CENTER';cu.align_y='CENTER';cu.size=1;cu.extrude=.007;cu.bevel_depth=.001;cu.bevel_resolution=2
 o=bpy.data.objects.new(name,cu);c.objects.link(o);o.location=loc;o.rotation_euler=(math.pi/2,0,0);bpy.context.view_layer.update();scale=min(width/max(o.dimensions.x,.0001),height/max(o.dimensions.z,.0001));o.scale=(scale,scale,scale);o.data.materials.append(mat)
 o['exact_text']=text;o['editable_source']='品牌贴图/品牌文字源.json';bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.select_set(False);glyphchecks.append(dict(name=name,text=text,vertices=len(o.data.vertices)));return o
def texmat(name,filename,emission=0):
 m=bpy.data.materials.new(name);m.use_nodes=True;nt=m.node_tree;p=nt.nodes.get('Principled BSDF');im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(T/filename),check_existing=True);im.image.pack();nt.links.new(im.outputs['Color'],p.inputs['Base Color']);nt.links.new(im.outputs['Alpha'],p.inputs['Alpha']);p.inputs['Roughness'].default_value=.45
 if emission:
  nt.links.new(im.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=emission
 m.surface_render_method='DITHERED';return m
def face(name,w,h,y,mat,c):
 me=bpy.data.meshes.new(name);me.from_pydata([[-w/2,y,-h/2],[w/2,y,-h/2],[w/2,y,h/2],[-w/2,y,h/2]],[],[[0,1,2,3]]);me.update();uv=me.uv_layers.new(name='UVMap')
 for i,p in enumerate([(0,0),(1,0),(1,1),(0,1)]):uv.data[i].uv=p
 o=bpy.data.objects.new(name,me);c.objects.link(o);o.data.materials.append(mat);return o
poly=json.loads((R/'数据/Logo轮廓.json').read_text(encoding='utf8'))
def icon(c,center=(0,0,0),height=.4,emission=0):
 W,H=poly['width'],poly['height'];k=height/H;pts=[((x-W/2)*k,(H/2-y)*k) for x,y in poly['points']];n=len(pts);depth=.025;verts=[(x,yy,z) for yy in [-depth/2,depth/2] for x,z in pts]
 # Filled silhouette has real thickness; exact artwork supplies color on the front.
 faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 me=bpy.data.meshes.new('源图轮廓实体');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Logo图标_实体轮廓',me);c.objects.link(o);o.location=center;o.data.materials.append(gold)
 bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
 front=face('原Logo图形贴面',W*k,H*k,-depth/2-.0005,texmat('图标原色'+str(emission),'HG_ICON.png',emission),c);front.location=center
 return o
def mirror(c):
 for o in c.objects:
  if o.type!='MESH':continue
  o.location.x=-o.location.x
  for v in o.data.vertices:v.co.x=-v.co.x
  bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.reverse_faces(bm,faces=bm.faces);bm.to_mesh(o.data);bm.free();o['variant']='mirror'
def record(id,c,kind,w,h):
 for o in c.objects:o['asset_id']=id;o['fixed_world_orientation']=True;o['camera_facing']=False
 assets.append(dict(id=id,collection=c,kind=kind,width=w,height=h))
for id,label in [('NAME_B1','薇亚の窝'),('NAME_B2','子豪の窝'),('NAME_B3','舒亚の窝'),('NAME_BW','公共浴室')]:
 c=coll(id);cube(id+'_牌体',(0,0,0),(.44,.026,.19),ivory,c,.018);glyph(label,(0,-.016,0),.38,.11,ink,c,id+'_固定字形');record(id,c,'nameplate',.44,.19)
for variant in ['normal','mirror']:
 c=coll('HG_PLAQUE_'+variant);cube('实体牌体',(0,0,0),(1.6,.07,.76),black,c,.06);face('完整标识及域名',1.6,.76,-.036,texmat('完整版_'+variant,'HG_FULL_'+variant+'.png'),c);record('HG_PLAQUE_'+variant,c,'non_emissive',1.6,.76)
 c=coll('HG_NEON_'+variant);cube('外边框',(0,0,0),(1.6,.07,.76),gold,c,.06);cube('黑底',(0,-.012,0),(1.57,.075,.73),black,c,.055)
 icon(c,(-.56,-.061,.12),.42,1.7);glyph('黄瓜',(-.08,-.053,.11),.45,.23,neongold,c,'黄瓜_本体发光');glyph('短剧',(.43,-.053,.11),.45,.23,neonwhite,c,'短剧_本体发光');glyph('hgdju.com',(0,-.053,-.22),1.1,.12,neongold,c,'永久域名_本体发光')
 # Backlight is a separate disabled material-bearing object, never substituted for glowing glyphs.
 b=cube('背光层_默认关闭',(0,.04,0),(1.52,.008,.68),backmat,c,.05);b.hide_render=True;b.hide_viewport=True;b['optional_backlight']=True
 if variant=='mirror':mirror(c)
 record('HG_NEON_'+variant,c,'glyph_emission',1.6,.76)
 c=coll('HG_SCULPTURE_'+variant);bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.24,depth=.075,location=(0,0,-.24));o=move(bpy.context.object,c);o.name='实体圆底座';o.data.materials.append(ivory);icon(c,(0,0,.05),.6);glyph('黄瓜短剧',(0,-.242,-.24),.36,.052,green,c,'底座品牌文字');
 if variant=='mirror':mirror(c)
 record('HG_SCULPTURE_'+variant,c,'sculpture',.5,.65)
# Validate font coverage character-by-character instead of accepting tofu geometry.
for ch in '薇亚の窝子豪舒公共浴室黄瓜短剧':
 cu=bpy.data.curves.new('check_'+ch,'FONT');cu.font=font;cu.body=ch;o=bpy.data.objects.new('check_'+ch,cu);S.collection.objects.link(o);bpy.context.view_layer.objects.active=o;o.select_set(True);bpy.ops.object.convert(target='MESH');glyphchecks.append(dict(character=ch,vertices=len(o.data.vertices)));bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.camera_add(location=(0,-3,.12));cam=bpy.context.object;cam.name='资产检查机位';cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1.95;S.camera=cam
for pos,power,size in [((-2,-3,3),350,4),((2,-2,1),220,3)]:
 bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
manifest=[]
for item in assets:
 c=item['collection'];id=item['id']
 for a in assets:a['collection'].hide_render=a['collection']!=c
 bpy.ops.object.select_all(action='DESELECT')
 for o in c.objects:
  if not o.get('optional_backlight'):o.hide_viewport=False;o.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(O/(id+'.glb')),export_format='GLB',use_selection=True,export_extras=True,export_materials='EXPORT')
 # Write a standalone scene containing only this asset collection; no other asset dependencies.
 isolated=bpy.data.scenes.new(id);isolated.collection.children.link(c);isolated.unit_settings.system='METRIC';isolated['说明']='独立标识资产，正面朝-Y；单位m；文字已转网格。'
 bpy.data.libraries.write(str(O/(id+'.blend')),{isolated},fake_user=True,compress=True);bpy.data.scenes.remove(isolated)
 cam.data.ortho_scale=max(item['width']*1.18,item['height']*1200/650*1.2)
 S.render.filepath=str(O/(id+'_预览.png'));bpy.ops.render.render(write_still=True)
 manifest.append({k:v for k,v in item.items() if k!='collection'}|dict(meshes=len([o for o in c.objects if o.type=='MESH']),files=[id+'.blend',id+'.glb',id+'_预览.png']))
for index,a in enumerate(assets):
 a['collection'].hide_render=False
 for o in a['collection'].objects:o.location.x+=(index%2)*2.2;o.location.z-=(index//2)*1.05
cam.location=(1.1,-12,-2.1);cam.rotation_euler=(Vector((1.1,0,-2.1))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=6.0
S.render.resolution_x=1500;S.render.resolution_y=1800;S.render.filepath=str(O/'资产库总览.png');bpy.ops.render.render(write_still=True)
S['品牌规则']='所有完整版固定含hgdju.com；mirror为整组水平翻转；门牌正常方向；不随相机转向。';bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(O/'门牌与品牌资产库_P3.blend'))
(R/'检查/模型构建结果.json').write_text(json.dumps(dict(assets=manifest,glyphs=glyphchecks,format='Blender4.5.9 / GLB2.0',emission='独立字形及图标自发光；背光为单独可选关闭层'),ensure_ascii=False,indent=2),encoding='utf8')
print('P3_ASSETS_COMPLETE',len(manifest))
