"""Build P4-M1 from the approved P4 plan. Blender 4.5 LTS, no M3 mutation.
Run: blender -b --python scripts/build_p4_model.py [-- --render]
"""
import bpy, json, math, hashlib, ast, copy, sys
from pathlib import Path
from mathutils import Vector, Matrix
R=Path(__file__).resolve().parents[1]
P=R/'整体平面_P4_20261022/数据/整体空间方案_P4.json'
D=json.loads(P.read_text('utf8'))
O=R/'全屋模型_P4-M1_20261022'
for sub in ['模型','数据','检查','预览','贴图']: (O/sub).mkdir(parents=True,exist_ok=True)
AS=R/'完整平面与品牌_P3_R2_20261022'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
S=bpy.context.scene;S.unit_settings.system='METRIC';S.render.engine='CYCLES'
S.cycles.samples=20;S.cycles.use_denoising=True
try:
 p=bpy.context.preferences.addons['cycles'].preferences;p.compute_device_type='OPTIX';p.get_devices()
 for device in p.devices:device.use=device.type=='OPTIX'
 if any(device.use for device in p.devices):S.cycles.device='GPU'
except Exception:pass
S.render.resolution_x=1600;S.render.resolution_y=1100;S.render.resolution_percentage=100
S.render.image_settings.file_format='PNG';S.view_settings.view_transform='AgX'
S.world.use_nodes=True;S.world.node_tree.nodes['Background'].inputs[0].default_value=(.75,.84,1,1);S.world.node_tree.nodes['Background'].inputs[1].default_value=.5
MAT={};COL={};DOORS={};ATTACH=[];CAM=[];WALLS=copy.deepcopy(D['walls']);OPS=copy.deepcopy(D['openings'])
def material(n,rgb,rough=.65,metal=0,trans=0):
 m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);m.use_nodes=True;p=m.node_tree.nodes['Principled BSDF'];p.inputs['Base Color'].default_value=(*rgb,1);p.inputs['Roughness'].default_value=rough;p.inputs['Metallic'].default_value=metal;p.inputs['Transmission Weight'].default_value=trans;MAT[n]=m;return m
for n,c in {'wall':(.77,.73,.64),'floor':(.48,.32,.19),'frame':(.065,.075,.08),'furniture':(.61,.48,.32),'fabric':(.24,.36,.35),'detail':(.05,.06,.065),'garden':(.18,.32,.1),'stone':(.67,.65,.58),'white':(.86,.84,.79),'roof':(.45,.48,.48),'dark':(.12,.15,.17),'soil':(.1,.065,.03)}.items():material(n,c)
material('glass',(.8,.93,.95),.07,0,1);material('frosted',(.8,.9,.9),.35,0,.75);material('mirror',(.93,.95,.98),.06,1)
def collection(l,cat):
 key=f'F{l}_{cat}'
 if key not in COL:COL[key]=bpy.data.collections.new(key);S.collection.children.link(COL[key])
 return COL[key]
def register(o,id,level,category,source='',mat='wall'):
 o.name=id
 if mat:o.data.materials.append(MAT[mat])
 for c in list(o.users_collection):c.objects.unlink(o)
 collection(level,category).objects.link(o);o['source_id']=source;o['category']=category;o['level']=level;o['revision']='P4-M1'
 return o
def box(id,b,l=0,cat='wall',src='',mat='wall'):
 if any(b[i+3]-b[i]<=.000001 for i in range(3)):return None
 bpy.ops.mesh.primitive_cube_add(size=1,location=[(b[i]+b[i+3])/2 for i in range(3)]);o=bpy.context.object;o.dimensions=[b[i+3]-b[i] for i in range(3)];bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 register(o,id,l,cat,src,mat)
 if cat in ['furniture','terrace_furniture']:
  mod=o.modifiers.new('small_real_edge','BEVEL');mod.width=min(.018,min(o.dimensions)/5);mod.segments=2
 return o
def cyl(id,c,r,h,l=0,cat='furniture',src='',mat='detail',axis=None):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=r,depth=h,location=c);o=bpy.context.object
 if axis:o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler()
 return register(o,id,l,cat,src,mat)
def bar(id,a,b,r,l,src='',cat='guard',mat='frame'):return cyl(id,(Vector(a)+Vector(b))/2,r,(Vector(b)-Vector(a)).length,l,cat,src,mat,Vector(b)-Vector(a))
def slab(id,b,z,l,cat='slab',mat='stone'):return box(id,[b[0],b[1],z-.22,b[2],b[3],z],l,cat,id,mat)
def inside(x,y,b):return b[0]<x<b[2] and b[1]<y<b[3]
def rect_cells(rects,holes=[]):
 xs=sorted(set(round(v,5) for b in rects+holes for v in [b[0],b[2]]));ys=sorted(set(round(v,5) for b in rects+holes for v in [b[1],b[3]]));out=[]
 for j in range(len(ys)-1):
  start=None
  for i in range(len(xs)-1):
   x=(xs[i]+xs[i+1])/2;y=(ys[j]+ys[j+1])/2;ok=any(inside(x,y,b) for b in rects) and not any(inside(x,y,b) for b in holes)
   if ok and start is None:start=xs[i]
   if start is not None and (not ok or i==len(xs)-2):out.append([start,ys[j],xs[i+1] if ok else xs[i],ys[j+1]]);start=None
 return out
def multi_slab(prefix,rs,holes,z,l,cat='slab',mat='stone'):
 for i,b in enumerate(rect_cells(rs,holes)):slab(prefix+str(i),b,z,l,cat,mat)
mainroof=D['roof_levels']['main_roof']['rectangles'];ground=D['roof_levels']['lower_roof']['base'];terr=D['courtyard']['box'];bal=next(r['box'] for r in D['rooms'] if r['id']=='BAL')
multi_slab('ground_',ground,[],0,1)
multi_slab('floor2_',ground+mainroof+[terr,bal],[D['stairs'][0]['opening']],3.3,2)
multi_slab('roof2_',mainroof,[D['stairs'][1]['opening']],6.6,3,'roof')
for r in D['rooms']:
 if r['id'] in ['RS3','SUP']:continue
 b=r['box'];z=(r['level']-1)*3.3
 box('finish_'+r['id'],[b[0],b[1],z+.001,b[2],b[3],z+.012],r['level'],'finish',r['id'],'stone' if r['id'] in ['BW','MW','WC','BAL','RS'] else 'floor')
# Perimeter walls explicitly close unlabelled circulation edges, without moving room bounds.
def wall(id,a,b,l,h=3.08,mat='wall',t=.2):WALLS.append(dict(id=id,a=a,b=b,level=l,height=h,material=mat,thickness=t))
wall('F1_CIRC_W',[-.1,-1.6],[-.1,1.9],1);wall('F1_CIRC_E',[21.9,-.1],[21.9,1.9],1)
wall('F1_STAIR_S',[-.1,-1.6],[9.06,-1.6],1)
OPS.append(dict(id='W_STAIR_LOWER',wall='F1_STAIR_S',level=1,start=.15,end=8.8,sill=.2,head=2.9,type='window'))
for id,a,b in [('SUP_W',[-3.8,-1.6],[-3.8,1.9]),('SUP_S',[-3.8,-1.6],[-.1,-1.6]),('SUP_N',[-3.8,1.9],[-.1,1.9])]:wall(id,a,b,1)
OPS.append(dict(id='D_SERVICE',wall='SUP_N',level=1,start=-2.8,end=-1.8,sill=0,head=2.2,type='door'))
sh=D['roof_levels']['stairhouse'];x,y,X,Y=sh['box']
for id,a,b in [('R3S',[x-.1,y-.1],[X+.1,y-.1]),('R3N',[x-.1,Y+.1],[X+.1,Y+.1]),('R3W',[x-.1,y-.1],[x-.1,Y+.1]),('R3E',[X+.1,y-.1],[X+.1,Y+.1])]:wall(id,a,b,3,sh['top']-6.6,'dark')
OPS.append(dict(id='D_ROOF_EXIT',wall='R3N',level=3,start=sh['exit'][0],end=sh['exit'][1],sill=0,head=2.2,type='door'))
OPS.append(dict(id='W_ROOF_STAIR',wall='R3E',level=3,start=-4.9,end=-3.2,sill=1.2,head=2.15,type='window'))
slab('stairhouse_cap',[x-.35,y-.35,X+.35,Y+.35],9.42,3,'roof','dark')
# Union co-linear shared walls, retaining every source opening.
groups={}
for w in WALLS:
 h=abs(w['a'][1]-w['b'][1])<.0001;axis=0 if h else 1;v=w['a'][1-axis];lo=w['a'][axis];hi=w['b'][axis];ht=1.1 if w['id']=='GUARD' else w.get('height',3.08)
 key=(w['level'],h,round(v,5),w['thickness'],ht,w.get('material','wall'));groups.setdefault(key,[]).append((lo,hi,w['id']))
APERTURES=[]
for gi,(key,segments) in enumerate(groups.items()):
 l,h,v,t,height,mat=key;z=(l-1)*3.3;lo=min(q[0] for q in segments);hi=max(q[1] for q in segments);ids=[q[2] for q in segments]
 ops=[o for o in OPS if o['wall'] in ids]
 cuts=sorted(set([lo,hi]+[v for q in segments for v in q[:2]]+[v for op in ops for v in [op['start'],op['end']]]))
 def piece(n,a,b,z0,z1,material=mat,cat='wall',depth=t,offset=0):
  bb=[a,v+offset-depth/2,z+z0,b,v+offset+depth/2,z+z1] if h else [v+offset-depth/2,a,z+z0,v+offset+depth/2,b,z+z1]
  return box(n,bb,l,cat,'|'.join(ids),material)
 for j,(a,b) in enumerate(zip(cuts,cuts[1:])):
  if not any(q[0]-.00001<(a+b)/2<q[1]+.00001 for q in segments):continue
  op=next((o for o in ops if o['start']-.00001<(a+b)/2<o['end']+.00001),None)
  if op:piece(f'wall_{gi}_{j}_sill',a,b,0,op.get('sill',0));piece(f'wall_{gi}_{j}_head',a,b,op['head'],height)
  else:piece(f'wall_{gi}_{j}',a,b,0,height)
 if height<2:piece('short_guard_cap',lo,hi,height,height+.05,'furniture','guard',t+.04)
 for op in ops:
  a,b=op['start'],op['end'];sill=op.get('sill',0);head=op['head'];oid=op['id'];typ=op['type'];isdoor=typ in ['door','glassdoor'] or oid in ['G_BATH','G_BALCONY']
  APERTURES.append(dict(op,axis='X' if h else 'Y',line=v,world_bottom=z+sill,world_top=z+head))
  for tag,u,U,k,K in [('L',a,a+.035,sill,head),('R',b-.035,b,sill,head),('T',a,b,head-.035,head)]+([] if isdoor else [('B',a,b,sill,sill+.035)]):piece(oid+tag,u,U,k,K,'frame','frame',t+.02)
  if oid=='D_RS_ENTRY':continue # same aligned portal as D_ROOF_ACCESS, no duplicate leaf
  door_mat='furniture' if typ=='door' else 'frosted' if oid=='G_BATH' else 'glass'
  leaf=piece(oid+'_leaf' if isdoor else oid+'_pane',a+.036,(a+b)/2-.012 if oid=='D_COURT' else b-.036,sill+.015,head-.036,door_mat,'door' if isdoor else 'glass',.035 if typ=='door' else .012)
  if oid=='D_COURT':
   other=piece(oid+'_leaf_R',(a+b)/2+.012,b-.036,sill+.015,head-.036,door_mat,'door',.012);other['hinge_world']=[v,b,z];other['operation']='outward';piece(oid+'_meeting_stile',(a+b)/2-.018,(a+b)/2+.018,sill,head,'frame','door',.035)
   piece(oid+'_handle_L',(a+b)/2-.15,(a+b)/2-.09,.98,1.02,'frame','door',.12)
  if isdoor:
   leaf['operation']='double outward' if oid=='D_COURT' else 'hinged';leaf['hinge_world']=[a,v,z] if h else [v,a,z];leaf['opening_clear_width']=b-a-.07;DOORS[oid]=leaf
   piece(oid+'_handle',b-.2,b-.09,.98,1.02,'frame','door',.12)
  elif b-a>1.8:piece(oid+'_mullion',(a+b)/2-.018,(a+b)/2+.018,sill,head,'frame','frame',.04)
# Duplicate RSN/H_S walls overlap across only 0.1 m. Both openings align, preserving a single portal.
st=D['stairs'][0];sx,sy,ex,ey=st['footprint']
for i in range(21):box(f'ST12_step_{i+1:02}',[sx+i*.36,sy,0,sx+(i+1)*.36,ey,(i+1)*.15],1,'stairs','ST12','floor')
bar('ST12_handrail',[sx,sy+.07,1.05],[ex,sy+.07,4.2],.035,1,'ST12')
for i in range(0,22,3):bar('ST12_post'+str(i),[sx+i*.36,sy+.07,i*.15],[sx+i*.36,sy+.07,i*.15+.95],.023,1,'ST12')
# Each flight has ten treads and eleven rises; shared turnaround landing = +4.95 m.
for i in range(10):
 top=3.3+(i+1)*.15;yy=-2.1-i*.28
 box(f'ST23_up_{i+1:02}',[12.2,yy-.28,top-.2,13.4,yy,top],2,'stairs','ST23','floor')
 top=4.95+(i+1)*.15;yy=-4.9+i*.28
 box(f'ST23_return_{i+1:02}',[10.8,yy,top-.2,12,yy+.28,top],2,'stairs','ST23','floor')
slab('ST23_midlanding',[10.8,-5.9,13.4,-4.9],4.95,2,'stairs','floor')
for xx in [12.3,13.3]:bar('ST23_lower_stringer'+str(xx),[xx,-2.1,3.32],[xx,-4.9,4.72],.075,2,'ST23','stairs','dark')
for xx in [10.9,11.9]:bar('ST23_upper_stringer'+str(xx),[xx,-4.9,4.97],[xx,-2.1,6.37],.075,2,'ST23','stairs','dark')
for n,a,b in [('east',[12.22,-2.1,4.35],[12.22,-4.9,5.85]),('west',[11.98,-4.9,6],[11.98,-2.1,7.5])]:bar('ST23_rail_'+n,a,b,.035,2,'ST23')
for xx in [12.22,11.98]:
 for j in [0,3,6,9]:
  yy=-2.1-j*.28 if xx>12 else -4.9+j*.28;zz=3.3+(j+1)*.15 if xx>12 else 4.95+(j+1)*.15
  bar('ST23_post'+str(xx)+str(j),[xx,yy,zz],[xx,yy,zz+.9],.02,2,'ST23')
# Ground-to-roof supports sit outside approved room footprints.
for i,(xx,yy) in enumerate(D['courtyard']['supports']['points']):box('terrace_column'+str(i),[xx-.12,yy-.12,0,xx+.12,yy+.12,3.08],1,'structure','TERRACE_PUBLIC','stone')
for i,(xx,yy) in enumerate([(10.55,-6.15),(14.65,-6.15),(14.65,-1.85)]):box('annex_column'+str(i),[xx-.12,yy-.12,0,xx+.12,yy+.12,3.08],1,'structure','RS','stone')
for key,b in D['ground_exterior'].items():
 if isinstance(b,list):box(key,[b[0],b[1],-.06,b[2],b[3],.01],0,'patio',key,'stone')
def rail(id,a,b,z,height=1.1,l=2):
 length=math.dist(a,b);count=math.ceil(length/.8)
 for i in range(count+1):
  p=Vector(a).lerp(Vector(b),i/count);bar(id+'_post'+str(i),[*p,z],[*p,z+height],.022,l,id)
 for k in [.15,.4,.65,height]:bar(id+'_horizontal'+str(k),[*a,z+k],[*b,z+k],.022,l,id)
for i,(a,b) in enumerate([([15.2,-3.1],[23.3,-3.1]),([23.3,-3.1],[23.3,7.9]),([21.1,7.9],[23.3,7.9]),([15.2,-3.1],[15.2,-1.6])]):rail('terrace_rail'+str(i),a,b,3.3)
for j in range(13):box('privacy_slat'+str(j),[21.1,1.65,3.3+j*.125,23.3,1.75,3.36+j*.125],2,'privacy','TERRACE_PUBLIC','furniture')
# Furniture code is shared with the existing builder; footprints come solely from P4.
tree=ast.parse((R/'scripts/build_p23.py').read_text('utf8'))
loop=next(n for n in tree.body if isinstance(n,ast.For) and isinstance(n.iter,ast.Subscript) and ast.unparse(n.iter)=="D['furniture']")
furniture_code=ast.unparse(loop)
furniture_code=furniture_code.replace("k = f['kind']", "k = f['kind']; MAT['fabric'] = material('cloth_'+id, tuple(int(f.get('color','#82958b')[j:j+2],16)/255 for j in (1,3,5)))")
furniture_code=furniture_code.replace("1.9 if shelf", ".7 if id == 'C02' else 1.9 if shelf")
basef=copy.deepcopy(D['furniture']);D['furniture']=[f for f in basef if f['kind']!='shower']
exec(compile(furniture_code,str(R/'scripts/build_p23.py'),'exec'))
D['furniture']=basef
# Real mirrors, shower screens and the supporting furniture surfaces.
for ob in list(S.objects):
 if ob.get('category')=='furniture' and ('mirror' in ob.name):ob.data.materials.clear();ob.data.materials.append(MAT['mirror'])
for f in basef:
 if f['kind']!='shower':continue
 x,y,X,Y=f['box'];z=(f['level']-1)*3.3
 box(f['id']+'_tray',[x,y,z+.01,X,Y,z+.06],2,'furniture',f['id'],'white')
 box(f['id']+'_screen',[X-.015,y,z+.06,X,Y,z+2.15],2,'furniture',f['id'],'glass')
 bar(f['id']+'_pipe',[x+.2,y+.05,z+.85],[x+.2,y+.05,z+2],.018,2,f['id'],'furniture')
 cyl(f['id']+'_head',[x+.2,y+.18,z+2],.12,.018,2,'furniture',f['id'],'frame')
for f in D['courtyard']['furniture']:
 x,y,X,Y=f['box'];id=f['id'];z=3.3
 if f['kind']=='planter':
  ht=.95 if id=='T07' else .55;box(id+'_planter',[x,y,z,X,Y,z+ht],2,'terrace_furniture',id,'stone');box(id+'_soil',[x+.05,y+.05,z+ht,X-.05,Y-.05,z+ht+.01],2,'terrace_furniture',id,'soil')
  count=max(1,int(max(X-x,Y-y)/.6))
  for j in range(count):
   xx=x+(X-x)*(j+.5)/count if X-x>Y-y else (x+X)/2;yy=(y+Y)/2 if X-x>Y-y else y+(Y-y)*(j+.5)/count
   bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.23,location=(xx,yy,z+ht+.16));register(bpy.context.object,id+'_plant'+str(j),2,'terrace_furniture',id,'garden')
 else:
  temp=dict(f,room='TERRACE_PUBLIC',level=2,color='#a2ad98');D['furniture']=[temp];exec(compile(furniture_code,'shared_furniture','exec'))
  if id=='T01':
   # Patio sofa faces south towards table; move back to north within same footprint.
   ob=bpy.data.objects.get(id+'_back');ob.location.y=Y-(ob.dimensions.y/2)
D['furniture']=basef
for xx,yy in D['courtyard']['drainage']['primary_points']:box('terrace_drain_'+str(xx),[xx-.08,yy-.05,3.301,xx+.08,yy+.05,3.31],2,'drain','TERRACE_PUBLIC','frame')
# Roof parapets derived from union boundary, never used to constrain interiors.
cells=rect_cells(mainroof);edges={}
for b in cells:
 for a,c in [((b[0],b[1]),(b[2],b[1])),((b[2],b[1]),(b[2],b[3])),((b[2],b[3]),(b[0],b[3])),((b[0],b[3]),(b[0],b[1]))]:
  if a[1]==c[1]:
   # Subdivide horizontal runs at every cell endpoint for exact shared-edge cancellation.
   cuts=sorted(set([a[0],c[0]]+[v for bb in cells for v in [bb[0],bb[2]] if min(a[0],c[0])<v<max(a[0],c[0])]))
   parts=[((u,a[1]),(v,a[1])) for u,v in zip(cuts,cuts[1:])]
  else:parts=[tuple(sorted([a,c]))]
  for e in parts:edges[e]=edges.get(e,0)+1
for i,(e,count) in enumerate(edges.items()):
 if count!=1:continue
 a,b=e;h=a[1]==b[1];box('roof_edge'+str(i),[min(a[0],b[0])-.06,min(a[1],b[1])-.06,6.6,max(a[0],b[0])+.06,max(a[1],b[1])+.06,6.92],3,'roof_edge','roof','stone')
# Site, garage, pedestrian route and garden.
T=D['site'];slab('site',T['bounds'],-.08,0,'site','garden')
paths=list(T['side_paths']);p=T['entry_path'];hw=T['path_width']/2
for a,b in zip(p,p[1:]):paths.append([min(a[0],b[0])-hw,min(a[1],b[1])-hw,max(a[0],b[0])+hw,max(a[1],b[1])+hw])
multi_slab('site_path',paths,[], -.005,0,'path','stone')
x,y,X,Y=T['garage_outer'];slab('garage_floor',[x,y,X,Y],0,0,'garage','stone');slab('garage_roof',[x-.1,y-.1,X+.1,Y+.1],2.95,0,'garage_roof','stone')
for i,b in enumerate([[x,y,x+.2,Y],[X-.2,y,X,Y],[x,Y-.2,8.3,Y],[9.3,Y-.2,X,Y]]):box('garage_wall'+str(i),[b[0],b[1],0,b[2],b[3],2.73],0,'garage',mat='stone')
box('garage_exit_header',[8.3,Y-.2,2.2,9.3,Y,2.73],0,'garage',mat='stone')
bx,by,bX,bY=T['bounds']
for i,b in enumerate([[bx,by,bx+.2,bY],[bX-.2,by,bX,bY],[bx,bY-.2,bX,bY],[bx,by,2.9,by+.2],[9.3,by,20.1,by+.2],[21.7,by,bX,by+.2]]):box('site_wall'+str(i),[b[0],b[1],0,b[2],b[3],2.2],0,'site_wall',mat='stone')
for j in range(25):box('garage_gate_louver'+str(j),[2.9,by-.015,j*.095,9.3,by+.045,j*.095+.055],0,'site_gate',mat='frame')
for j in range(15):box('pedestrian_gate_slat'+str(j),[20.1,by-.02,j*.14,21.7,by+.08,j*.14+.11],0,'site_gate',mat='furniture')
for i,(xx,yy) in enumerate(T['trees']):
 cyl('tree_trunk'+str(i),[xx,yy,1.2],.12,2.4,0,'landscape',mat='furniture')
 for j in range(3):
  bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.9,location=(xx+(j-1)*.35,yy,2.3+j*.32));register(bpy.context.object,'tree_crown'+str(i)+str(j),0,'landscape',mat='garden')
# Physical brand assets. Mount positions are resolved onto actual walls/furniture.
def instance(asset,id,pos,normal,size,l,cat='brand'):
 with bpy.data.libraries.load(str(AS/'独立模型'/(asset+'.blend')),link=False) as (a,b):b.objects=[n for n in a.objects]
 root=bpy.data.objects.new(id,None);collection(l,cat).objects.link(root);root.location=pos
 n=Vector(normal);right=Vector((0,0,1)).cross(n).normalized() if abs(n.z)<.9 else Vector((1,0,0));up=right.cross(-n).normalized();rot=Matrix((right,-n,up)).transposed().to_4x4();root.rotation_euler=rot.to_euler()
 root.scale=(size[0]/( .44 if asset.startswith('NAME') else .5 if 'SCULPTURE' in asset else 1.6),1,size[1]/(.19 if asset.startswith('NAME') else .65 if 'SCULPTURE' in asset else .76))
 root['level']=l;root['category']=cat;root['source_id']=id;root['camera_facing']=False;root['asset']=asset
 for o in b.objects:
  if o is None or o.type not in ['MESH','FONT']:continue
  if o.get('optional_backlight'):bpy.data.objects.remove(o,do_unlink=True);continue
  collection(l,cat).objects.link(o);o.parent=root;o['source_id']=id;o['category']=cat;o['level']=l;o.hide_render=False;o.hide_viewport=False
 return root
def attach_wall(br):
 pos=Vector(br['position']);r=next((r for r in D['rooms'] if r['id']==br['room']),None);candidates=[]
 if r is None:return list(pos),br['normal'],'explicit carrier'
 rb=r['box'];width,height=br['size']
 for w in WALLS:
  if w['level']!=br['level'] or w['id']=='GUARD':continue
  h=abs(w['a'][1]-w['b'][1])<.001;axis=0 if h else 1;v=w['a'][1-axis];lo=w['a'][axis];hi=w['b'][axis];z=(br['level']-1)*3.3
  # Only existing wall segments at this room perimeter, with inward-facing normal.
  choices=[(rb[1],(0,1,0)),(rb[3],(0,-1,0))] if h else [(rb[0],(1,0,0)),(rb[2],(-1,0,0))]
  valid=[n for edge,n in choices if abs(edge-v)<.25]
  if not valid:continue
  n=valid[0];a=max(lo,rb[axis])+width/2+.05;b=min(hi,rb[axis+2])-width/2-.05
  if a>b:continue
  for i in range(61):
   u=a+(b-a)*i/60;zz=min(z+2.7-height/2,max(z+1.35,pos.z));pp=Vector((u,v,zz) if h else (v,u,zz));pp+=Vector(n)*(w['thickness']/2+.038)
   obs=[o for o in OPS if o['wall']==w['id'] and u+width/2>o['start'] and u-width/2<o['end'] and zz+height/2>z+o.get('sill',0) and zz-height/2<z+o['head']]
   if not obs:candidates.append(((pp-pos).length,pp,n,w['id']))
 if not candidates:return list(pos),br['normal'],'stand required'
 _,pp,n,wid=min(candidates,key=lambda c:c[0]);return list(pp),list(n),wid
for br in D['brands']:
 id=br['id'];pos,n,carrier=attach_wall(br);asset='HG_NEON_'+br['variant'] if br['kind']=='neon' else 'HG_PLAQUE_'+br['variant']
 if id=='BR_BAL_M':pos=[22,7.75,4.13];carrier='BAL rail';n=[0,-1,0]
 if id=='BR_TERRACE_N':pos=[18.5,1.56,5.05];carrier='B1S';n=[0,-1,0]
 if id=='BR_TERRACE_M':pos=[16.138,-2.1,4.1];carrier='T07';n=[1,0,0]
 if id=='BR_EXT_N':pos=[18.5,-16.838,1.7];carrier='site_wall';n=[0,-1,0]
 if id=='BR_EXT_M':pos=[25.762,-8.5,1.8];carrier='site_wall';n=[-1,0,0]
 if id=='BR_B1_STAND':asset='HG_SCULPTURE_normal';pos=[14.1,4.5,4.0+.2775*(br['size'][1]/.65)];n=[1,0,0];carrier='A02 top'
 if id=='BR_B1_FABRIC':
  # UV-fixed print lies on the mattress surface, never facing the camera.
  pos=[16,6.15,3.862];bpy.ops.mesh.primitive_plane_add(size=1,location=pos);ob=register(bpy.context.object,id,2,'brand',id,None);ob.scale=(.22,.22,1)
  m=bpy.data.materials.new('bed_icon_print');m.use_nodes=True;nt=m.node_tree;im=nt.nodes.new('ShaderNodeTexImage');im.image=bpy.data.images.load(str(AS/'品牌贴图/HG_ICON.png'));im.image.pack();p=nt.nodes.get('Principled BSDF');nt.links.new(im.outputs['Color'],p.inputs['Base Color']);nt.links.new(im.outputs['Alpha'],p.inputs['Alpha']);p.inputs['Roughness'].default_value=.95;m.surface_render_method='DITHERED';ob.data.materials.append(m);carrier='A01 mattress'
 else:
  if carrier=='stand required':
   # Open-plan room has no wall at the diagram label: use a floor-supported slim art stand.
   z=(br['level']-1)*3.3;xx,yy,zz=pos
   box(id+'_standbase',[xx-.16,yy-.16,z,xx+.16,yy+.16,z+.04],br['level'],'brand_support',id,'frame');bar(id+'_standpost',[xx,yy,z],[xx,yy,zz],.018,br['level'],id,'brand_support')
  ob=instance(asset,id,pos,n,br['size'],br['level']);ob['variant']=br['variant'];ob['domain']=br['domain'] or '';ob['carrier']=carrier
  if br['light']=='backlight':
   bpy.ops.object.light_add(type='AREA',location=Vector(pos)-Vector(n)*.02);light=register(bpy.context.object,id+'_backlight',br['level'],'brand_light',id,None);light.data.energy=2;light.data.color=(1,.67,.23);light.data.shape='RECTANGLE';light.data.size=br['size'][0]*.8;light.data.size_y=br['size'][1]*.8;light.rotation_euler=Vector(n).to_track_quat('Z','Y').to_euler()
 ATTACH.append(dict(id=id,plan_position=br['position'],realized_position=pos,normal=n,size=br['size'],variant=br['variant'],carrier=carrier,light=br['light'],domain=br['domain'],camera_facing=False))
for rid,label in [('B1','薇亚の窝'),('B2','子豪の窝'),('B3','舒亚の窝')]:
 op=next(o for o in OPS if o['id']=='D_'+rid);ob=instance('NAME_'+rid,'NAME_'+rid,[(op['start']+op['end'])/2,1.665,4.85],[0,-1,0],[.44,.19],2,'nameplate');ob['exact_text']=label
 parent=DOORS['D_'+rid];world=ob.matrix_world.copy();bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=parent;ob.matrix_world=world
instance('NAME_BW','NAME_BW',[.04,-.12,4.85],[1,0,0],[.44,.19],2,'nameplate')['exact_text']='公共浴室'
# Daylight, ceiling lights and persisted diagnostic cameras.
bpy.ops.object.light_add(type='SUN',location=(0,0,20));sun=bpy.context.object;sun.name='day_sun';sun.rotation_euler=(.5,-.45,-.6);sun.data.energy=2.2;sun.data.angle=.15
for r in D['rooms']:
 if r['id'] in ['BAL','B','C','SUP','RS3']:continue
 x,y,X,Y=r['box'];z=(r['level']-1)*3.3
 bpy.ops.object.light_add(type='AREA',location=((x+X)/2,(y+Y)/2,z+3));o=register(bpy.context.object,'ceiling_'+r['id'],r['level'],'light',r['id'],None);o.data.energy=18*math.sqrt((X-x)*(Y-y));o.data.shape='DISK';o.data.size=min(3,X-x,Y-y)
def camera(id,pos,target,scale=None,lens=28):
 bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name=id;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_end=300;o.data.clip_start=.03
 if scale:o.data.type='ORTHO';o.data.ortho_scale=scale
 CAM.append(dict(id=id,pos=pos,target=target,ortho_scale=scale,lens=lens));return o
camera('01_完整外观',[43,-46,34],[10,-1,3.3],48)
camera('02_二楼剖开总览',[33,-29,37],[10,1.6,3.5],33)
camera('03_一楼剖开总览',[32,-28,34],[10,3,0],33)
camera('04_公共庭院',[24.7,-5.5,6.1],[17.8,.5,4.4],None,24)
camera('05_走廊朝浴室',[14.5,.75,4.9],[-.2,.75,4.8],None,23)
camera('06_大姐卧室',[19.5,2.8,5.05],[14.5,6.2,4.1],None,22)
camera('07_二楼正投影',[10,1.4,35],[10,1.4,3.3],30)
camera('08_屋顶楼梯剖开',[19,-11,14],[12.2,-3.7,5.4],12)
S.camera=bpy.data.objects['01_完整外观'];S['model_revision']='P4-M1';S['approved_plan_sha256']=hashlib.sha256(P.read_bytes()).hexdigest();S['status']='按用户确认P4重建；影视空间模型；模型视图待用户验收';S['daylight']='day';S['plan_is_authority']=True
bpy.context.view_layer.update()
objects=[]
for o in S.objects:
 if o.type!='MESH':continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];objects.append(dict(id=o.name,source=o.get('source_id',''),category=o.get('category',''),level=o.get('level',0),bbox=[min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)]))
meta=dict(revision='P4-M1',status=S['status'],plan_sha256=S['approved_plan_sha256'],plan=D,objects=objects,apertures=APERTURES,brand_attachments=ATTACH,cameras=CAM,limitations=['家具及建筑为影视空间资产，不是施工结构模型。','植物、软装与材料为基础表现；后续实景图仍需逐张验收。','品牌贴装点随真实载体校正；房间、家具平面不变，变更记录见品牌固定变换。'])
(O/'数据/模型空间数据.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),'utf8');(O/'数据/品牌固定变换.json').write_text(json.dumps(ATTACH,ensure_ascii=False,indent=2),'utf8')
txt=bpy.data.texts.new('模型空间数据.json');txt.write(json.dumps(meta,ensure_ascii=False));txt=bpy.data.texts.new('品牌文字可编辑源.json');txt.write((AS/'品牌贴图/品牌文字源.json').read_text('utf8'))
bpy.context.preferences.filepaths.save_version=0;bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=str(O/'模型/秘密教学_P4-M1.blend'),compress=True)
bpy.ops.export_scene.gltf(filepath=str(O/'模型/秘密教学_P4-M1.glb'),export_format='GLB',export_cameras=True,export_extras=True,export_apply=True)
print('P4_MODEL_SAVED',len(objects),flush=True)
if '--render' in sys.argv:
 for cam in CAM:
  cid=cam['id'];hidden=[]
  for o in S.objects:
   lev=o.get('level',0);cat=o.get('category','')
   hide=False
   if cid.startswith(('02','07')):hide=lev>=3 or cat in ['roof','roof_edge','garage_roof']
   if cid.startswith('03'):hide=lev>=2 or cat in ['roof','roof_edge','garage_roof']
   if cid.startswith('08'):hide=cat in ['roof','roof_edge'] or (cat in ['wall','frame','glass','door'] and ('RSE' in o.get('source_id','') or 'RSS' in o.get('source_id','') or 'R3E' in o.get('source_id','') or 'R3S' in o.get('source_id',''))) or (cat=='brand' and o.get('source_id')=='BR_RS_N')
   if hide and not o.hide_render:o.hide_render=True;hidden.append(o)
  S.camera=bpy.data.objects[cid];S.render.filepath=str(O/'预览'/(cid+'.png'));bpy.ops.render.render(write_still=True)
  for o in hidden:o.hide_render=False
  print('P4_RENDERED',cid,flush=True)
