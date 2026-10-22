"""Independent Blend/GLB readback and source geometry checks. Blender Python."""
import bpy,json,math,hashlib,sys
from pathlib import Path
from mathutils import Vector
R=Path(__file__).resolve().parents[1];O=R/'全屋模型_P4-M1_20261022';repo=R.parents[1]
P=R/'整体平面_P4_20261022/数据/整体空间方案_P4.json';D=json.loads(P.read_text('utf8'));M=json.loads((O/'数据/模型空间数据.json').read_text('utf8'))
checks=[]
def ck(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
def bbox(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [min(v[i] for v in pts) for i in range(3)]+[max(v[i] for v in pts) for i in range(3)]
bpy.ops.wm.open_mainfile(filepath=str(O/'模型/秘密教学_P4-M1.blend'));S=bpy.context.scene;bpy.context.view_layer.update()
ck('P4确认基线SHA256',S['approved_plan_sha256']==hashlib.sha256(P.read_bytes()).hexdigest())
for k in ['rooms','furniture','stairs']:ck('平面数据原样保留_'+k,D[k]==M['plan'][k])
meshes=[o for o in S.objects if o.type=='MESH'];reference={o.name:bbox(o) for o in meshes};sources={}
for o in meshes:sources.setdefault(o.get('source_id',''),[]).append(o)
for f in D['furniture']:
 obs=[o for o in sources.get(f['id'],[]) if o.get('category')=='furniture'];ck('家具存在_'+f['id'],bool(obs))
 if not obs:continue
 bb=[bbox(o) for o in obs];merged=[min(b[i] for b in bb) for i in range(3)]+[max(b[i+3] for b in bb) for i in range(3)];a=f['box'];z=(f['level']-1)*3.3
 # Thin fittings, taps and tubes may overhang the plan object; core bodies must fit.
 core=[o for o in obs if any(s in o.name for s in ['_frame','_body','_base','_top','_seat','_rug','_tray','_mirror','_round','_rim','_ball'])]
 violations=[]
 for o in core:
  b=bbox(o)
  if any([b[0]<a[0]-.051,b[1]<a[1]-.051,b[3]>a[2]+.051,b[4]>a[3]+.051]):violations.append(o.name)
 ck('家具主体占地_'+f['id'],not violations,violations)
for fid,expected in [('A01',[13.6,4.9,17.5,7.42]),('C01',[6.2,1.8,7.7,4]),('C02',[6.6,4.2,7.3,4.8])]:
 f=next(f for f in D['furniture'] if f['id']==fid);ck('用户指定尺寸_'+fid,all(abs(a-b)<1e-5 for a,b in zip(f['box'],expected)))
ck('子豪门中心9.65',abs((next(o for o in D['openings'] if o['id']=='D_B2')['start']+next(o for o in D['openings'] if o['id']=='D_B2')['end'])/2-9.65)<1e-5)
ck('浴室真实玻璃门',bpy.data.objects['G_BATH_leaf'].data.materials[0].name.startswith('frosted'))
ck('舒亚对面落地窗保留','W_SHUYA_OPPOSITE_pane' in bpy.data.objects)
ck('庭院双扇玻璃门',all(n in bpy.data.objects for n in ['D_COURT_leaf','D_COURT_leaf_R','D_COURT_meeting_stile']))
ck('两段楼梯踏步数',sum(o.name.startswith('ST12_step') for o in meshes)==21 and sum(o.name.startswith(('ST23_up_','ST23_return_')) for o in meshes)==20)
walks=[('二楼公共通路',D['routes'][1]['points']),('庭院入口及主通道',D['courtyard']['route']),('屋顶梯间入口',[[10,-.8],[13.9,-.8],[13.9,-2.3],[12.8,-2.3]]),('薇亚入口',[[14.05,.8],[14.05,2.3]]),('子豪入口',[[9.65,.8],[9.65,2.7]]),('舒亚入口',[[1.35,.8],[1.35,2.6]]),('浴室入口',[[.6,.8],[-1,.8]])]
obstacles=[(o.name,bbox(o)) for o in meshes if o.get('category') in ['wall','furniture','brand_support','terrace_furniture']]
for name,points in walks:
 hits=[];samples=0
 for a,b in zip(points,points[1:]):
  n=max(1,math.ceil(math.dist(a,b)/.08))
  for j in range(n+1):
   xx=a[0]+(b[0]-a[0])*j/n;yy=a[1]+(b[1]-a[1])*j/n;samples+=1
   for oid,bb in obstacles:
    if bb[5]<3.35 or bb[2]>5.1:continue
    dx=max(bb[0]-xx,0,xx-bb[3]);dy=max(bb[1]-yy,0,yy-bb[4])
    if dx*dx+dy*dy<.18**2:hits.append(oid)
 ck(name+'开放门扇时连续通行',not hits,dict(radius=.18,samples=samples,collisions=sorted(set(hits))))
for stair,lev,z in [(D['stairs'][0],2,3.3),(D['stairs'][1],3,6.6)]:
 x,y,X,Y=stair['opening'];blocked=[]
 for o in meshes:
  if o.get('category') not in ['slab','roof','finish'] or o.get('level')!=lev:continue
  b=bbox(o)
  if b[2]<z+.02 and b[5]>z-.25 and min(X,b[3])-max(x,b[0])>1e-4 and min(Y,b[4])-max(y,b[1])>1e-4:blocked.append(o.name)
 ck(stair['id']+'洞口没有楼板封堵',not blocked,blocked)
# Vertical headroom above tread centers, with all export geometry present.
for sid in ['ST12','ST23']:
 clear=[]
 tread=[o for o in meshes if o.name.startswith('ST12_step' if sid=='ST12' else ('ST23_up_','ST23_return_'))]
 ceilings=[o for o in meshes if o.get('category') in ['slab','roof','wall']]
 for o in tread:
  b=bbox(o);xx=(b[0]+b[3])/2;yy=(b[1]+b[4])/2;zz=b[5]
  above=[bbox(q)[2]-zz for q in ceilings if bbox(q)[0]+1e-4<xx<bbox(q)[3]-1e-4 and bbox(q)[1]+1e-4<yy<bbox(q)[4]-1e-4 and bbox(q)[2]>zz+.01]
  if above:clear.append(min(above))
 ck(sid+'踏步中心垂直净空>=2.2m',not clear or min(clear)>=2.2,round(min(clear),3) if clear else 'open')
for rid,label in [('B1','薇亚の窝'),('B2','子豪の窝'),('B3','舒亚の窝'),('BW','公共浴室')]:
 ob=bpy.data.objects['NAME_'+rid];ck('固定门牌_'+label,ob.get('exact_text')==label and any(q.type=='MESH' and q.get('exact_text')==label for q in ob.children))
ck('40个品牌位置固定',len(M['brand_attachments'])==40 and all(not a['camera_facing'] for a in M['brand_attachments']))
ck('完整版域名完整',all(a['domain']=='hgdju.com' for a in M['brand_attachments'] if a['id'] not in ['BR_B1_STAND','BR_B1_FABRIC']))
ck('全部位图内嵌',all(im.packed_file for im in bpy.data.images if im.source=='FILE'))
ck('全屋保存未残留剖切隐藏',not any(o.hide_render for o in meshes))
ck('模型不依赖相机朝向约束',not any(c.type in ['TRACK_TO','DAMPED_TRACK','LOCKED_TRACK'] for o in meshes for c in o.constraints))
blend_count=len(meshes);glbfile=O/'模型/秘密教学_P4-M1.glb'
ck('GLB实际二进制',glbfile.read_bytes()[:4]==b'glTF')
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(glbfile));bpy.context.view_layer.update()
gm=[o for o in bpy.context.scene.objects if o.type=='MESH'];ck('GLB网格数与Blend一致',len(gm)==blend_count,dict(blend=blend_count,glb=len(gm)))
diff=[]
for o in gm:
 if o.name not in reference:diff.append(o.name+':missing');continue
 delta=max(abs(a-b) for a,b in zip(reference[o.name],bbox(o)))
 if delta>.002:diff.append(dict(object=o.name,max_error=delta))
ck('GLB坐标回读误差<=2mm',not diff,diff[:20])
# Existing accepted media and M3 must still match the original signed manifests.
A=repo/'assets/秘密教学第7集合格资产';a=json.loads((A/'合格资产清单.json').read_text('utf8'))
for row in a['assets']:ck('保留认可原图_'+row['id'],hashlib.sha256((A/row['file']).read_bytes()).hexdigest()==row['sha256'])
old=json.loads((repo/'docs/episode7-scenes/当前建模交付清单.json').read_text('utf8'))
for row in old['model_files']:ck('保留M3_'+Path(row['file']).name,hashlib.sha256((repo/row['file']).read_bytes()).hexdigest()==row['sha256'])
report=dict(revision='P4-M1',passed=sum(c['passed'] for c in checks),total=len(checks),failed=[c for c in checks if not c['passed']],checks=checks)
(O/'检查/模型回读与几何核对.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print('P4_VERIFICATION',report['passed'],report['total'],json.dumps(report['failed'],ensure_ascii=False),flush=True)
if report['failed']:raise RuntimeError('P4 model verification failed')
