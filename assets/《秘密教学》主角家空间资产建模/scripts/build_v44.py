"""Save v4.4 from the packed v4.3 model; photograph real-height geometry."""
import bpy,json,sys,math,argparse
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from lighting import set_time
p=argparse.ArgumentParser();p.add_argument('--preview',action='store_true');a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
D=json.loads((R/'模型/空间主数据_v4.4.json').read_text(encoding='utf8'))
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_主角家_直接渲染_v4.3.blend'));s=bpy.context.scene
# No object deletion, camera-only revision; restore full structure visibility.
for d in D['objects']:
    o=bpy.data.objects.get(d['id'])
    if o and ('walls' in d['group'] or 'slabs' in d['group'] or d['group'] in ['Roof','F2_guard','Stairs']):o.hide_render=False;o.hide_set(False)
c=next(c for c in D['cameras'] if c['id']=='H203')
# Relocate the ONE corridor logo to the physically visible guard end wall.
carrier=bpy.data.objects['BR_HALL'];carrier.location=(.89,7.23,4.0);carrier.dimensions=(1.1,.03,.36)
art=bpy.data.objects['BR_HALL_ART'];mat=art.data.materials[0]
mesh=bpy.data.meshes.new('BR_HALL_v44_face');mesh.from_pydata([(.34,7.241,3.8167),(1.44,7.241,3.8167),(1.44,7.241,4.1833),(.34,7.241,4.1833)],[],[(0,1,2,3)]);mesh.update();uv=mesh.uv_layers.new()
# Viewed from the north, east is image-left: reverse U on this north-facing wall.
for i,co in enumerate([(1,0),(0,0),(0,1),(1,1)]):uv.data[i].uv=co
art.data=mesh;mesh.materials.append(mat)
bpy.ops.object.camera_add(location=c['pos']);cam=bpy.context.object;cam.name='H203';cam.rotation_euler=(Vector(c['target'])-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=c['lens'];cam.data.sensor_width=36;cam.data.sensor_fit='HORIZONTAL';cam.data.clip_start=.03;cam.data.clip_end=250;s.camera=cam
s['revision']='v4.4: real-height H203; original dimensions pending reference calibration';s['cutaway']=False
text=bpy.data.texts.new('空间主数据_v4.4.json');text.write(json.dumps(D,ensure_ascii=False,indent=2))
set_time(s,bpy.data.objects,False)
s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.use_denoising=True
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for dev in prefs.devices:dev.use=dev.type!='CPU'
    if any(dev.use for dev in prefs.devices):s.cycles.device='GPU'
except Exception:pass
bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(R/'模型/秘密教学_主角家_v4.4.blend'))
out=R/'预览/v4.4';out.mkdir(parents=True,exist_ok=True)
s.render.filepath=str(out/'H203_模型底图.png');bpy.ops.render.render(write_still=True)
# Export projection metadata directly from the same camera for diagnostics.
from bpy_extras.object_utils import world_to_camera_view
projection={}
for id in ['D203_leaf','D204_leaf','D205_leaf','PLAQUE_D203','PLAQUE_D204','PLAQUE_D205','TEXT_D203','TEXT_D204','TEXT_D205','BR_HALL_ART']:
    o=bpy.data.objects.get(id)
    if not o:continue
    pts=[world_to_camera_view(s,cam,o.matrix_world@Vector(v)) for v in o.bound_box]
    projection[id]={'pixel_box':[round(min(v.x for v in pts)*1920,1),round((1-max(v.y for v in pts))*1080,1),round(max(v.x for v in pts)*1920,1),round((1-min(v.y for v in pts))*1080,1)],'exact_text':o.get('exact_text',''),'in_front':all(v.z>0 for v in pts)}
(R/'校验/H203_文字与门窗投影.json').write_text(json.dumps(projection,ensure_ascii=False,indent=2),encoding='utf8')
print('V44_SAVED_RENDERED')
