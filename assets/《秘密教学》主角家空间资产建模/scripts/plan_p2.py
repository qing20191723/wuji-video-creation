"""Horizontal 2D proposal. Coordinates in metres, north up; no model writes."""
from pathlib import Path
import math, json, hashlib, html
import plan_svg as g
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'平面确认'
ROOMS=[];F=[];WALLS=[];OPEN=[];CLEAR=[];ROUTES=[]
def room(id,name,l,b,c='#eee9df',poly=None):
    area=(b[2]-b[0])*(b[3]-b[1]) if not poly else abs(sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(poly,poly[1:]+poly[:1])))/2
    ROOMS.append(dict(id=id,name=name,level=l,box=b,color=c,polygon=poly,net_area=round(area,2)))
def f(id,name,l,b,k='cabinet',c='#d9c8b1',r=None,head=None):F.append(dict(id=id,name=name,level=l,box=b,kind=k,color=c,room=r,head=head))
def wall(id,l,a,b,ops=(),th=.2):
    WALLS.append(dict(id=id,level=l,a=a,b=b,thickness=th))
    for u,v,t,n,opts in ops:OPEN.append(dict(id=n,wall=id,level=l,start=u,end=v,type=t,**opts))
def win(a,b,n,s=.6,h=2.8):return(a,b,'window',n,dict(sill=s,head=h))
def door(a,b,n,s=1):return(a,b,'door',n,dict(side=s,head=2.2))
def glass(a,b,n):return(a,b,'glass',n,dict(sill=0,head=2.8))
def clear(id,l,a,b,label):CLEAR.append(dict(id=id,level=l,a=a,b=b,value=round(math.dist(a,b),2),label=label))
def route(id,l,p):ROUTES.append(dict(id=id,level=l,points=p))

room('L','开放客厅',1,[.2,.2,9.8,5.8]);room('K','开放厨房',1,[.2,6,4.6,10.2],'#deebe7');room('D','开放餐厅',1,[4.6,6,9.8,10.2],'#f0e9d8')
room('MH','主卧直通廊',1,[10,5.5,13.8,7.1],'#e0efeb');room('MB','主卧',1,[14,5.4,19.8,10.2],'#ecdfdf');room('MW','主卫',1,[20,5.4,21.8,10.2],'#dcebef')
room('LA','洗衣房',1,[10,7.3,13.8,10.2],'#e0e9e6');room('E','玄关 / 公共通路',1,[10,.2,11.2,5.3],'#e4efeb');room('R','阅读角及公共连接',1,[11.2,2.6,18,5.2])
room('WC','客卫',1,[18.2,.2,21.8,2.4],'#dcebef');room('ST','家用储物',1,[18.2,2.6,21.8,5.2],'#e6e5dc')
room('B3','舒亚 / 二姐',2,[.2,4.4,6.4,10.2],'#e5e7f0')
room('B2','子豪',2,[6.6,4.4,13,10.2],'#e5ecdf')
room('B1','薇亚 / 大姐',2,[13.2,4.4,18.6,9.4],'#f2e2e5');room('H2','三卧室直走廊',2,[.2,2.6,19.8,4.2],'#e1eeea')
room('WB','公用浴室',2,[.2,.2,3.4,2.4],'#dcebef');room('LC','布草储物',2,[3.6,.2,4.8,2.4]);room('A','A 上平台',2,[16.72,1.1,18.32,2.6],'#e1eeea')
room('FB','临街连续阳台',2,[.2,-1.4,21.8,2.4],poly=[(.2,-1.4),(21.8,-1.4),(21.8,0),(9.8,0),(9.8,2.4),(5,2.4),(5,0),(.2,0)])
room('AB','东侧木平台 / 大姐阳台',2,[18.8,0,21.8,10.2],poly=[(20,0),(21.8,0),(21.8,10.2),(18.8,10.2),(18.8,4.4),(20,4.4)])

wall('1-S',1,[.1,.1],[21.9,.1],[win(.6,4.1,'W101',.25),win(5.1,9.4,'W102',.25),door(10.05,11.05,'D101'),win(12.1,16.5,'W103',.4),win(19,21,'W104',1.5)])
wall('1-N',1,[.1,10.3],[21.9,10.3],[win(1.5,3.5,'W105',1.15,1.75),win(5.6,9,'W106',.5),win(10.6,12.9,'W107',1.1),win(14.7,19.3,'W108',.3),win(20.3,21.5,'W109',1.5,2.2)])
wall('1-W',1,[.1,.1],[.1,10.3],[win(1.2,4.8,'W110',.3)]);wall('1-E',1,[21.9,.1],[21.9,10.3],[win(6.1,8,'W111',1.5)])
wall('1-MW',1,[13.9,5.3],[13.9,10.3],[door(5.8,6.8,'D106')]);wall('1-MS',1,[13.9,5.3],[21.9,5.3]);wall('1-BATH',1,[19.9,5.3],[19.9,10.3],[door(8.3,9.2,'D107')])
wall('1-HN',1,[9.9,7.2],[13.9,7.2],[door(10.5,11.4,'D104')]);wall('1-HS',1,[10,5.4],[13.9,5.4]);wall('1-LW',1,[9.9,7.2],[9.9,10.3])
wall('1-WCE',1,[18.1,.1],[18.1,5.3],[door(.5,1.4,'D105'),door(3.4,4.3,'D108')]);wall('1-WCN',1,[18.1,2.5],[21.9,2.5]);wall('1-TV',1,[4.2,5.9],[7.4,5.9])
wall('1-STN',1,[11.3,2.5],[16.82,2.5]);wall('1-STS',1,[11.3,1],[16.82,1]);wall('1-STA',1,[16.82,1],[16.82,2.5])
wall('2-N',2,[.1,10.3],[13.1,10.3],[win(1.7,5.1,'W207',.55),win(8.2,11.9,'W206',.45)])
wall('2-B1N',2,[13.1,9.5],[18.7,9.5],[win(13.6,15.65,'W205a',.65),win(15.95,17.9,'W205b',.65)])
wall('2-W',2,[.1,2.5],[.1,10.3],[win(2.8,4,'W214',.1)])
wall('2-B3S',2,[.1,4.3],[6.5,4.3],[door(.5,1.4,'D205')]);wall('2-B3E',2,[6.5,4.3],[6.5,10.3])
wall('2-B2S',2,[6.5,4.3],[13.1,4.3],[door(8,9,'D204')])
wall('2-B12',2,[13.1,4.3],[13.1,10.3]);wall('2-B1S',2,[13.1,4.3],[18.7,4.3],[door(13.3,14.2,'D203')]);wall('2-B1E',2,[18.7,4.3],[18.7,9.5],[glass(5.3,7.2,'G201')])
wall('2-HNE',2,[18.7,4.3],[19.9,4.3])
wall('2-HE',2,[19.9,2.5],[19.9,4.3],[glass(2.8,4,'G204')])
wall('2-HS',2,[.1,2.5],[11.3,2.5],[door(2.2,3.1,'D207',-1),door(3.8,4.6,'D208',-1),glass(6,8,'G203'),win(9.9,10.8,'W208',.1)])
wall('2-PAR',2,[11.3,2.5],[16.72,2.5],th=.16);wall('2-STB',2,[11.3,1],[11.3,2.5],th=.16)
wall('2-STS',2,[11.3,1],[16.72,1],[win(12.1,15.6,'W202',.45,1.02)]);wall('2-AS',2,[16.72,1],[18.42,1],[win(16.9,18.15,'W209',.1)]);wall('2-AE',2,[18.42,1],[18.42,2.5],[win(1.15,2.3,'W211',.1)])
wall('2-BATHS',2,[.1,.1],[4.9,.1],[win(.5,2.7,'W212',1.5)]);wall('2-BATHW',2,[.1,.1],[.1,2.5]);wall('2-BATHE',2,[3.5,.1],[3.5,2.5]);wall('2-LINE',2,[4.9,.1],[4.9,2.5])
wall('2-SER',2,[18.42,2.5],[19.9,2.5],[win(18.65,19.65,'W213',.1)])
g.OPEN=OPEN

# Explicit head direction and dimensions; V3 reference-relative arrangement, no mirrors.
# Frame 2.25m long x 2.10m wide; mattress 2.00 x 2.00m, proposed not measured.
f('A01','灰格大床 / 床架2.25长×2.10宽',2,[13.4,7.1,15.65,9.2],'bed','#b7b7bb','B1','W')
f('A02','床头柜',2,[13.6,6.45,14.2,7.05],r='B1');f('A03','白色书架',2,[13.2,5.4,13.6,6.8],r='B1')
f('A04','电脑桌 / 第二窗下',2,[15.85,8.75,17.65,9.4],'desk',r='B1');f('A05','电脑椅',2,[16.4,7.75,17,8.35],'chair',r='B1')
f('A06','梳妆台 / 东墙',2,[18,8.05,18.6,9.35],'desk',r='B1');f('A07','粉色圆凳',2,[17.25,8.1,17.8,8.65],'circle','#d8b2bd','B1')
f('A08','穿衣镜',2,[18.4,7.25,18.6,8],'mirror',r='B1');f('A09','衣柜 / 南墙',2,[15.7,4.4,17.4,5],r='B1')
f('A10','粉色圆毯',2,[15.4,5.05,17.9,7.55],'roundrug','#d6a3b1','B1');f('A11','健身车 / 阳台旁',2,[17.55,4.55,18.3,5.85],'bike',r='B1')
f('A12','瑜伽球',2,[14.4,6.4,15.1,7.1],'circle','#ce8ba2','B1');f('A13','黑黄蹦床',2,[13.7,5.3,14.8,6.4],'trampoline',r='B1')
f('B01','绿色床（床头东）',2,[10.6,5.9,12.8,7.7],'bed','#9cae85','B2','E')
f('B02','电视矮柜',2,[6.6,6.05,7.05,8],r='B2');f('B03','电脑桌',2,[6.6,8.2,7.25,9.85],'desk',r='B2');f('B04','电脑椅',2,[7.6,8.65,8.2,9.25],'chair',r='B2')
f('B05','窗边衣柜',2,[12.35,8.9,13,10.2],r='B2');f('B06','穿衣镜',2,[12.85,8.3,13,8.85],'mirror',r='B2');f('B07','衣帽架',2,[12.4,7.9,13,8.3],'rack',r='B2')
f('B08','吉他 / 床头侧',2,[11.85,7.85,12.25,8.3],r='B2');f('B09','望远镜',2,[10.3,9.05,11.15,9.95],'scope',r='B2')
f('B10','灰地毯',2,[7.5,6.25,10.3,8.65],'rug','#ccc9c4','B2');f('B11','矮茶几',2,[8.15,7.1,9.35,7.8],'table',r='B2');f('B12','入口抽屉柜',2,[9.35,4.4,10.1,4.95],r='B2');f('B13','入口书架',2,[11.7,4.4,12.9,4.8],r='B2')
# P2.3: rotate the reference-relative arrangement clockwise; preserve furniture sizes.
# Outer room envelope remains 6.2 x 5.8m; unused edge margins are refitted, not scaled.
f('C01','灰蓝格床（床头南）',2,[4.5,4.4,6,6.6],'bed','#99a2b8','B3','S');f('C02','床尾小书架',2,[5.05,6.75,5.75,7.35],r='B3')
f('C03','电脑桌 / 与床头及入口同墙',2,[2,4.4,4,5.05],'desk',r='B3',head='S');f('C04','白色电脑椅',2,[2.65,5.45,3.25,6.05],'chair',r='B3');f('C05','窗下收藏矮柜',2,[1.7,9.75,4,10.2],r='B3')
f('C06','衣物架 / 收藏柜',2,[.2,6.2,.85,10.2],'rack',r='B3');f('C07','落地镜',2,[.2,5.35,.38,5.95],'mirror',r='B3');f('C08','星形地毯',2,[1.6,6.4,4.4,9.2],'starrug','#b5b7d1','B3')
f('C09','床与书桌之间抽屉柜',2,[4.05,4.4,4.5,5],r='B3')
f('M01','酒红床（床头西）',1,[14.2,7.5,16.4,9.5],'bed','#9f626d','MB','W');f('M02','窗侧床头柜',1,[14.2,9.55,14.8,10.15],r='MB');f('M03','门侧床头柜',1,[14.2,6.9,14.8,7.45],r='MB')
f('M04','衣柜',1,[15,5.4,16.9,6],r='MB');f('M05','深木梳妆台',1,[17.25,5.4,18.55,6],'desk',r='MB');f('M06','梳妆椅',1,[17.6,6.35,18.15,6.9],'chair',r='MB');f('M07','衣架',1,[18.9,5.4,19.75,5.95],'rack',r='MB')
# Worktop overlays (hob/sink) are deliberate nested objects, not collisions.
f('K01','冰箱',1,[.2,9.2,1.15,10.2],'fridge',r='K');f('K02','水槽台面',1,[1.15,9.55,4.6,10.2],r='K');f('K03','灶台台面',1,[.2,6.9,.85,9.2],r='K')
f('K04','灶台/烟机',1,[.2,8.1,.85,9],'hob',r='K');f('K05','横窗下水槽',1,[2,9.55,3,10.2],'sink',r='K');f('K06','开放半岛',1,[3.95,7.8,4.6,9.55],r='K');f('K07','南侧操作台',1,[.2,6.2,2.2,6.85],r='K')
f('D01','六人玻璃餐桌',1,[6.3,7.5,8.4,8.5],'table','#dce9e7','D')
for i,b in enumerate([[6.5,6.85,7,7.35],[7.65,6.85,8.15,7.35],[6.5,8.65,7,9.15],[7.65,8.65,8.15,9.15],[5.65,7.75,6.15,8.25],[8.55,7.75,9.05,8.25]]):f('DC'+str(i+1),'餐椅',1,b,'chair',r='D')
f('D02','餐厅壁架',1,[9.35,9.3,9.8,10.2],r='D')
f('L01','浅灰长沙发',1,[1.7,.5,5.6,1.45],'sofa','#cfd3d1','L');f('L02','贵妃位',1,[1.7,1.45,2.65,2.65],'sofa','#cfd3d1','L');f('L03','抽象地毯',1,[2.3,1.8,6.6,4.3],'rug','#d3ccc1','L');f('L04','玻璃茶几',1,[3.3,2.45,4.7,3.25],'table',r='L');f('L05','电视柜',1,[4.25,5.4,7.35,5.8],r='L');f('L06','参考书架',1,[8.9,4.5,9.4,5.8],r='L')
f('LA1','洗烘设备',1,[12.9,8.45,13.6,10.05],'washer',r='LA');f('LA2','洗衣台',1,[10.2,9.55,12.9,10.2],r='LA');f('LA3','洗衣篮',1,[10.2,8.3,10.8,8.9],'circle',r='LA')
f('R1','阅读双椅',1,[15,3.7,17,4.55],'sofa',r='R');f('R2','书架',1,[16.6,4.75,17.8,5.2],r='R');f('E1','鞋柜',1,[11.2,3.6,11.6,5.2],r='R')
f('WC1','坐便',1,[20.8,1.3,21.55,2.1],'wc',r='WC');f('WC2','台盆',1,[19.3,1.8,20.4,2.4],'sink',r='WC');f('ST1','储物柜',1,[19.5,4.6,21.8,5.2],r='ST')
f('MW1','浴缸',1,[20.05,9.4,21.75,10.15],'tub',r='MW');f('MW2','台盆',1,[21.2,6.9,21.8,8.1],'sink',r='MW');f('MW3','坐便',1,[20.15,5.7,20.85,6.45],'wc',r='MW')
f('WB1','淋浴',2,[.25,.25,1.25,1.25],'tub',r='WB');f('WB2','坐便',2,[1.5,.4,2.2,1.15],'wc',r='WB');f('WB3','台盆',2,[.2,1.7,1.4,2.4],'sink',r='WB');f('LC1','布草层架',2,[3.6,.2,4.8,.8],r='LC')
clear('A-desk',2,(16.1,7.55),(16.1,8.75),'桌前使用深1.20m');clear('A-foot',2,(15.65,7.5),(18.4,7.5),'床尾至镜前2.75m')
clear('A-entry',2,(14.8,5.2),(15.7,5.2),'入口折行横向余量0.90m')
clear('B-foot',2,(7.05,6.2),(10.6,6.2),'床尾至电视柜3.55m');clear('B-desk',2,(7.25,9.4),(8.45,9.4),'桌前使用深1.20m')
clear('C-side',2,(3.3,6.3),(4.5,6.3),'床侧活动1.20m');clear('C-desk',2,(2.3,5.05),(2.3,6.25),'桌前使用深1.20m')
clear('M-side',1,(15.5,6),(15.5,7.5),'衣柜至床侧1.50m');clear('M-foot',1,(16.4,8),(19.8,8),'床尾至卫浴墙3.40m')
clear('H-width',2,(10,2.6),(10,4.2),'走廊净宽1.60m');clear('K-entry',1,(2.2,7),(3.95,7),'厨房入口净1.75m')
route('主卧直达',1,[(9.1,6.3),(11.8,6.3),(13.9,6.3),(15.3,6.3)])
route('开放客餐厨',1,[(7.9,3.6),(8,6.4),(4.9,6.4),(3.2,7.1),(3.2,8.7)])
route('二楼主通路',2,[(.8,3.4),(7.1,3.4),(12,3.4),(17.5,3.4),(17.5,1.8)])
route('舒亚入口',2,[(.95,3.4),(.95,4.8),(1.3,5.6),(1.3,6.5)])
route('薇亚入口至活动区',2,[(13.75,3.4),(13.75,4.75),(15.25,4.75),(15.3,5.5),(15.4,6.3),(16,6.6),(17,7)])
REFS={
'B1':('大姐卧室/大姐卧室_俯拍视角（日景）.png',['床头在西墙，床长边面向北侧双窗。','电脑桌在第二窗下；梳妆台与镜子在东墙。','东墙玻璃门通阳台，健身车位于门旁。','书架、球、蹦床在西侧；衣柜南侧，入口西南。','房间5.40×5.00m；床架2.25×2.10m，占房间17.5%。']),
'B2':('男主卧室/男主卧室_侧面视角（日景）.png',['北窗；西墙电视柜与电脑桌连续排列。','床头、吉他、衣帽架、镜子、衣柜在东侧。','望远镜面向窗；矮茶几在电视与床之间。','入口依据背面图位于电视墙转角的南墙。','删除入口凹位，恢复完整矩形37.12㎡。']),
'B3':('二姐卧室/二姐房间_正视图（日景）.png',['房内关系顺时针转90°；外轮廓暂保持6.20×5.80m。','床头、抽屉柜、电脑桌、入口均在南墙。','从北向南看：左床、中桌、右门；衣物架在右侧西墙。','入口直接接直走廊，无凹位；北窗沿用辅助视角关系。','无第二门；本轮露台在东侧，从走廊东端进入。']),
'MB':('阿姨卧室/卧室/主卧卧室_俯拍（日景）.png',['原图整体逆时针旋转90°，没有镜像或单独搬家具。','床头与入口仍同墙；主卫仍在床尾对墙。','外窗与衣柜/梳妆台/衣架分处床的两侧。','落位后床头西、窗北、主卫东；入口正对直廊。'])}

def stair(s,l):
    s.rect([11.4,1.1,16.72,2.4],'#dedbd2','#83928b',1)
    for i in range(20):s.line((11.4+i*.28,1.1),(11.4+i*.28,2.4),'#8a928c',.8)
    s.line((16.5,1.75),(11.7,1.75),g.TEAL,2.5,arrow=True)
    s.wt(14,1.35,'A → B 下楼 / 直跑梯',11,anchor='middle')
    s.wt(17.5,1.5,'A上口' if l==2 else 'A上口投影',10,anchor='middle')
    s.wt(10.5,1.5,'B下口投影' if l==2 else 'B下口',10,anchor='middle')
    if l==2:s.wt(14,2.1,'楼板开口 / 非走廊',10,anchor='middle')
def floor(s,l):
    if l==2:
        s.rect([0,0,22,10.4],'#e9e9e4','#aab5ae',1,'5 5')
        s.wt(19.5,1.4,'下层屋面',11,anchor='middle')
    for r in ROOMS:
        if r['level']!=l:continue
        if r['polygon']:s.poly(r['polygon'],r['color'],'none')
        else:s.rect(r['box'],r['color'],'none')
    for q in sorted([q for q in F if q['level']==l],key=lambda q:0 if 'rug' in q['kind'] else 1):g.furniture(s,q)
    for w in WALLS:
        if w['level']==l:g.wall_draw(s,w)
    stair(s,l)
    for rt in ROUTES:
        if rt['level']==l:
            for a,b in zip(rt['points'],rt['points'][1:]):s.line(a,b,g.TEAL,1.8,'6 4',True)
    if l==1:
        for a,b in [((4.7,6),(4.7,10.2)),((.2,5.9),(4.2,5.9)),((7.4,5.9),(9.8,5.9))]:s.line(a,b,g.TEAL,1,'5 4')
        labels=[(4.6,4.5,'开放客厅'),(2,7.3,'开放厨房'),(7.2,6.4,'开放餐厅'),(11.9,8,'洗衣房'),(17.8,7.3,'主卧 27.84㎡'),(20.9,8.4,'主卫'),(13.2,3.6,'通行 / 阅读'),(20,3.7,'储物'),(20,.7,'客卫')]
    else:
        labels=[(2.5,8.8,'舒亚 / 二姐'),(9.6,8.6,'子豪'),(16.1,6.7,'薇亚 / 大姐'),(2.5,3.5,'三卧室同一直走廊'),(1.7,1.4,'公用浴室'),(4.2,1.3,'布草'),(7.4,.9,'阳台入口'),(8,-.8,'临街连续阳台'),(20.6,7.4,'东侧木露台')]
        for rid in ['FB','AB']:
            r=next(r for r in ROOMS if r['id']==rid);pts=r['polygon']
            for a,b in zip(pts,pts[1:]+pts[:1]):
                # shared 0m edge is open connection between front balcony and side terrace
                if a[1]==0 and b[1]==0 and max(a[0],b[0])>20:
                    if min(a[0],b[0])>=20:continue
                    a=(min(a[0],20),0);b=(min(b[0],20),0)
                s.line(a,b,'#8e9e92',1.6)
        s.wt(16,9.95,'退台屋面（不通行）',10,anchor='middle')
    for x,y,t in labels:s.wt(x,y,t,13,anchor='middle',weight=700)

def floors():
    for l,n in [(1,'02_一楼家具平面图'),(2,'03_二楼家具平面图')]:
        s=g.Sheet('《秘密教学》｜'+('一楼：餐厨西侧，主卧东侧' if l==1 else '二楼：卧室比例与东侧露台修订'),'P2.3 待确认 · 项目北在上，临街南在下 · 四卧室放大图和原图对照见网页',[0,0,22,12],63,(160,940),(1800,1280))
        floor(s,l);s.dim((0,-2),(22,-2),'主体横向展开 22.00m');s.dim((23,0),(23,10.4),'主体进深 10.40m')
        s.txt(1590,250,'N ↑',22,weight=700);s.txt(1590,280,'项目北',14)
        if l==1:
            s.dim((4.6,10.9),(14,10.9),'厨房—主卧边界间隔 9.40m')
            s.txt(100,1125,'厨房与主卧不共墙：中间为开放餐厅、公共连接、洗衣房及主卧直通廊。',18,weight=700)
            s.txt(100,1160,'主卧整套关系旋转90°接入横向布局；D106在直廊尽头；D107只从主卧进入主卫。',16)
        else:
            for a,b,t in [(.2,6.4,'舒亚 35.96㎡'),(6.6,13,'子豪 37.12㎡'),(13.2,18.6,'薇亚 27.00㎡')]:s.dim((a,10.9),(b,10.9),t)
            s.txt(100,1125,'三卧室相邻并排，三扇入口共南墙、直接接直廊。舒亚关系顺时针转90°，撤销入口凹位。',18,weight=700)
            s.txt(100,1160,'舒亚从北向南看：左床、中桌、右门。东端接木露台；临街为连续窄阳台。灰色区为下层屋面。',16)
        s.finish(n)

def details():
    for rid,n in [('MB','04_主卧家具放大图'),('B1','05_大姐卧室家具放大图'),('B2','06_子豪卧室家具放大图'),('B3','07_二姐卧室家具放大图')]:
        r=next(q for q in ROOMS if q['id']==rid);x,y,xx,yy=r['box'];sc=105
        s=g.Sheet('《秘密教学》｜'+r['name']+' · 原图关系复核','床头、外窗、工作区、门位为固定锚点；右侧逐项说明。',r['box'],sc,(110-x*sc,900+y*sc),(1800,1150))
        if r['polygon']:s.poly(r['polygon'],r['color'],'none')
        else:s.rect(r['box'],r['color'],'none')
        px,py=s.xy(x-.2,yy+.2)
        s.p.append(f'<defs><clipPath id="clip"><rect x="{px}" y="{py}" width="{(xx-x+.4)*sc}" height="{(yy-y+.4)*sc}"/></clipPath></defs><g clip-path="url(#clip)">')
        for q in sorted([q for q in F if q['room']==rid],key=lambda q:0 if 'rug' in q['kind'] else 1):g.furniture(s,q,True)
        for w in WALLS:
            if w['level']==r['level'] and w['b'][0]>=x-.2 and w['a'][0]<=xx+.2 and w['b'][1]>=y-.2 and w['a'][1]<=yy+.2:g.wall_draw(s,w,False)
        s.p.append('</g>')
        if rid=='B3':
            s.line((5.2,9.2),(5.2,8),g.BLUE,2,arrow=True)
            s.wt(5.2,9.4,'原图视线：朝南',13,anchor='middle',color=g.BLUE)
        prefix={'B1':'A-','B2':'B-','B3':'C-','MB':'M-'}[rid]
        for c in CLEAR:
            if c['id'].startswith(prefix):s.dim(c['a'],c['b'],c['label'],True)
        s.dim((x,y-.45),(xx,y-.45),f'净宽 {xx-x:.2f}m');s.dim((xx+.45,y),(xx+.45,yy),f'净深 {yy-y:.2f}m')
        s.wt((x+xx)/2,yy+.6,f'项目北 ↑ · 净面积 {r["net_area"]:.2f}㎡',18,anchor='middle',weight=700)
        items=[]
        for q in F:
            if q['room']==rid:
                b=q['box'];items.append(f'{q["id"]}  {q["name"]}  [{b[2]-b[0]:.2f}×{b[3]-b[1]:.2f}m]')
        s.notes(940,170,[('原图关系与本次拟定尺度',REFS[rid][1]),('家具编号 / 设计占地',items)],790)
        s.txt(110,1020,'尺寸为拟定值；原图用于确定相对关系，不能提供实测尺寸。详见网页“原图对照”。',16)
        s.finish(n)

# Keep villa coordinates and the accepted street-side garage arrangement.
# Extend the site southward instead of taking space from the rear or the rooms.
FRONT_EXTENSION=2.3
SITE=dict(bounds=[-1.8,-10.3,24.2,13.4],building=[0,0,22,10.4],garage_outer=[5,-10.3,17,-4.5],garage_net=[5.2,-10.1,16.8,-4.7],garage_gate=[6,14],pedestrian_gate=[20.5,22.1],road=[-1.8,-15.7,29.2,-10.3],east_lane=[24.2,-15.7,29.2,13.4],car_length=4.8,car_width=1.9,turn_radius=4.2,front_garden_depth=4.5,path_width=1.4)
GARDEN_BEDS=[[.4,-1.25,9.5,-.25],[11.6,-1.25,19.6,-.25],[5.3,-4.25,16.7,-3.15],[17.5,-4.25,19.6,-3.15]]
GARDEN_PATHS=[[4.8,-2.9,22.1,-1.5],[9.85,-2.9,11.25,.2],[20.5,-10.1,22.1,-1.5],[17,-6.5,22.1,-5.1]]
GARDEN_ROUTES=[[(21.3,-10.2),(21.3,-2.2),(10.55,-2.2),(10.55,0)],[(16.65,-5.8),(21.3,-5.8),(21.3,-2.2)],[(5.5,-2.2),(10.55,-2.2)]]
def vehicle_trace():
    # Slow reverse quarter-circle from transverse parked pose; reverse for entry.
    poses=[]
    for i in range(91):
        t=math.pi/2*i/90;poses.append((12.8-4.2*math.sin(t),-4.9-4.2*(1-math.cos(t)),t))
    poses += [(8.6,-9.1-d,math.pi/2) for d in [.2,.4,.6,.8,1,1.2,1.4]]
    return [(x,y-FRONT_EXTENSION,t) for x,y,t in poses]
VEHICLE_POSES=vehicle_trace()
def car_corners(x,y,t):
    return [(x+a*math.cos(t)-b*math.sin(t),y+a*math.sin(t)+b*math.cos(t)) for a,b in [(-2.4,-.95),(2.4,-.95),(2.4,.95),(-2.4,.95)]]

def site():
    s=g.Sheet('《秘密教学》｜前庭花园修订总平面','P2.3 · 保留已确认布局；拉开车库与别墅间距，花草＋步道为主 · 尺寸待用户校准',SITE['bounds'],32,(175,650),(1800,1280))
    s.rect(SITE['road'],'#d5dcd9','none');s.rect(SITE['east_lane'],'#d5dcd9','none')
    s.rect(SITE['bounds'],'#e5eddf',g.WALL,4)
    s.rect(SITE['building'],'#efe6dc',g.WALL,2)
    s.rect([.2,6,4.6,10.2],'#dce9e3','none');s.wt(2.4,8,'开放厨房',15,anchor='middle')
    s.rect([14,5.4,21.8,10.2],'#ebdcdc','none');s.wt(17.8,8,'主卧套房',17,anchor='middle')
    s.wt(11,4,'主体 22.00 × 10.40m',21,anchor='middle',weight=700)
    for rid in ['FB','AB']:
        r=next(r for r in ROOMS if r['id']==rid);s.poly(r['polygon'],'none',g.BLUE,1.5)
    for box in GARDEN_PATHS:s.rect(box,'#efe4cf','none')
    for box in GARDEN_BEDS:
        s.rect(box,'#a7c093','#7b9974',1)
        for i in range(int((box[2]-box[0])/.6)):
            x=box[0]+.3+.6*i;y=(box[1]+box[3])/2
            s.circ(x,y,.11,['#dca3b3','#e5c66b','#afa0cb'][i%3],'none')
    s.wt(5,-.95,'窗前低矮花草',11,anchor='middle')
    s.wt(15.6,-.95,'低矮种植带',11,anchor='middle')
    s.wt(11,-3.9,'车库后花境',11,anchor='middle')
    s.wt(5.5,-1.9,'花园步道 1.40m',12,anchor='middle')
    s.wt(3,-3.9,'前庭花园',16,anchor='middle')
    s.dim((18.8,-4.5),(18.8,0),'花园净深4.50m')
    s.rect(SITE['garage_outer'],'#d9e1de',g.WALL,3)
    s.wt(11,-5.3,'沿街车库 / 净11.60×5.40m',15,anchor='middle')
    s.line((6,-10.3),(14,-10.3),'#faf9f5',8);s.line((6,-10.3),(14,-10.3),g.BLUE,2)
    s.wt(10,-10.95,'车库卷闸 8.00m',13,anchor='middle')
    s.line((17,-6.3),(17,-5.3),'#faf9f5',6);s.line((17,-6.3),(16,-6.3),'#8e7859',1.5)
    s.wt(18.4,-6.9,'车库侧门接步道',11,anchor='middle')
    s.line((20.5,-10.3),(22.1,-10.3),'#faf9f5',8);s.line((20.5,-10.3),(20.5,-8.7),'#8e7859',1.5)
    s.wt(21.3,-10.95,'独立人行门1.60m',12,anchor='middle')
    for route in GARDEN_ROUTES:
        for a,b in zip(route,route[1:]):s.line(a,b,g.TEAL,2,arrow=True)
    for pose in VEHICLE_POSES[::15]:s.poly(car_corners(*pose),'none','#a7b7be',.8)
    for a,b in zip(VEHICLE_POSES,VEHICLE_POSES[1:]):s.line(a[:2],b[:2],g.ORANGE,1.5)
    s.poly(car_corners(*VEHICLE_POSES[0]),'#a9bec7',g.INK,1.5)
    s.wt(12.8,-7.2,'4.8×1.9m 横停',12,anchor='middle')
    s.rect([10.4,-8.95,15.2,-5.45],'none',g.ORANGE,.8,'5 4')
    s.wt(7.7,-6.5,'倒车转向区',12,anchor='middle')
    s.wt(3,-7,'前院种植',16,anchor='middle');s.wt(11,11.9,'后院净深3.00m',16,anchor='middle')
    s.wt(26.6,6,'东侧巷道',16,anchor='middle');s.wt(17,-14.2,'临街道路（宽5.40m为转弯校准假设）',13,anchor='middle')
    for x,y in [(-.9,2),(-.9,6),(-.9,11.5),(23.2,6),(23.2,10.8),(4,12),(18,12),(1,-7),(2.8,-8.3)]:s.circ(x,y,.45,'#9db88f','#7b9974')
    s.dim((-1.8,14.1),(24.2,14.1),'地块横向26.00m');s.dim((-2.6,-10.3),(-2.6,13.4),'地块进深23.70m')
    s.dim((0,-11.8),(22,-11.8),'临街建筑面宽22.00m');s.dim((22,4.4),(24.2,4.4),'东侧2.20m')
    s.notes(1260,190,[('本轮只调整前庭',['车库沿街横向位置与右侧人行门保留。','车库—别墅间距由2.20m增至4.50m。','花草种植＋步道，不安排座椅。','室内、阳台露台及后院不移动。']),('花园与入户关系',['主步道净宽拟1.40m，右侧通路1.60m。','独立人行门与车库侧门汇入步道。','入户门前保留通道，不以花坛堵门。','窗前用低矮植物，花境不占行走范围。']),('用地与尺寸待校准',['前界、车库及街道整体向南平移2.30m。','地块26×21.4m改为26×23.7m。','增加59.8㎡设计用地，不挤占房间。','原照片不能证明地界，待你校准。']),('保留的复核事项',['车身轨迹随车库平移，出入关系不变。','南侧窗位及右侧木体量仍需立面核对。','具体植物、铺装与排水留待后续细化。'])],475)
    s.txt(70,1190,'蓝线＝阳台投影；橙线＝倒车轨迹；绿色箭头＝步行动线。仅二维修订，未修改三维模型。',16)
    s.finish('01_全地块总平面图')

def notes():
    s=g.Sheet('《秘密教学》｜P2.3 修改与逻辑复核','参考可确定相对关系；尺寸和未显示的接法仍需确认。',[0,0,1,1],1,(0,0),(1800,1200))
    s.notes(70,170,[('已修正的关系',['主体22.0×10.4m，街面为长边，不再纵向排成长条。','厨房西北、主卧东北，无共墙；横向边界间隔9.40m。','餐厨开放；主卧直通廊轴线与门中心同为Y=6.30m。','二楼相邻三房：舒亚—子豪—薇亚；主走廊保持笔直。','楼梯A上口在薇亚端，向西下降到B端一楼落地。']),('卧室从原图恢复的内容',['薇亚：床头西、双窗北、梳妆/镜/阳台东，衣柜南。','子豪：床和电视对置、桌接电视、望远镜面窗。','舒亚：南墙左床中桌右门（北向南看），西墙衣物架。','主卧：整间关系统一转90°，头侧入口、尾侧主卫。','网页附四房原图与平面并排，避免只靠文字声称一致。']),('相对关系与绝对尺度分开',['舒亚35.96㎡；子豪恢复37.12㎡；薇亚27.00㎡。','大姐床尾至镜前4.00→2.75m；主卧及其他卧室未缩小。','原图没有实测尺寸，不能把图片像素比当成精确米数。','尺寸仅供比例推敲，最终由用户校准。'])],790)
    s.notes(940,170,[('本次纠错及尚待复核',['沿用大姐房27㎡与床架占比17.5%，本轮未改室内。','车库保持沿街横向布局，与前界一同向南移2.30m。','前庭加深至4.50m，以花草和1.40m步道为主。','公用浴室位于楼下公共区上方，后续需校核管线和隔声。','南侧公共区窗位与原图不完全相同；不把外景当实测立面。']),('检查的范围与局限',['二维检查墙体开口、家具占地、门扇及主要路径。','楼梯两层同坐标，20踢面×0.165m、19踏面×0.28m。','平台1.60×1.50m，梯宽1.30m，挑空边界不得通行。','承重、楼梯头部净高、露台支承仍需下一轮模型复核。','本图不是施工图，也不能据此宣布建筑结构已验收。']),('当前文件与下一步',['P2.3替换P2.2图纸；本次只修平面，模型仍为V4。','不修改三维模型，不生成正式场景图。','房间关系保留，待确认前庭间距并校准尺寸。','通过后才把同一组坐标写入唯一模型。'])],790)
    s.finish('08_修改说明与确认要点')

def save():
    data=dict(revision='P2.3_20261020',status='比例修订待确认；具体尺寸由用户校准；未更新模型',units='m',rooms=ROOMS,furniture=F,walls=WALLS,openings=OPEN,clearances=CLEAR,routes=ROUTES,site=SITE,garden=dict(beds=GARDEN_BEDS,paths=GARDEN_PATHS,routes=GARDEN_ROUTES),vehicle_trace=VEHICLE_POSES,stairs=dict(footprint=[11.4,1.1,16.72,2.4],A=[16.72,1.1,18.32,2.6],B=[9.8,1.1,11.4,2.4],rises=20,rise=.165,treads=19,tread=.28),reference_relationships=REFS)
    (OUT/'平面方案数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    table=['# P2.3 门窗表','','编号 | 层 | 类型 | 宽m | 窗台m | 顶高m','---|---|---|---:|---:|---:']+[f'{o["id"]} | {o["level"]} | {o["type"]} | {o["end"]-o["start"]:.2f} | {o.get("sill","—")} | {o.get("head","—")}' for o in OPEN]
    (OUT/'门窗表.md').write_text('\n'.join(table),encoding='utf8')
    table=['# P2.3 家具与净尺寸','','## 房间（开放区域面积为功能分区面积）','','空间 | 净包络m | 净面积㎡','---|---:|---:']
    for r in ROOMS:
        b=r['box'];table.append(f'{r["name"]} | {b[2]-b[0]:.2f} × {b[3]-b[1]:.2f} | {r["net_area"]:.2f}')
    table+=['','子豪房已撤销入口凹位，恢复完整矩形37.12㎡；所有数值为比例推敲暂定值，最终由用户校准。','','## 家具','','编号 | 空间 | 名称 | 占地m','---|---|---|---:']
    for q in F:
        b=q['box'];table.append(f'{q["id"]} | {q["room"]} | {q["name"]} | {b[2]-b[0]:.2f} × {b[3]-b[1]:.2f}')
    (OUT/'家具与净尺寸表.md').write_text('\n'.join(table),encoding='utf8')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'模型').glob('*') if p.suffix in ['.json','.blend','.glb']}
    (OUT/'模型未修改校验.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf8')
    pages=sorted(p.stem for p in OUT.glob('*.svg'));buttons=''.join(f'<button data-sheet="{n}">{n.replace("_"," · ",1)}</button>' for n in pages)
    # Version the actual image URLs; a revision on the HTML alone cannot invalidate cached SVGs.
    sheet_versions={n:hashlib.sha256((OUT/(n+'.svg')).read_bytes()).hexdigest()[:16] for n in pages}
    idx=json.loads((ROOT/'制作记录/V3参考索引.json').read_text(encoding='utf8'))['files'];refs=[]
    for rid,num in [('B1','05'),('B2','06'),('B3','07'),('MB','04')]:
        name,items=REFS[rid];match=next(x for x in idx if x['relative_path']==name);src='../参照/V3/'+match['id']+'.png';sheet=next(p for p in pages if p.startswith(num))
        refs.append(f'<article><h2>{rid} · {name}</h2><p>{"；".join(items)}</p><div class="pair"><img src="{src}"><img src="{sheet}.svg?v={sheet_versions[sheet]}"></div></article>')
    for group,names in [
        ('外景主要依据 / 正面及俯拍优先',['别墅外景/别墅_正面视角（日景）.png','别墅外景/别墅_俯拍视角（日景）.png','别墅外景/别墅_侧面视角（日景）.png','别墅外景/别墅_背面视角（日景）.png']),
        ('大姐床房比例 / 其余三个视角交叉核对',['大姐卧室/大姐卧室_侧面俯拍视角（日景）.png','大姐卧室/大姐卧室_床尾看床头视角（日景）.png','大姐卧室/大姐卧室_床头看床尾视角（日景）.png'])]:
        cards=[]
        for name in names:
            match=next(x for x in idx if x['relative_path']==name)
            cards.append(f'<figure><img src="../参照/V3/{match["id"]}.png"><figcaption>{name}</figcaption></figure>')
        refs.append(f'<article><h2>{group}</h2><div class="pair">'+''.join(cards)+'</div></article>')
    doc='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>秘密教学 P2.3 横向平面确认</title><style>
body{margin:0;font:16px "Microsoft YaHei",sans-serif;background:#edf0eb;color:#263c45}header{background:#263c45;color:white;padding:20px 28px}header p{font-size:14px}nav{display:flex;flex-wrap:wrap;gap:8px;padding:16px 24px}button,a{padding:9px 12px;background:#faf9f5;border:1px solid #b7c8bd;border-radius:5px;text-decoration:none;color:#263c45;cursor:pointer}button.active{background:#3b887a;color:white}#tools{padding:8px 24px 18px;display:flex;gap:10px}#canvas{overflow:auto;padding:0 24px 24px}#drawing{width:100%;display:block}#canvas.actual #drawing{width:1800px}article{padding:24px;background:white;margin:24px}article p{line-height:1.8}.pair{display:grid;grid-template-columns:1fr 1fr;align-items:center;gap:12px}.pair img{width:100%}h2{font-size:18px}footer{padding:24px}</style>
<header><b>《秘密教学》｜P2.3 横向展开 · 待确认平面</b><p>厨房与主卧分处东西两端；车库位置保留，前庭加深为花草步道小花园。下方附原图对照。三维模型未更新。</p></header><nav>BUTTONS</nav><div id="tools"><a id="png" download>高清PNG</a><a id="svg" download>可编辑SVG</a><button id="zoom">切换原尺寸</button><a href="#references">卧室与外景原图对照 ↓</a><a href="门窗表.md">门窗表</a><a href="说明.md">说明</a></div><div id="canvas"><img id="drawing" alt="P2.3平面"></div><section id="references">REFS</section><footer>仅保留当前待确认图纸；P2.2已被本轮图纸替换。比例修订稿，具体尺寸由用户校准；非实测或施工图。</footer>
<script>const sheetVersions=SHEET_VERSIONS;function select(n){const v='?v='+sheetVersions[n];document.querySelector('#drawing').src=n+'.svg'+v;document.querySelector('#png').href=n+'.png'+v;document.querySelector('#svg').href=n+'.svg'+v;document.querySelectorAll('[data-sheet]').forEach(b=>b.classList.toggle('active',b.dataset.sheet===n));}document.querySelectorAll('[data-sheet]').forEach(b=>b.onclick=()=>select(b.dataset.sheet));document.querySelector('#zoom').onclick=()=>document.querySelector('#canvas').classList.toggle('actual');select('01_全地块总平面图');</script></html>'''.replace('BUTTONS',buttons).replace('REFS',''.join(refs)).replace('SHEET_VERSIONS',json.dumps(sheet_versions,ensure_ascii=False))
    doc=doc.replace('<a href="门窗表.md">门窗表</a>', '<a href="门窗表.md">门窗表</a><a href="家具与净尺寸表.md">家具尺寸</a><a href="逻辑复核.md">逻辑复核</a>')
    (OUT/'打开平面图.html').write_text(doc,encoding='utf8')
    md=['# P2.3 横向展开平面（待确认）','','仅修订二维平面；模型未修改。本次P2.3仅将前庭加深并加入花草步道，替换P2.2。具体尺寸由用户校准，本图数字不构成尺寸定稿。','',
    '- 主体22.00×10.40m；厨房与主卧无共墙，横向边界间隔9.40m。','- 四卧室逐项按参考布局复核，主卧整套关系旋转90°。','- 二姐房内关系顺时针90°，床头、电脑桌与入口同在南墙；凹位与未证实第二门撤销，子豪恢复矩形。','- 大姐床架长2.25×宽2.10m；房间27㎡，床架占比17.5%，旧稿11.5%。','- 地块26×23.7m；车库净11.6×5.4m及右侧人行门保留，前庭由2.2m加深至4.5m，布置花草及1.4m步道；向南增地59.8㎡。','- 连续临街阳台通东侧木露台；旧西侧后露台取消，公共露台入口在走廊东端。','- 主体22×10.4m暂保留；南侧浴室、楼梯窗位和屋顶体量仍需立面复核，不宣称原图完全吻合。','', '## 图纸']+[f'- [{n} PNG]({n}.png) / [SVG]({n}.svg)' for n in pages]
    for rid,(p,items) in REFS.items():md+=['',f'## {rid}: {p}']+['- '+t for t in items]
    (OUT/'说明.md').write_text('\n'.join(md),encoding='utf8')
def main():
    OUT.mkdir(exist_ok=True);floors();details();site();notes();save();print('P2.3: eight sheets and source-comparison gallery generated. Models unchanged.')
if __name__=='__main__':main()
