from pathlib import Path
import json,math,collections,hashlib
from PIL import Image,ImageChops
R=Path(__file__).resolve().parents[1];O=R/'完整平面与品牌_P3_R2_20261022'
D=json.loads((O/'数据/空间方案_P3.json').read_text(encoding='utf8'));old=json.loads((R/'白模当前/模型/建模方案.json').read_text(encoding='utf8'))
f0={f['id']:f for f in old['furniture']};rooms={r['id']:r for r in D['rooms']};errors=[];checks=[]
def add(name,ok,detail=None):
 checks.append(dict(name=name,passed=bool(ok),detail=detail))
 if not ok:errors.append(dict(name=name,detail=detail))
def size(b):return [round(b[2]-b[0],5),round(b[3]-b[1],5)]
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-5 and min(a[3],b[3])-max(a[1],b[1])>1e-5
soft={'rug','roundrug','starrug'}
for f in D['furniture']:
 if f['id'] in f0:
  expected=[3.9,2.52] if f['id']=='A01' else size(f0[f['id']]['box'])
  add('家具尺寸:'+f['id'],all(abs(a-b)<1e-4 for a,b in zip(size(f['box']),expected)),dict(actual=size(f['box']),expected=expected))
 r=rooms[f['room']]['box'];b=f['box'];add('家具在房间内:'+f['id'],b[0]>=r[0]-.001 and b[1]>=r[1]-.001 and b[2]<=r[2]+.001 and b[3]<=r[3]+.001)
allowed=[{'K04','K03'},{'K05','K02'}]
for i,f in enumerate(D['furniture']):
 if f['kind'] in soft:continue
 for g in D['furniture'][i+1:]:
  if f['room']!=g['room'] or g['kind'] in soft or {f['id'],g['id']} in allowed:continue
  if overlap(f['box'],g['box']):add('家具无穿插',False,[f['id'],g['id']])
for c in D['clearances']:
 hits=[f['id'] for f in D['furniture'] if f['room']==c['room'] and f['kind'] not in soft and overlap(f['box'],c['box'])]
 add('使用空间:'+c['id'],not hits,hits)
walls={w['id']:w for w in D['walls']}
for o in D['openings']:
 w=walls[o['wall']];hor=w['a'][1]==w['b'][1];axis=0 if hor else 1
 add('洞口在墙段内:'+o['id'],o['start']>=w['a'][axis]-.001 and o['end']<=w['b'][axis]+.001)
 if o['type']!='door':continue
 side=-1 if o['id'] in ['D_ROOF_ACCESS','D_RS_ENTRY'] else o.get('side',1);u=o['start'];radius=o['end']-u;fix=w['a'][1-axis];hits=set()
 for f in D['furniture']:
  if f['level']!=o['level'] or f['kind'] in soft:continue
  b=f['box']
  for k in range(19):
   a=k*math.pi/36
   for j in range(1,21):
    t=j/20*radius;pt=[u+t*math.cos(a),fix+side*t*math.sin(a)] if hor else [fix+side*t*math.sin(a),u+t*math.cos(a)]
    if b[0]+.015<pt[0]<b[2]-.015 and b[1]+.015<pt[1]<b[3]-.015:hits.add(f['id'])
 add('开门扫掠:'+o['id'],not hits,sorted(hits))
# Reachable representative use points: 0.50m body diameter on a 0.10m room grid.
targets={'B1':[[15.4,4.5],[17.9,5.5],[18.45,5.6],[20,4.0],[19.0,6.9]],'B3':[[1.2,3.5],[3.5,4.1],[5.0,3.3],[5.6,5.4]],'B2':[[10.4,3.4],[10.4,6.8],[11.8,8.1]],'BW':[[-1.0,.6],[-2.0,-.5],[-1.9,1.0]]}
for id,pts in targets.items():
 x,y,X,Y=rooms[id]['box'];step=.1;rad=.25;obs=[f['box'] for f in D['furniture'] if f['room']==id and f['kind'] not in soft]
 def valid(p):
  xx,yy=p
  if not(x+rad<=xx<=X-rad and y+rad<=yy<=Y-rad):return False
  for a,b,A,B in obs:
   dx=max(a-xx,0,xx-A);dy=max(b-yy,0,yy-B)
   if dx*dx+dy*dy<rad*rad-.0001:return False
  return True
 nodes={(i,j) for i in range(int((X-x)/step)+1) for j in range(int((Y-y)/step)+1) if valid((x+i*step,y+j*step))}
 entry={'B1':[13.95,2.4],'B2':[9.65,2.4],'B3':[1.35,2.4],'BW':[-.7,.8]}[id]
 nearest=lambda p:min(nodes,key=lambda ij:(x+ij[0]*step-p[0])**2+(y+ij[1]*step-p[1])**2)
 start=nearest(entry);seen={start};q=collections.deque([start])
 while q:
  i,j=q.popleft()
  for v in [(i-1,j),(i+1,j),(i,j-1),(i,j+1)]:
   if v in nodes and v not in seen:seen.add(v);q.append(v)
 for p in pts:
  n=nearest(p);distance=math.hypot(x+n[0]*step-p[0],y+n[1]*step-p[1]);add('房间通行:'+id+str(p),n in seen and distance<=.4,dict(nearest_distance=round(distance,3),reachable=n in seen))
# Meaningful semantic invariants and stair math.
fm={f['id']:f for f in D['furniture']};op={o['id']:o for o in D['openings']}
add('R1二姐床贴右墙',abs(fm['C01']['box'][2]-rooms['B3']['box'][2])<1e-6)
add('R2床尾小书架与床居中对齐',abs(sum(fm['C02']['box'][::2])-sum(fm['C01']['box'][::2]))<1e-6)
add('R2床尾小书架间距保持',abs(fm['C02']['box'][1]-fm['C01']['box'][3]-.2)<1e-6)
add('R1大姐床尾靠近电脑桌',abs(fm['A04']['box'][0]-fm['A01']['box'][2]-.2)<1e-6)
add('R1子豪门位置',abs((op['D_B2']['start']+op['D_B2']['end'])/2-9.65)<1e-6)
add('二姐床头书桌入口同墙',fm['C01']['head']=='S' and abs(fm['C01']['box'][1]-fm['C03']['box'][1])<.001)
add('二姐原图左右次序',op['D_B3']['end']<fm['C03']['box'][0]<fm['C09']['box'][0]<fm['C01']['box'][0])
add('浴室玻璃门位于走廊尽头',op['G_BATH']['type']=='glass' and op['G_BATH']['wall']=='H_W')
add('舒亚对面仍为落地窗',op['W_SHUYA_OPPOSITE']['type']=='window' and op['W_SHUYA_OPPOSITE']['sill']==.03)
for st in D['stairs']:add('楼梯层高闭合:'+st['id'],abs(st['rises']*st['rise']-3.3)<1e-8)
add('直梯跑长',abs((D['stairs'][0]['footprint'][2]-D['stairs'][0]['footprint'][0])-21*.36)<1e-8)
add('上下平台投影一致',rooms['B']['box']==rooms['C']['box'])
add('通顶楼梯净空预留',D['stairs'][1]['clear_height']>=2.2)
add('品牌不面向摄影机',all(b['fixed_to_carrier'] and not b['camera_facing'] for b in D['brands']))
add('完整版含永久域名',all(b['domain']=='hgdju.com' for b in D['brands'] if b['master']!='HG_ICON'))
for entry in json.loads((R.parent.parent/'docs/episode7-scenes/当前建模交付清单.json').read_text(encoding='utf8'))['model_files']:
 p=R.parent.parent/entry['file'];add('原交付未修改:'+p.name,hashlib.sha256(p.read_bytes()).hexdigest()==entry['sha256'])
manifest=json.loads((R.parent/'秘密教学第7集合格资产/合格资产清单.json').read_text(encoding='utf8'))
for a in manifest['assets']:
 p=R.parent/'秘密教学第7集合格资产'/a['file'];add('认可原图未修改:'+a['id'],hashlib.sha256(p.read_bytes()).hexdigest()==a['sha256'])
if (O/'品牌贴图/HG_FULL_normal.png').exists():
 a=Image.open(O/'品牌贴图/HG_FULL_normal.png').convert('RGBA');b=Image.open(O/'品牌贴图/HG_FULL_mirror.png').convert('RGBA');diff=ImageChops.difference(a.transpose(Image.Transpose.FLIP_LEFT_RIGHT),b);pix=list(diff.getdata());mean=sum(sum(v) for v in pix)/(len(pix)*4);add('整组镜像像素核对',mean<1,dict(mean_error=mean,note='浏览器亚像素栅格化允许<1/255平均差'))
out=dict(revision=D['revision'],checks=checks,errors=errors,passed=len(errors)==0,limitations=D['unresolved'],not_claimed=['真实梁底净空及结构验算','整屋渲染的品牌遮挡和镜面反射','用户平面验收'])
(O/'检查/空间与资产校核.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(checks=len(checks),errors=errors),ensure_ascii=False))
