"""Check saved structure, packed textures and camera, export portable neutral GLB."""
import bpy,json
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_主角家_v4.4.blend'))
D=json.loads((R/'模型/空间主数据_v4.4.json').read_text(encoding='utf8'));issues=[];checked=0
for d in D['objects']:
    if not ('walls' in d['group'] or 'slabs' in d['group'] or d['group'] in ['Stairs','F2_guard']):continue
    checked+=1;o=bpy.data.objects.get(d['id'])
    if not o:issues.append([d['id'],'missing']);continue
    if o.hide_render:issues.append([d['id'],'hidden'])
    if d['kind']=='box':
        pts=[o.matrix_world@Vector(v) for v in o.bound_box];actual=[min(p[k] for p in pts) for k in range(3)]+[max(p[k] for p in pts) for k in range(3)]
        if max(abs(x-y) for x,y in zip(actual,d['box']))>.0002:issues.append([d['id'],'bounds mismatch'])
texts={o.name:o.get('exact_text') for o in bpy.data.objects if o.name.startswith('TEXT_')}
assert texts=={'TEXT_D203':'薇亚的窝','TEXT_D204':'子豪の窝','TEXT_D205':'舒亚の窝'}
assert not issues,issues
images=[{'name':i.name,'packed':bool(i.packed_file)} for i in bpy.data.images if i.source=='FILE' and i.users];assert all(i['packed'] for i in images)
c=next(c for c in D['cameras'] if c['id']=='H203');cam=bpy.data.objects['H203'];assert (cam.location-Vector(c['pos'])).length<.00001
report={'checked_structural_objects':checked,'issues':issues,'exact_model_door_text':texts,'image_dependencies':images,'camera':c,'proof_limit':'几何一致不等于原房间比例已校准；门牌模型精确不等于生成图中小字逐字可辨。'}
(R/'校验/模型回读_v4.4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
# Neutral structural GLB: omit detailed plants/textures, retain actual closed doors and plaques.
bpy.ops.object.select_all(action='DESELECT')
ids={d['id'] for d in D['objects']}
for o in bpy.data.objects:
    if o.name in ids or o.name.startswith(('TEXT_','PLAQUE_','HANDLE_')) or o.name=='H203':o.hide_set(False);o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(R/'模型/秘密教学_空间结构_v4.4.glb'),export_format='GLB',use_selection=True,export_cameras=True,export_extras=True)
print('V44_CHECK_PASS',checked)
