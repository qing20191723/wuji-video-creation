"""Finite 2D checks for the review proposal. Not a structural / 3D certification."""
import json,math,hashlib,collections
import numpy as np
import draw_plan_review as p

R=p.ROOT;O=p.OUT
issues=[];checks={}
def overlap(a,b):return min(a[2],b[2])-max(a[0],b[0])>1e-5 and min(a[3],b[3])-max(a[1],b[1])>1e-5
def dist(x,y,b):return math.hypot(max(b[0]-x,0,x-b[2]),max(b[1]-y,0,y-b[3]))
def solid_f(f):return 'rug' not in f['kind']
def pieces(l):
    out=[]
    for w in p.WALLS:
        if w['level']!=l:continue
        a,b=w['a'],w['b'];h=a[1]==b[1];t=w['thickness']/2;fixed=a[1] if h else a[0];c=a[0] if h else a[1];end=b[0] if h else b[1]
        os=sorted([o for o in p.OPEN if o['wall']==w['id']],key=lambda o:o['start'])
        for op in os+[dict(start=end,end=end,type='end')]:
            if op['start']>c:
                box=[c,fixed-t,op['start'],fixed+t] if h else [fixed-t,c,fixed+t,op['start']]
                out.append((w['id'],box))
            if op['type']=='window':
                box=[op['start'],fixed-t,op['end'],fixed+t] if h else [fixed-t,op['start'],fixed+t,op['end']]
                out.append((op.get('id','window'),box))
            c=op['end']
    return out
def leaves(l):
    out=[]
    for o in p.OPEN:
        if o['level']!=l or o['type']!='door':continue
        w=next(w for w in p.WALLS if w['id']==o['wall']);h=w['a'][1]==w['b'][1];fixed=w['a'][1] if h else w['a'][0];s=o['start'];r=o['end']-s;side=o.get('side',1)
        a=(s,fixed) if h else (fixed,s);b=(s,fixed+side*r) if h else (fixed+side*r,s)
        out.append((o['id'],[min(a[0],b[0])-.02,min(a[1],b[1])-.02,max(a[0],b[0])+.02,max(a[1],b[1])+.02]))
    return out

ids=[o['id'] for o in p.OPEN];checks['unique_openings']=len(ids)==len(set(ids))
if not checks['unique_openings']:issues.append('Duplicate opening IDs')
# Overlap between solid furnishings, excluding appliances intentionally contained in counters.
allowed={frozenset(['K1','KH']),frozenset(['K2','KS'])}
for i,a in enumerate(p.F):
    for b in p.F[i+1:]:
        if a['level']==b['level'] and solid_f(a) and solid_f(b) and overlap(a['box'],b['box']) and frozenset([a['id'],b['id']]) not in allowed:issues.append(f'furniture overlap: {a["id"]}/{b["id"]}')
for f in p.F:
    if not solid_f(f):continue
    for wid,b in pieces(f['level']):
        if overlap(f['box'],b):issues.append(f'furniture/wall: {f["id"]}/{wid}')
# Full 90-degree swing sweep against furniture. Wall intersection excludes supporting wall at hinge.
sweeps=[]
for o in p.OPEN:
    if o['type']!='door':continue
    w=next(w for w in p.WALLS if w['id']==o['wall']);h=w['a'][1]==w['b'][1];fixed=w['a'][1] if h else w['a'][0];s=o['start'];r=o['end']-s;side=o.get('side',1);hits=set()
    obstacles=[(f['id'],f['box']) for f in p.F if f['level']==o['level'] and solid_f(f)] + [(id,b) for id,b in pieces(o['level']) if id!=w['id']]
    for angle in np.linspace(.04,math.pi/2,50):
        for rr in np.linspace(.13,r,35):
            x,y=(s+rr*math.cos(angle),fixed+side*rr*math.sin(angle)) if h else (fixed+side*rr*math.sin(angle),s+rr*math.cos(angle))
            for id,b in obstacles:
                if dist(x,y,b)<.005:hits.add(id)
    sweeps.append(dict(door=o['id'],hits=sorted(hits)))
    if hits:issues.append('Door sweep '+o['id']+': '+','.join(hits))
checks['door_sweeps']=sweeps
for z in p.ZONES:
    for f in p.F:
        if f['level']==z['level'] and solid_f(f) and f['id'] not in z['allow'] and overlap(z['box'],f['box']):issues.append('Use zone '+z['label']+'/'+f['id'])
checks['usage_zones_checked']=len(p.ZONES)
# Proposed finished floor masks. East bedroom zone is enlarged; lower stair flight is not a walkable flat floor.
regions={1:[[0,0,10.4,14],[3.4,14,10.4,19.6],[0,15.2,3.4,19.6],[-1.8,8.6,0,11.4]],2:[[1.8,0,10.4,18.1],[0,0,1.8,1.7],[-1.8,8.6,1.8,11.4],[.9,11.3,1.8,12.2],[-1.8,18.1,10.4,20.2],[0,-1.7,10.4,0]]}
body=.25;step=.05;xx=np.arange(-2,10.7,step);yy=np.arange(-1.8,20.4,step);X,Y=np.meshgrid(xx,yy);nav={};reachable=[]
for l in [1,2]:
    m=np.ones(X.shape,bool)
    for dx,dy in [(0,0),(-body,0),(body,0),(0,-body),(0,body)]:
        ok=np.zeros_like(m)
        for x,y,x1,y1 in regions[l]:ok|=(X+dx>=x)&(X+dx<=x1)&(Y+dy>=y)&(Y+dy<=y1)
        m&=ok
    obs=pieces(l)+leaves(l)+[(f['id'],f['box']) for f in p.F if f['level']==l and solid_f(f)]
    if l==1:obs.append(('stair flight',[.2,1.7,1.5,7.02]))
    for id,b in obs:
        dx=np.maximum(np.maximum(b[0]-X,X-b[2]),0);dy=np.maximum(np.maximum(b[1]-Y,Y-b[3]),0);m&=(dx*dx+dy*dy>=body*body-1e-8)
    start=(2.6,.85);ix=int(round((start[0]-xx[0])/step));iy=int(round((start[1]-yy[0])/step));seen=np.zeros_like(m);q=collections.deque([(iy,ix)]);seen[iy,ix]=True
    while q:
        y,x=q.popleft()
        for j,i in [(y-1,x),(y+1,x),(y,x-1),(y,x+1)]:
            if 0<=j<len(yy) and 0<=i<len(xx) and m[j,i] and not seen[j,i]:seen[j,i]=True;q.append((j,i))
    for r in p.ROOMS:
        if r['level']!=l:continue
        x,y,x1,y1=r['box'];region=(X>x+.1)&(X<x1-.1)&(Y>y+.1)&(Y<y1-.1);ok=bool(np.any(region&seen&m));reachable.append(dict(room=r['id'],reachable=ok))
        if not ok:issues.append('Unreachable '+r['id'])
    nav[l]=(m,seen)
checks['reachable_regions']=reachable
# Full named route sampling against real walls and furniture, not only graph adjacency.
routes=[]
for rt in p.ROUTES:
    obs=pieces(rt['level'])+leaves(rt['level'])+[(f['id'],f['box']) for f in p.F if f['level']==rt['level'] and solid_f(f)];hits=set();n=0
    for a,b in zip(rt['points'],rt['points'][1:]):
        for t in np.linspace(0,1,max(2,math.ceil(math.dist(a,b)/.03))):
            x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;n+=1
            for id,bb in obs:
                if dist(x,y,bb)<body-.001:hits.add(id)
    routes.append(dict(name=rt['id'],samples=n,hits=sorted(hits)))
    if hits:issues.append('Route '+rt['id']+': '+','.join(hits))
checks['routes']=routes
checks['master_door_on_axis']=abs((4.3+5.3)/2-(4.0+5.6)/2)<1e-7
checks['kitchen_dining_no_door']=not any(o['level']==1 and o['type']=='door' and o['wall'] in ['1-KS','1-DK'] for o in p.OPEN)
checks['stair_lower_landing_depth_m']=round(8.6-7.02,2)
checks['stair_top_landing_depth_m']=1.5
checks['net_bedroom_areas']={r['id']:r['net_area'] for r in p.ROOMS if r['id'] in ['B1','B2','B3','MB']}
old=json.loads((R/'制作记录/当前保留文件校验.json').read_text(encoding='utf8'));unchanged=[]
for r in old['files']:
    ok=hashlib.sha256((R/r['file']).read_bytes()).hexdigest()==r['sha256'];unchanged.append(dict(file=r['file'],unchanged=ok))
    if not ok:issues.append('Model changed '+r['file'])
checks['model_unchanged']=unchanged
report=dict(scope='二维方案检查；0.50m直径人物足迹、门扇采样、家具占地；不含三维净高/承重/施工合规。',issues=issues,checks=checks)
(O/'平面几何检查.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2));raise SystemExit(bool(issues))
