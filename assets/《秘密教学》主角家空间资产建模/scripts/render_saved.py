"""Photograph the saved physical model. No geometry generation or AI service."""
import argparse,sys,json,hashlib
from pathlib import Path
import bpy
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'scripts'))
from lighting import set_time
p=argparse.ArgumentParser()
p.add_argument('--camera',default='DIRECT_客厅_后视图',help='Actual Blender camera name, or all')
p.add_argument('--time',choices=['day','night','both'],default='day')
p.add_argument('--samples',type=int,default=96)
p.add_argument('--width',type=int,default=1920)
p.add_argument('--list',action='store_true')
p.add_argument('--output',default=str(R/'预览/保存模型拍摄'))
a=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
model=R/'模型/秘密教学_主角家_直接渲染_v4.3.blend'
bpy.ops.wm.open_mainfile(filepath=str(model));s=bpy.context.scene
cams={o.name:o for o in bpy.data.objects if o.type=='CAMERA' and (o.name.startswith('DIRECT_') or o.name in ['H2_PAN','H2_ELEV'])}
if a.list:
    print(json.dumps(list(cams),ensure_ascii=False));raise SystemExit(0)
if a.camera!='all' and a.camera not in cams:raise ValueError('Unknown camera. Run --list.')
chosen=list(cams.values()) if a.camera=='all' else [cams[a.camera]]
try:
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='OPTIX';prefs.get_devices()
    for d in prefs.devices:d.use=d.type!='CPU'
    if any(d.use for d in prefs.devices):s.cycles.device='GPU'
except Exception:pass
s.render.engine='CYCLES';s.cycles.samples=a.samples;s.cycles.use_denoising=True;s.render.image_settings.file_format='PNG';s.render.resolution_percentage=100
states=['day','night'] if a.time=='both' else [a.time];out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
basehide={o.name:o.hide_render for o in bpy.data.objects};records=[]
for cam in chosen:
    for o in bpy.data.objects:o.hide_render=basehide[o.name]
    elev=cam.name=='H2_ELEV'
    if elev:
        for o in bpy.data.objects:
            if o.type not in ['LIGHT','CAMERA']:o.hide_render=not(o.name.startswith(('F2_BEDROOM_W','PLAQUE_','TEXT_','HANDLE_')) or o.name in ['D203_leaf','D204_leaf','D205_leaf','BR_HALL_ART'])
    s.camera=cam;s.render.resolution_x=a.width;s.render.resolution_y=round(a.width/(3 if elev else 16/9))
    for state in states:
        set_time(s,bpy.data.objects,state=='night')
        label={'H2_PAN':'二楼走廊_三门同框平视全景','H2_ELEV':'二楼走廊_三门正面关系图'}.get(cam.name,cam.name.removeprefix('DIRECT_'))
        target=out/(label+('（日景）' if state=='day' else '（夜间）')+'.png');s.render.filepath=str(target);bpy.ops.render.render(write_still=True)
        records.append({'file':target.name,'camera':cam.name,'time':state,'resolution':[s.render.resolution_x,s.render.resolution_y],'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'method':'saved Blender model direct render','cutaway_auxiliary':elev})
(out/'拍摄记录.json').write_text(json.dumps({'model_sha256':hashlib.sha256(model.read_bytes()).hexdigest(),'model_file':model.name,'renders':records},ensure_ascii=False,indent=2),encoding='utf8')
print('SAVED_MODEL_RENDER_DONE',len(records))
