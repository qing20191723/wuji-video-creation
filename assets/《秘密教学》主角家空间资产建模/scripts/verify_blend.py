import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'模型/空间主数据_v4.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_全屋空间_v4.blend'))
problems=[]
for d in D['objects']:
 o=bpy.data.objects.get(d['id'])
 if not o:problems.append([d['id'],'missing']);continue
 if d['kind']=='box':
  corners=[o.matrix_world@__import__('mathutils').Vector(v) for v in o.bound_box];actual=[min(p[k] for p in corners) for k in range(3)]+[max(p[k] for p in corners) for k in range(3)]
  if max(abs(a-b) for a,b in zip(actual,d['box']))>.0001:problems.append([d['id'],'bounds mismatch',actual,d['box']])
  if o.hide_render:problems.append([d['id'],'saved hidden'])
result={'model_geometry_count':len(D['objects']),'matched_objects':len(D['objects'])-len(problems),'camera_count':len([o for o in bpy.data.objects if o.type=='CAMERA']),'problems':problems,'source_embedded':'空间主数据_v4.json' in bpy.data.texts}
(R/'校验/Blender回读核对.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');print('BLEND_VERIFY',json.dumps(result,ensure_ascii=False))
