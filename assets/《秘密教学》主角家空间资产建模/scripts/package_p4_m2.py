"""Reproducible P4-M2 plans and local viewer; never modify previous deliveries."""
from pathlib import Path
import ast,html,json,math,shutil,csv,hashlib
R=Path(__file__).resolve().parents[1];OUT=R/'全屋模型_P4-M2_20261022'
M=json.loads((OUT/'数据/模型空间数据.json').read_text('utf8'));D=M['plan']
for n in ['图纸','贴图']:(OUT/n).mkdir(exist_ok=True)
INK='#243b40';GREEN='#38796c';ORANGE='#b36c31'
source=(R/'scripts/build_p3_delivery.py').read_text('utf8').replace('P3-R2 · 2026-10-22','P4-M2 · 2026-10-23')
nodes=[n for n in ast.parse(source).body if isinstance(n,(ast.ClassDef,ast.FunctionDef)) and n.name in ['Sheet','drawwalls']]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'drawing_primitives','exec'))
def route(s,ps,col=GREEN):
 for a,b in zip(ps,ps[1:]):s.line(a,b,col,3)
 a,b=ps[-2:];t=math.atan2(b[1]-a[1],b[0]-a[0])
 for k in [-.45,.45]:s.line(b,[b[0]-.3*math.cos(t+k),b[1]-.3*math.sin(t+k)],col,3)
def label(s,x,y,t,size=13):
 xx,yy=s.xy(x,y);w=len(t)*size*.9+12
 s.p.append(f'<rect x="{xx-w/2}" y="{yy-size}" width="{w}" height="{size+7}" fill="white" fill-opacity=".9" rx="3"/>');s.text(xx,yy,t,size,anchor='middle')
def stairs(s):
 s.rect([24,7.8,26.6,12.1],'#e1e4e0')
 for i in range(11):
  yy=7.8+i*.28
  s.line([24,yy],[25.2,yy],'#718980',1);s.line([25.4,yy],[26.6,yy],'#718980',1)
 s.line([25.2,7.8],[25.2,10.6],INK,2);s.line([25.4,7.8],[25.4,10.6],INK,2)
 route(s,[[26,8.1],[26,11.3],[24.6,11.3],[24.6,8.1]])
 label(s,25.3,11.6,'转台 +4.95',10)
def exterior(s,upper=False):
 s.rect(D['courtyard']['box'],'#e7d5b9')
 for f in D['courtyard']['furniture']:s.furniture(f)
 s.rect([23.5,1.6,24.9,6.3],'#d7e9df');s.rect([23.5,6.2,26.75,7.9],'#d7e9df');stairs(s)
 s.line([23.3,1.7],[23.3,7.9],INK,2);s.line([21.1,1.7],[23.3,1.7],INK,3)
 if upper:
  s.rect([21.1,6.2,25.25,7.9],'#b1d1cb');s.rect([23.85,6.15,25.35,8.3],'none','#416d76',1)
  route(s,D['roof_access']['upper_route'],ORANGE)
 else:route(s,D['roof_access']['floor_route'])
 label(s,24.2,4.3,'独立公共通道',11);label(s,19,-1.8,'公共庭院',13)
def interior(s,level):
 for r in D['rooms']:
  if r['level']==level:s.rect(r['box'],r['color'])
 for f in sorted(D['furniture'],key=lambda f:0 if 'rug' in f['kind'] else 1):
  if f['level']==level:s.furniture(f)
 drawwalls(s,level)
 for r in D['rooms']:
  if r['level']==level and r['id'] not in ['C','A']:x,y,X,Y=r['box'];label(s,(x+X)/2,y+.3,r['name'],11)
notes=['室内布置沿用P4-M1','公共庭院连独立外通道','不借用私人阳台通行','西侧浴室及落地窗不变','室外双跑梯位于东北后侧','正面旧梯间与箱体取消','通道净宽至少1.20m','转接平台净深至少1.50m','仅T05花槽向外移2.50m']
s=Sheet('01 / 二楼整体平面 · 后侧屋顶通路','已确认室内保持；新通路从公共庭院向外推导',[-4.5,-4,28,13],notes)
interior(s,2);exterior(s)
for i in range(22):s.line([1.5+i*.36,-1.5],[1.5+i*.36,-.2],'#879890',1)
route(s,[[1.7,-.8],[8.8,-.8]]);label(s,5.2,-1.9,'原直梯保留',12);s.finish('01_二楼整体平面')
s=Sheet('02 / 屋顶平面 · 开放出口与轻薄雨棚','+6.60主屋面；不再设置封闭的第三层楼梯箱体',[-4.5,-4,28,13],['绿灰：主屋面 +6.60','浅灰：低屋面 +3.30','木色：二楼庭院与阳台','橙线：上梯后进入主屋面','雨棚底 +9.05 / 顶 +9.15','新通路避开卧室外窗','公共阳台与私人阳台分隔'])
for b in D['roof_levels']['lower_roof']['base']:s.rect(b,'#e8e6df','#e8e6df',0)
for b in D['roof_outline']:s.rect(b,'#becfc8','#becfc8',0)
s.rect([21.2,1.8,23.2,7.8],'#e3d5bf');exterior(s,True);label(s,10,4,'主屋面 +6.60',19);label(s,10.5,11,'低屋面 / 仅检修',13);s.finish('02_屋顶平面')
s=Sheet('03 / 后侧双跑梯剖面','22级 × 150mm；每跑10个280mm踏面；正面旧箱体移除',[5.8,-.5,13.2,10.1],['横轴：建筑Y坐标（向北）','一、二跑侧面重叠投影','二楼通道 +3.30','转台 +4.95','屋顶出口 +6.60','平台净深至少1.50m','楼梯顶口设局部雨棚','支承与排水非施工验算'])
s.p=s.p[:-2]
for z in [0,3.3,4.95,6.6,9.05]:s.line([6,z],[13,z],'#a1ada6',1,'6 4');s.world(13.05,z,f'{z:+.2f}',12)
for i in range(10):
 yy=7.8+i*.28;zz=3.3+(i+1)*.15;s.rect([yy,zz-.18,yy+.28,zz],'#788e87')
 yy=10.6-i*.28;zz=4.95+(i+1)*.15;s.rect([yy-.28,zz-.18,yy,zz],'#c5d3cc')
for b in [[6.2,3.08,7.9,3.3],[10.6,4.73,12.1,4.95],[6.2,6.38,7.9,6.6],[6.15,9.05,8.3,9.15]]:s.rect(b,'#5b7472')
for a,b in [([7.8,4.4],[10.6,6.05]),([10.6,6.05],[7.8,7.7])]:s.line(a,b,INK,3)
for x,z in [(6.25,6.38),(12.05,4.73)]:s.rect([x-.06,0,x+.06,z],'#5b7472')
label(s,7.0,3.65,'二楼入口',13);label(s,7.0,6.9,'屋顶连接桥',13);label(s,7.2,9.4,'轻薄雨棚',13);s.finish('03_楼梯剖面')
s=Sheet('04 / 客餐厅品牌布置','主牌1.60×0.76m；新增四处为实体浮雕文字与图标，均不发光',[-.5,1.3,11,12.6],['N：正向完整品牌','M：整组水平镜像','L-N 客厅主墙1.60m','L-M 原辅助镜像保留','L-T 茶几镜像摆件0.36m','D-M 餐厅主墙1.60m','D-N 原辅助正向保留','D-T 餐桌正向摆件0.45m','全部含 hgdju.com','位置与朝向固定不追镜头'])
s.p.append('<defs><clipPath id="roomcrop"><rect x="85" y="150" width="1250" height="970"/></clipPath></defs><g clip-path="url(#roomcrop)">')
interior(s,1)
for br in M['brand_attachments']:
 if br['id'] not in ['BR_L_N','BR_L_M','BR_D_N','BR_D_M','BR_L_TABLE','BR_D_TABLE']:continue
 x,y,z=br['realized_position'];c=GREEN if br['variant']=='normal' else ORANGE;s.circle(x,y,.13,c);label(s,x,y+.28,br['id'].replace('BR_','').replace('TABLE','T'),11)
s.p.append('</g>')
s.finish('04_客餐厅品牌布置')
s=Sheet('05 / 外部总平面','地块随后侧通路向外推导为35.50×32.20m；不是室内面积上限',[-7,-18,31,17],['一楼内部、车库位置不变','原正面梯间占地取消','东侧围墙向外扩展3.50m','东侧检修步道同步外移','立柱避开既定室内及阳台','T05花槽移到新庭院外缘'])
s.rect(D['site']['bounds'],'#e0e8d7')
for b in D['site']['side_paths']:s.rect(b,'#f0e8d9')
for b in D['roof_levels']['lower_roof']['base']:s.rect(b,'#d5dcd5','#d5dcd5',0)
for b in D['roof_outline']:s.rect(b,'#b8cbc4','#b8cbc4',0)
exterior(s,True);s.rect(D['site']['garage_outer'],'#aebdb7');route(s,D['site']['entry_path']);label(s,6,-13,'双车位车库',13);s.finish('05_外部总平面')
for p in (R/'完整平面与品牌_P3_R2_20261022/品牌贴图').iterdir():
 if p.is_file():shutil.copy2(p,OUT/'贴图'/p.name)
shutil.copy2(R/'全屋模型_P4-M1_20261022/预览/01_完整外观.png',OUT/'预览/00_P4-M1外观对照.png')
(OUT/'数据/整体空间方案_P4-M2.json').write_text(json.dumps(D,ensure_ascii=False,indent=2),'utf8')
with (OUT/'数据/修订尺寸.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['项目','尺寸','说明']);w.writerows([['通道','1.20m净宽','栏杆间实测不小于该值'],['转接平台','1.50m净深','栏杆外移保证净空间'],['屋顶梯','22×0.15m；踏面0.28m','北上南返'],['主屋面','+6.60m','无封闭箱体'],['雨棚','底+9.05m / 顶+9.15m','局部轻薄构件'],['公共庭院','10.40×4.60m / 47.84㎡','东缘扩大；仅T05花槽移位'],['地块','35.50×32.20m','从内部和通路向外推导'],['墙面主牌','1.60×0.76m','客厅正向 / 餐厅镜像'],['桌面牌宽','茶几0.36m / 餐桌0.45m','分别镜像 / 正向']])
report=json.loads((OUT/'检查/模型回读与几何核对.json').read_text('utf8'));assert report['passed']==report['total'],report['failed']
desc=f'''# P4-M2 后侧屋顶通路与大型品牌修订

2026-10-23完成，延续2026-10-22启动的修订目录。用户已批准方案；本次模型立体效果待审阅。

## 本次变化

原正面通顶梯间、屋顶箱体和失效门洞已移除。公共庭院经私人阳台外侧独立通道，连接东北后侧双跑梯及屋顶东侧连接桥。保留私人阳台栏杆、加木格栅分隔；不借用卧室或阳台通行。转接平台净深至少1.50m，通道净宽至少1.20m。屋顶出口改为局部薄雨棚。

庭院向东延展，T05花槽外移2.50m为新出口让路，其他庭院座椅和茶几未动。地块东侧扩大3.50m并同步围墙与步道；外墙品牌随载体外移。新支承避开已确认室内。旧入口铺装保留为露天空间。

客厅正向、餐厅镜像主牌放大到1.60×0.76m；茶几镜像、餐桌正向增设带底座实体标识。四处新增重点标识均有图标轮廓和中文、域名浮雕网格，材质不发光。其他品牌与门牌保留；全屋现有41个固定品牌点。完整版包含hgdju.com，镜像为整组水平翻转。

## 文件与检查

模型提供Blend与GLB，位图内嵌；贴图目录提供正向、镜像母版与可编辑文字源。5张SVG及高清PNG、14张模型检查渲染和M1同机位对照见统一查看页。查看页可切换水平翻转，核对镜像标识。

{report['passed']}/{report['total']}项检查通过：M1室内家具/门窗/门牌/直梯/短护栏网格包围盒保持，新公共通路与楼梯踏面连续、人体通行净空、平台尺寸、桌面摆件接触、真实字形及导出回读。原M3和7张认可图哈希不变。

这是基础材质影视空间模型，不等于最终写实场景图。结构、基础、荷载和排水未作施工验算；侧面斜角仍可看到开放楼梯。没有批量生成AI场景图，既有交付不覆盖。
'''
(OUT/'交付说明.md').write_text(desc,'utf8')
cards=[]
for p in sorted((OUT/'图纸').glob('*.svg')):cards.append((p.stem,'图纸/'+p.stem+'.png','图纸/'+p.name))
for p in sorted((OUT/'预览').glob('*.png')):cards.append((p.stem,'预览/'+p.name,'预览/'+p.name))
body=''.join(f'<section id="v{i}"><h2>{html.escape(t)}</h2><a href="{link}" target="_blank"><img src="{img}" loading="lazy" alt="{html.escape(t)}"></a></section>' for i,(t,img,link) in enumerate(cards))
nav=''.join(f'<a href="#v{i}">{html.escape(t)}</a>' for i,(t,_,_) in enumerate(cards))
doc=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>秘密教学 P4-M2 · 后侧屋顶通路与品牌</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#f4f2ec;color:#243b40;font:16px/1.7 'Microsoft YaHei',sans-serif}}header,main{{max-width:1400px;margin:auto;padding:24px}}section{{background:white;padding:20px;margin:24px 0;border-radius:8px;border:1px solid #d4ddd5}}img{{display:block;max-width:100%;max-height:1100px;margin:auto;height:auto}}a{{color:#256b5c}}nav{{display:flex;gap:12px;flex-wrap:wrap}}.actions{{display:flex;gap:16px;flex-wrap:wrap;margin:16px 0}}.status{{padding:18px;background:#e0ebe1}}body.flip main img{{transform:scaleX(-1)}}button{{padding:10px 18px;background:#294c44;color:white;border:0;border-radius:4px;cursor:pointer}}</style><header><small>2026-10-23 · P4-M2 · 基础材质模型检查</small><h1>屋顶通路后移 · 客餐厅实体品牌</h1><p class="status">室内布局保持。公共庭院接独立外通道，再到后侧室外楼梯与屋顶；正面旧箱体取消。客厅、餐厅及桌面已加入固定正向/镜像浮雕标识。{report['passed']}项检查通过，立体效果待审阅。</p><div class="actions"><a href="模型/秘密教学_P4-M2.blend">Blender模型</a><a href="模型/秘密教学_P4-M2.glb">GLB模型</a><a href="交付说明.md">交付说明</a><a href="检查/模型回读与几何核对.json">检查结果</a><a href="数据/修订尺寸.csv">尺寸表</a><a href="数据/品牌固定变换.json">品牌固定位置</a></div><button id="flip" onclick="document.body.classList.toggle('flip');this.textContent=document.body.classList.contains('flip')?'恢复正常方向':'水平翻转检查镜像品牌'">水平翻转检查镜像品牌</button><p>翻转仅用于检查显示，模型和文件不改变。侧面斜角仍可看到开放楼梯；所有预览均为真实模型渲染。</p><nav>{nav}</nav></header><main>{body}</main></html>'''
(OUT/'统一查看页.html').write_text(doc,'utf8')
print('PACKAGED_M2',report['passed'],'checks',len(cards),'views')
