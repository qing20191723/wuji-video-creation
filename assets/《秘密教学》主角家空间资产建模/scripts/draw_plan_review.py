"""2D review proposal only. Never imports or writes the V4 model files.
Units: metres. X east / Y project north. All rooms use inside-face bounds.
Run from any directory. SVG text remains editable; no image generation involved.
"""
from pathlib import Path
import math, json, html, hashlib

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'平面确认'
OUT.mkdir(exist_ok=True)
INK='#263c45'; WALL='#425861'; BLUE='#4188a0'; TEAL='#3b887a'; ORANGE='#c27b35'
ROOMS=[]; F=[]; WALLS=[]; OPEN=[]; CLEAR=[]; ROUTES=[]
def room(id,name,l,b,color='#f2e9df'):
    ROOMS.append(dict(id=id,name=name,level=l,box=b,color=color,net_area=round((b[2]-b[0])*(b[3]-b[1]),2)))
def furn(id,name,l,b,kind='cabinet',color='#d9c8b1',parent=None):
    F.append(dict(id=id,name=name,level=l,box=b,kind=kind,color=color,room=parent))
def wall(id,l,a,b,opens=(),th=.2):
    WALLS.append(dict(id=id,level=l,a=a,b=b,thickness=th))
    # opening: start/end global coordinate, kind, label; default hinged leaf +axis, into east/north
    for o in opens:
        s,e,kind,label,*extras=o
        opts=extras[0] if extras else {}
        OPEN.append(dict(id=label,wall=id,level=l,start=s,end=e,type=kind,**opts))
def clear(id,l,a,b,label):CLEAR.append(dict(id=id,level=l,a=a,b=b,label=label,value=round(math.dist(a,b),2)))

# F2: three adjacent bedrooms, no central courtyard or transverse service hall.
room('B1','薇亚 / 大姐卧室',2,[3.6,.2,10.2,6.4],'#f3e3e6')
room('B2','子豪 / 男主卧室',2,[3.6,6.6,10.2,12.0],'#e6eddf')
room('B3','舒亚 / 二姐卧室',2,[3.6,12.2,10.2,17.8],'#e5e7f0')
room('H2','直走廊',2,[1.8,1.7,3.4,18.0],'#e8efed')
room('A','A端上平台',2,[.2,.2,3.4,1.7],'#e8efed')
room('WB','公用浴室',2,[-1.6,8.8,1.6,11.2],'#deebef')
room('LT','后露台',2,[-1.6,18.2,10.2,20.0],'#eee9df')
room('FB','临街阳台',2,[.2,-1.5,10.2,-.2],'#eee9df')
# Ground: open living/dining/kitchen, straight approach to master entrance.
room('L','客厅',1,[3.6,.2,10.2,5.6])
room('D','开放餐厅',1,[3.6,5.8,10.2,10.0],'#eee6d8')
room('K','开放厨房',1,[5.8,10.2,10.2,13.2],'#e3ecea')
room('MH','主卧直走廊',1,[4.0,10.2,5.6,13.4],'#e8efed')
room('MB','主卧',1,[3.6,13.6,10.2,19.4],'#ede0df')
room('MW','主卫',1,[.2,15.4,3.4,19.4],'#deebef')
room('LA','洗衣房',1,[-1.6,8.8,1.6,11.2],'#e3ecea')
room('WC','客卫',1,[.2,11.4,1.6,13.8],'#deebef')
room('H1','公共通路',1,[1.8,1.7,3.4,13.8],'#e8efed')
room('E','玄关',1,[.2,.2,3.4,1.5],'#eee6d8')

# Structural line work: openings are true gaps, not a symbol placed over a solid wall.
for l in [1,2]:
    wall(f'{l}-S',l,[0,.1],[10.4,.1],[(1.95,3.05,'door','D101',{'side':1}),(4.6,9.4,'window','W113',{'sill':.4,'head':2.8})] if l==1 else [(0.25,1.45,'window','W201',{'sill':.1,'head':2.8}),(5.35,7.95,'glass','G201',{'sill':0,'head':2.8})])
    wall(f'{l}-STW',l,[.1,1.6],[.1,8.7],[(2.2,5,'window',f'W{l}02',{'sill':.45,'head':1.02}),(7.2,8.4,'window',f'W{l}03',{'sill':.1,'head':2.8})])
    wall(f'{l}-LWW',l,[-1.7,8.7],[-1.7,11.3],[(9.0,10.5,'window',f'W{l}04',{'sill':1.2,'head':2.6})])
    wall(f'{l}-LWS',l,[-1.7,8.7],[1.7,8.7])
    wall(f'{l}-LWN',l,[-1.7,11.3],[1.7,11.3])
    wall(f'{l}-LWE',l,[1.7,8.7],[1.7,11.3],[(8.9,9.9,'door','D104' if l==1 else 'D207',{'side':-1})])
    # Upper corridor parapet / lower supporting stair wall share the same line.
    wall(f'{l}-STG',l,[1.65,1.7],[1.65,7.02 if l==1 else 8.7],th=.1)
wall('2-BW',2,[3.5,.1],[3.5,18.1],[(3.35,4.35,'door','D203',{'side':1}),(10.4,11.4,'door','D204',{'side':1}),(16.2,17.2,'door','D205',{'side':1})])
wall('2-B12',2,[3.5,6.5],[10.3,6.5]);wall('2-B23',2,[3.5,12.1],[10.3,12.1])
wall('2-BN',2,[3.5,17.9],[10.3,17.9])
wall('2-BE',2,[10.3,.1],[10.3,17.9],[(1.15,3.05,'window','W205a',{'sill':.65,'head':2.8}),(3.9,6.05,'window','W205b',{'sill':.65,'head':2.8}),(7.0,9.9,'window','W206',{'sill':.45,'head':2.8}),(13,16,'window','W207',{'sill':.55,'head':2.8})])
wall('2-HW',2,[1.7,11.3],[1.7,18.1],[(11.45,12.1,'open','C201'),(12.4,14.6,'window','W208',{'sill':.1,'head':2.8}),(15,17.7,'window','W209',{'sill':.1,'head':2.8})])
wall('2-LIN-W',2,[.9,11.3],[.9,12.2]);wall('2-LIN-N',2,[.9,12.2],[1.7,12.2])
wall('2-HN',2,[1.7,18.1],[3.5,18.1],[(1.95,3.2,'glass','G202',{'sill':0,'head':2.7})])
wall('2-AW',2,[.1,.1],[.1,1.6],[(.3,1.35,'window','W210',{'sill':.1,'head':2.8})])
# Ground exterior / room partitions.
wall('1-EAST',1,[10.3,.1],[10.3,19.5],[(1.0,4.8,'window','W105',{'sill':.3,'head':2.8}),(6.4,9.25,'window','W106',{'sill':.55,'head':2.8}),(11.1,12.6,'window','W107',{'sill':1.15,'head':1.7}),(14.5,18.9,'window','W108',{'sill':.3,'head':2.8})])
wall('1-NORTH',1,[.1,19.5],[10.3,19.5],[(.6,2.6,'window','W109',{'sill':1.45,'head':2.1})])
wall('1-MWEST',1,[3.5,13.5],[3.5,19.5],[(17.1,18.05,'door','D107',{'side':-1})])
wall('1-MENTRY',1,[3.5,13.5],[10.3,13.5],[(4.3,5.3,'door','D106',{'side':1})])
wall('1-MHW',1,[3.9,10.2],[3.9,13.5],[(11.4,12.6,'open','O104')])
wall('1-MHE',1,[5.7,10.2],[5.7,13.5])
wall('1-KN',1,[5.7,13.3],[10.3,13.3])
wall('1-WC-W',1,[.1,11.3],[.1,13.9],[(12.1,13,'window','W111',{'sill':1.5,'head':2.5})])
wall('1-WC-E',1,[1.7,11.3],[1.7,13.9],[(12.6,13.5,'door','D105',{'side':-1})])
wall('1-WC-N',1,[.1,13.9],[3.9,13.9])
wall('1-MW-W',1,[.1,15.3],[.1,19.5]);wall('1-MW-S',1,[.1,15.3],[3.5,15.3])
wall('1-WENTRY',1,[.1,.1],[.1,1.6],[(.3,1.35,'window','W112',{'sill':.1,'head':2.7})])
wall('1-H-E',1,[3.5,1.6],[3.5,10.2],[(1.8,3.4,'open','O101'),(6.0,9.9,'open','O102')])
wall('1-TV',1,[5.35,5.7],[8.05,5.7])

# Furniture: real footprints, labelled in enlarged drawings.
def f(id,name,l,b,kind='cabinet',color='#d9c8b1',r=None):furn(id,name,l,b,kind,color,r)
f('S01','浅灰沙发',1,[5.5,.5,9.4,1.45],'sofa','#d5d6d4','L');f('S02','贵妃位',1,[8.45,1.45,9.4,2.65],'sofa','#d5d6d4','L')
f('S03','玻璃茶几',1,[6.15,2.35,7.55,3.15],'table','#dce9e7','L');f('S04','抽象地毯',1,[5.15,1.8,9.35,4.5],'rug','#ded9ce','L')
f('S05','电视隔断',1,[5.4,5.25,8,5.6],'cabinet','#cbd3d0','L');f('S06','书架',1,[9.75,4.3,10.2,5.5],r='L')
f('DT','玻璃餐桌',1,[5.0,7.1,7.1,8.1],'table','#dce9e7','D')
for i,b in enumerate([[5.2,6.45,5.7,6.95],[6.35,6.45,6.85,6.95],[5.2,8.25,5.7,8.75],[6.35,8.25,6.85,8.75],[4.35,7.35,4.85,7.85],[7.25,7.35,7.75,7.85]]):f(f'DC{i}','餐椅',1,b,'chair',r='D')
f('DS','餐厅壁架',1,[9.75,9.35,10.2,9.95],r='D')
f('K1','北侧台面',1,[6.9,12.55,10.2,13.2],r='K');f('K2','水槽台面',1,[9.55,10.2,10.2,12.55],r='K')
f('K3','开放半岛台',1,[5.8,10.2,8.15,10.85],r='K');f('K4','半岛转角',1,[5.8,10.85,6.45,11.2],r='K')
f('KF','双门冰箱',1,[6,12.2,6.9,13.2],'fridge','#dce0df','K')
f('KH','灶台/烟机',1,[7.3,12.55,8.2,13.2],'hob','#67747a','K');f('KS','水槽',1,[9.55,11.1,10.2,12.1],'sink','#c8dee4','K')
f('LM','洗烘设备',1,[-1.6,9.6,-.9,11.1],'washer','#dce0df','LA');f('LC','洗衣台',1,[-.9,10.55,1.6,11.2],r='LA');f('LB','洗衣篮',1,[-1.4,8.9,-.8,9.5],'circle',r='LA')
f('WC1','坐便',1,[.4,11.65,1.1,12.4],'wc','#edf1ee','WC');f('WC2','台盆',1,[.2,13.3,.65,13.8],'sink',r='WC')
f('SH','玄关柜',1,[.2,.3,.7,1.4],r='E')
# Master: entry on headboard side; bathroom accessed only from foot end.
f('MBED','酒红床 / 2.0×2.2',1,[7.1,13.85,9.1,16.05],'bed','#9c6269','MB')
f('MN1','床头柜',1,[6.35,13.85,6.95,14.45],r='MB');f('MN2','床头柜',1,[9.3,13.85,9.9,14.45],r='MB')
f('MC','衣柜',1,[3.6,14.9,4.2,17.0],r='MB');f('MV','深木梳妆台',1,[3.6,18.1,4.2,19.4],r='MB');f('MS','梳妆椅',1,[4.5,18.5,5.0,19.0],'chair',r='MB')
f('MR','衣架',1,[6.0,18.8,7.4,19.35],'rack',r='MB')
f('MT','浴缸',1,[.5,18.5,2.4,19.2],'tub','#d8e8ed','MW');f('MWC','坐便',1,[2.45,15.65,3.15,16.45],'wc','#edf1ee','MW');f('MVS','台盆柜',1,[.2,16.2,.85,17.7],'sink',r='MW')
# Big sister — north headboard, east dual windows, south balcony.
f('AB','灰格床 / 2.0×2.2',2,[5.0,4.0,7.0,6.2],'bed','#b4b6b8','B1');f('AN','床头柜',2,[4.2,5.25,4.8,5.85],r='B1')
f('AS','白色书架',2,[3.7,6.05,4.9,6.4],r='B1');f('AW','衣柜',2,[3.7,.2,5.1,.8],r='B1')
f('AD','电脑桌',2,[9.55,3.7,10.2,5.5],'desk',r='B1');f('AC','电脑椅',2,[8.55,4.3,9.1,4.9],'chair',r='B1')
f('AV','白色梳妆台',2,[8.15,.2,9.45,.75],'desk','#e9e7df','B1');f('AVC','粉色圆凳',2,[8.5,1.05,9,1.55],'circle','#d5b2bc','B1')
f('AM','穿衣镜',2,[9.6,.2,10.15,.4],'mirror',r='B1');f('AR','粉色圆毯',2,[5.4,1.05,8.1,3.75],'roundrug','#d9acb7','B1')
f('AT','蹦床',2,[3.85,1.9,4.95,3.0],'trampoline','#b8bbba','B1');f('AY','瑜伽球',2,[5.2,.9,5.9,1.6],'circle','#d58ba5','B1');f('AX','健身车',2,[9.25,1.8,10,3.1],'bike','#aab3b3','B1')
# Boy.
f('BB','绿色床 / 1.8×2.2',2,[6.8,9.6,8.6,11.8],'bed','#a0b58d','B2');f('BN','床头柜',2,[6.1,11.1,6.65,11.7],r='B2')
f('BW','衣柜',2,[9.6,10.1,10.2,11.9],r='B2');f('BD','电脑桌',2,[8.1,6.6,9.9,7.25],'desk',r='B2');f('BC','电脑椅',2,[8.6,7.65,9.2,8.25],'chair',r='B2')
f('BTV','电视柜',2,[4,6.6,6.1,7.05],r='B2');f('BR','地毯',2,[4.85,7.6,8.0,9.25],'rug','#deded3','B2');f('BT','茶几',2,[5.7,8.1,6.9,8.7],'table',r='B2')
f('BTE','望远镜',2,[9.05,8.5,9.9,9.35],'scope',r='B2');f('BG','吉他',2,[6.2,9.7,6.55,10.25],'guitar',r='B2');f('BS','书架',2,[3.6,7.4,4.05,9.3],r='B2')
# Little sister.
f('CB','灰蓝床 / 1.6×2.1',2,[7,15.5,8.6,17.6],'bed','#9aa9bd','B3');f('CN','床头柜',2,[8.85,17,9.45,17.6],r='B3')
f('CD','电脑桌',2,[3.6,13.2,4.25,15.2],'desk',r='B3');f('CC','电脑椅',2,[4.65,13.8,5.25,14.4],'chair',r='B3')
f('CW','衣物/收藏架',2,[4.4,12.2,7.4,12.85],'rack',r='B3');f('CL','窗下收藏柜',2,[9.75,13.2,10.2,15.4],r='B3');f('CM','穿衣镜',2,[3.6,12.3,3.8,13.0],'mirror',r='B3')
f('CR','星形地毯',2,[5.5,13.2,8.8,15.3],'starrug','#a2abc5','B3')
f('WS','浴室台盆',2,[-1.6,9.5,-.95,11.1],'sink',r='WB');f('WT','淋浴',2,[-.1,10,1.6,11.2],'tub',r='WB');f('WW','坐便',2,[-.6,8.9,.1,9.6],'wc',r='WB')
f('LIN','嵌入布草柜',2,[1.0,11.45,1.6,12.1],r='H2')

ZONES=[
 dict(room='B1',level=2,box=[3.7,.8,5.1,1.8],label='柜前 1.00m',allow=['AW']),
 dict(room='B1',level=2,box=[8.35,3.7,9.55,5.5],label='椅区 1.20m',allow=['AC','AD']),
 dict(room='B1',level=2,box=[8.15,.75,9.45,1.75],label='梳妆使用区',allow=['AVC','AV']),
 dict(room='B2',level=2,box=[8.7,10.1,9.6,11.9],label='柜前 0.90m',allow=['BW']),
 dict(room='B2',level=2,box=[8.1,7.25,9.9,8.45],label='椅区 1.20m',allow=['BC','BD']),
 dict(room='B3',level=2,box=[4.4,12.85,7.4,13.75],label='柜前 0.90m',allow=['CW']),
 dict(room='B3',level=2,box=[4.25,13.2,5.45,15.2],label='椅区 1.20m',allow=['CC','CD']),
 dict(room='MB',level=1,box=[4.2,14.9,5.2,17.0],label='柜前 1.00m',allow=['MC']),
 dict(room='MB',level=1,box=[4.2,18.1,5.4,19.4],label='梳妆使用区',allow=['MS','MV']),
 dict(room='K',level=1,box=[6,11.2,6.9,12.2],label='冰箱开启区',allow=['KF']),
 dict(room='D',level=1,box=[5.2,8.55,5.7,9.05],label='拉椅',allow=['DC2']),
 dict(room='D',level=1,box=[6.35,8.55,6.85,9.05],label='拉椅',allow=['DC3'])]

clear('CA1',2,[7,4.6],[8.55,4.6],'床侧至椅区 1.55m')
clear('CA2',2,[6,2.8],[6,4.0],'床尾活动带 1.20m')
clear('CB1',2,[8.6,10.4],[9.6,10.4],'床侧 1.00m')
clear('CB2',2,[7.7,7.25],[7.7,9.6],'床尾至柜线 2.35m')
clear('CC1',2,[8.6,16.2],[10.2,16.2],'床侧 1.60m')
clear('CC2',2,[7.8,14.3],[7.8,15.5],'床尾活动带 1.20m')
clear('CM1',1,[9.1,15.2],[10.2,15.2],'床侧 1.10m')
clear('CM2',1,[8.1,16.05],[8.1,17.25],'床尾活动带 1.20m')
clear('CK1',1,[8.15,11.4],[9.55,11.4],'操作/进入净宽 1.40m')
clear('CK2',1,[7.6,10.85],[7.6,12.55],'台面间净宽 1.70m')
clear('CH',2,[1.8,15.5],[3.4,15.5],'走廊净宽 1.60m')
clear('CD1',1,[6.55,9.05],[6.55,10.2],'拉椅后通路 1.15m')
ROUTES=[dict(id='主卧直达',level=1,points=[[4.8,9.4],[4.8,12.8],[4.8,14.4]]),dict(id='楼梯至卧室',level=2,points=[[.85,1.6],[.85,.85],[2.6,.85],[2.6,16.7],[3.9,16.7]]),dict(id='一楼落地至餐厅',level=1,points=[[.85,7.3],[.85,7.65],[2.6,7.65],[3.0,9.5],[4.8,9.5]])]

class Sheet:
    def __init__(self,title,sub,bounds,scale=60,offset=(100,1420),size=(1800,1700)):
        self.title=title;self.bounds=bounds;self.scale=scale;self.ox,self.oy=offset;self.w,self.h=size
        self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">', '<defs><marker id="arr" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10" fill="#3b887a"/></marker></defs>', '<style>text{font-family:"Microsoft YaHei","Noto Sans CJK SC",sans-serif;fill:#263c45} .small{font-size:15px} .num{font-family:Arial,sans-serif}</style>',f'<rect width="{self.w}" height="{self.h}" fill="#faf9f5"/>']
        self.txt(65,65,title,32,weight=700);self.txt(65,102,sub,17)
        self.txt(65,self.h-44,'待确认平面方案 P1 · 2026-10-15 · 影视设计参考尺寸，非实测 / 非施工图 · 尚未写入 V4 模型',16)
        self.p.append(f'<path d="M65 {self.h-72}H{self.w-65}" stroke="#bec9c5"/>')
    def xy(self,x,y):return (self.ox+x*self.scale,self.oy-y*self.scale)
    def txt(self,x,y,t,size=16,anchor='start',weight=400,color=None):
        self.p.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}"'+(f' style="fill:{color}"' if color else '')+'>'+html.escape(str(t))+'</text>')
    def wt(self,x,y,t,size=15,**kw):self.txt(*self.xy(x,y),t,size,**kw)
    def rect(self,b,fill='none',stroke=INK,sw=1,dash=None,rx=0):
        x,y=self.xy(b[0],b[3]);w=(b[2]-b[0])*self.scale;h=(b[3]-b[1])*self.scale
        self.p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" rx="{rx}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
    def line(self,a,b,col=INK,w=1,dash=None,arrow=False):
        x,y=self.xy(*a);xx,yy=self.xy(*b)
        self.p.append(f'<path d="M{x:.2f} {y:.2f}L{xx:.2f} {yy:.2f}" fill="none" stroke="{col}" stroke-width="{w}"'+(f' stroke-dasharray="{dash}"' if dash else '')+(' marker-end="url(#arr)"' if arrow else '')+'/>')
    def circ(self,x,y,r,fill,stroke=INK):
        a,b=self.xy(x,y);self.p.append(f'<circle cx="{a:.2f}" cy="{b:.2f}" r="{r*self.scale:.2f}" fill="{fill}" stroke="{stroke}"/>')
    def poly(self,points,fill,stroke=INK,w=1):
        ps=' '.join(f'{x:.2f},{y:.2f}' for x,y in [self.xy(*p) for p in points]);self.p.append(f'<polygon points="{ps}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')
    def dim(self,a,b,label,small=False):
        self.line(a,b,ORANGE,1.3)
        dx,dy=b[0]-a[0],b[1]-a[1];n=math.hypot(dx,dy);px,py=-dy/n*.08,dx/n*.08
        for p in [a,b]:self.line((p[0]-px,p[1]-py),(p[0]+px,p[1]+py),ORANGE,1.5)
        m=((a[0]+b[0])/2,(a[1]+b[1])/2)
        if abs(dx)<.01:
            x,y=self.xy(*m);self.p.append(f'<text x="{x-9:.2f}" y="{y:.2f}" font-size="{13 if small else 16}" text-anchor="middle" transform="rotate(-90 {x-9:.2f} {y:.2f})" style="fill:{ORANGE}">{html.escape(label)}</text>')
        else:self.wt(m[0],m[1]+.12,label,13 if small else 16,anchor='middle',color=ORANGE)
    def notes(self,x,y,sections,width=600):
        for title,lines in sections:
            self.p.append(f'<rect x="{x}" y="{y-24}" width="{width}" height="34" fill="#e3ebe6" rx="4"/>');self.txt(x+14,y,title,20,weight=700);y+=35
            for line in lines:self.txt(x+14,y,line,16);y+=29
            y+=25
    def finish(self,name):
        self.p.append('</svg>');(OUT/(name+'.svg')).write_text('\n'.join(self.p),encoding='utf8')

def furniture(s,f,detail=False):
    b=f['box'];x,y,xx,yy=b;k=f['kind'];c=f['color'];cx=(x+xx)/2;cy=(y+yy)/2
    if k in ['rug','starrug']:s.rect(b,c,'#c2c1bd',.7,dash='4 3')
    elif k in ['circle','roundrug','trampoline']:s.circ(cx,cy,min(xx-x,yy-y)/2,c)
    else:s.rect(b,c,'#7b8987',1,rx=3)
    if k=='bed':
        # Master headboard south, all upstairs beds headboard north.
        head=y if f['id']=='MBED' else yy-.5
        s.rect([x+.08,head+.07,xx-.08,head+.43],'#f4f0e7','#82908d',.7,rx=4)
        s.line((x+.08,head+.5),(xx-.08,head+.5),'#7b8987',1)
    elif k=='desk':
        if xx-x>yy-y:s.rect([cx-.26,yy-.18,cx+.26,yy-.07],'#597078',INK,.5)
        else:s.rect([x+.08,cy-.26,x+.19,cy+.26],'#597078',INK,.5)
    elif k=='hob':
        for a in [x+.2,xx-.2]:
            for z in [y+.16,yy-.16]:s.circ(a,z,.07,'none')
    elif k in ['sink','tub']:s.rect([x+.08,y+.08,xx-.08,yy-.08],'#eff6f5','#8da7ac',1,rx=6)
    elif k=='wc':s.circ(cx,cy,.2,'#fff')
    elif k=='bike':s.line((x+.15,y+.15),(xx-.15,yy-.15),INK,3);s.circ(cx,cy,.18,'none')
    elif k=='scope':
        for pt in [(x,y),(xx,y),(cx,yy)]:s.line((cx,cy),pt,INK,1.5)
        s.line((x,yy),(xx,y),INK,4)
    elif k=='starrug':
        pts=[]
        for i in range(10):
            t=i*math.pi/5+math.pi/2;r=.72 if i%2==0 else .3;pts.append((cx+r*math.cos(t),cy+r*math.sin(t)))
        s.poly(pts,'#71809d','none')
    if detail:
        label=f['name'];txtsize=14
        # Put long labels outside narrow symbols, ID inside identifies each item unambiguously.
        s.wt(cx,cy-.055,f['id'],14,anchor='middle',weight=700)
    elif k not in ['rug','roundrug','starrug']:s.wt(cx,cy-.05,f['id'],10,anchor='middle')

def wall_draw(s,w,ids=True):
    a,b=w['a'],w['b'];hor=a[1]==b[1];start=a[0] if hor else a[1];end=b[0] if hor else b[1];fixed=a[1] if hor else a[0]
    op=sorted([o for o in OPEN if o['wall']==w['id']],key=lambda z:z['start']);cursor=start
    def pt(t):return (t,fixed) if hor else (fixed,t)
    for o in op+[dict(start=end,end=end,type='end')]:
        if o['start']>cursor:s.line(pt(cursor),pt(o['start']),WALL,w['thickness']*s.scale)
        if o['type']=='end':break
        u,v=o['start'],o['end'];t=o['type'];r=v-u
        if t in ['window','glass']:
            for off in [-.035,.035]:s.line((u,fixed+off) if hor else (fixed+off,u),(v,fixed+off) if hor else (fixed+off,v),BLUE,1.8)
            s.line(pt((u+v)/2-.015),pt((u+v)/2+.015),BLUE,7)
            if t=='glass':s.line((u+.1,fixed+.13) if hor else (fixed+.13,u+.1),(v-.1,fixed+.13) if hor else (fixed+.13,v-.1),TEAL,1.2,arrow=True)
        elif t=='door':
            sign=o.get('side',1);hinge=pt(u);tip=(u,fixed+sign*r) if hor else (fixed+sign*r,u)
            s.line(hinge,tip,'#8e7859',1.8)
            pts=[]
            for i in range(21):
                th=i/20*math.pi/2;pts.append((u+r*math.cos(th),fixed+sign*r*math.sin(th)) if hor else (fixed+sign*r*math.sin(th),u+r*math.cos(th)))
            for p,q in zip(pts,pts[1:]):s.line(p,q,'#b0a28e',.8)
        elif t=='open':s.line(pt(u),pt(v),TEAL,1.5,'5 5')
        if ids:
            p=pt((u+v)/2);s.wt(p[0]+(.15 if not hor else 0),p[1]+(.17 if hor else 0),o['id'],10,color=BLUE if t in ['window','glass'] else INK)
        cursor=o['end']

def stair(s,l):
    s.rect([.2,1.7,1.5,7.02],'#e5e1d8','#9aa29c',1)
    for i in range(20):s.line((.2,1.7+i*.28),(1.5,1.7+i*.28),'#9b9e95',.7)
    s.line((.85,2.2),(.85,6.7),TEAL,3,arrow=True)
    s.wt(.85,4.3,'A→B 下',11,anchor='middle')
    s.wt(.85,1.35,'A 上口' if l==2 else 'A 上口投影',10,anchor='middle');s.wt(.85,7.45,'B 下口投影' if l==2 else 'B 下口',10,anchor='middle')
    if l==2:s.wt(.85,5.0,'挑空',12,anchor='middle')

def floor(s,l):
    for r in ROOMS:
        if r['level']==l:s.rect(r['box'],r['color'],'none')
    for z in ZONES:
        if z['level']==l and z['room'] in ['K','D']:s.rect(z['box'],'none',ORANGE,1,'4 4')
    # Rugs first; furniture on top.
    for f in sorted([f for f in F if f['level']==l],key=lambda z:0 if 'rug' in z['kind'] else 1):furniture(s,f)
    for w in WALLS:
        if w['level']==l:wall_draw(s,w)
    stair(s,l)
    for rt in ROUTES:
        if rt['level']==l:
            for p,q in zip(rt['points'],rt['points'][1:]):s.line(p,q,TEAL,2,'7 5',True)
    if l==1:
        s.line((3.6,10.1),(10.2,10.1),TEAL,1.5,'5 5');s.wt(7.8,9.7,'开放餐厨界面（无门）',14,anchor='middle',color=TEAL)
        for x,y,t in [(6.65,4.65,'客厅'),(8.65,6.2,'开放餐厅'),(8,11.6,'开放厨房'),(6.6,17.8,'主卧 38.28㎡'),(1.65,17.6,'主卫'),(-.1,9.3,'洗衣房'),(.8,12.8,'客卫')]:s.wt(x,y,t,16,anchor='middle',weight=700)
        s.wt(4.8,12.5,'直达主卧门',12,anchor='middle',color=TEAL)
        s.wt(1.6,14.55,'侧后室外通路',12,anchor='middle')
    else:
        for x,y,t in [(6.6,3.65,'薇亚 / 大姐 · 40.92㎡'),(6.6,9.05,'子豪 · 35.64㎡'),(6.8,15.0,'舒亚 / 二姐 · 36.96㎡'),(0,9.3,'公用浴室'),(5,19.15,'后露台 · 深1.80m'),(5,-.9,'临街阳台 · 深1.30m')]:s.wt(x,y,t,15,anchor='middle',weight=700)
        s.wt(2.6,17.4,'无扩大厅',11,anchor='middle',color=TEAL)
        s.line((.2,-1.5),(.2,-.2),'#8b9a94',3);s.line((10.2,-1.5),(10.2,-.2),'#8b9a94',3)
        s.line((-1.6,18.2),(-1.6,20),'#8b9a94',3);s.line((10.2,18.2),(10.2,20),'#8b9a94',3)
        s.line((.2,-1.5),(10.2,-1.5),'#8b9a94',3);s.line((-1.6,20),(10.2,20),'#8b9a94',3)

def north_scale(s,x=55,y=148):
    s.txt(x,y,'项目北 ↑',16,weight=700);s.txt(x,y+25,'临街南向在下方',13)
    a=(s.bounds[0],s.bounds[1]-.5);b=(a[0]+3,a[1]);s.line(a,b,INK,3)
    s.wt(a[0],a[1]-.3,'0',12);s.wt(b[0],b[1]-.3,'3m',12,anchor='end')

COMMON=[('读图方式',['深色实线＝墙体；绿色虚线＝开放分区 / 动线。','浅蓝双线＝窗；玻璃门另有平移箭头。','棕色门扇＋弧线＝平开门；橙色＝净距。','家具字母编号对应卧室放大图及家具表。','净面积按室内墙面计算；开放区为功能区面积。'])]

def make_floors():
    for l,name in [(1,'02_一楼家具平面图'),(2,'03_二楼家具平面图')]:
        s=Sheet('《秘密教学》｜'+('一楼家具平面图' if l==1 else '二楼家具平面图'),'先核对房间关系、家具与净距，再更新三维模型。',[-2,-2,11,20.5],58,(190,1430))
        floor(s,l);north_scale(s)
        s.dim((11.9 if l==2 else 10.85,.2),(11.9 if l==2 else 10.85,19.4 if l==1 else 17.8),'主体室内纵向 '+('19.20m' if l==1 else '17.60m'))
        if l==2:
            for a,b in [(.2,6.4),(6.6,12),(12.2,17.8)]:s.dim((11.3,a),(11.3,b),f'{b-a:.2f}m')
        s.dim((3.6,-2.1),(10.2,-2.1),'卧室区净宽 6.60m')
        sections=([('本次改动',['01  餐厨直接相连，撤掉家政前厅和厨房滑门。','02  主卧门位于直走廊正尽头，不再拐入门前廊。','03  洗衣房从公共通路进入；主卫只由主卧进入。','04  主卧扩大为净 6.60×5.80m；保留酒红床与深木家具。']),('开放厨房 / 餐厅',['北侧：冰箱、灶台、烟机；东侧：水槽与横窗。','南侧：开放半岛台；入口在半岛右端。','台面内净距 1.70m；半岛端至水槽柜 1.40m。','餐桌 2.10×1.00m，六席；北侧拉椅后通路 1.15m。']),('入口与采光',['D106 主卧门宽 1.00m，中心与走廊中心对齐。','D107 主卫门在床尾侧，外部公共通路不可进入。','W107 厨房横窗：窗台1.15 / 窗顶1.70m。','W108 主卧大窗：窗台0.30 / 窗顶2.80m。','W109 浴缸端墙横窗：窗台1.45 / 窗顶2.10m。'])] if l==1 else [('卧室净尺寸 / 净面积',['薇亚：6.60×6.20m ＝ 40.92㎡。','子豪：6.60×5.40m ＝ 35.64㎡。','舒亚：6.60×5.60m ＝ 36.96㎡。','三房按原图分别排家具，不以相同方块代替。']),('二姐门外区域',['直走廊净宽 1.60m；尽头直接到后露台玻璃门。','撤掉旧16.2㎡边界框服务过厅，不另设横向大厅。','公用浴室改在走廊西侧，与一楼洗衣房上下对应。','布草柜嵌入西侧，不占走廊净宽。']),('窗与楼梯',['W205a/b 大姐双窗：窗台0.65 / 窗顶2.80m。','G201 大姐阳台玻璃门：0.00 / 2.80m。','W208/209 连续高窗：0.10 / 2.80m。','W202 横向低窗：0.45 / 1.02m。','A端上平台→沿直梯向B端下楼；护栏高约1.16m。','层高3.30m；20踢面×0.165m，19踏面×0.28m。'])])
        sizes=[]
        for r in ROOMS:
            if r['level']==l:
                b=r['box'];sizes.append(f'{r["name"]}  {b[2]-b[0]:.2f}×{b[3]-b[1]:.2f}m  /  {r["net_area"]:.2f}㎡')
        s.notes(940,180,sections+COMMON+[('净尺寸与面积 / 开放区为功能划分',sizes)],780)
        # compact opening schedule makes dimensions explicit without cluttering the drawing.
        if l==2:
            for c in CLEAR:
                if c['id']=='CH':s.dim(c['a'],c['b'],'1.60m',True)
        else:
            for c in CLEAR:
                if c['id'] in ['CK1','CK2']:s.dim(c['a'],c['b'],f"{c['value']:.2f}m",True)
        s.finish(name)

def make_bedrooms():
    specs=[('MB','04_主卧家具放大图',1,'主卧：门在走廊正尽头，主卫位于床尾侧'),('B1','05_大姐卧室家具放大图',2,'薇亚：双窗、阳台、工作 / 梳妆 / 运动区域'),('B2','06_子豪卧室家具放大图',2,'子豪：绿色床品、望远镜、吉他与工作区'),('B3','07_二姐卧室家具放大图',2,'舒亚：灰蓝床品、星形地毯、电脑与收藏')]
    for rid,name,l,subtitle in specs:
        r=next(r for r in ROOMS if r['id']==rid);x,y,xx,yy=r['box'];sc=115
        s=Sheet('《秘密教学》｜'+r['name']+'家具放大图',subtitle,r['box'],sc,(115-x*sc,1080+y*sc),(1800,1400))
        s.rect(r['box'],r['color'],'none')
        # Clip to room plus 0.35m so adjacent-room walls don't leak into this sheet.
        px,py=s.xy(x-.35,yy+.35);s.p.append(f'<defs><clipPath id="roomclip"><rect x="{px}" y="{py}" width="{(xx-x+.7)*sc}" height="{(yy-y+.7)*sc}"/></clipPath></defs><g clip-path="url(#roomclip)">')
        for z in ZONES:
            if z['room']==rid:
                s.rect(z['box'],'#f5ead8',ORANGE,1,'5 4');s.wt((z['box'][0]+z['box'][2])/2,z['box'][3]-.16,z['label'],11,anchor='middle',color=ORANGE)
        for f in sorted([f for f in F if f['room']==rid],key=lambda z:0 if 'rug' in z['kind'] else 1):furniture(s,f,True)
        for w in WALLS:
            if w['level']==l:wall_draw(s,w,False)
        s.p.append('</g>')
        cs={'MB':['CM1','CM2'],'B1':['CA1','CA2'],'B2':['CB1','CB2'],'B3':['CC1','CC2']}[rid]
        for c in CLEAR:
            if c['id'] in cs:s.dim(c['a'],c['b'],c['label'],True)
        s.dim((x,y-.45),(xx,y-.45),f'净宽 {xx-x:.2f}m');s.dim((xx+.45,y),(xx+.45,yy),f'净深 {yy-y:.2f}m')
        s.wt((x+xx)/2,yy+.6,f'净面积 {r["net_area"]:.2f}㎡ · 北向在上',19,anchor='middle',weight=700)
        fs=[f for f in F if f['room']==rid]
        rows=[]
        for f in fs:
            b=f['box'];rows.append(f'{f["id"]}  {f["name"]}  ·  {b[2]-b[0]:.2f}×{b[3]-b[1]:.2f}m')
        specific={'MB':['入口在床头侧；走廊轴线 x=4.80m，门中心同轴。','主卫由西墙床尾侧门进入；东墙保留大窗。','衣柜、梳妆台、衣架保留原图相对分区。'], 'B1':['东墙保留两扇大窗；南墙玻璃门通临街阳台。','床头靠北；书架与运动区靠西，工作区靠东。','粉色圆毯为活动区，不作为阻挡通行的实体。'], 'B2':['东侧大窗与望远镜相邻；床右侧留1.00m。','工作区、电视柜与床尾休闲区分别可辨认。','家具朝向按整体坐标旋转，不镜像原人物识别物。'], 'B3':['东侧大窗、窗下收藏；西侧书桌与电脑。','南侧衣物 / 收藏区；床和星形地毯各自留出通路。','原俯拍图疑似第二扇门暂按柜门处理，未新增房间。']}[rid]
        s.notes(1010,180,[('家具清单与真实占地',rows),('空间核对',specific),('尺寸说明',['尺寸为影视设计参考，按家具和动作空间推导。','门扇、椅子拉出、柜前使用区逐项检查。','衣物架、镜子、收藏架不是无用途占位方块。'])],710)
        s.finish(name)

def make_site():
    s=Sheet('《秘密教学》｜全地块总平面图','室内先定尺度 → 外墙随之调整 → 配置院落与围墙。项目南向为临街侧。',[-4,-13,13,23],33,(230,1000),(1800,1700))
    s.rect([-4,-10,13,23],'#e6ecdf',WALL,5)
    s.rect([-4,-14,13,-10],'#d9dedd','none');s.wt(4.5,-12.2,'临街道路 / 画面下方为项目南',16,anchor='middle')
    s.rect([13,-10,15,23],'#e1e4e1','none');s.wt(14,17,'侧巷',13,anchor='middle')
    # main first floor footprint including laundry wing, with outdoor service recess
    footprint=[(0,0),(10.4,0),(10.4,19.6),(0,19.6),(0,15.2),(3.4,15.2),(3.4,14),(0,14),(0,11.4),(-1.8,11.4),(-1.8,8.6),(0,8.6)]
    s.poly(footprint,'#f3e8da',WALL,2)
    s.rect([3.6,13.6,10.2,19.4],'#e9dbdb','none');s.wt(6.9,16.5,'主卧套房',17,anchor='middle')
    s.wt(5.6,7.0,'别墅主体',22,anchor='middle',weight=700);s.wt(5.6,5.9,'室内先定 / 外轮廓已扩展',13,anchor='middle')
    # Upstairs boundaries overlay, no misleading filled blocks.
    s.rect([0,-1.7,10.4,0],'none',BLUE,2,'7 4');s.rect([-1.8,18,10.4,20.2],'none',BLUE,2,'7 4')
    s.wt(5,19.9,'二楼后露台投影',12,anchor='middle',color=BLUE)
    s.rect([-2,-9.8,5,-3.2],'#dce2e0',WALL,2);s.wt(1.5,-3.9,'车库净 6.60×6.20m',14,anchor='middle')
    s.rect([.35,-9.0,2.25,-4.2],'#b4c3c8',INK,1,rx=7);s.rect([.5,-7.6,2.1,-5.4],'#d7e3e7',INK,1,rx=6)
    s.wt(1.3,-6.7,'车辆',13,anchor='middle');s.wt(1.3,-7.3,'1.9×4.8m',12,anchor='middle')
    s.rect([-.45,-9.0,3.05,-4.2],'none',ORANGE,1,'5 4')
    s.line((-1.4,-10),(4.2,-10),'#faf9f5',8);s.line((-1.4,-9.8),(4.2,-9.8),'#faf9f5',8);s.line((-1.4,-9.95),(4.2,-9.95),BLUE,2)
    s.line((5,-5.4),(5,-4.4),'#faf9f5',5);s.line((5,-5.4),(4,-5.4),'#8e7859',1.5)
    s.line((1.3,-12.8),(1.3,-8.7),TEAL,3,arrow=True)
    s.wt(1.3,-10.7,'车行门 5.60m',13,anchor='middle')
    s.line((9.6,-10),(11,-10),'#faf9f5',8);s.wt(10.3,-10.7,'人行门',13,anchor='middle')
    s.rect([9.6,-9.9,11.1,-1.6],'#eeebe3','none');s.rect([2,-1.6,11.1,-.1],'#eeebe3','none')
    for a,b in [((10.35,-9.6),(10.35,-.85)),((10.35,-.85),(2.55,-.85)),((2.55,-.85),(2.55,.7))]:s.line(a,b,TEAL,2,arrow=True)
    s.wt(7.2,-4.5,'前院',18,anchor='middle');s.wt(7.2,-5.3,'入口与绿化',13,anchor='middle')
    s.wt(5,21.7,'后院 / 净深 3.40m',15,anchor='middle')
    for x,y in [(-3,2),(-3,5),(-3,15),(-2.8,21.5),(11.8,4),(11.8,8),(11.8,16),(9,22),(7.2,-7),(7.2,-3.3)]:s.circ(x,y,.45,'#a3b891','#7f9a75')
    s.dim((-4,-14.8),(13,-14.8),'地块参考宽 17.00m');s.dim((-4.7,-10),(-4.7,23),'地块参考深 33.00m')
    s.dim((10.4,12),(13,12),'侧距 2.60m',True);s.dim((-4,10),(-1.8,10),'2.20m',True)
    s.notes(900,180,[('场地与外观基准',['地块参考：17.00×33.00m，约561㎡。','别墅主体参考外包络：10.40×19.60m。','洗衣 / 公卫在西侧局部突出1.80m。','地块与外轮廓为本次补充设计，不是实测。']),('车库与人员入口',['沿用V3正立面：临街车库＋右侧独立人行门。','车库按一辆车校准，净6.60×6.20m。','车辆按1.90×4.80m；两侧开门带各0.80m。','直进直出；不声称库内可以完成180°掉头。','车库后侧与住宅之间留3.20m前庭。','人行通道净1.50m，与车行路线分开。']),('围墙 / 庭院 / 外窗',['围墙闭合，只有车行门、人行门两处入口。','东侧通路2.60m；西侧突出部最窄2.20m。','住宅后墙至围墙3.40m。','蓝色虚线是二楼阳台 / 后露台投影。','大窗外侧有室外空间，不对着新增室内房间。']),('外景变化必须确认',['保留浅外墙、黑窗框、平屋顶和临街车库语言。','主体纵深、窗位和阳台分段随室内布局调整。','不承诺新平面能与全部旧外景逐像素对应。','本次不生成外景图，也不更新三维模型。'])],790)
    s.finish('01_全地块总平面图')

def make_notes():
    s=Sheet('《秘密教学》｜本次修改与确认要点','这是一套二维待确认方案；旧模型尚未反映下面的修改。',[0,0,1,1],1,(0,0),(1800,1500))
    s.notes(70,180,[('先修正关系，再制作模型',['厨房：取消滑门及中间家政前厅，直接面向开放餐厅。','主卧：直走廊尽头即主卧门，门中心与走廊中心同轴；主卫只从主卧进入。','二楼：大姐—子豪—二姐连续并排；保留A上口、A→B下楼、B一楼落地。','二姐门外：取消横向服务大厅，公共浴室移至走廊西侧，布草柜嵌入墙边。']),('房间不再是统一长条',['大姐：旧边界框28.12㎡ → 新室内净40.92㎡。','子豪：旧边界框28.12㎡ → 新室内净35.64㎡。','二姐：旧边界框28.12㎡ → 新室内净36.96㎡。','主卧：旧边界框26.00㎡ → 新室内净38.28㎡。','旧值为边界框面积，新值为内墙面净面积，不能当作同口径增长率。']),('来自参考的内容',['用户本轮厨房后视 / 侧视：开放台面、冰箱灶台、水槽横窗与餐厅连接。','本轮餐厅侧视：六人玻璃餐桌、灰色吊灯、大窗与开放通行。','V3各卧室：家具种类、床品身份、工作区 / 梳妆区 / 收藏及运动器材。','楼道参考：直梯、实体护栏、高窗、尽头露台玻璃门。','V3外景：围墙、临街车库、独立人行门、平屋顶与黑框玻璃。'])],790)
    s.notes(940,180,[('本次补充设计 / 需要你确认',['所有绝对尺寸、净距、地块17×33m和车库6.6×6.2m。','三间卧室新的比例、具体门距与外窗在外墙上的精确位置。','公用浴室西侧突出体量、下层洗衣房的上下叠合关系。','主卧套房向后展开，外墙纵深和外景窗位随之调整。']),('原图矛盾的处理',['二姐俯拍出现疑似两个门：仅一扇连接公共走廊；另一处按柜门待核。','厨房部分视角有不同水槽边界：采用本轮侧视确定水槽靠外墙横窗，','后视确定半岛面向餐厅；不把反射或画面边缘再复制成一套水槽。','卧室局部角度存在镜头夸张，尺寸以家具和活动净距推导，非照片测量。']),('本次验收范围',['查看七张图：总地块、一楼、二楼、四卧室放大。','平面净距、门扇、家具占地与楼梯上下定位已进行图面检查。','窗台 / 窗顶高度在门窗表记录；家具真实占地在JSON和放大图记录。','不作结构、承重、消防或施工合规结论；不将二维检查看作三维验收。','本轮确认后才改模型；不会拿旧模型继续批量出图。']),('确认后推进',['将通过的平面坐标作为下一轮唯一输入。','更新模型、相机和外立面，再核对卧室原图身份。','正式场景制作继续等待模型及机位检查完成。'])],790)
    s.finish('08_修改说明与确认要点')

def save_data():
    data=dict(status='待用户确认；二维方案，未写入V4模型',revision='P1_20261015',units='m',axis='X东/Y项目北；南为临街侧',rooms=ROOMS,walls=WALLS,openings=OPEN,furniture=F,clearances=CLEAR,usage_zones=ZONES,routes=ROUTES,site=dict(bounds=[-4,-10,13,23],garage_net=[-1.8,-9.6,4.8,-3.4]),reference_policy='本轮图片与纠正优先，其余V3；绝对尺寸为补充设计')
    (OUT/'平面方案数据.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
    lines=['# 门窗表（二维方案 P1，待确认）','','编号 | 楼层 | 类别 | 开口宽 m | 窗台 m | 窗顶 m','---|---|---|---:|---:|---:']
    for o in OPEN:lines.append(f'{o["id"]} | {o["level"]} | {o["type"]} | {o["end"]-o["start"]:.2f} | {o.get("sill","—")} | {o.get("head",2.2 if o["type"]=="door" else "—")}')
    (OUT/'门窗表.md').write_text('\n'.join(lines),encoding='utf8')
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'模型').glob('*') if p.suffix in ['.json','.blend','.glb']}
    (OUT/'模型未修改校验.json').write_text(json.dumps(hashes,ensure_ascii=False,indent=2),encoding='utf8')
    pages=sorted(x.stem for x in OUT.glob('*.svg'))
    # All eight editable sheets have an identical, stable basename for the PNG counterpart.
    buttons=''.join(f'<button data-sheet="{html.escape(n)}">{html.escape(n.replace("_"," · ",1))}</button>' for n in pages)
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>秘密教学 · 待确认平面图</title>
<style>*{box-sizing:border-box}body{margin:0;background:#eceeea;color:#263c45;font:16px "Microsoft YaHei",sans-serif}header{padding:20px 28px;background:#263c45;color:white}header p{margin:8px 0 0;font-size:14px}nav{display:flex;gap:8px;flex-wrap:wrap;padding:16px 24px}button,a{border:1px solid #b7c8bd;border-radius:6px;background:#faf9f5;color:#263c45;padding:9px 12px;cursor:pointer;text-decoration:none}button.active{background:#3b887a;color:white}#tools{display:flex;gap:10px;padding:0 24px 16px;align-items:center}#canvas{overflow:auto;height:calc(100vh - 250px);padding:0 24px 24px}img{display:block;width:100%;max-width:1800px;margin:auto;background:white}#canvas.actual img{width:1800px;max-width:none}footer{padding:10px 24px;font-size:13px}</style>
<header><b>《秘密教学》｜平面确认 P1</b><p>本页是新平面方案。V4 三维模型保持原样，尚未按本图更新。先看一楼、二楼，再核对卧室与室外。</p></header>
<nav>BUTTONS</nav><div id="tools"><a id="png" download>下载高清 PNG</a><a id="svg" download>下载可编辑 SVG</a><button id="zoom">切换原尺寸 / 适应窗口</button><a href="门窗表.md">门窗表</a><a href="说明.md">来源与检查</a></div><div id="canvas"><img id="drawing" alt="待确认平面图"></div><footer>尺寸均为影视设计参考；所有图纸同向、同坐标。未确认前不更新模型、不恢复场景生图。</footer>
<script>const img=document.querySelector('#drawing');function select(n){img.src=encodeURI(n+'.svg');document.querySelector('#png').href=encodeURI(n+'.png');document.querySelector('#svg').href=encodeURI(n+'.svg');document.querySelectorAll('[data-sheet]').forEach(b=>b.classList.toggle('active',b.dataset.sheet===n));}document.querySelectorAll('[data-sheet]').forEach(b=>b.onclick=()=>select(b.dataset.sheet));document.querySelector('#zoom').onclick=()=>document.querySelector('#canvas').classList.toggle('actual');select('02_一楼家具平面图');</script></html>'''.replace('BUTTONS',buttons)
    (OUT/'打开平面图.html').write_text(page,encoding='utf8')
    refs=[
        ('开放厨房','场景资产/厨房/厨房_侧视图.png；厨房_后视图.png','本轮指定，开放台面及餐厅关系优先'),
        ('餐厅','场景资产/餐厅/餐厅_侧视图.png','六席餐桌、大窗、开放通行'),
        ('楼道','场景资产/别墅楼道和楼梯间参考/图片.png','高窗、横窗、实体护栏、露台门；旧文字不采用'),
        ('大姐','场景图V3版/大姐卧室/大姐卧室_俯拍视角（日景）.png','双窗与阳台，工作/梳妆/运动分区'),
        ('子豪','场景图V3版/男主卧室/男主卧室_侧面视角（日景）.png','床、电视、电脑、望远镜、吉他'),
        ('二姐','场景图V3版/二姐卧室/二姐房间_俯拍图（夜间）.png','床、桌、收藏和地毯；疑似第二扇门列为待核'),
        ('主卧','场景图V3版/阿姨卧室/卧室/主卧卧室_俯拍（日景）.png','头侧入口、脚侧卫浴、深木家具'),
        ('室外','场景图V3版/别墅外景/别墅_正面视角（日景）.png；别墅_俯拍视角（日景）.png','围墙、车库、独立入口和建筑语言')]
    text=['# 平面确认 P1','','状态：待用户确认。三维模型及正式场景图片均未修改。','','## 图纸','']
    text += [f'- [{n} PNG]({n}.png) · [SVG]({n}.svg)' for n in pages]
    text += ['','## 采用依据','','参考路径相对于用户的《秘密教学》全局通用资产目录。绝对尺寸均为本次设计推导，并非图片测量。','','区域 | 参考 | 采用内容','---|---|---']+[f'{a}|{b}|{c}' for a,b,c in refs]
    text += ['','## 确认边界','','保留三卧室并排与楼梯 A/B 关系；其余尺寸、精确门距、公卫移至西侧、外墙轮廓和庭院均为本次提案。', '厨房台面操作净距1.70m，入口1.40m；为保留冰箱开启和使用空间，没有压回1.20–1.40m。','后露台局部超出一楼外墙约0.60m；仅为二维边界提案，下一阶段需配置相应楼板/支承，不作为已解决结构。','二姐参考中的疑似第二扇门不新增公共房门，按柜门候选记录，待原图进一步核对。','','## 检查结果','','见 `平面几何检查.json` 与 `图纸输出检查.json`：家具占地、12处使用区、门扇采样、18处功能区可达性及3条路线。','图面检查采用0.50m人物足迹；不是三维净高、结构、承重或施工合规验收。','V4的JSON、Blender、GLB与既有校验值逐一比对保持不变。','','## 重建图纸','','`python scripts/draw_plan_review.py`','`python scripts/check_plan_review.py`','`node scripts/render_plan_review.cjs`','','脚本只写平面确认目录，不将二维提案写入三维模型。']
    (OUT/'说明.md').write_text('\n'.join(text),encoding='utf8')

if __name__=='__main__':
    make_site();make_floors();make_bedrooms();make_notes();save_data()
    print(json.dumps(dict(svg=len(list(OUT.glob('*.svg'))),rooms=len(ROOMS),furniture=len(F),openings=len(OPEN)),ensure_ascii=False))
