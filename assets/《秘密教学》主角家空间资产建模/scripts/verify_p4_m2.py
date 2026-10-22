"""Independent saved Blend/GLB checks, including preserved M1 geometry and new routes."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=(R/'scripts/verify_p4_model.py').read_text('utf8').replace('P4-M1','P4-M2')
src=src.replace("for k in ['rooms','furniture','stairs']:ck('平面数据原样保留_'+k,D[k]==M['plan'][k])", "ck('室内家具数据原样保留',D['furniture']==M['plan']['furniture'])\nck('非屋顶梯间房间原样保留',[r for r in D['rooms'] if r['id'] not in ['RS','RS3']]==M['plan']['rooms'])\nck('直梯数据原样保留',D['stairs'][0]==M['plan']['stairs'][0])")
src=src.replace("('屋顶梯间入口',[[10,-.8],[13.9,-.8],[13.9,-2.3],[12.8,-2.3]])", "('后侧室外楼梯入口',M['plan']['roof_access']['floor_route'])")
src=src.replace("for stair,lev,z in [(D['stairs'][0],2,3.3),(D['stairs'][1],3,6.6)]:", "for stair,lev,z in [(D['stairs'][0],2,3.3),(M['plan']['stairs'][1],3,6.6)]:")
src=src.replace("ck('40个品牌位置固定',len(M['brand_attachments'])==40", "ck('41个品牌位置固定',len(M['brand_attachments'])==41")
extra=r'''
old=json.loads((R/'全屋模型_P4-M1_20261022/数据/模型空间数据.json').read_text('utf8'))
old_objects={o['id']:o for o in old['objects']}
new_objects={o['id']:o for o in M['objects']}
unchanged=[]
for oid,oo in old_objects.items():
 if oo['category'] in ['furniture','nameplate'] or oid.startswith(('ST12_','G_BATH','W_SHUYA_OPPOSITE','D_COURT','D_B1','D_B2','D_B3','short_guard')):
  nn=new_objects.get(oid)
  if not nn or max(abs(x-y) for x,y in zip(oo['bbox'],nn['bbox']))>1e-5:unchanged.append(oid)
ck('M1室内家具门窗门牌直梯护栏真实网格包围盒不变',not unchanged,unchanged)
ck('旧正面梯间墙体和支柱已移除',not any(o.name.startswith(('annex_column','stairhouse_cap','ceiling_RS')) or any(w in o.get('source_id','').split('|') for w in ['RSS','RSN','RSW','RSE','R3S','R3N','R3W','R3E']) for o in meshes))
ck('旧屋顶入口已封闭','D_ROOF_ACCESS_leaf' not in bpy.data.objects and not any(o['id']=='D_ROOF_ACCESS' for o in M['apertures']))
ck('主屋面取消旧梯间外凸',all(b[1]>-2 for b in M['plan']['roof_outline']))
ck('户外通道净宽至少1.2',24.85-.022-(23.55+.022)>=1.2)
ck('转接平台栏杆间净深至少1.5',7.85-.022-(6.25+.022)>=1.5)
ck('阳台外侧公私分隔仍完整',any(o.name.startswith('terrace_rail') and o.get('category')=='guard' and abs(o.location.x-23.3)<.03 for o in meshes) and sum(o.name.startswith('access_privacy') for o in meshes)==36)
# Exact surface rays rather than AABB-only collision checks for new 3D paths.
from mathutils.bvhtree import BVHTree
verts=[];faces=[]
floorverts=[];floorfaces=[]
for ob in meshes:
 cat=ob.get('category','')
 if cat in ['wall','guard','structure','privacy','weather_screen','canopy','furniture','terrace_furniture','roof_edge']:
  off=len(verts);verts += [tuple(ob.matrix_world@v.co) for v in ob.data.vertices];faces += [tuple(off+i for i in p.vertices) for p in ob.data.polygons]
 if cat in ['slab','finish','stairs','access_slab','roof']:
  off=len(floorverts);floorverts += [tuple(ob.matrix_world@v.co) for v in ob.data.vertices];floorfaces += [tuple(off+i for i in p.vertices) for p in ob.data.polygons]
bvh=BVHTree.FromPolygons(verts,faces);fbvh=BVHTree.FromPolygons(floorverts,floorfaces)
def routecheck(name,points):
 hits=[];missing=[];samples=0
 for a,b in zip(points,points[1:]):
  n=max(1,math.ceil(math.dist(a,b)/.06))
  for j in range(n+1):
   p=Vector(a).lerp(Vector(b),j/n);samples+=1
   for dx,dy in [(0,0),(.2,0),(-.2,0),(0,.2),(0,-.2)]:
    origin=p+Vector((dx,dy,.21));hit=bvh.ray_cast(origin,Vector((0,0,1)),1.99)
    if hit[0] is not None:hits.append([round(v,3) for v in origin])
   hit=fbvh.ray_cast(p+Vector((0,0,.2)),Vector((0,0,-1)),.43)
   if hit[0] is None:missing.append([round(v,3) for v in p])
 ck(name+'人体通行和2.2米净高',not hits,dict(samples=samples,hits=hits[:15]))
 ck(name+'下方连续踏面',not missing,missing[:15])
routecheck('公共庭院到新楼梯',[[*p,3.3] for p in M['plan']['roof_access']['floor_route']])
routecheck('屋顶出口连接',[[*p,6.6] for p in M['plan']['roof_access']['upper_route']])
routecheck('双跑梯',[[26,7.8,3.45]]+[[26,7.8+(i+.5)*.28,3.3+(i+1)*.15] for i in range(10)]+[[26,11.35,4.95],[24.6,11.35,4.95]]+[[24.6,10.6-(i+.5)*.28,4.95+(i+1)*.15] for i in range(10)]+[[24.6,7.75,6.6]])
for bid in ['BR_L_N','BR_D_M','BR_L_TABLE','BR_D_TABLE']:
 ob=bpy.data.objects[bid];texts={q.get('exact_text') for q in ob.children}
 ck(bid+'真实浮雕图标及文字',ob.get('glyph_geometry') and {'黄瓜','短剧','hgdju.com'}<=texts)
 ck(bid+'均匀缩放无镜头约束',max(ob.scale)-min(ob.scale)<1e-6 and not ob.constraints)
 ck(bid+'非发光材质',all(not m.use_nodes or not m.node_tree.nodes.get('Principled BSDF') or m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value==0 for q in ob.children for m in q.data.materials))
for bid,table in [('BR_L_TABLE','L04_top'),('BR_D_TABLE','D01_top')]:
 a=bbox(bpy.data.objects[bid+'_base']);b=bbox(bpy.data.objects[table]);ck(bid+'底座落桌且不超桌边',abs(a[2]-b[5])<1e-4 and a[0]>=b[0] and a[3]<=b[3] and a[1]>=b[1] and a[4]<=b[4])
for bid in ['BR_L_N','BR_D_M']:
 ob=bpy.data.objects[bid];bb=[bbox(q) for q in ob.children];aa=[min(b[i] for b in bb) for i in range(3)]+[max(b[i+3] for b in bb) for i in range(3)]
 overlap=[]
 for q in meshes:
  if q.get('category') not in ['glass','door','furniture']:continue
  b=bbox(q)
  if all(min(aa[i+3],b[i+3])-max(aa[i],b[i])>.002 for i in range(3)):overlap.append(q.name)
 ck(bid+'避让门窗家具',not overlap,overlap)
'''
src=src.replace("blend_count=len(meshes)",extra+"\nblend_count=len(meshes)")
exec(compile(src,str(R/'scripts/verify_p4_model.py'),'exec'))
