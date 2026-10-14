"""Create a non-destructive v4.4 camera / display revision from accepted geometry."""
import json, math
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text(encoding='utf8'))
def write(p,v):
    q=R/p;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8')
D=read('模型/空间主数据_v4.json')
if (R/'模型/空间主数据_v4.4.json').exists():
    raise SystemExit('v4.4 already exists; this is a one-time migration. Edit current data explicitly; do not reset current production status.')
D['version']='v4.4'
D['revision_scope']='完整墙高显示、实际高位摄影机、空间复核；未凭无尺度参考擅改已确认房间边界与门序。'
D['display']={'cut_walls_default':False,'cut_height_m':1.15,'actual_camera_cutaway':False}
pos=[1.98,12.78,5.55];yaw=math.radians(3);pitch=math.radians(15)
target=[pos[0]+8*math.sin(yaw),pos[1]-8*math.cos(yaw),pos[2]-8*math.tan(pitch)]
D['cameras'].append(dict(id='H203',name='后露台方向看三间卧室·真实高位日景',pos=pos,target=target,lens=20,mode='all',ref='别墅二楼走廊.png',camera_height_above_floor=2.25,downward_pitch_degrees=15,sensor_width_mm=36,aspect=16/9,cutaway=False))
for c in D['cameras']:
    if c['id'] in ['AX1','AX2']:c['name']=c['name'].replace('俯视剖切','俯视·完整墙高')
cfg=read('模型/空间制作配置_v4.1.json')
D['door_plaques']=cfg['door_plaques'];D['production_cameras']=cfg['production_cameras']
D['brands']=cfg['brands']
br=next(b for b in D['brands'] if b['id']=='BR_HALL');br.update(box=[.34,7.22,1.44,7.24],width=1.1,center_height=.70,carrier='二楼护栏B端端墙，朝后露台；唯一实体标牌')
ob=next(o for o in D['objects'] if o['id']=='BR_HALL');ob['box']=[.34,7.22,3.82,1.44,7.24,4.18];ob['label']='黄瓜短剧唯一标牌：护栏B端端墙'
write('模型/空间主数据_v4.4.json',D)
hist=R/'制作记录/历史/制作清单_v4.3.json'
manifest=read('制作记录/制作清单.json')
if not hist.exists():write('制作记录/历史/制作清单_v4.3.json',manifest)
for row in manifest:
    row['status']='awaiting_model_camera_and_reference_edit'
    row['model_version']='v4.4';row['method']='Blender camera base + imagegen reference edit + geometry review'
    row['prompt']='待本机位模型底图检查后单独编写。保留门窗、家具位置和原图房间身份；白天柔和散射光，夜晚明亮暖白光。每空间仅一个固定、可读的无域名黄瓜短剧实体标牌。正式图不剖墙，不以前景门楣房梁取景。旧提示词仅供历史追溯，不执行。'
    for k in ['generated_path','raw_path','active_file_exists','attempt_id']:row.pop(k,None)
    if row['id']=='H203':
        row['output']='楼梯与走廊/二楼走廊_后露台方向看三间卧室（高位日景）.png'
        row['view']='后露台方向真实高位';row['camera']='H203'
        row['door_order_near_to_far']=['舒亚の窝','子豪の窝','薇亚的窝']
write('制作记录/制作清单.json',manifest)
old=read('制作记录/流程变更.json')
if not (R/'制作记录/历史/流程变更_v4.3.json').exists():write('制作记录/历史/流程变更_v4.3.json',old)
write('制作记录/流程变更.json',dict(date='2026-10-14',active_method='模型确定摄影机和结构，imagegen结合原图编辑材质，逐张复核结构与文字',model='v4.4',formal_scene_ready=0,formal_scene_target=95,auxiliary_target=2,pilot_renders=32,prior_renders_role='结构参考，不能当作合格正式场景',user_authorization='开始实施，末尾那句是旧计划遗留文字'))
# Avoid false precision: derived geometry metrics are not measurements of the source images.
audit=[]
for r in D['rooms']:
    x,y,xx,yy=r['box'];fs=[f for f in D['furniture'] if f['level']==r['level'] and x<=sum(f['box'][::2])/2<=xx and y<=sum(f['box'][1::2])/2<=yy]
    audit.append(dict(id=r['id'],room=r['name'],boundary_size_m=[round(xx-x,3),round(yy-y,3)],boundary_area_m2=round((xx-x)*(yy-y),3),furniture_ids=[f['id'] for f in fs],net_area_claimed=False))
write('校验/空间尺寸复核_v4.4.json',dict(scope='影视参考尺寸；边界面积不是净使用面积。单张透视图不足以唯一反推尺寸。',rooms=audit,door_centers_y=[3.025,5.825,10.725],door_center_gaps_m=[2.8,4.9],corridor_clear_width_m=1.48,wall_height_m=3.08,guard_including_cap_m=1.16,geometry_changes=[],deferred=['三间卧室同为7.4×3.8米，原图家具方向各异，尚不足以唯一反推尺寸；本轮不伪造尺寸校准完成。','服务过厅16.2㎡及布草区10.23㎡为边界面积，使用效率需进一步房内反向机位验证。','外立面窗口与原外景不能逐窗一一对应，延续既有冲突记录。']))
print('v4.4 data / current manifest saved; accepted geometry preserved')
