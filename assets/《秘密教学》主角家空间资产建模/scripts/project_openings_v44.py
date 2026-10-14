"""Add actual window/opening corner projections; no scene or image modification."""
import bpy,json
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from pathlib import Path
R=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(R/'模型/秘密教学_主角家_v4.4.blend'))
s=bpy.context.scene;cam=bpy.data.objects['H203'];D=json.loads((R/'模型/空间主数据_v4.4.json').read_text(encoding='utf8'))
p=R/'校验/H203_文字与门窗投影.json';P=json.loads(p.read_text(encoding='utf8'))
for o in D['openings']:
    if o['id'] not in ['W201','W202','W203','W204','D201']:continue
    low=o.get('sill',0);high=o.get('head',o.get('h',2.6))
    corners=[[*o['a'],o['z']+low],[*o['b'],o['z']+low],[*o['b'],o['z']+high],[*o['a'],o['z']+high]]
    ps=[world_to_camera_view(s,cam,Vector(v)) for v in corners]
    if not all(v.z>0 for v in ps):continue
    box=[min(v.x for v in ps)*1920,(1-max(v.y for v in ps))*1080,max(v.x for v in ps)*1920,(1-min(v.y for v in ps))*1080]
    if box[0]>1920 or box[2]<0 or box[1]>1080 or box[3]<0:continue
    P['OPENING_'+o['id']]={'pixel_box':[round(v,1) for v in box],'pixel_corners':[[round(v.x*1920,1),round((1-v.y)*1080,1)] for v in ps],'exact_text':o['id'],'in_front':True,'visibility':'projected opening; may be partly occluded by guard'}
p.write_text(json.dumps(P,ensure_ascii=False,indent=2),encoding='utf8');print('OPENING_PROJECTIONS_SAVED')
