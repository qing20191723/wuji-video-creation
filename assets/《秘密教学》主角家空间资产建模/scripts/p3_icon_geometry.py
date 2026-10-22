"""Deterministic vector/mesh tracing of the supplied brand, not generative redraw."""
from pathlib import Path
import json,collections,math
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parents[1]/'完整平面与品牌_P3_20261022'
p=R/'品牌贴图/HG_ICON.png';im=Image.open(p).convert('RGBA');a=np.array(im);rgb=a[:,:,:3]
mask=(rgb.max(2)>90)&(a[:,:,3]>128)&((rgb.max(2).astype(int)-rgb.min(2).astype(int))>35)
h,w=mask.shape;seen=np.zeros_like(mask);components=[]
for y,x in zip(*np.where(mask)):
 if seen[y,x]:continue
 q=collections.deque([(x,y)]);seen[y,x]=1;pts=[]
 while q:
  xx,yy=q.popleft();pts.append((xx,yy))
  for X,Y in [(xx-1,yy),(xx+1,yy),(xx,yy-1),(xx,yy+1)]:
   if 0<=X<w and 0<=Y<h and mask[Y,X] and not seen[Y,X]:seen[Y,X]=1;q.append((X,Y))
 components.append(pts)
components.sort(key=len,reverse=True);keep=np.zeros_like(mask)
for pts in components[:2]:
 for x,y in pts:keep[y,x]=1
# Fill the logo's enclosed black details; retain source RGB and make only the exterior transparent.
outside=np.zeros_like(mask);q=collections.deque()
for x in range(w):q.extend([(x,0),(x,h-1)])
for y in range(h):q.extend([(0,y),(w-1,y)])
while q:
 x,y=q.popleft()
 if x<0 or y<0 or x>=w or y>=h or keep[y,x] or outside[y,x]:continue
 outside[y,x]=1;q.extend([(x-1,y),(x+1,y),(x,y-1),(x,y+1)])
sil=~outside;a[:,:,3]=sil.astype(np.uint8)*255
Image.fromarray(a).save(p)
# Pixel-boundary polygon, simplified in image space.
edges={}
for y,x in zip(*np.where(sil)):
 for condition,p0,p1 in [(y==0 or not sil[y-1,x],(x,y),(x+1,y)),(x==w-1 or not sil[y,x+1],(x+1,y),(x+1,y+1)),(y==h-1 or not sil[y+1,x],(x+1,y+1),(x,y+1)),(x==0 or not sil[y,x-1],(x,y+1),(x,y))]:
  if condition:edges[p0]=p1
loops=[]
while edges:
 start=next(iter(edges));cur=start;pts=[]
 while cur in edges:
  pts.append(cur);cur=edges.pop(cur)
  if cur==start:break
 loops.append(pts)
poly=max(loops,key=len)
def simplify(points,eps):
 if len(points)<3:return points
 a,b=np.array(points[0],dtype=float),np.array(points[-1],dtype=float);v=b-a;den=np.linalg.norm(v)
 ds=[np.linalg.norm(np.array(p)-a) if den==0 else abs(np.cross(v,np.array(p)-a))/den for p in points]
 i=int(np.argmax(ds))
 if ds[i]>eps:return simplify(points[:i+1],eps)[:-1]+simplify(points[i:],eps)
 return [points[0],points[-1]]
mid=len(poly)//2;poly=simplify(poly[:mid+1],.9)[:-1]+simplify(poly[mid:]+[poly[0]],.9)[:-1]
data=dict(width=w,height=h,points=[[int(x),int(y)] for x,y in poly],component_sizes=[len(c) for c in components[:5]],source='原Logo位图轮廓确定性提取；图标外形不重新生成')
(R/'数据/Logo轮廓.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Fixed SVG is self-contained and identical to the final PNG.
import base64
uri='data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
(R/'品牌贴图/HG_ICON.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}"><image width="{w}" height="{h}" href="{uri}"/></svg>',encoding='utf-8')
print(json.dumps(dict(vertices=len(poly),components=data['component_sizes'])))
