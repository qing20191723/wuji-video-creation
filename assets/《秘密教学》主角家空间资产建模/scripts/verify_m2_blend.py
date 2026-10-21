import bpy,json,struct
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'白模当前'
D=json.loads((O/'模型/空间数据.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(O/'模型/秘密教学_P2.4-M3.blend'))
errors=[]
for d in D['objects']:
 ob=bpy.data.objects.get(d['id'])
 if ob is None:errors.append([d['id'],'missing']);continue
 pts=[ob.matrix_world@Vector(p) for p in ob.bound_box];b=[min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)]
 if max(abs(x-y) for x,y in zip(b,d['box']))>1e-4:errors.append([d['id'],'bounds'])
 if ob.hide_render and d['category']!='glass':errors.append([d['id'],'unexpected hidden'])
assert bpy.context.scene['model_revision']=='P2.4-M3'
raw=(O/'模型/秘密教学_P2.4-M3.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];gltf=json.loads(raw[20:20+n].decode('utf8'))
glass=[m for m in gltf['materials'] if m.get('name')=='glass']
if not glass or glass[0].get('alphaMode')!='BLEND':errors.append(['GLB','opaque glass'])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(O/'模型/秘密教学_P2.4-M3.glb'))
mesh_count=sum(ob.type=='MESH' for ob in bpy.data.objects)
if mesh_count!=len(D['objects']):errors.append(['GLB mesh count',mesh_count,len(D['objects'])])
result=dict(revision=D['revision'],passed=not errors,blend_checked_objects=len(D['objects']),glb_imported_meshes=mesh_count,glb_glass_alpha_mode=glass[0].get('alphaMode') if glass else None,errors=errors)
(O/'检查记录/M3模型回读检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print('M3_READBACK',json.dumps(result,ensure_ascii=False))
if errors:raise SystemExit(1)
