"""P4-M2 amendment; reuse the reviewed M1 construction primitives without editing M1.
Run with Blender --background --python this_file [-- --render].
"""
from pathlib import Path
import json, copy
R=Path(__file__).resolve().parents[1]
source=(R/'scripts/build_p4_model.py').read_text('utf8')
def replace(old,new):
 global source
 assert source.count(old)==1, (old[:90],source.count(old))
 source=source.replace(old,new)
def section(start,end,new):
 global source
 a=source.index(start);b=source.index(end,a)
 source=source[:a]+new+'\n'+source[b:]
source=source.replace('P4-M1','P4-M2')
replace("D=json.loads(P.read_text('utf8'))", "D=json.loads(P.read_text('utf8'))\n"+r'''
# Approved interiors remain byte-equivalent as data; only the external amendment changes.
D['revision']='P4-M2';D['status']='用户授权后侧室外屋顶通路及客餐厅品牌修订；立体效果待审阅'
D['rooms']=[r for r in D['rooms'] if r['id'] not in ['RS','RS3']]
D['walls']=[w for w in D['walls'] if not w['id'].startswith('RS')]
D['openings']=[o for o in D['openings'] if o['id'] not in ['D_RS_ENTRY','D_ROOF_ACCESS']]
for key in ['roof_outline']:
 D[key]=[b for b in D[key] if b[1]>-2]
D['roof_levels']['main_roof']['rectangles']=copy.deepcopy(D['roof_outline'])
D['roof_levels']['lower_roof']['subtract']=[b for b in D['roof_levels']['lower_roof']['subtract'] if b[1]>-4]
D['roof_levels'].pop('stairhouse')
D['roof_levels']['exit_canopy']={'box':[23.85,6.15,25.35,8.3],'underside':9.05,'top':9.15}
D['stairs'][1].update(footprint=[24,7.8,26.6,12.1],opening=[24,7.8,26.6,12.1],landing_depth=1.5,direction='北上南返',outdoor=True)
# East planter moves outwards, opening access without rearranging seating or interiors.
D['courtyard']['box'][2]=25.7
D['courtyard']['net_area']=round((25.7-15.3)*4.6,2)
next(f for f in D['courtyard']['furniture'] if f['id']=='T05')['box']=[25.1,-2.85,25.55,1.45]
D['courtyard']['supports']['points'] += [[25.6,-2.8],[25.6,1.45]]
D['site']['bounds'][2]=29.5
D['site']['side_paths'][1]=[27.5,-10,28.7,14.2]
D['site']['side_paths'][2]=[-5.3,13,28.7,14.2]
D['site']['building_bounds']=[-3.9,-3.1,26.75,12.2]
D['site']['source']='P4-M2先保留内部，再推导后侧屋顶通路及35.50×32.20m地块范围'
D['ground_exterior']['note']='原正面楼梯间已移除；原入口地面保留为露天铺装'
D['roof_access']={
 'route':'公共庭院→阳台外独立通道→东北后侧室外双跑梯→屋顶东侧',
 'walkway_box':[23.5,1.6,24.9,6.3], 'clear_width':1.2,
 'bottom_landing':[23.5,6.3,26.75,7.8], 'landing_clear_depth':1.5,
 'upper_bridge':[21.1,6.3,25.25,7.8], 'upper_elevation':6.6,
 'floor_route':[[13.9,-.25],[16.3,-.25],[16.3,-.75],[21.9,-.75],[24.2,-.75],[24.2,7.05],[26,7.05],[26,7.8]],
 'upper_route':[[24.6,7.8],[24.6,7.05],[20.5,7.05]],
 'privacy':'保留私人阳台外栏杆；新增外侧木格栅，不开公共阳台入口',
 'materials':['浅米色石材','深灰金属','木饰面'],
 'drainage':'通道外缘线性排水及后侧雨水管；坡度和支承为影视模型构造，非施工验算'}
D['routes'][2]={'id':'R23','level':2,'points':D['roof_access']['floor_route'],'note':D['roof_access']['route']}
old_att=json.loads((R/'全屋模型_P4-M1_20261022/数据/品牌固定变换.json').read_text('utf8'))
old_att={b['id']:b for b in old_att}
D['brands']=[b for b in D['brands'] if b['room']!='RS']
for b in D['brands']:
 prev=old_att[b['id']];b['fixed_position']=prev['realized_position'];b['fixed_normal']=prev['normal'];b['fixed_carrier']=prev['carrier']
for bid,pos,n,carrier in [('BR_L_N',[5.65,7.562,2.45],[0,-1,0],'1-TV 客厅实墙上部'),('BR_D_M',[9.762,9.92,1.9],[-1,0,0],'1-LW 餐厅东侧实墙')]:
 b=next(b for b in D['brands'] if b['id']==bid)
 b.update(position=pos,normal=n,size=[1.6,.76],kind='plaque',light='none',fixed_position=pos,fixed_normal=n,fixed_carrier=carrier,uniform_scale=True)
for bid,room,pos,n,width,variant,carrier in [('BR_L_TABLE','L',[4.22,4.68,.5655],[0,-1,0],.36,'mirror','L04 茶几'),('BR_D_TABLE','D',[7.5,9.8,.886875],[0,1,0],.45,'normal','D01 餐桌')]:
 D['brands'].append(dict(id=bid,room=room,level=1,carrier=carrier,position=pos,normal=n,size=[width,width*.76/1.6],variant=variant,kind='plaque',light='none',main=False,master='HG_FULL_'+variant,domain='hgdju.com',fixed_to_carrier=True,camera_facing=False,fixed_position=pos,fixed_normal=n,fixed_carrier=carrier,uniform_scale=True))
D['authorization_updates'].append('P4-M2：用户批准后侧室外屋顶通路，补充放大客餐厅正向/镜像实体品牌；保留室内布局')
D['unresolved']=['新模型立体效果待用户审阅；旧P4-M1及原认可图保留。','室外结构支承、基础与排水构造为影视模型表达，未作施工验算。','后续写实场景图仍需逐张核对家具、品牌与跨机位一致性。']
''')
section("sh=D['roof_levels']['stairhouse']", '# Union co-linear shared walls', '# No enclosed rooftop box in M2.')
section('# Each flight has ten treads', '# Ground-to-roof supports', '# ST23 is rebuilt outdoors below after rail helpers are defined.')
section("for i,(xx,yy) in enumerate([(10.55", 'for key,b in D[', '# Former south annex support columns removed.')
replace("([23.3,-3.1],[23.3,7.9])", "([25.8,-3.1],[25.8,1.7])")
replace("([15.2,-3.1],[23.3,-3.1])", "([15.2,-3.1],[25.8,-3.1])")
replace("([21.1,7.9],[23.3,7.9])", "([21.1,7.9],[23.3,7.9]),([23.3,1.7],[23.3,7.9]),([24.9,1.7],[25.8,1.7])")
replace('# Furniture code is shared',r'''
# Independent public walkway; existing private balcony rails remain uninterrupted.
for id,b,z in [('access_walk',[23.5,1.6,24.9,6.3],3.3),('access_lower',[23.5,6.2,26.75,7.9],3.3),('access_upper',[21.1,6.2,25.25,7.9],6.6),('ST23_midlanding',[24,10.6,26.6,12.1],4.95)]:slab(id,b,z,2,'stairs' if id.startswith('ST23') else 'access_slab','stone')
for i in range(10):
 yy=7.8+i*.28;top=3.3+(i+1)*.15
 box(f'ST23_up_{i+1:02}',[25.4,yy,top-.18,26.6,yy+.28,top],2,'stairs','ST23','stone')
 yy=10.6-i*.28;top=4.95+(i+1)*.15
 box(f'ST23_return_{i+1:02}',[24,yy-.28,top-.18,25.2,yy,top],2,'stairs','ST23','stone')
 for suffix,a,b in [('up',[25.4,7.8+i*.28,3.3+(i+1)*.15],[26.6,7.8+i*.28,3.3+(i+1)*.15]),('return',[24,10.6-(i+1)*.28,4.95+(i+1)*.15],[25.2,10.6-(i+1)*.28,4.95+(i+1)*.15])]:bar('ST23_nosing_'+suffix+str(i),a,b,.008,2,'ST23','nosing','frame')
for x0,z0,ya,yb in [(25.4,3.3,7.8,10.6),(26.6,3.3,7.8,10.6),(24,4.95,10.6,7.8),(25.2,4.95,10.6,7.8)]:
 bar('ST23_stringer',[x0,ya,z0-.1],[x0,yb,z0+1.55],.075,2,'ST23','structure','dark')
 bar('ST23_handrail',[x0,ya,z0+1.1],[x0,yb,z0+2.75],.028,2,'ST23')
 for j in range(23):
  t=j/22;yy=ya+(yb-ya)*t;zz=z0+1.65*t
  bar('ST23_baluster',[x0,yy,zz],[x0,yy,zz+1.1],.016,2,'ST23')
for id,a,b,z in [
 ('walk_W',[23.55,1.7],[23.55,6.3],3.3),('walk_E',[24.85,1.7],[24.85,6.3],3.3),
 ('landing_S',[24.85,6.25],[26.75,6.25],3.3),('landing_E',[26.75,6.25],[26.75,7.8],3.3),
 ('landing_N',[23.5,7.85],[25.4,7.85],3.3),('landing_W',[23.5,6.3],[23.5,7.85],3.3),
 ('mid_N',[24,12.1],[26.6,12.1],4.95),('mid_W',[24,10.6],[24,12.1],4.95),('mid_E',[26.6,10.6],[26.6,12.1],4.95),
 ('bridge_S',[21.2,6.25],[25.25,6.25],6.6),('bridge_N',[21.2,7.85],[24,7.85],6.6),('bridge_E',[25.25,6.25],[25.25,7.8],6.6)]:rail(id,a,b,z,l=2)
# Supports lie wholly outside the approved interior and balcony footprints.
for j,(xx,yy,zz) in enumerate([(23.55,1.6,3.08),(24.85,1.6,3.08),(23.55,6.3,6.38),(25.25,6.3,6.38),(26.7,7.75,3.08),(24,12.05,4.73),(26.6,12.05,4.73)]):box('access_column'+str(j),[xx-.07,yy-.07,0,xx+.07,yy+.07,zz],1,'structure','ROOF_ACCESS','dark')
for j in range(36):
 yy=1.85+j*.12
 box('access_privacy'+str(j),[23.36,yy,3.3,23.42,yy+.055,4.9],2,'privacy','ROOF_ACCESS','furniture')
box('roof_exit_canopy',[23.85,6.15,9.05,25.35,8.3,9.15],3,'canopy','ROOF_ACCESS','dark')
for xx,yy in [(23.9,6.2),(25.3,6.2),(25.3,8.25)]:bar('canopy_post',[xx,yy,6.6],[xx,yy,9.05],.035,3,'ROOF_ACCESS','structure')
box('canopy_wind_screen',[25.28,6.2,7.7,25.3,8.2,9.05],3,'weather_screen','ROOF_ACCESS','glass')
for yy in [2,5.9,7.45]:
 box('walk_drain',[24.72,yy-.1,3.301,24.78,yy+.1,3.31],2,'drain','ROOF_ACCESS','frame')
bar('access_downpipe',[26.72,11.95,.1],[26.72,11.95,4.95],.035,1,'ROOF_ACCESS','drain')
# Furniture code is shared''')
replace('# Site, garage, pedestrian route and garden.',r'''
# Open the east roof parapet only at the new upper bridge connection.
for ob in list(S.objects):
 if ob.name.startswith('roof_edge'):
  bb=[ob.matrix_world@Vector(v) for v in ob.bound_box]
  xmin=min(p.x for p in bb);xmax=max(p.x for p in bb);ymin=min(p.y for p in bb);ymax=max(p.y for p in bb)
  if abs((xmin+xmax)/2-21.2)<.01 and ymax>6.3 and ymin<7.8:
   bpy.data.objects.remove(ob,do_unlink=True)
   for a,b in [(ymin,6.3),(7.8,ymax)]:
    if b>a:box('roof_edge_bridge',[xmin,a,6.6,xmax,b,6.92],3,'roof_edge','roof','stone')
# Site, garage, pedestrian route and garden.''')
replace("def attach_wall(br):\n", "def attach_wall(br):\n if 'fixed_position' in br:return br['fixed_position'],br['fixed_normal'],br['fixed_carrier']\n")
replace("pos=[25.762,-8.5,1.8]", "pos=[29.262,-8.5,1.8]")
replace("ob=instance(asset,id,pos,n,br['size'],br['level']);", "if br.get('uniform_scale'):asset='HG_NEON_'+br['variant']\n  ob=instance(asset,id,pos,n,br['size'],br['level']);\n  if br.get('uniform_scale'):\n   ob.scale=(br['size'][0]/1.6,)*3;ob['asset']='HG_RELIEF_'+br['variant'];ob['glyph_geometry']=True\n   for child in ob.children:\n    for slot in child.material_slots:\n     if slot.material:\n      mm=slot.material.copy();mm.name='nonemissive_relief';slot.material=mm\n      if mm.use_nodes:\n       pp=mm.node_tree.nodes.get('Principled BSDF')\n       if pp:pp.inputs['Emission Strength'].default_value=0\n  if id in ['BR_L_TABLE','BR_D_TABLE']:\n   ztop=.45 if id=='BR_L_TABLE' else .75;xx,yy,_=pos;ww=br['size'][0]\n   box(id+'_base',[xx-ww*.55,yy-.085,ztop,xx+ww*.55,yy+.085,ztop+.03],1,'brand_support',id,'dark')\n  ")
# Remove the old RS-special camera and generate the explicitly requested review views.
section("camera('01_完整外观'", "S.camera=bpy.data.objects", r'''
camera('01_完整外观',[43,-46,34],[10,-1,3.3],48)
camera('02_正面低机位',[11,-45,5.5],[11,3,3.5],None,36)
camera('03_背面与新楼梯',[42,34,24],[18,6,4.7],31)
camera('04_二楼剖开总览',[38,-27,37],[12,3,3.5],35)
camera('05_后侧通路',[28,-.5,8],[24.5,8.4,4.8],None,24)
camera('06_后侧楼梯剖面',[32,10,8],[24.8,9,5.5],12)
camera('07_二楼正投影',[11,3,40],[11,3,3.3],38)
camera('08_屋顶正投影',[11,3,40],[11,3,6.6],38)
camera('09_客厅正向',[4.3,2.7,1.65],[5.4,7.6,1.7],None,23)
camera('10_客厅反向',[5.5,6.6,1.65],[3.6,3.4,.7],None,23)
camera('11_餐厅正向',[5.5,8.3,1.65],[9.8,10,1.7],None,23)
camera('12_餐厅反向',[8.7,11.5,1.65],[5.7,8.2,1.35],None,23)
camera('13_客厅竖屏',[4.22,3.0,1.35],[4.4,5.5,1.25],None,23)
camera('14_餐厅竖屏',[6,9.8,1.4],[9.6,9.9,1.5],None,23)
''')
a=source.index("if '--render' in sys.argv:")
source=source[:a]+r'''
if '--render' in sys.argv:
 requested=None
 if '--views' in sys.argv:requested=sys.argv[sys.argv.index('--views')+1].split(',')
 for cam in CAM:
  cid=cam['id']
  if requested and cid[:2] not in requested:continue
  hidden=[]
  for o in S.objects:
   lev=o.get('level',0);cat=o.get('category','');hide=False
   if cid.startswith(('04','07')):hide=lev>=3 or cat in ['roof','roof_edge','garage_roof'] or (o.location.z>6 and cat in ['access_slab','guard'])
   if cid.startswith('06'):hide=cat in ['canopy','weather_screen']
   if hide and not o.hide_render:o.hide_render=True;hidden.append(o)
  S.render.resolution_x=900 if cid.startswith(('13','14')) else 1600
  S.render.resolution_y=1600 if cid.startswith(('13','14')) else 1100
  S.camera=bpy.data.objects[cid];S.render.filepath=str(O/'预览'/(cid+'.png'));bpy.ops.render.render(write_still=True)
  for o in hidden:o.hide_render=False
  print('M2_RENDERED',cid,flush=True)
'''
exec(compile(source,str(R/'scripts/build_p4_model.py'),'exec'))
