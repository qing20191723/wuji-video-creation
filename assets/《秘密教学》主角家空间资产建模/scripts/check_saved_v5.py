"""Open exported Blend, verify its embedded geometry and set a useful review view."""
import bpy,json,os
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'));bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_V3校准模块_v5.blend'))
saved=json.loads(bpy.data.texts['空间校准主数据_v5.json'].as_string());assert saved==D,'embedded master data mismatch'
missing=[d['id'] for d in D['objects'] if d['id'] not in bpy.data.objects];assert not missing,missing
s=bpy.context.scene;s.camera=bpy.data.objects['HOME_floor2']
for d in D['objects']:
 o=bpy.data.objects[d['id']];visible=d['module']=='HOME' and (d.get('level')==2 or d['role']=='stair') and d['role'] not in ('ceiling','glass');o.hide_set(not visible);o.hide_render=not visible
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA'
if os.environ.get('V5_VERIFY_ONLY')!='1':
 bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(R/'模型/秘密教学_V3校准模块_v5.blend'))
report={'embedded_data_equal':True,'expected_objects':len(D['objects']),'missing':missing,'default_camera':s.camera.name,'note':'Object presence and embedded data check; not full mesh topology or material identity validation.'}
(R/'校验/v5_保存模型回读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report))
