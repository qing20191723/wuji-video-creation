"""Expand shot coverage from fixed P4-M2 geometry; never mutate the model."""
from pathlib import Path
import json, math

ROOT=Path(__file__).resolve().parent
MODEL=ROOT.parent/'全屋模型_P4-M2_20261022/数据/模型空间数据.json'
d=json.loads(MODEL.read_text('utf8')); p=json.loads((ROOT/'presets.json').read_text('utf8'))
rooms={r['id']:r for r in d['plan']['rooms']}
original=[s for s in p['shots'] if not s.get('coverage_expansion')]
for s in original:
    s['category']='classic'
    if s['id'] in ('F03','F04'):s['room']='MB'
    if s['id'] in ('K01','K02'):s['room']='K'
p['rooms']=[dict(id=i,name=n) for i,n in [('B1','薇亚卧室'),('B2','子豪卧室'),('B3','舒亚卧室'),('MB','一楼主卧'),('L','客厅'),('D','餐厅'),('K','厨房'),('H2','楼道与直梯'),('BW','公共浴室'),('F1','一楼其他空间'),('COURT','庭院与屋顶'),('EXT','别墅外观')]]
p['categories']=[dict(id=i,name=n) for i,n in [('classic','原有机位'),('corners','四角斜看'),('axes','对向全景'),('detail','家具与品牌'),('height','高低机位')]]
solid=[o for o in d['objects'] if o['category'] not in ('brand','landscape','glass','nameplate')]
def blocked(pos,pad=.13):
    return any(all(o['bbox'][k]-pad<pos[k]<o['bbox'][k+3]+pad for k in range(3)) for o in solid)
def free(pos,box):
    # Keep intended corner/direction; small in-room translation only.
    choices=[]
    for dx in [0,-.2,.2,-.4,.4,-.6,.6,-.8,.8,-1,1]:
        for dy in [0,-.2,.2,-.4,.4,-.6,.6,-.8,.8,-1,1]:
            v=[pos[0]+dx,pos[1]+dy,pos[2]]
            if not(box[0]+.28<=v[0]<=box[2]-.28 and box[1]+.28<=v[1]<=box[3]-.28):continue
            if not blocked(v):choices.append((dx*dx+dy*dy,v))
    if not choices:raise ValueError(('No free camera',pos))
    return [round(v,4) for v in min(choices,key=lambda x:x[0])[1]]
new=[]
prefix={'B1':'A','B2':'Z','B3':'S','MB':'M','L':'L','D':'D'}
types={'corners':'四角斜看','axes':'对向全景','detail':'家具与品牌','height':'高低机位'}
def add(r,name,xy,target,category='detail',height=1.6,fov=68,source=None):
    floor=3.3 if rooms[r]['level']==2 else 0
    used={s['id'] for s in original+new};n=1
    while f'{prefix[r]}{n:02}' in used:n+=1
    pos=free([xy[0],xy[1],floor+height],rooms[r]['box'])
    item=dict(id=f'{prefix[r]}{n:02}',room=r,name=name,position=pos,target=[target[0],target[1],floor+target[2]],fov=fov,type=types[category],category=category,floor=floor,exterior=False,coverage_expansion=True)
    if source:item['target_source']=source
    if category=='height' and height>2.2:item['note']='高位虚拟机位，用于俯拍构图；保持原墙体与家具位置。'
    new.append(item)

# Positions and targets below follow the actual fixed furnishings, not a remodel.
details={
'B1':[
 ('电脑桌正向细看',(18.6,5.6),(18.6,7.35,1.0),'A04'),
 ('梳妆台正向细看',(18.9,7.0),(20.7,7.05,1.0),'A06')],
'B2':[
 ('床头侧近景',(10.2,4.2),(12.75,4.2,.9),'B01'),
 ('床尾方向反打',(12.5,4.2),(9.2,4.2,.95),None),
 ('绿色床长边侧面',(11.7,6.5),(11.9,4.2,.65),'B01'),
 ('电视矮柜正向',(10.5,4.4),(8.15,4.4,.7),'B02'),
 ('电脑桌正向细看',(10.7,7.6),(8.2,7.6,1),'B03'),
 ('电脑桌侧向',(9.6,6.1),(8.2,7.6,1),'B03'),
 ('窗边望远镜',(10.8,6.3),(10.9,8.1,1.1),'B09'),
 ('入口书架方向',(11.6,3.5),(12.5,2.0,1.1),'B13'),
 ('穿衣区与窗边衣柜',(10.9,6.6),(12.85,7.8,1.35),'B05')],
'B3':[
 ('床头正向细看',(6.9,5.7),(6.9,2.0,.8),'C01'),
 ('床侧看贴墙关系',(4.7,3.6),(7.1,2.9,.65),'C01'),
 ('床尾小书架正向',(6.9,6.5),(6.95,4.5,.7),'C02'),
 ('电脑桌正向细看',(3.6,4.7),(3.6,2.15,1),'C03'),
 ('电脑桌侧向',(5.5,3.6),(3.5,2.15,1),'C03'),
 ('窗下收藏柜',(3.4,5.6),(3.4,7.75,1.0),'C05'),
 ('衣物架与收藏柜正向',(3.1,5.3),(.35,5.3,1.2),'C06'),
 ('床侧回看房门',(5.5,3.8),(1.35,1.7,1.4),None),
 ('星形地毯与活动区',(5.8,6.5),(3.6,5.7,.1),'C08')],
'MB':[
 ('床头正向细看',(18.2,10.3),(14.45,10.3,.85),'M01'),
 ('床头侧回看床尾',(14.7,10.4),(18.2,10.0,1.1),None),
 ('床北侧朝梳妆区',(16.4,11.6),(17.8,7.5,1.1),'M05'),
 ('床南侧看床面',(15.5,8.3),(15.4,10.3,.7),'M01'),
 ('梳妆台正向',(18,10.5),(17.9,7.5,1.0),'M05'),
 ('梳妆台侧向',(16.8,9.3),(18.0,7.5,1.0),'M05'),
 ('衣柜正向',(15.9,10.9),(15.9,7.5,1.3),'M04'),
 ('窗侧床头柜近景',(15.8,11.1),(14.5,11.65,.65),'M02'),
 ('门侧床头柜近景',(16.1,8.5),(14.5,9.0,.65),'M03'),
 ('衣架与东侧通路',(18.2,9.6),(19.3,7.5,1.2),'M07')],
'L':[
 ('沙发正面与茶几关系',(3.7,6.5),(3.7,2.8,.85),'L01'),
 ('长沙发东侧斜拍',(7.0,3.7),(3.8,2.8,.85),'L01'),
 ('贵妃位侧面',(4.5,4.0),(2.15,3.8,.75),'L02'),
 ('茶几桌面俯看',(5.4,5.6),(4.0,4.65,.5),'L04'),
 ('电视墙主品牌正向',(5.65,5.5),(5.65,7.55,2.45),None),
 ('主墙右侧辅助品牌',(7.5,4.8),(8.3,7.55,1.8),None),
 ('西窗侧回看沙发',(1.0,5.8),(4.8,3.0,1.0),'L01'),
 ('参考书架正向',(7.0,6.0),(9.15,7.0,1.4),'L06')],
'D':[
 ('餐桌南侧朝北窗',(7.35,8.15),(7.35,10.9,1.1),'D01'),
 ('餐桌北侧朝客厅',(7.35,11.4),(7.35,8.5,1.1),'D01'),
 ('餐桌东端朝厨房',(9.2,9.8),(6.6,9.8,.9),'D01'),
 ('餐桌西端朝品牌墙',(5.2,9.8),(9.65,9.9,1.5),'D01'),
 ('南侧餐椅坐姿反打',(6.7,8.8),(7.6,10.7,1.15),None),
 ('北侧餐椅坐姿反打',(7.8,10.8),(6.7,8.9,1.15),None),
 ('镜像主品牌正向',(7.4,9.92),(9.762,9.92,1.9),None),
 ('餐厅壁架侧拍',(7.7,11.2),(9.55,11.55,1.1),'D02'),
 ('品牌摆件北侧斜拍',(6.9,10.9),(7.5,9.8,.91),None)]
}
for r in ['B1','B2','B3','MB','L','D']:
    x0,y0,x1,y1=rooms[r]['box'];cx=(x0+x1)/2;cy=(y0+y1)/2
    corners=[('西南',(x0+.65,y0+.65)),('东南',(x1-.65,y0+.65)),('西北',(x0+.65,y1-.65)),('东北',(x1-.65,y1-.65))]
    for name,xy in corners:add(r,name+'角看全景',xy,(cx,cy,1.15),'corners',fov=74)
    for name,xy,target in [('南侧朝北墙',(cx,y0+.65),(cx,y1-.25,1.25)),('北侧朝南墙',(cx,y1-.65),(cx,y0+.25,1.25)),('西侧朝东墙',(x0+.65,cy),(x1-.25,cy,1.25)),('东侧朝西墙',(x1-.65,cy),(x0+.25,cy,1.25))]:add(r,name,xy,target,'axes',fov=72)
    for name,xy,height in [('西南侧低机位',corners[0][1],.78),('东南侧坐姿视线',corners[1][1],1.15),('西北侧高位俯看',corners[2][1],2.45),('东北侧高位俯看',corners[3][1],2.45),('中央高位俯拍',(cx+.2,cy-.45),2.65)]:add(r,name,xy,(cx,cy,.65),'height',height=height,fov=76)
    needed=25-len([s for s in original+new if s['room']==r])
    for name,xy,target,source in details[r][:needed]:
        h=1.15 if '坐姿' in name else 1.7 if '俯看' in name else 1.6
        add(r,name,xy,target,height=h,fov=58 if '近景' in name or '品牌' in name else 66,source=source)
    assert len([s for s in original+new if s['room']==r])==25,r
p['shots']=original+new
p['coverage_revision']='C2-20261025'
p['coverage_note']='四间卧室、客厅与餐厅各25机位；分类覆盖，不声称穷尽连续空间所有视角。'
(ROOT/'presets.json').write_text(json.dumps(p,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(total=len(p['shots']),added=len(new),counts={r:len([s for s in p['shots'] if s['room']==r]) for r in ['B1','B2','B3','MB','L','D']}),ensure_ascii=False))
