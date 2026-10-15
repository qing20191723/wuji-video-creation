"""Inspect room-preservation transforms and sampled standing-body route clearance.
Does not certify construction engineering, turning radii, door swing or final image fidelity.
"""
import json,math
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'))
ids=[o['id'] for o in D['objects']];fail=[]
if len(ids)!=len(set(ids)):fail.append('duplicate_ids')
for o in D['objects']:
 if any(o['box'][i]>=o['box'][i+3] for i in range(3)):fail.append('invalid_box:'+o['id'])
original={o['id']:o for o in D['objects'] if o['module']!='HOME'};preserved=[]
for o in D['objects']:
 if o['module']=='HOME' and o.get('source_id') and o.get('zone')=='rooms':
  src=original[o['source_id']];ad=[o['box'][i+3]-o['box'][i] for i in range(3)];bd=[src['box'][i+3]-src['box'][i] for i in range(3)]
  if max(abs(a-b) for a,b in zip(ad,bd))>1e-4:fail.append('scaled:'+o['id'])
  preserved.append(o['id'])
# Stand with a 0.52m diameter body, 1.75m height; feet 0.20m excluded for stair risers.
# Doors are assumed opened. Every other solid wall/cabinet/ceiling remains present.
skip={'floor','site','landscape','rug','decor','brand','glass','frame','door','rail','stair'}
obstacles=[o for o in D['objects'] if o['module']=='HOME' and o['role'] not in skip]
hits={};samples=0
for route in D.get('walk_routes',[]):
 pts=route['points']
 for seg,(a,b) in enumerate(zip(pts,pts[1:])):
  n=max(1,math.ceil(math.dist(a,b)/.08))
  for i in range(n+1):
   t=i/n;p=[a[k]+t*(b[k]-a[k]) for k in range(3)];samples+=1
   for o in obstacles:
    q=o['box'];dx=max(q[0]-p[0],0,p[0]-q[3]);dy=max(q[1]-p[1],0,p[1]-q[4])
    if dx*dx+dy*dy<.26**2 and q[2]<p[2]+1.75 and q[5]>p[2]+.2:
     hits.setdefault(o['id'],{'route':route['id'],'segment':seg,'sample':[round(v,3) for v in p],'role':o['role']})
report={'version':D['version'],'module_count':len(D['modules']),'object_count':len(ids),'preserved_room_objects':len(preserved),'schema_failures':fail,'route_samples':samples,'route_assumptions':'0.52m body diameter, 1.75m height; doors open; sampled centers every <=0.08m; excludes rail/door swing and vehicle motion','route_collisions':hits,'design_gaps_failed':[x for x in D['checks'] if not x['pass']],'not_checked':['structural engineering','full door swing sweeps','all possible human routes','vehicle turning swept area','material/detail identity']}
(R/'校验/v5_空间复核.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=False))
