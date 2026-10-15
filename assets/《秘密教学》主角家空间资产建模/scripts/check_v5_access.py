"""Conservative 5cm plan-grid check of supported floor and body clearance.
Doors/sliders assumed open; not a door swing, vehicle or engineering check.
"""
import json,math
from pathlib import Path
from collections import deque
import numpy as np
R=Path(__file__).resolve().parents[1];D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'))
obs=[o for o in D['objects'] if o['module']=='HOME'];step=.05
(R/'预览/v5').mkdir(parents=True,exist_ok=True)
xs=np.arange(3.5,23,.05);ys=np.arange(13,36,.05);X,Y=np.meshgrid(xs,ys);results=[]
def ix(x,y):return (int(round((y-ys[0])/step)),int(round((x-xs[0])/step)))
targets={1:{'入口':(17.4,14.3),'客厅':(11.6,19.9),'餐厅':(15.0,19.9),'厨房':(15.3,23.5),'主卧':(11.0,30.0),'主卫':(9.3,33.8),'洗衣房':(18.8,28.4),'客卫':(18.6,32.0),'B端':(4.7,23.4)},2:{'A端':(6.5,16.2),'大姐':(6.2+3.8,2.2+15.2),'子豪':(6.5+3.8,13.5+15.2),'舒亚':(14.8+3.8,12.2+15.2),'公用浴室':(6.2,27.5),'后露台':(15.1,32.4),'大姐阳台':(15.0,17.3)}}
open_slider_glass={o['id'].replace('_O','_')+'glass' for o in D['openings'] if o['module']=='HOME' and o['type']=='slider'}
for level,z,seed in [(1,0,(17.4,14.3)),(2,3.3,(6.5,16.2))]:
 support=np.zeros(X.shape,bool);blocked=np.zeros(X.shape,bool)
 for o in obs:
  b=o['box']
  if o['role'] in ('floor','exterior') and abs(b[5]-z)<.03 and b[2]<z:
   support|=(X>=b[0])&(X<=b[3])&(Y>=b[1])&(Y<=b[4])
  if o['role'] in ('door','stair','rug','decor','brand','site','landscape','floor','marking') or o['id'] in open_slider_glass:continue
  if b[2]>=z+1.75 or b[5]<=z+.2:continue
  dx=np.maximum(np.maximum(b[0]-X,X-b[3]),0);dy=np.maximum(np.maximum(b[1]-Y,Y-b[4]),0)
  blocked|=dx*dx+dy*dy<.26**2
 # Foot support 0.2m to either side, not merely a center over a floor.
 supported=support.copy()
 for axis in (0,1):
  for k in (-4,4):supported &= np.roll(support,k,axis=axis)
 walk=supported&~blocked;visited=np.zeros_like(walk);q=deque();p=ix(*seed)
 if walk[p]:q.append(p);visited[p]=True
 while q:
  y,x=q.popleft()
  for yy,xx in ((y-1,x),(y+1,x),(y,x-1),(y,x+1)):
   if 0<=yy<walk.shape[0] and 0<=xx<walk.shape[1] and walk[yy,xx] and not visited[yy,xx]:visited[yy,xx]=True;q.append((yy,xx))
 for name,(x,y) in targets[level].items():
  p=ix(x,y);results.append({'floor':level,'name':name,'point':[x,y,z],'has_support':bool(supported[p]),'body_clear':bool(not blocked[p]),'reachable':bool(visited[p])})
 np.savez_compressed(R/f'预览/v5/access_F{level}.npz',walk=walk,visited=visited,xs=xs,ys=ys)
report={'grid_m':step,'body_diameter_m':.52,'height_m':1.75,'door_state':'open; sliders open; window/frame thickness not swept','targets':results,'all_targets_reachable':all(x['reachable'] for x in results),'limitations':['plan-grid checks flat floors only; stair continuity separately sampled','not a door-swing, vehicle-sweep or engineering certification','fixed furniture envelope approximation; no moving chairs']}
(R/'校验/v5_房间可达性.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
