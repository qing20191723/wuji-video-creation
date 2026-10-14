import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_主角家_直接渲染_v4.3.blend'))
D=json.loads((R/'模型/空间主数据_v4.json').read_text(encoding='utf8'));issues=[];checked=0
for d in D['objects']:
 if not ('walls' in d['group'] or 'slabs' in d['group'] or d['group']=='Stairs' or d['group']=='F2_guard'):continue
 o=bpy.data.objects.get(d['id']);checked+=1
 if o is None:issues.append([d['id'],'missing']);continue
 if d['kind']!='box':continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];actual=[min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)]
 if max(abs(x-y) for x,y in zip(actual,d['box']))>.0002:issues.append([d['id'],'changed bounds'])
texts={o.name:o.get('exact_text') for o in bpy.data.objects if o.name.startswith('TEXT_')}
assert texts=={'TEXT_D203':'薇亚的窝','TEXT_D204':'子豪の窝','TEXT_D205':'舒亚の窝'},texts
assert not issues,issues
images=[{'name':i.name,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE' and i.users]
assert all(i['packed'] for i in images),images
report={'checked_structural_objects':checked,'structural_changes':issues,'door_text':texts,'image_dependencies':images,'direct_camera_count':sum(o.name.startswith('DIRECT_') for o in bpy.data.objects),'all_model_cameras':sum(o.type=='CAMERA' for o in bpy.data.objects),'note':'验证空间结构与精确标牌；不等于全部房间精模与图像质量验收通过。'}
(R/'校验/直接渲染模型回读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=True))
