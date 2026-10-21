"""0.50m body-footprint reachability to explicit furniture approach locations."""
from pathlib import Path
import json, math
from collections import deque
R=Path(__file__).resolve().parents[1];O=R/'白模当前'
D=json.loads((O/'模型/建模方案.json').read_text(encoding='utf8'))
probes={
 'B3':{'床侧':[7.75,5.7],'书桌椅旁':[4.7,5.65],'衣柜前':[3.8,8.4],'北侧矮柜前':[5.4,9.35]},
 'B2':{'床侧':[11.7,6.8],'书桌椅旁':[11.15,10.2],'衣柜前':[13.4,10.7],'茶几旁':[11.8,7.5]},
 'B1':{'床侧':[17.55,7.2],'电脑椅前':[18.2,7.35],'衣柜前':[18,5.4],'健身车旁':[18.65,5.6],'阳台门前':[19.65,6.1]}}
entry={'B3':[8.4,4.75],'B2':[12.35,4.75],'B1':[15.4,4.75]}
rooms=[]
for rid,targets in probes.items():
 room=next(r for r in D['rooms'] if r['id']==rid);x,y,X,Y=room['box']
 obstacles=[f['box'] for f in D['furniture'] if f['room']==rid and 'rug' not in f['kind']]
 def free(px,py):
  if not(x+.25<=px<=X-.25 and y+.25<=py<=Y-.25):return False
  return all(max(b[0]-px,0,px-b[2])**2+max(b[1]-py,0,py-b[3])**2>=.25**2 for b in obstacles)
 step=.05
 nodes={(i,j) for i in range(math.ceil((X-x)/step)) for j in range(math.ceil((Y-y)/step)) if free(x+i*step,y+j*step)}
 def nearest(p):return min(nodes,key=lambda ij:(x+ij[0]*step-p[0])**2+(y+ij[1]*step-p[1])**2)
 start=nearest(entry[rid]);seen={start};q=deque([start])
 while q:
  i,j=q.popleft()
  for n in [(i+1,j),(i-1,j),(i,j+1),(i,j-1)]:
   if n in nodes and n not in seen:seen.add(n);q.append(n)
 results=[]
 for name,p in targets.items():
  n=nearest(p);offset=math.dist(p,[x+n[0]*step,y+n[1]*step])
  results.append(dict(name=name,point=p,reachable=n in seen and offset<.1,nearest_offset=round(offset,3)))
 rooms.append(dict(id=rid,width=round(X-x,2),depth=round(Y-y,2),area=room['net_area'],targets=results))
report=dict(revision=D['revision'],passed=all(t['reachable'] for r in rooms for t in r['targets']),body_diameter=.5,grid_step=.05,rooms=rooms,scope='静态家具占地的指定使用点连通；门扇扫掠另见几何检查；不代表柜门抽屉或全屋无盲角验收')
(O/'检查记录/M3卧室使用空间检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False))
if not report['passed']:raise SystemExit(1)
