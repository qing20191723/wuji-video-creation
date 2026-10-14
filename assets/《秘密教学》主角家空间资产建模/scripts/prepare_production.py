"""Derive production records from the accepted spatial baseline; no geometry redesign."""
from pathlib import Path
import json, hashlib, csv
R=Path(__file__).resolve().parents[1]
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
D=json.loads((R/'模型/空间主数据_v4.json').read_text(encoding='utf8'))
save(R/'制作记录/模型认可基线.json',{'date':'2026-10-14','user_decision':'大致没有问题，小瑕疵不影响视频生成；允许恢复场景图片制作','geometry_sha256':hashlib.sha256(json.dumps(D['objects'],sort_keys=True).encode()).hexdigest(),'scope':'保留现有结构；新增机位、灯光与标牌，不移动门窗或家具'})
D['production']={'version':'v4.1','geometry_baseline':'v4_20261014_user_accepted','day':'自然散射光，无强烈直射、硬边光斑','night':'明亮柔和暖白主光，少量淡黄色；蓝紫仅二姐局部点缀','framing':'正式图不得以门框门楣房梁为前景；俯拍使用房间内部高位视角，必要时仅在该视图剖去遮挡构件，不改实体模型。'}
D['door_plaques']=[{'door':'D203','room':'大姐','text':'薇亚的窝','center':[3.325,3.025,4.95]}, {'door':'D204','room':'男主','text':'子豪の窝','center':[3.325,5.825,4.95]}, {'door':'D205','room':'二姐','text':'舒亚の窝','center':[3.325,10.725,4.95]}]
for p in D['door_plaques']:p.update(width=.46,height=.23,style='浅木色圆角小贴牌，深色可爱手写字，不加书名号')
D['production_cameras']=[
 {'id':'H2_PAN','name':'二楼走廊_三门同框平视全景','pos':[.5,.85,4.92],'target':[3.4,5.95,4.92],'lens':19,'resolution':[2400,1350],'projection':'PERSP','use':'正式场景；A端真实平台内机位，护栏遮挡下半部符合物理关系'},
 {'id':'H2_ELEV','name':'二楼走廊_三门正面关系图','pos':[-8,6.875,4.95],'target':[3.4,6.875,4.95],'lens':35,'ortho_scale':10.8,'resolution':[3000,1000],'projection':'ORTHO','use':'辅助立面关系图；剖去西侧墙、护栏及其遮挡，只显示卧室门墙，不是实际机内单次透视'},
 {'id':'LIV_MAIN','name':'客厅_前视图','pos':[9.7,1.1,1.62],'target':[5.55,5.45,1.62],'lens':22,'resolution':[2400,1350],'projection':'PERSP','use':'模型约束主视图'},
 {'id':'YOU_MAIN','name':'二姐房间_正视图','pos':[8.3,9.65,4.92],'target':[3.7,9.65,4.92],'lens':22,'resolution':[2400,1350],'projection':'PERSP','use':'床头书桌房门同墙；灰蓝床品星形地毯'}]
save(R/'模型/空间制作配置_v4.1.json',D)
save(R/'制作记录/灯光与机位.json',{'lighting':D['production'],'cameras':D['production_cameras'],'plaques':D['door_plaques']})
items=json.loads((R/'制作记录/原95张制作清单.json').read_text(encoding='utf8'))
for item in items:
    item['previous_status']=item.get('status','unknown');item['status']='awaiting_model_and_lighting_review'
    item['model_version']='v4.1';item.pop('sha256',None)
    if item['id'] in ['H201','H205']:
        item['view']='三门同框平视全景';item['camera_id']='H2_PAN'
        item['output']='楼梯与走廊/二楼走廊_三门同框平视全景（'+item['time']+'）.png'
    if item['id'] in ['LIV01','LIV05']:item['camera_id']='LIV_MAIN'
    if item['id'] in ['YOU01','YOU05']:item['camera_id']='YOU_MAIN'
for t,suf in [('日景','D'),('夜间','N')]:items.append({'id':'H2_REL_'+suf,'room':'二楼走廊','view':'三门正面关系图','time':t,'output':'辅助关系图/二楼走廊_三门正面关系图（'+t+'）.png','camera_id':'H2_ELEV','model_version':'v4.1','status':'pending','purpose':'辅助关系图，不属于95张正式场景'})
save(R/'制作记录/制作清单.json',items)
assert len(items)==97
print('Prepared 97 records; accepted geometry remains unchanged.')
