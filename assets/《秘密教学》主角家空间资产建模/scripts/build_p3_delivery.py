"""P3: furniture-first floor plans and fixed brand asset source. No M3 mutation."""
from pathlib import Path
import json, math, copy, html, hashlib, base64, csv
R=Path(__file__).resolve().parents[1]
OUT=R/'完整平面与品牌_P3_R2_20261022'
for s in ['图纸','数据','品牌贴图','独立模型','检查','参考']:(OUT/s).mkdir(parents=True,exist_ok=True)
OLD=json.loads((R/'白模当前/模型/建模方案.json').read_text(encoding='utf-8'))
F0={f['id']:f for f in OLD['furniture']}
D=dict(revision='P3-R2-20261022',status='C02同步对齐C01床尾；待用户平面验收；未回写M3',units='m',rooms=[],furniture=[],walls=[],openings=[],stairs=[],brands=[],cameras=[],clearances=[],routes=[],unresolved=[])
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def room(id,name,level,b,color='#e9efeb',source='P3设计新增'):
 d=dict(id=id,name=name,level=level,box=b,color=color,net_area=round((b[2]-b[0])*(b[3]-b[1]),3),source=source);D['rooms'].append(d);return d
def fur(id,roomid,level,b,name=None,kind=None,head=None):
 f=copy.deepcopy(F0.get(id,dict(id=id,color='#becabf',kind=kind or 'cabinet',head=head)))
 f.update(room=roomid,level=level,box=[round(v,3) for v in b]);
 if name:f['name']=name
 if kind:f['kind']=kind
 if head:f['head']=head
 D['furniture'].append(f);return f
def wall(id,level,a,b):D['walls'].append(dict(id=id,level=level,a=a,b=b,thickness=.2))
def rectwalls(r):
 x,y,X,Y=r['box'];i=r['id'];l=r['level']
 for s,a,b in [('S',[x-.1,y-.1],[X+.1,y-.1]),('N',[x-.1,Y+.1],[X+.1,Y+.1]),('W',[x-.1,y-.1],[x-.1,Y+.1]),('E',[X+.1,y-.1],[X+.1,Y+.1])]:wall(i+s,l,a,b)
def opening(id,w,start,end,type='door',side=1):
 wa=next(x for x in D['walls'] if x['id']==w)
 D['openings'].append(dict(id=id,wall=w,level=wa['level'],start=start,end=end,type=type,sill=.6 if type=='window' else 0,head=2.8 if type!='door' else 2.2,side=side))
def clear(id,roomid,b):D['clearances'].append(dict(id=id,room=roomid,box=b,purpose='使用空间；非家具实体'))
# 1. Independent interiors: all coordinates below are local, before corridor/site design.
local_b1={'A01':[.2,3.1,4.1,5.62],'A02':[.4,2.4,1,3],'A03':[0,1,.4,2.4],
 'A04':[4.3,5.35,6.1,6],'A05':[4.85,4.15,5.45,4.75],'A06':[7,4.65,7.6,5.95],
 'A07':[6.05,4.8,6.6,5.35],'A08':[7.4,3.4,7.6,4.15],'A09':[4.3,0,6.0,.6],
 'A10':[3.3,1.0,5.8,3.5],'A11':[6.4,.15,7.15,1.45],'A12':[.9,1.5,1.6,2.2],'A13':[2.3,.1,3.4,1.2]}
local_b3={'C01':[6.2,0,7.7,2.2],'C02':[6.6,2.4,7.3,3],'C03':[2.55,0,4.55,.65],
 'C04':[3.2,1.05,3.8,1.65],'C05':[2.2,5.75,4.5,6.2],'C06':[0,1.6,.65,5.6],
 'C07':[0,.7,.18,1.3],'C08':[2.2,2.5,5,5.3],'C09':[4.7,0,5.15,.6]}
local_b2={f['id']:[round(f['box'][0]-9.2,3),round(f['box'][1]-4.4,3),round(f['box'][2]-9.2,3),round(f['box'][3]-4.4,3)] for f in OLD['furniture'] if f['room']=='B2'}
local_b2['B12']=[2.75,0,3.5,.55] # entry cabinet clears the newly specified door swing
local_dims={'B3':[max(b[2] for b in local_b3.values()),max(b[3] for b in local_b3.values())],
 'B2':[max(b[2] for b in local_b2.values()),max(b[3] for b in local_b2.values())],
 'B1':[max(b[2] for b in local_b1.values()),max(b[3] for b in local_b1.values())]}
offsets={'B3':[0,1.8]};offsets['B2']=[local_dims['B3'][0]+.2,1.8];offsets['B1']=[offsets['B2'][0]+local_dims['B2'][0]+.2,1.8]
for id,name,local,col in [('B3','舒亚卧室',local_b3,'#e4e8f0'),('B2','子豪卧室',local_b2,'#e6eddf'),('B1','薇亚卧室',local_b1,'#f3e2e7')]:
 ox,oy=offsets[id];w,h=local_dims[id];rr=room(id,name,2,[ox,oy,ox+w,oy+h],col,'家具布置推导；M3只用于未改变家具尺寸');rectwalls(rr)
 for fid,b in local.items():fur(fid,id,2,[b[0]+ox,b[1]+oy,b[2]+ox,b[3]+oy])
furbed=next(f for f in D['furniture'] if f['id']=='A01');furbed.update(name='大床 / 按用户定位延长，床宽保持',revision_note='R1床长3.90m、宽2.52m；床尾距电脑桌左边0.20m；取代本轮初稿等比1.20方案')
opening('D_B3','B3S',.9,1.8);opening('D_B2','B2S',offsets['B2'][0]+1.25,offsets['B2'][0]+2.25)
opening('D_B1','B1S',offsets['B1'][0]+.2,offsets['B1'][0]+1.1)
for id,localwin in [('B3',[(2.2,5.4)]),('B2',[(1.2,4.4)]),('B1',[(.35,2.95),(4.15,6.25)])]:
 for n,(a,b) in enumerate(localwin):opening('W_'+id+str(n),id+'N',offsets[id][0]+a,offsets[id][0]+b,'window')
opening('G_BALCONY','B1E',3.45,4.75,'glass')
for id,b in [('B1-床南侧',[1,2.2,4.1,3.1]),('B1-床尾南段',[4.1,3.1,4.85,4.05]),('B1-衣柜前',[4.3,.6,6,1.5]),('B1-阳台通路',[5.8,1.65,7.6,2.95]),('B1-书桌椅后',[4.3,3.25,5.65,4.15]),('B1-镜前',[6.4,3.4,7.4,4.15])]:
 ox,oy=offsets['B1'];clear(id,'B1',[b[0]+ox,b[1]+oy,b[2]+ox,b[3]+oy])
clear('B3-床左通路','B3',[4.55,2.45,5.4,4]);clear('B3-衣架前','B3',[.65,3.4,1.55,7.3]);clear('B3-椅后','B3',[2.55,3.45,4.55,4.3])
# 2. Fit shared circulation to the interiors, never the reverse.
hall_end=round(offsets['B1'][0]+1.7,3)
room('H2','二楼公共走廊',2,[0,0,hall_end,1.6],'#edf2e9','按三房入口连接后确定')
room('C','舒亚端二楼收头',2,[0,-1.5,1.5,0],'#edf2e9','保留短端部地面/落地窗关系')
room('A','上平台及端部通路',2,[9.06,-1.5,hall_end,0],'#edf2e9','直梯上平台延展接全屋；尺寸为新设计')
wall('H_W',2,[-.1,-1.6],[-.1,1.7]);wall('H_E',2,[hall_end+.1,-1.6],[hall_end+.1,1.7]);wall('H_S',2,[-.1,-1.6],[hall_end+.1,-1.6]);wall('GUARD',2,[1.5,-.1],[9.06,-.1])
opening('G_BATH','H_W',.2,1.4,'glass');opening('W_SHUYA_OPPOSITE','H_S',.15,1.4,'window');opening('W_STAIR_STRIP','H_S',1.95,8.65,'window');opening('W_PLATFORM_SIDE','H_S',9.35,10.35,'window');opening('W_PLATFORM_END','H_E',-1.45,1.45,'window')
for o in D['openings']:
 if o['id'] in ['W_SHUYA_OPPOSITE','W_PLATFORM_SIDE','W_PLATFORM_END']:o['sill']=.03
 if o['id']=='W_STAIR_STRIP':o.update(sill=.65,head=1.25)
stairs=dict(id='ST12',from_level=1,to_level=2,footprint=[1.5,-1.5,9.06,-.2],rises=22,rise=.15,treads=21,tread=.36,width=1.3,direction='+X',floor_height=3.3,opening=[1.5,-1.5,9.06,-.2],guard_height=1.1)
D['stairs'].append(stairs)
bath=room('BW','公共浴室',2,[-3.7,-1.5,-.2,1.6],'#deedf0','V3设施关系；入口使用用户确认玻璃门');rectwalls(bath)
# shared east wall is H_W; remove duplicate so door renders once.
D['walls']=[w for w in D['walls'] if w['id']!='BWE']
fur('BW1','BW',2,[-1.65,-1.5,-.25,-.9],'台盆','sink');fur('BW2','BW',2,[-3.7,-1.5,-2.4,-.2],'玻璃淋浴区','shower');fur('BW3','BW',2,[-3.3,.65,-2.5,1.4],'坐便','wc')
opening('W_BATH','BWW',-.05,1.3,'window');clear('BW-入口与转身','BW',[-2.25,-.7,-.3,.6]);clear('BW-坐便前','BW',[-2.5,.6,-1.6,1.4])
# Roof access is a separate annex off the large upper landing, leaving the straight flight and its windows intact.
rs=room('RS','通顶楼梯间',2,[10.6,-6.1,14.6,-1.8],'#e8e5ee','本轮授权设计：公共上平台旁双跑楼梯');rectwalls(rs)
opening('D_ROOF_ACCESS','H_S',13.4,14.4);opening('D_RS_ENTRY','RSN',13.4,14.4)
D['stairs'].append(dict(id='ST23',from_level=2,to_level=3,footprint=[10.8,-5.9,13.4,-2.1],rises=22,rise=.15,treads_per_flight=10,tread=.28,width=1.2,landing_depth=1.0,floor_height=3.3,opening=[10.8,-5.9,13.4,-2.1],direction='U',clear_height=2.2))
room('RS3','屋顶出入口小房子',3,[10.6,-6.1,14.6,-1.8],'#e3e7eb','灰色体量参考V3，位置由楼梯路线推导')
room('BAL','大姐阳台',2,[21.2,1.8,23.2,7.8],'#dce6da','宽度由室内阳台通路向外安排')
# 3. Ground-floor retained interiors translated as intact blocks, with new public front gallery.
for r in OLD['rooms']:
 if r['level']!=1 or r['id']=='B':continue
 rr=copy.deepcopy(r);rr['box']=[r['box'][0],r['box'][1]+1.8,r['box'][2],r['box'][3]+1.8];rr['source']='M3一楼内部关系整块保留；向北平移1.8m接公共通路';D['rooms'].append(rr)
for f in OLD['furniture']:
 if f['level']==1:fur(f['id'],f['room'],1,[f['box'][0],f['box'][1]+1.8,f['box'][2],f['box'][3]+1.8])
for w in OLD['walls']:
 if w['level']==1 and w['id'] not in ['1-STN','1-STS','1-STA']:
  ww=copy.deepcopy(w);ww['a'][1]+=1.8;ww['b'][1]+=1.8;D['walls'].append(ww)
for o in OLD['openings']:
 if o['level']==1 and o['wall'] not in ['1-STN','1-STS','1-STA']:
  oo=copy.deepcopy(o);w=next(w for w in OLD['walls'] if w['id']==o['wall'])
  if w['a'][0]==w['b'][0]:oo['start']+=1.8;oo['end']+=1.8
  D['openings'].append(oo)
room('F1H','一楼连接通路',1,[0,0,22,1.8],'#edf2e9','新楼梯下平台接玄关和公共区')
room('B','一楼下平台',1,[0,-1.5,1.5,0],'#edf2e9','位于C平台下方；接一楼公共通路')
room('SUP','浴室下方设备/支承预留',1,[-3.7,-1.5,-.2,1.8],'#eee9df','设计新增；不冒充漫画原有房间')
wall('F1H_S',1,[0,-.1],[22,-.1]);opening('D_MAIN_NEW','F1H_S',10.0,11.4)
opening('D_STAIR_EXIT','F1H_S',.2,1.3)
# 4. Exterior follows the union of interior requirements.
D['site']=dict(building_bounds=[-3.9,-6.3,23.4,12.2],bounds=[-5.9,-16.6,25.6,15.2],garage_outer=[4.5,-16.6,16.5,-10.8],garage_net=[4.7,-16.4,16.3,-11.0],front_garden_depth=4.5,path_width=1.4,pedestrian_gate=[20.3,21.9],source='从房间与楼梯间最外边界向外推导；非旧地块限额')
D['roof_outline']=[[-3.9,-1.7,0,1.8],[0,-1.7,22,12.2],[10.4,-6.3,14.8,-1.7],[21,1.6,23.4,8]]
D['routes']=[dict(id='R12',level=1,points=[[10.7,-.8],[10.7,.8],[.75,.8],[.75,-.8],[1.5,-.8],[9.06,-.8]],note='一楼入口→公共通路→下平台→直梯'),dict(id='R2',level=2,points=[[9.06,-.8],[10,-.8],[10,.8],[.6,.8]],note='上平台→三房走廊→浴室'),dict(id='R23',level=2,points=[[10,-.8],[13.9,-.8],[13.9,-2.3],[12.8,-2.3],[12.8,-5.4],[11.4,-5.4],[11.4,-2.3]],note='公共上平台→新增双跑楼梯→屋顶')]
D['unresolved']=['本版为内部先行设计稿，尺寸及新外轮廓待用户验收；不是施工图。','二姐V3俯拍含额外门，与正面参考不一致；采用正面单入口关系，不新增该门。','浴室玻璃门暂按双扇推拉表达，具体门框、五金需近景参考校准。','一楼既有内部布局保持；新增公共连接通路及浴室下方设备/支承区域属于设计新增。','新增屋顶楼梯间与外挑区域的结构支承、防水和管线尚未进行工程设计。','固定品牌布置已设计；全屋材质模型及其镜面反射、最终机位遮挡须在后续整模中验证。']
D['design_order']=['摆放各房间家具','留使用通路','家具包络推导房间尺寸','拼合房间并连接走廊','安排上下楼路线','推导建筑外轮廓','推导地块与花园']
D['authorization_updates']=['2026-10-22 用户允许重新安排三间卧室门距并延展走廊，内部布局正确优先。','床等比例调整，其余既有家具尺寸不变。','公共浴室沿用V3内部；二姐布局本轮修正；屋顶小房子可合理设计。']
D['authorization_updates'].append('R1最新图示：子豪门移至x38.5%位置；大姐床向电脑桌延长且宽度暂保持；二姐床贴右墙；入口小柜移开门扇。')
D['authorization_updates'].append('R2：C02床尾小书架随C01贴墙后的床位向右平移0.80m，横向中心对齐床尾；尺寸0.70×0.60m及床尾间距0.20m保持。')
dump(OUT/'数据/空间方案_P3.json',D)
dump(OUT/'数据/房间独立布局.json',dict(order='先家具后房间；以下不含走廊或地块约束',local_furniture={'B1':local_b1,'B2':local_b2,'B3':local_b3},derived_dimensions=local_dims,assembly_offsets=offsets))

# SVG plans, shared data and a readable room/furniture key.
INK='#243b40'; GREEN='#38796c'; ORANGE='#b36c31'
class Sheet:
 def __init__(self,title,sub,bounds,notes=None):
  self.W=1800;self.H=1240;self.bounds=bounds;self.scale=min(1240/(bounds[2]-bounds[0]),900/(bounds[3]-bounds[1]));self.ox=90-bounds[0]*self.scale;self.oy=1080+bounds[1]*self.scale
  self.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1240" viewBox="0 0 1800 1240"><style>text{{font-family:"Microsoft YaHei",sans-serif;fill:{INK}}}</style><rect width="1800" height="1240" fill="#f8f7f2"/>']
  self.text(65,65,title,32,weight=700);self.text(65,105,sub,17)
  self.p.append('<path d="M65 126H1735" stroke="#bccbc1"/>');self.text(65,1190,'P3-R2 · 2026-10-22    先家具 → 内部范围 → 楼层整合 → 外轮廓    |    影视空间设计稿 · 待验收',17)
  self.text(1430,165,'图纸说明',23,weight=700)
  for i,line in enumerate(notes or []):self.text(1430,207+i*29,line,16)
  self.line([bounds[2]-.8,bounds[3]-1.8],[bounds[2]-.8,bounds[3]-.6],GREEN,3);self.world(bounds[2]-.8,bounds[3]-.4,'N',18)
 def xy(self,x,y):return self.ox+x*self.scale,self.oy-y*self.scale
 def text(self,x,y,s,size=16,color=None,weight=400,anchor='start'):
  self.p.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}"'+(f' style="fill:{color}"' if color else '')+'>'+html.escape(str(s))+'</text>')
 def world(self,x,y,s,size=16,**kw):self.text(*self.xy(x,y),s,size,**kw)
 def line(self,a,b,color=INK,width=2,dash=None):
  x,y=self.xy(*a);X,Y=self.xy(*b);self.p.append(f'<path d="M{x:.2f},{y:.2f} L{X:.2f},{Y:.2f}" fill="none" stroke="{color}" stroke-width="{width}"'+(f' stroke-dasharray="{dash}"' if dash else '')+'/>')
 def rect(self,b,fill='none',stroke='#899a95',width=1,rx=0):
  x,y=self.xy(b[0],b[3]);self.p.append(f'<rect x="{x:.2f}" y="{y:.2f}" width="{(b[2]-b[0])*self.scale:.2f}" height="{(b[3]-b[1])*self.scale:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" rx="{rx}"/>')
 def circle(self,x,y,r,fill):
  xx,yy=self.xy(x,y);self.p.append(f'<circle cx="{xx}" cy="{yy}" r="{r*self.scale}" fill="{fill}" stroke="#819088"/>')
 def dim(self,b):
  x,y,X,Y=b;self.line([x,y-.25],[X,y-.25],ORANGE,1);self.world((x+X)/2,y-.55,f'{X-x:.2f} m',15,anchor='middle',color=ORANGE)
  self.world(X+.15,(y+Y)/2,f'{Y-y:.2f} m',14,color=ORANGE)
 def furniture(self,f,detail=False):
  b=f['box'];x,y,X,Y=b;k=f['kind'];c=f.get('color','#c8d0c3');cx=(x+X)/2;cy=(y+Y)/2
  if k in ['circle','roundrug','trampoline']:self.circle(cx,cy,min(X-x,Y-y)/2,c)
  else:self.rect(b,c,'#8b9993',1,3)
  if k=='bed':
   hd=f.get('head');p=[x+.08,y+.08,x+.45,Y-.08] if hd=='W' else [X-.45,y+.08,X-.08,Y-.08] if hd=='E' else [x+.08,y+.08,X-.08,y+.4] if hd=='S' else [x+.08,Y-.4,X-.08,Y-.08];self.rect(p,'#f5f2e9')
  if k=='desk':self.rect([cx-.18,cy-.06,cx+.18,cy+.06],'#536a70')
  if k=='shower':self.line([X,y],[X,Y],'#3f9eb4',3);self.line([x,Y],[X,Y],'#3f9eb4',3)
  if k not in ['rug','roundrug','starrug']:self.world(cx,cy-.05,f['id'],14 if detail else 10,anchor='middle')
 def finish(self,name):
  self.p.append('</svg>');(OUT/'图纸'/f'{name}.svg').write_text('\n'.join(self.p),encoding='utf-8')
def drawwalls(s,level,roomids=None):
 for w in D['walls']:
  if w['level']!=level:continue
  if roomids and not any(w['id'].startswith(i) for i in roomids) and not ('BW' in roomids and w['id']=='H_W'):continue
  a,b=w['a'],w['b'];hor=a[1]==b[1];lo=a[0] if hor else a[1];hi=b[0] if hor else b[1];fixed=a[1] if hor else a[0]
  pt=lambda t:[t,fixed] if hor else [fixed,t]
  ops=sorted([o for o in D['openings'] if o['wall']==w['id']],key=lambda o:o['start']);cur=lo
  for o in ops+[dict(start=hi,end=hi,type='end')]:
   if o['start']>cur:s.line(pt(cur),pt(o['start']),'#40585c',max(3,.13*s.scale))
   if o['type']=='end':break
   u,v=o['start'],o['end'];typ=o['type']
   if typ in ['glass','window']:
    s.line(pt(u),pt(v),'#319bb1',4)
    if typ=='glass':s.world(*pt((u+v)/2),'玻璃',10)
   else:
    # Hinge at start; room entries swing north/east. Site-to-annex doors swing south.
    side=-1 if o['id'] in ['D_ROOF_ACCESS','D_RS_ENTRY'] else o.get('side',1)
    end=[u,fixed+side*(v-u)] if hor else [fixed+side*(v-u),u]
    s.line(pt(u),end,'#937343',1.4);x,y=s.xy(*pt(v));X,Y=s.xy(*end);rr=(v-u)*s.scale
    s.p.append(f'<path d="M{x} {y} A{rr} {rr} 0 0 {1 if hor and side==1 else 0} {X} {Y}" fill="none" stroke="#a58d65" stroke-dasharray="4 3"/>')
   cur=max(cur,v)
def drawstairs(s,which):
 for st in D['stairs']:
  if st['id'] not in which:continue
  x,y,X,Y=st['footprint'];s.rect(st['footprint'],'#e4e6e1')
  if st['id']=='ST12':
   for i in range(22):s.line([x+i*.36,y],[x+i*.36,Y],'#8c9a94',1)
   s.line([x+.2,(y+Y)/2],[X-.2,(y+Y)/2],GREEN,3);s.world((x+X)/2,Y+.15,'直梯 ↑ 22×150 / 踏步360',13,anchor='middle')
  else:
   for i in range(11):
    yy=Y-i*.28;s.line([x,yy],[x+1.2,yy],'#8c9a94',1);s.line([X-1.2,yy],[X,yy],'#8c9a94',1)
   s.world((x+X)/2,y+.5,'折返平台',11,anchor='middle');s.world(x+.6,Y-.6,'↑',22);s.world(X-.6,Y-.6,'↓',22)
def floor_sheet(level,name,title):
 bounds=[-4.6,-6.9,24.7,13] if level==1 else [-4.6,-6.9,24.7,10]
 s=Sheet(title,'尺寸由家具与通行空间推导；所有数值为本版设计结果',bounds,['蓝色：窗 / 玻璃门','深线：墙体 / 护栏','浅绿色：公共通路','家具编号对应尺寸表','新外轮廓不限制室内','','三房门距按内部重排','走廊长度随入口确定','原M3文件未修改'])
 for r in D['rooms']:
  if r['level']==level:s.rect(r['box'],r['color']);x,y,X,Y=r['box'];s.world((x+X)/2,(y+Y)/2,r['name'],14,anchor='middle')
 for f in sorted(D['furniture'],key=lambda f:0 if 'rug' in f['kind'] else 1):
  if f['level']==level:s.furniture(f)
 drawwalls(s,level);drawstairs(s,['ST12'] if level==1 else ['ST12','ST23']);s.finish(name)
floor_sheet(1,'01_一楼家具平面','01 / 一楼内部家具与公共连接')
floor_sheet(2,'02_二楼家具平面','02 / 二楼内部布局与公共浴室')
def detail(id,name,title,notes):
 r=next(r for r in D['rooms'] if r['id']==id);x,y,X,Y=r['box'];s=Sheet(title,f"净尺寸 {X-x:.2f} × {Y-y:.2f} m  |  净面积 {r['net_area']:.2f} ㎡  |  先布置、后测算",[x-.8,y-.8,X+1,Y+.7],notes)
 s.rect(r['box'],r['color'])
 for c in D['clearances']:
  if c['room']==id:s.rect(c['box'],'#d7eadb','#75a185')
 for f in sorted(D['furniture'],key=lambda f:0 if 'rug' in f['kind'] else 1):
  if f['room']==id:s.furniture(f,True)
 drawwalls(s,2,[id]);s.dim(r['box']);line=560
 for f in D['furniture']:
  if f['room']==id:s.text(1430,line,f"{f['id']}  {f['name'].split('/')[0].strip()}",14);line+=27
 s.finish(name)
detail('B1','03_大姐卧室放大','03 / 薇亚卧室 · 家具优先扩展',['R1：床长3.90 / 宽2.52m','床尾距电脑桌左边0.20m','其他家具尺寸保持不变','床头西侧 / 书桌第二窗下','梳妆台 / 镜 / 阳台在东侧','浅绿：使用空间','面积为排布结果，非限额'])
detail('B3','04_二姐卧室放大','04 / 舒亚卧室 · 恢复参考次序',['R2：C02对齐C01床尾','小书架尺寸及间距保持','面向入口墙看：','左侧床 → 抽屉柜 → 书桌','→ 右侧入口','床头、书桌、门同墙','不采用俯拍图的额外门'])
detail('BW','05_公共浴室放大','05 / 公共浴室 · V3设施关系',['从走廊向内看：','左前台盆 / 左后淋浴','右后坐便 / 后墙窗','入口为浴室玻璃门','舒亚对面落地窗不变','推拉细节为设计暂定'])
# Roof/site and cross-level correspondence.
s=Sheet('06 / 屋顶平面与出屋面楼梯','屋顶小房子由公共楼梯落位；非完整第三层住宅',[-4.6,-6.9,24.7,13],['深灰体量：屋顶楼梯间','入口接公共上平台','原直梯继续只连接1—2层','新增双跑梯连接2—屋顶','屋面其余部分为检修通路','支承 / 防水需后续工程校核'])
for b in D['roof_outline']:s.rect(b,'#e7e9e2')
s.rect([10.6,-6.1,14.6,-1.8],'#65737b');drawstairs(s,['ST23']);s.line([11.4,-2.1],[11.4,.8],GREEN,4);s.world(11.4,1.1,'屋面出口',16,anchor='middle');s.finish('06_屋顶平面')
s=Sheet('07 / 楼梯纵剖与楼层对应','层高3.30m，板厚0.22m沿用暂定基线；洞口随楼梯确定',[-1,-1,19,9],['直梯：22级 × 0.15m','水平段：21步 × 0.36m','净宽：1.30m','通顶双跑：每跑11级','每跑10步 × 0.28m','净宽：1.20m','图中绿色为通行方向','洞口不放梁；梁底待设计'])
for z,label in [(0,'一楼 ±0.00'),(3.3,'二楼 +3.30'),(6.6,'屋顶 +6.60')]:s.line([0,z],[17.5,z],'#889b91',1,'8 6');s.world(17.6,z,label,14)
for i in range(22):
 x=1.5+i*.36;z=(i+1)*.15;s.line([x,z],[x+.36,z],INK,2);s.line([x,z-.15],[x,z],INK,2)
s.rect([0,3.08,1.5,3.3],'#c1c9c1');s.rect([9.06,3.08,15.1,3.3],'#c1c9c1');s.world(4,4.2,'直梯上方完整开洞',18)
for i in range(11):
 x=10.8+i*.28;z=3.3+(i+1)*.15;s.line([x,z],[x+.28,z],GREEN,2);s.line([x,z-.15],[x,z],GREEN,2)
for i in range(11):
 x=13.88-i*.28;z=4.95+(i+1)*.15;s.line([x,z],[x-.28,z],ORANGE,2);s.line([x,z-.15],[x,z],ORANGE,2)
s.world(10.7,7.5,'通顶双跑梯（展开示意）',17);s.world(1.5,.4,'下平台B',16);s.world(.1,3.6,'端部C',16);s.world(9.4,3.6,'上平台A',16);s.finish('07_楼梯剖面')
s=Sheet('08 / 总平面 · 从内到外推导','地块边界由新室内包络、通行与花园推导；不沿用旧面积限额',[-7,-18,27,17],['蓝灰：内部建筑包络','粉色：二楼卧室投影','深灰：通顶楼梯间','车库与建筑之间保留花园','花园最小纵深4.50m','步道宽1.40m','新增设计地块无现实用地约束'])
s.rect(D['site']['bounds'],'#dce5d2')
for b in D['roof_outline']:s.rect(b,'#e8ece5')
for r in D['rooms']:
 if r['level']==2 and r['id'] in ['B1','B2','B3','BW']:s.rect(r['box'],r['color']);x,y,X,Y=r['box'];s.world((x+X)/2,(y+Y)/2,r['name'],13,anchor='middle')
s.rect([10.6,-6.1,14.6,-1.8],'#7a8383');s.rect(D['site']['garage_outer'],'#c3c9c5');s.world(10.5,-13.4,'临街车库',18,anchor='middle')
s.rect([20.3,-16.6,21.7,-.1],'#e8e0cd');s.rect([10,-8.2,21.7,-6.8],'#e8e0cd');s.world(3,-8,'花园 / 步道',17);s.world(21,-17.1,'人行入口',15,anchor='middle');s.dim(D['site']['bounds']);s.finish('08_总平面')

# Brand placements: world-anchored, no billboard/look-at transform.
def brand(id,roomid,level,carrier,pos,normal,size,variant='normal',kind='art',light='none',main=True):
 D['brands'].append(dict(id=id,room=roomid,level=level,carrier=carrier,position=pos,normal=normal,size=size,variant=variant,kind=kind,light=light,main=main,master='HG_FULL_'+variant,domain='hgdju.com',fixed_to_carrier=True,camera_facing=False))
for id in ['B1','B2','B3','L','K','D','MB','MW','WC','LA','R','ST','E','SUP']:
 r=next(r for r in D['rooms'] if r['id']==id);x,y,X,Y=r['box'];z=(r['level']-1)*3.3
 # Existing wall/art/screen carriers; each room's master pair occupies different surfaces.
 brand('BR_'+id+'_N',id,r['level'],'已有墙面品牌画',[x+.02,(y+Y)/2,z+1.8],[1,0,0],[.72,.36],kind='art')
 brand('BR_'+id+'_M',id,r['level'],'已有柜面/屏幕或墙画',[X-.02,(y+Y)/2,z+1.65],[-1,0,0],[.60,.30],'mirror',kind='texture')
for b in D['brands']:
 if b['room']=='B1':
  if b['variant']=='normal':b.update(carrier='床头西墙品牌画',position=[13.42,6.15,5.2],size=[1.1,.55])
  else:b.update(carrier='东墙梳妆台上实体牌',position=[20.98,7.1,5.4],size=[1.2,.6],kind='plaque',light='backlight')
 if b['room']=='B2' and b['variant']=='normal':b.update(carrier='电视屏幕品牌壁纸',position=[7.92,4.1,4.7],size=[1.0,.5])
 if b['room']=='B3' and b['variant']=='normal':b.update(carrier='书桌上方原装饰墙',position=[3.55,1.82,5.1],normal=[0,1,0],size=[.8,.4])
brand('BR_BW_N','BW',2,'台盆上方墙画',[-1.0,-1.48,5.1],[0,1,0],[.6,.3])
brand('BR_BW_M','BW',2,'坐便侧墙装饰',[-2.9,1.58,5.1],[0,-1,0],[.6,.3],'mirror')
brand('BR_H2_N','H2',2,'卧室门之间品牌画',[12.4,1.68,5.15],[0,-1,0],[.8,.4])
brand('BR_H2_M','H2',2,'浴室侧端墙品牌画',[-.08,-.55,5.1],[1,0,0],[.6,.3],'mirror')
brand('BR_RS_N','RS',2,'楼梯间平台实物铭牌',[14.58,-3.3,5.1],[-1,0,0],[.6,.3],kind='plaque')
brand('BR_BAL_M','BAL',2,'阳台边柜小型牌',[22.0,7.75,4.2],[0,-1,0],[.45,.225],'mirror',kind='plaque')
brand('BR_EXT_N','EXT',1,'车库右侧入户墙实体霓虹牌',[18.5,-16.58,1.7],[0,-1,0],[1.6,.8],kind='neon',light='glyph_emission')
brand('BR_EXT_M','EXT',1,'庭院侧墙品牌画',[25.58,-8.5,1.8],[-1,0,0],[1.2,.6],'mirror',kind='plaque')
brand('BR_B1_STAND','B1',2,'床头柜立体摆件',[13.95,4.5,4.35],[1,0,0],[.22,.32],kind='sculpture',main=False)
brand('BR_B1_FABRIC','B1',2,'床尾织物局部印花',[16.0,6.15,4.0],[0,0,1],[.22,.22],kind='icon_texture',main=False)
for b in D['brands']:
 if b['kind'] in ['icon_texture','sculpture']:b['master']='HG_ICON';b['domain']=None
for r in D['rooms']:
 if r['id'] in ['B1','B2','B3','L','K','D','MB','BW','MW','WC','LA','R','ST']:
  x,y,X,Y=r['box'];z=(r['level']-1)*3.3+1.55
  for suffix,pos,target in [('EW',[x+.8,(y+Y)/2,z],[X,(y+Y)/2,z]),('WE',[X-.8,(y+Y)/2,z],[x,(y+Y)/2,z])]:D['cameras'].append(dict(id='CAM_'+r['id']+'_'+suffix,room=r['id'],position=pos,target=target,lens=24,aspect='9:16',status='固定布置覆盖预检机位；最终无遮挡渲染待整模'))
for level in [1,2]:
 s=Sheet(f'{8+level:02d} / {level}楼固定品牌布置','N 正向完整版 / M 整组镜像 / 小型图标附着物件；所有域名随完整母版固定',[-4.6,-6.9,24.7,13],['主元素：每空间少量设置','不同载体分担正反机位','不要求每镜出现Logo','不移动家具换取露出','N与M都包含 hgdju.com','房间门牌不做镜像','镜面反射由后续渲染验证'])
 for r in D['rooms']:
  if r['level']==level:s.rect(r['box'],r['color'])
 for f in D['furniture']:
  if f['level']==level:s.furniture(f)
 for b in D['brands']:
  if b['level']==level and b['room']!='EXT':
   x,y,z=b['position'];s.circle(x,y,.16,'#c79439' if b['variant']=='normal' else '#719d9c');s.world(x+.22,y+.07,b['id'].replace('BR_',''),11);nx,ny,_=b['normal'];s.line([x,y],[x+nx*.55,y+ny*.55],ORANGE,2)
 s.finish(f'{8+level:02d}_{level}楼品牌布置')
dump(OUT/'数据/空间方案_P3.json',D)
dump(OUT/'数据/品牌固定台账.json',D['brands']);dump(OUT/'数据/机位预检表.json',D['cameras'])
for file,rows,fields in [('房间尺寸.csv',D['rooms'],['id','name','level','box','net_area','source']),('家具尺寸.csv',D['furniture'],['id','name','room','box','kind']),('品牌覆盖.csv',D['brands'],['id','room','carrier','variant','position','normal','size','light','master'])]:
 with (OUT/'数据'/file).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
print(json.dumps(dict(out=str(OUT),rooms=len(D['rooms']),furniture=len(D['furniture']),brands=len(D['brands']),derived_dimensions=local_dims),ensure_ascii=False))
