import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]/'完整平面与品牌_P3_20261022';M=R/'独立模型';results=[]
for p in sorted(M.glob('*.glb')):
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=str(p))
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
 embedded=[i for i in bpy.data.images if i.source=='FILE']
 with bpy.data.libraries.load(str(p.with_suffix('.blend')),link=False) as (src,dst):
  scene_names=list(src.scenes);dst.scenes=src.scenes
 loaded=[s for s in dst.scenes if s]
 results.append(dict(asset=p.stem,glb_meshes=len(meshes),glb_vertices=sum(len(o.data.vertices) for o in meshes),blend_scenes=scene_names,blend_meshes=sum(len([o for o in s.objects if o.type=='MESH']) for s in loaded),images=len(embedded),passed=bool(meshes) and bool(loaded)))
(R/'检查/模型回读检查.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf8')
assert len(results)==10 and all(x['passed'] for x in results)
print('MODEL_READBACK_PASSED',len(results))
