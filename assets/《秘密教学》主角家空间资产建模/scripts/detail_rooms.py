"""Executed inside direct_render.py. Dress accepted footprints; never move walls."""
from mathutils import Matrix
graycloth=fabric('客厅_浅灰亚麻',(.43,.45,.46),(.6,.61,.62))
greencloth=fabric('大姐_深绿靠枕',(.035,.10,.066),(.08,.14,.09))
burgundy=fabric('主卧_酒红床品',(.058,.0025,.008),(.085,.006,.015))
eldercloth=fabric('大姐_灰格床品',(.33,.34,.34),(.07,.075,.08),True)
malecloth=fabric('男主_绿色图案床品',(.23,.38,.16),(.075,.18,.07),True)
glass=mat('透明玻璃',(.93,.97,.97),.09)
glass.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=1
glass.node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value=1.46

def group_local(before,center,angle):
    transform=Matrix.Translation(Vector(center)) @ Matrix.Rotation(angle,4,'Z')
    for ob in bpy.data.objects:
        if ob.name not in before:ob.matrix_world=transform @ ob.matrix_world

def diningchair(name,x,y,angle):
    before=set(o.name for o in bpy.data.objects)
    box(name+'_seat',(0,0,.455),(.46,.46,.07),darkwood,.025)
    box(name+'_pad',(0,0,.5),(.415,.415,.055),graycloth,.03)
    for xx in [-.18,.18]:
        for yy in [-.18,.18]:rod(name+'_leg',(xx*1.1,yy*1.1,.025),(xx,yy,.445),.022,darkwood)
        box(name+'_post',(xx,.19,.735),(.035,.038,.62),darkwood,.008)
    for xx in [-.105,0,.105]:box(name+'_slat',(xx,.19,.765),(.031,.025,.38),darkwood,.009)
    box(name+'_rail',(0,.19,.99),(.445,.045,.075),darkwood,.025)
    group_local(before,(x,y,0),angle)

def framedtable(name,b,h,material=darkwood):
    x,y,X,Y=b;cx=(x+X)/2;cy=(y+Y)/2
    box(name+'_glass',(cx,cy,h-.01),(X-x-.09,Y-y-.09,.016),glass,.004)
    for xx in [x+.04,X-.04]:box(name+'_rail',(xx,cy,h-.045),(.08,Y-y,.09),material,.01)
    for yy in [y+.04,Y-.04]:box(name+'_rail',(cx,yy,h-.045),(X-x-.16,.08,.09),material,.01)
    for xx in [x+.065,X-.065]:
        for yy in [y+.065,Y-.065]:box(name+'_leg',(xx,yy,(h-.09)/2),(.09,.09,h-.09),material,.01)

# Living room: same L footprint, upholstered back faces south and seats face TV.
for key in ['F101','F102','F103','F104','F105','F106','F107']+[f'DIN_C{i}' for i in range(6)]:remove_prefix(key)
for b in [(6,.6,9.7,1.5),(8.8,1.45,9.7,2.8)]:
    x,y,X,Y=b;box('L_SOFA_base',((x+X)/2,(y+Y)/2,.225),(X-x,Y-y,.28),graycloth,.085)
    for xx in [x+.15,X-.15]:
        for yy in [y+.15,Y-.15]:box('L_SOFA_foot',(xx,yy,.085),(.055,.055,.17),black,.008)
for xx in [6.67,7.77,8.84]:
    box('L_SOFA_seat',(xx,1.13,.445),(1.065,.67,.20),graycloth,.083)
    o=box('L_SOFA_back',(xx,.745,.725),(1.075,.26,.49),graycloth,.095);o.rotation_euler.x=math.radians(-8)
box('L_SOFA_chaise',(9.23,2.08,.445),(.84,1.36,.20),graycloth,.085)
for xx in [6.12,9.57]:box('L_SOFA_arm',(xx,1.08,.545),(.24,.91,.43),graycloth,.085)
for xx,col in [(6.45,cushion),(8.65,cushion)]:
    o=box('L_SOFA_cushion',(xx,.94,.74),(.46,.18,.43),col,.087);o.rotation_euler.x=-.22;o.rotation_euler.y=.08
# Soft throw lies over the east chaise, no new object in the walkway.
vv=[];ff=[]
for i in range(31):
    for j in range(21):
        u=i/30;v=j/20;zz=.575-.36*max(0,(v-.82)/.18)**1.3+.012*math.sin(u*24+v*11)
        vv.append((8.88+u*.68,1.62+v*1.25,zz))
for i in range(30):
    for j in range(20):k=i*21+j;ff.append((k,k+1,k+22,k+21))
me=bpy.data.meshes.new('throw');me.from_pydata(vv,[],ff);me.update();ob=bpy.data.objects.new('L_SOFA_throw',me);s.collection.objects.link(ob);assign(ob,blue);ob.modifiers.new('布厚','SOLIDIFY').thickness=.004
for p in me.polygons:p.use_smooth=True
framedtable('L_COFFEE',[6.2,2.3,8.3,3.3],.43)
box('L_REMOTE',(7.7,2.65,.455),(.16,.042,.018),black,.006)
for k in range(2):box('L_MAGAZINE',(6.55,2.82,.45+k*.011),(.29,.22,.009),[paper,blue][k],.002)
# Abstract carpet pattern in the shader, not a newly generated image.
rm=fabric('客厅_抽象灰米地毯',(.31,.30,.28),(.2,.2,.2));nt=rm.node_tree;n=nt.nodes;l=nt.links
tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5;noise.inputs['Roughness'].default_value=.8;l.new(tc.outputs['Generated'],noise.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
for e,c in zip(ramp.color_ramp.elements,[(.09,.085,.078,1),(.49,.46,.40,1)]):e.color=c
for pos,col in [(.36,(.23,.23,.22,1)),(.53,(.39,.37,.31,1)),(.65,(.59,.56,.49,1))]:ramp.color_ramp.elements.new(pos).color=col
l.new(noise.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],nt.nodes['Principled BSDF'].inputs['Base Color'])
box('L_RUG',(7.4,3.1,.015),(3.4,2.8,.025),rm,.015)
# Keep the accepted TV furniture width, add cabinet, actual screen and speakers.
box('L_MEDIA_back',(5.475,5.43,1.14),(1.55,.07,2.1),wall,.005)
box('L_MEDIA_cabinet',(5.475,5.30,.34),(1.47,.31,.55),white,.015)
box('L_MEDIA_top',(5.475,5.30,.63),(1.52,.33,.045),darkwood,.01)
for xx in [4.985,5.475,5.965]:
    box('L_MEDIA_door',(xx,5.135,.35),(.46,.02,.49),white,.006)
    rod('L_MEDIA_handle',(xx-.065,5.112,.50),(xx+.065,5.112,.50),.006,silver)
box('L_TV',(5.475,5.355,1.29),(1.18,.075,.68),black,.014)
screenoff=mat('关闭电视_玻璃屏',(.009,.014,.017),.17)
box('L_TV_screen',(5.475,5.313,1.29),(1.13,.004,.631),screenoff,.002)
for xx in [4.765,6.185]:
    box('L_SPEAKER',(xx,5.3,1.025),(.10,.12,.77),black,.007)
    for zz in [.83,1.1,1.28]:o=cyl('L_SPEAKER_cone',(xx,5.231,zz),.032,.006,black);o.rotation_euler.x=math.pi/2
box('L_PLAYER',(5.475,5.28,.685),(.29,.17,.045),black,.006)
if bpy.data.objects.get('BR_LIVING_ART'):
    bpy.data.objects['BR_LIVING_ART'].location.z+=.19

# Dining: six wooden slat-back chairs, glass top and gray pendant.
framedtable('DIN_TABLE',[4.75,6.45,6.75,7.45],.76)
for i,(x,y,ang) in enumerate([(5.04,6.05,math.pi),(6.34,6.05,math.pi),(5.04,7.90,0),(6.34,7.90,0),(4.29,6.93,math.pi/2),(7.19,6.93,-math.pi/2)]):diningchair('DIN_C'+str(i),x,y,ang)
pendantmat=mat('餐厅灰色吊灯',(.36,.37,.35),.45)
rod('DIN_pendant_cord',(5.75,6.95,2.48),(5.75,6.95,3.10),.007,black)
bpy.ops.mesh.primitive_cone_add(vertices=64,radius1=.29,radius2=.08,depth=.23,location=(5.75,6.95,2.37));ob=bpy.context.object;ob.name='DIN_pendant';assign(ob,pendantmat);ob.modifiers.new('灯罩圆边','BEVEL').width=.008
cyl('DIN_vase',(5.75,6.95,.84),.065,.14,glass)
for i in range(5):
    ang=i*2.4;xx=5.75+.05*math.cos(ang);yy=6.95+.05*math.sin(ang);rod('DIN_flower_stem',(5.75,6.95,.8),(xx,yy,1.02),.002,leafmat)
    for j in range(5):sphere('DIN_flower',(xx+.017*math.cos(j*math.tau/5),yy+.017*math.sin(j*math.tau/5),1.02),(.028,.028,.012),pink if i%2 else white)
for xx in [5.07,6.34]:
    box('DIN_mat',(xx,6.74,.774),(.36,.27,.003),cushion,.01)
    cyl('DIN_cup',(xx+.13,6.86,.827),.032,.1,white)

def bed(name,b,z,head,linen,frame):
    """Local width x length. Head is +Y; transform within the accepted box."""
    x,y,X,Y=b;w=X-x;length=Y-y;before=set(o.name for o in bpy.data.objects)
    box(name+'_frame',(0,0,.24),(w,length,.3),frame,.025)
    for xx in [-w/2+.1,w/2-.1]:
        for yy in [-length/2+.1,length/2-.1]:box(name+'_foot',(xx,yy,.09),(.08,.08,.18),frame,.006)
    box(name+'_head',(0,length/2-.055,.79),(w,.11,1.04),frame,.035)
    box(name+'_mattress',(0,0,.465),(w-.08,length-.08,.22),white,.075)
    for xx in [-w*.235,w*.235]:box(name+'_pillow',(xx,length/2-.45,.65),(w*.41,.47,.14),cushion,.069)
    vs=[];fs=[];nx,ny=45,40
    for i in range(nx+1):
        for j in range(ny+1):
            u=i/nx;v=j/ny;xx=(u-.5)*(w+.08);yy=-length/2-.045+v*(length-.62)
            drop=.29*max(0,(abs(u-.5)-.45)/.05)**1.5+.25*max(0,(.06-v)/.06)**1.5
            vs.append((xx,yy,.605-drop+.006*math.sin(u*37+v*20)+.005*math.sin(v*57)))
    for i in range(nx):
        for j in range(ny):k=i*(ny+1)+j;fs.append((k,k+1,k+ny+2,k+ny+1))
    me=bpy.data.meshes.new(name+'_linen');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name+'_quilt',me);s.collection.objects.link(o);assign(o,linen);o.modifiers.new('布厚','SOLIDIFY').thickness=.005
    for p in me.polygons:p.use_smooth=True
    if name=='E_BED':
        for xx,m in [(-.42,greencloth),(.42,pink)]:o=box(name+'_accent',(xx,length/2-.57,.73),(.43,.15,.38),m,.068);o.rotation_euler.x=.18
    group_local(before,((x+X)/2,(y+Y)/2,z),math.pi if head=='south' else 0)

for key in ['MASTER_BED','E_BED','M_BED','E_RUG']:remove_prefix(key)
bed('MASTER_BED',[11,11.2,13.15,13.6],0,'north',burgundy,darkwood)
bed('E_BED',[6.3,1.15,8.4,3.45],3.3,'north',eldercloth,oak)
bed('M_BED',[6,4.05,8,6.35],3.3,'south',malecloth,oak)
cyl('E_RUG',(6.75,1.55,3.315),.75,.023,pink)

# Replace rectangular furniture proxies with doors, drawers, worktops and legs.
for f in D['furniture']:
    key=f['id']
    if key not in ['M_BEDSIDE1','M_BEDSIDE2','M_WARDROBE','M_VANITY','E_WARD','E_VANITY','E_DESK','E_BOOK','M_DESK','M_WARD','M_TV','M_COFFEE','ENTRY_C','READ_BOOK']:continue
    remove_prefix(key);x,y,X,Y=f['box'];zz=(f['level']-1)*3.3;h=f['height'];cx=(x+X)/2;cy=(y+Y)/2;ww=X-x;dd=Y-y;m=darkwood if key.startswith('M_') and f['level']==1 else oak
    if f['kind'] in ['desk','vanity','table']:
        box(key+'_top',(cx,cy,zz+h-.025),(ww,dd,.05),m,.012)
        for xx in [x+.045,X-.045]:
            for yy in [y+.045,Y-.045]:box(key+'_leg',(xx,yy,zz+(h-.05)/2),(.055,.055,h-.05),m,.005)
    else:
        box(key+'_body',(cx,cy,zz+h/2),(ww,dd,h),m,.012)
        # Front is on long side toward room, not into the wall.
        longx=ww>dd;count=max(1,round((ww if longx else dd)/.5))
        for j in range(count):
            if longx:
                px=x+(j+.5)*ww/count;py=y-.009
                box(key+'_panel',(px,py,zz+h/2),(ww/count-.014,.018,h-.06),m,.005);rod(key+'_pull',(px+.12,py-.018,zz+h*.47),(px+.12,py-.018,zz+h*.57),.007,silver)
            else:
                px=X+.009;py=y+(j+.5)*dd/count
                box(key+'_panel',(px,py,zz+h/2),(.018,dd/count-.014,h-.06),m,.005);rod(key+'_pull',(px+.018,py+.1,zz+h*.47),(px+.018,py+.1,zz+h*.57),.007,silver)
    if f['kind']=='vanity':
        mirror=mat(key+'_mirror',(.78,.8,.82),.03,1);box(key+'_mirror_frame',(cx,y+.04,zz+h+.48),(min(ww,.94),.06,.9),m,.035);box(key+'_mirror',(cx,y+.005,zz+h+.48),(min(ww,.94)-.07,.008,.82),mirror,.015)
    if f['kind']=='desk':
        box(key+'_book',(cx,cy,zz+h+.02),(.25,.18,.035),blue,.003);plant(key+'_plant',(cx+.2,cy,zz+h),.6)
# Telescope, guitar and exercise cycle are explicit stable geometry.
for key in ['M_TELESCOPE','M_GUITAR','E_BIKE']:remove_prefix(key)
for ang in [0,2.1,4.2]:rod('M_TELESCOPE_leg',(10.25+.22*math.cos(ang),6.05+.22*math.sin(ang),3.32),(10.25,6.05,4.18),.012,silver)
rod('M_TELESCOPE_tube',(10.10,6.05,4.38),(10.47,6.05,4.6),.075,white);rod('M_TELESCOPE_mount',(10.25,6.05,4.16),(10.25,6.05,4.44),.025,black)
sphere('M_GUITAR_body',(8.27,4.2,3.59),(.25,.1,.39),darkwood);sphere('M_GUITAR_shoulder',(8.27,4.2,3.77),(.18,.09,.25),darkwood)
box('M_GUITAR_neck',(8.27,4.2,4.0),(.047,.04,.45),oak,.006)
o=cyl('M_GUITAR_hole',(8.27,4.258,3.67),.039,.002,black);o.rotation_euler.x=math.pi/2
for dx in [-.013,-.008,-.003,.003,.008,.013]:rod('M_GUITAR_string',(8.27+dx,4.26,3.49),(8.27+dx,4.23,4.25),.00055,silver)
for yy in [.40,1.19]:rod('E_BIKE_foot',(9.92,yy,3.36),(10.38,yy,3.36),.028,black)
rod('E_BIKE_base',(10.15,.4,3.38),(10.15,1.18,3.38),.032,black)
for p,q in [((10.15,.55,3.45),(10.15,.70,4.04)),((10.15,.55,3.45),(10.15,1.10,4.27)),((10.15,.70,4.04),(10.15,1.1,4.27))]:rod('E_BIKE_frame',p,q,.028,white)
o=cyl('E_BIKE_flywheel',(10.15,.94,3.63),.20,.13,black);o.rotation_euler.y=math.pi/2
box('E_BIKE_seat',(10.15,.68,4.10),(.25,.2,.07),black,.025);rod('E_BIKE_handle',(9.99,1.1,4.35),(10.31,1.1,4.35),.022,black)

# Append selected CC0 botanical meshes. Pack images so saved models are portable.
def realplant(asset,name,location,height):
    folder=R/'资源/PolyHaven'/asset;path=folder/(asset+'_2k.blend')
    if not path.exists():raise FileNotFoundError('Run fetch_cc0.py first: '+str(path))
    before=set(bpy.data.images)
    with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.objects=src.objects
    objs=[o for o in dst.objects if o and o.type=='MESH']
    for o in objs:s.collection.objects.link(o)
    pts=[o.matrix_world@Vector(v) for o in objs for v in o.bound_box];lo=Vector([min(p[i] for p in pts) for i in range(3)]);hi=Vector([max(p[i] for p in pts) for i in range(3)]);scale=height/(hi.z-lo.z);center=Vector(((lo.x+hi.x)/2,(lo.y+hi.y)/2,lo.z))
    transform=Matrix.Translation(Vector(location)) @ Matrix.Scale(scale,4) @ Matrix.Translation(-center)
    for o in objs:o.matrix_world=transform@o.matrix_world;o.name=name+'_'+o.name;o['license']='CC0';o['source_asset']='https://polyhaven.com/a/'+asset
    for im in set(bpy.data.images)-before:
        if im.source!='FILE':continue
        match=list(folder.rglob(Path(im.filepath.replace('\\','/')).name))
        if match:im.filepath=str(match[0]);im.reload();im.pack()
realplant('potted_plant_01','LIVING_PLANT',(10.17,.67,0),1.30)
for name,loc,h in [('DESK',(3.99,9.16,4.09),.24),('DINING',(7.15,8.6,0),.75)]:
    if name=='DESK':remove_prefix('Y_DESK_PLANT')
    realplant('potted_plant_04','BOTANICAL_'+name,loc,h)

# Extra cameras are positions in the same room, never in or beyond an entrance.
extra_jobs=[]
for label,pos,target,lens in [
 ('客厅_前视图',[9.65,.92,1.62],[5.5,5.35,1.25],24),
 ('客厅_侧视图',[4.05,2.65,1.62],[8.4,2.1,1.15],22),
 ('客厅_后视图',[5.7,4.7,1.62],[8.0,1.1,1.1],24),
 ('客厅_俯拍图',[8.3,4.6,2.90],[7.75,1.9,.3],18),
 ('餐厅_前视图',[7.10,8.65,1.62],[5.30,6.5,.95],22),
 ('餐厅_后视图',[4.05,5.8,1.62],[6.1,7.15,1.0],22),
 ('主卧卧室_床尾看床头',[12,9.7,1.62],[12,13.4,1.1],24),
 ('主卧卧室_侧视图',[10.05,10.5,1.62],[12.4,12.9,.9],22),
 ('大姐卧室_前视图',[5.0,.75,4.92],[7.4,2.8,4.1],22),
 ('男主卧室_前视图',[4.2,7.0,4.92],[7.5,4.55,4.1],22)]:
    bpy.ops.object.camera_add(location=pos);o=bpy.context.object;o.name='DIRECT_'+label;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.lens=lens;o.data.clip_start=.04;extra_jobs.append((label,o))
