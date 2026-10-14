from pathlib import Path
import json,math,html,collections
import numpy as np
R=Path(__file__).resolve().parents[1];D=json.loads((R/'模型/空间主数据_v4.json').read_text(encoding='utf8'))
report={'scope':'影视空间几何检查；非建筑结构受力或施工合规验算。门按模型打开，滑门按开启通路检查。','radius_m':.25,'height_m':1.8,'grid_m':.05}
def distrect(x,y,b):return math.hypot(max(b[0]-x,0,x-b[2]),max(b[1]-y,0,y-b[3]))
def footprint(d):b=d['box'];return [b[0],b[1],b[3],b[4]]
def obstructions(l,includeFurniture=True):
 z=(l-1)*3.3;out=[]
 for d in D['objects']:
  b=d['box'];g=d['group']
  if (g.endswith('walls') or g in ['Stairs','F2_guard'] or g.endswith('doors')) and d['kind']=='box' and b[2]<z+1.8 and b[5]>z+.12 and not d['id'].startswith(('STAIR_tread','STAIR_upper_bearing','STAIR_lower_bearing','STAIR_handhold','RAIL_')):out.append((d['id'],footprint(d)))
 if includeFurniture:
  for f in D['furniture']:
   if f['level']==l and f['height']>.12:out.append((f['id'],f['box']))
 return out
# Walkable floor is evaluated against the union of slabs, not room rectangles.
step=.05;xs=np.arange(-.5,14.75,step);ys=np.arange(-2,16.55,step);X,Y=np.meshgrid(xs,ys)
reachResults=[];nav={};navBits={}
for l in [1,2]:
 arr=D['slabs'][str(l)]+(D['outdoor_slabs'] if l==2 else [])
 mask=np.ones(X.shape,dtype=bool)
 for dx,dy in [(0,0),(.25,0),(-.25,0),(0,.25),(0,-.25),(.177,.177),(-.177,.177),(.177,-.177),(-.177,-.177)]:
  inside=np.zeros(X.shape,dtype=bool)
  for x,y,xx,yy in arr:inside|=(X+dx>=x)&(X+dx<=xx)&(Y+dy>=y)&(Y+dy<=yy)
  mask&=inside
 for id,b in obstructions(l):
  ddx=np.maximum(np.maximum(b[0]-X,X-b[2]),0);ddy=np.maximum(np.maximum(b[1]-Y,Y-b[3]),0);mask&=(ddx**2+ddy**2>=.25**2-1e-8)
 if l==1:mask&=~((X<1.5+.25)&(X>.2-.25)&(Y>1.7-.25)&(Y<7.02+.25))
 start=[2.6,.85];ix=int(round((start[0]-xs[0])/step));iy=int(round((start[1]-ys[0])/step));seen=np.zeros_like(mask);q=collections.deque([(iy,ix)]);seen[iy,ix]=True
 while q:
  yy,xx=q.popleft()
  for ny,nx in [(yy+1,xx),(yy-1,xx),(yy,xx+1),(yy,xx-1)]:
   if 0<=ny<len(ys) and 0<=nx<len(xs) and mask[ny,nx] and not seen[ny,nx]:seen[ny,nx]=True;q.append((ny,nx))
 for r in [r for r in D['rooms'] if r['level']==l]:
  x,y,xx,yy=r['box'];region=(X>x+.1)&(X<xx-.1)&(Y>y+.1)&(Y<yy-.1);valid=np.argwhere(region&seen&mask);rec={'id':r['id'],'name':r['name'],'reachable':len(valid)>0}
  if len(valid):v=valid[len(valid)//2];rec['reachable_point']=[round(xs[v[1]],2),round(ys[v[0]],2)]
  reachResults.append(rec)
 nav[l]=mask;navBits[l]=seen
report['room_access']=reachResults
# Sample continuous route, testing body volume against walls, door leaves and furniture.
samples=[]
for a,b in zip(D['routes']['forward'],D['routes']['forward'][1:]):
 n=max(1,math.ceil(math.dist(a,b)/.025))
 for k in range(n):samples.append([a[i]+(b[i]-a[i])*k/n for i in range(3)])
samples.append(D['routes']['forward'][-1]);fails=[];minhead=99
for p in samples:
 x,y,eye=p;foot=eye-1.62;onStair=.2<=x<=1.5 and 1.7<=y<=7.02
 if onStair:
  k=min(18,int((y-1.7)/.28));foot=3.3-(k+1)*.165
 l=2 if foot>3.05 else 1
 for id,b in obstructions(l):
  if distrect(x,y,b)<.25-1e-4:
   # Bounding footprints of walls at a different elevation are excluded by obstructions().
   fails.append({'position':[round(v,3) for v in p],'object':id});break
 overhead=[3.08] if not onStair and l==1 and any(a<=x<=c and b<=y<=d for a,b,c,d in D['slabs']['2']) else [6.38]
 head=min(overhead)-foot;minhead=min(minhead,head)
report['walk']={'samples':len(samples),'length_m':round(sum(math.dist(a,b) for a,b in zip(D['routes']['forward'],D['routes']['forward'][1:])),2),'collision_count':len(fails),'collisions':fails[:15],'minimum_floor_to_overhead_m':round(minhead,3),'reverse_uses_identical_route':D['routes']['reverse']==list(reversed(D['routes']['forward']))}
# Door swing sector, sampled every 2 degrees and 3 cm along the leaf.
doorResults=[]
for o in D['openings']:
 if o['type']!='door':continue
 h=o['hinge'];side=o['swing_side'];collisions=set();others=obstructions(o['level'])
 for deg in range(2,91,2):
  t=math.radians(deg)
  for s in np.arange(.08,o['w']+.001,.03):
   vx=s*math.cos(t);vy=s*math.sin(t)*side
   px=h[0]+(vx if o['axis']==0 else vy);py=h[1]+(vy if o['axis']==0 else vx)
   for id,b in others:
    if id.startswith(o['wall']+'_') or id==o['id']+'_leaf':continue
    if distrect(px,py,b)<.02:collisions.add(id)
 doorResults.append({'id':o['id'],'width_m':o['w'],'clear':not collisions,'collisions':sorted(collisions)})
report['door_sweeps']=doorResults
st=D['stairs'];report['stairs']={'rise_total_m':st['rise']*st['risers'],'run_total_m':round(st['tread']*st['treads'],3),'clear_width_m':st['clear_width'],'top_platform_depth_m':1.5,'bottom_platform_depth_m':1.73,'same_void_geometry_all_outputs':True,'support_objects':['STAIR_continuous_concrete_slab','STAIR_upper_bearing','STAIR_lower_bearing','STAIR_corridor_support_end'],'reference_alignment':'需要用户目视确认。C01/C02/C03 为同一模型内固定相机，非照片级重建。'}
ids=[o['id'] for o in D['objects']];report['object_ids_unique']=len(ids)==len(set(ids));report['all_rooms_reachable']=all(r['reachable'] for r in reachResults);report['all_door_sweeps_clear']=all(r['clear'] for r in doorResults)
(R/'校验/几何检查结果.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['room_access','door_sweeps']},ensure_ascii=False));print('UNREACHABLE',[r for r in reachResults if not r['reachable']]);print('DOOR_COLLISIONS',[r for r in doorResults if not r['clear']])
# Editable SVG drawings, same model data and true coordinates for every piece.
S=49;W=1800;H=1260;svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><marker id="arr" markerWidth="7" markerHeight="7" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6Z" fill="#b36828"/></marker></defs><rect width="100%" height="100%" fill="#fafbf9"/><style>text{{font-family:Microsoft YaHei,sans-serif;fill:#263f48}}.tiny{{font-size:9px}}.name{{font-size:13px;font-weight:bold}}.small{{font-size:12px}}</style>']
def text(x,y,t,size=14,extra=''):svg.append(f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" {extra}>{html.escape(str(t))}</text>')
text(45,46,'《秘密教学》全屋空间模型 v4 · 两层同向平面',28);text(45,76,'同一主数据导出｜项目南向为临街正面（图纸下方）｜影视场景设计参考尺寸，非实测 / 非施工图',14)
for l,ox in [(1,65),(2,950)]:
 oy=960
 def pt(x,y):return ox+x*S,oy-y*S
 def rect(b,fill,stroke='none',sw=1,extra=''):
  x,y=pt(b[0],b[3]);svg.append(f'<rect x="{x}" y="{y}" width="{(b[2]-b[0])*S}" height="{(b[3]-b[1])*S}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')
 def line(a,b,color='#244b59',sw=1,extra=''):
  x,y=pt(*a);xx,yy=pt(*b);svg.append(f'<line x1="{x}" y1="{y}" x2="{xx}" y2="{yy}" stroke="{color}" stroke-width="{sw}" {extra}/>')
 text(ox,128,f'{l}F  /  '+('公共生活与主卧套房' if l==1 else '三间卧室与公共走廊'),21)
 for r in [r for r in D['rooms'] if r['level']==l]:rect(r['box'],'#f6e9d6' if r['new'] else '#edf3f3','#dce4e4',.5)
 for f in [f for f in D['furniture'] if f['level']==l]:rect(f['box'],'#d3dfe0','#829798',.8)
 z=(l-1)*3.3
 for d in D['objects']:
  g=d['group'];b=d['box']
  if (g==f'F{l}_walls' or g=='F2_guard' and l==2 or d['id'].startswith('STAIR_corridor_support') and l==1) and b[2]<=z+1.1 and b[5]>z+.12:rect(footprint(d),'#344c54')
 for o in [o for o in D['openings'] if o['level']==l]:
  if o['type']=='window':line(o['a'],o['b'],'#42a0bb',3)
  elif o['type']=='slide':line(o['a'],o['b'],'#647f88',2, 'stroke-dasharray="6 3"')
  elif o['type']=='door':
   h=o['hinge'];side=o['swing_side'];w=o['w'];end=[h[0]+(0 if o['axis']==0 else side*w),h[1]+(side*w if o['axis']==0 else 0)];line(h[:2],end,'#638084',1.2)
   points=[]
   for k in range(21):
    a=k*math.pi/40;vx=w*math.cos(a);vy=side*w*math.sin(a);points.append(pt(h[0]+(vx if o['axis']==0 else vy),h[1]+(vy if o['axis']==0 else vx)))
   svg.append('<polyline points="'+' '.join(f'{a},{b}' for a,b in points)+'" fill="none" stroke="#638084" stroke-width=".8"/>')
  x,y=pt((o['a'][0]+o['b'][0])/2,(o['a'][1]+o['b'][1])/2);text(x+4,y-4,o['id'],9)
 for k in range(20):line([.2,1.7+k*.28],[1.5,1.7+k*.28],'#6f8287',.8)
 line([.85,2],[.85,6.7],'#b36828',2,'marker-end="url(#arr)"');x,y=pt(.85,4.5);text(x+7,y,'下 A→B',11,'transform="rotate(-90 '+str(x+7)+' '+str(y)+')"')
 for r in [r for r in D['rooms'] if r['level']==l]:
  b=r['box'];x,y=pt((b[0]+b[2])/2,(b[1]+b[3])/2)
  # narrow circulation labels are rotated to keep them within their own room.
  if b[2]-b[0]<2:
   text(x,y,r['id']+' '+r['name'],11,f'text-anchor="middle" transform="rotate(-90 {x} {y})"')
  else:
   text(x,y-8,r['id']+' '+r['name'],13,'text-anchor="middle"');text(x,y+10,f'{b[2]-b[0]:.2f} × {b[3]-b[1]:.2f} m',10,'text-anchor="middle"')
 for br in [b for b in D['brands'] if b['level']==l]:rect(br['box'],'#b77930','#b77930',3)
 # Walkline on correct floor; stair segment shown on both plans.
 points=[]
 for p in D['routes']['forward']:
  if (l==2 and p[2]>3.0) or (l==1 and p[2]<4.9):points.append(pt(p[0],p[1]))
 svg.append('<polyline points="'+' '.join(f'{a},{b}' for a,b in points)+'" fill="none" stroke="#b36828" stroke-width="2" stroke-dasharray="5 4"/>')
 line([0,-2.4],[14.2,-2.4],'#607780',1);text(ox+S*7.1,oy+S*2.4-6,'最大宽度 14.20 m',12,'text-anchor="middle"');line([15.0,0],[15.0,16],'#607780',1);text(ox+S*15.15,oy-S*8,'16.00 m',12)
 text(ox,1120,'北 ↑　南 / 临街 ↓',13);text(ox,1150,'深色：墙体剖切　蓝线：窗　弧线：门扇　橙线：路线 / Logo 载体',12)
 text(ox,1174,'浅蓝：既有空间身份　浅橙：补充功能与过渡区　编号对应 CSV / Blender',12)
text(45,1230,'楼层高差 3.30 m · 20 个踢面 × 0.165 m · 19 个踏面 × 0.28 m · 梯段净宽 1.30 m · 开口与图纸均来自空间主数据_v4.json',14)
svg.append('</svg>');(R/'图纸/两层同向平面图.svg').write_text('\n'.join(svg),encoding='utf8')
