"""Geometry, clearance and route checks against actual exported mesh bounds."""
from pathlib import Path
import json,math,hashlib
R=Path(__file__).resolve().parents[1];O=R/'白模当前'
M=json.loads((O/'模型/空间数据.json').read_text(encoding='utf8'));D=M['plan'];checks=[]
def check(name,passed,detail=''):checks.append(dict(name=name,passed=bool(passed),detail=detail))
def area(a,b):return max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
approval=json.loads((R/'平面确认/F4用户确认记录.json').read_text(encoding='utf8'))
check('已确认六个F4图纸文件未改动',all(hashlib.sha256((R/'平面确认'/f['file']).read_bytes()).hexdigest()==f['sha256'] for f in approval['files']))
check('模型实际读取M2建模方案',M['revision']=='P2.4-M2' and M['source_sha256']==hashlib.sha256((O/'模型/建模方案.json').read_bytes()).hexdigest())
st=D['stairs'];v=D['architecture']['void'];par=next(w for w in D['walls'] if w['id']=='2-PAR')
check('护栏长度等于实际梯段长度',abs(par['b'][0]-par['a'][0]-(st['footprint'][2]-st['footprint'][0]))<1e-6)
check('洞口内没有二楼楼板',all(area(v,b)<1e-8 for b in D['architecture']['floor2_rects']))
check('C与B上下叠置',area(st['B'],st['C'])>1 and st['C'][2]==v[0])
check('A可绕护栏端头侧向接走廊',st['A'][2]-par['b'][0]>=1.3)
check('22级连续升至3.30m',abs(st['rises']*st['rise']-3.3)<1e-6 and st['treads']==st['rises']-1)
check('二楼只有三道卧室木门',set(o['id'] for o in D['openings'] if o['level']==2 and o['type']=='door')=={'D203','D204','D205'})
check('A端为大窗，C端为高窗，梯侧为横窗',all(any(o['id']==x and o['type']=='window' for o in D['openings']) for x in ['W_A_END','W_C_HIGH','W_STRIP']))
check('西侧屋面外围护栏闭合至建筑边界',[[0,-1.4],[0,10.4]] in D['exterior_rails'] and [[0,10.4],[7.7,10.4]] in D['exterior_rails'] and any(o['id']=='rail_top_6' for o in M['objects']))
bed=next(f['box'] for f in D['furniture'] if f['id']=='A01');check('大姐床仍为2.25×2.10m',abs(bed[2]-bed[0]-2.25)<1e-6 and abs(bed[3]-bed[1]-2.1)<1e-6)
outside=[];collisions=[]
for f in D['furniture']:
 if f['level']!=2:continue
 r=next(r for r in D['rooms'] if r['id']==f['room']);a=f['box'];b=r['box']
 if a[0]<b[0]-1e-6 or a[1]<b[1]-1e-6 or a[2]>b[2]+1e-6 or a[3]>b[3]+1e-6:outside.append(f['id'])
 for g in D['furniture']:
  if g['room']==f['room'] and g['id']>f['id'] and 'rug' not in f['kind']+g['kind'] and area(a,g['box'])>.00001:collisions.append([f['id'],g['id']])
check('二楼家具占地不越房间边界',not outside,outside)
check('二楼主要家具占地无重叠（地毯除外）',not collisions,collisions)
sweeps=[]
for op in [o for o in D['openings'] if o['level']==2 and o['type']=='door']:
 rid={'D203':'B1','D204':'B2','D205':'B3'}[op['id']];a=op['start']+.045;length=op['end']-op['start']-.09
 for i in range(91):
  ang=math.radians(i)
  for j in range(25):
   x=a+math.cos(ang)*length*j/24;y=4.3+math.sin(ang)*length*j/24
   for f in D['furniture']:
    b=f['box']
    if f['room']==rid and 'rug' not in f['kind'] and b[0]-.021<x<b[2]+.021 and b[1]-.021<y<b[3]+.021:sweeps.append([op['id'],f['id']])
check('三卧室门扇90度开启无家具碰撞',not sweeps,sorted(set(map(tuple,sweeps))))
# 0.5m-wide body path. Door meshes evaluated in their open transform.
motions={m['id']:m for m in M['motions']};obstacles=[]
for ob in M['objects']:
 if ob['category'] not in ['wall','frame','guard','furniture','door']:continue
 if 'rug' in ob['id']:continue
 b=ob['box'][:]
 if ob['id'] in motions:
  mot=motions[ob['id']];px,py,_=mot['pivot'];ang=mot['angle'];ps=[]
  for x in [b[0],b[3]]:
   for y in [b[1],b[4]]:ps.append([px+(x-px)*math.cos(ang)-(y-py)*math.sin(ang),py+(x-px)*math.sin(ang)+(y-py)*math.cos(ang)])
  b=[min(p[0] for p in ps),min(p[1] for p in ps),b[2],max(p[0] for p in ps),max(p[1] for p in ps),b[5]]
 obstacles.append((ob['id'],b))
route_hits=[];floor_holes=[];clearances=[];samples=0
route=D['walk_route']
for a,b in zip(route,route[1:]):
 dist=math.dist(a['pos'],b['pos'])
 for i in range(max(2,math.ceil(dist/.04))+1):
  n=max(2,math.ceil(dist/.04));u=i/n;p=[x+(y-x)*u for x,y in zip(a['pos'],b['pos'])];x,y,z=p
  if 9.4<=x<16.96 and 1.1<=y<=2.4:z=1.6+.15*(math.floor((x-9.4)/.36+1e-7)+1)
  else:z=4.9 if z>4 else 1.6
  foot=z-1.6;samples+=1
  for id,bb in obstacles:
   # Walking step nosings and support walls below foot are not body obstructions.
   if bb[5]<=foot+.2 or bb[2]>=foot+1.8:continue
   dx=max(bb[0]-x,0,x-bb[3]);dy=max(bb[1]-y,0,y-bb[4])
   if dx*dx+dy*dy<.25**2:route_hits.append(id)
  supports=[ob for ob in M['objects'] if ob['category'] in ['slab','stairs'] and ob['box'][0]-1e-5<=x<=ob['box'][3]+1e-5 and ob['box'][1]-1e-5<=y<=ob['box'][4]+1e-5 and abs(ob['box'][5]-foot)<.0001]
  if not supports:floor_holes.append([round(x,2),round(y,2),round(foot,2)])
  ceilings=[ob['box'][2]-foot for ob in M['objects'] if ob['category'] in ['slab','roof'] and ob['box'][0]<=x<=ob['box'][3] and ob['box'][1]<=y<=ob['box'][4] and ob['box'][2]>foot+.2]
  if ceilings:clearances.append(min(ceilings))
check('连续路线0.50m足迹无墙体及家具碰撞',not route_hits,sorted(set(route_hits)))
check('连续路线始终有楼面或踏步支承',not floor_holes,floor_holes[:15])
check('路线竖向净空不低于2.0m',min(clearances)>=2 if clearances else False,round(min(clearances),3) if clearances else None)
result=dict(revision=M['revision'],passed=all(x['passed'] for x in checks),checks=checks,route_samples=samples,scope='F4关系、二楼家具与指定路线；不代替全空间覆盖或结构施工验收',limitations=D['unresolved'],dimensions=D['provisional_dimensions'])
(O/'检查记录/M2几何与动线检查.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False))
if not result['passed']:raise SystemExit(1)
