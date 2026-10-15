"""Independent V3 local room specifications; not stretched to fit v4 boxes."""
module('M','子豪卧室 · 独立校准',5.6,5.4,['V3_059','V3_060','V3_061','V3_062','V3_063'],'保留床在右、电视与书桌在左、望远镜朝窗的关系。')
room(5.6,5.4,{'S':[(.65,1.0,0,2.2,'door')],'N':[(.75,3.9,.42,2.75,'window')]})
box('bed_base',[3.25,1.1,.08,5.45,2.95,.3],'wood');box('headboard',[5.4,1.02,.05,5.55,3.0,1.05],'wood');box('mattress',[3.27,1.13,.3,5.4,2.92,.53]);box('green_duvet',[3.24,1.1,.53,4.95,2.96,.61],'#7e9074','bed');ell('pillow1',[4.8,1.2,.55,5.35,2.0,.8],'#a5b095');ell('pillow2',[4.8,2.04,.55,5.35,2.83,.8],'#c9c9bb');box('bedside',[4.9,.43,0,5.5,1.0,.52],'wood')
box('TV_cab',[.12,1.25,0,.61,3.5,.55],'wood');box('TV',[.13,1.55,.65,.22,3.08,1.56],'dark');table('desk',.12,3.85,.68,1.3);box('desk_monitor',[.17,4.08,.84,.24,4.91,1.36],'dark');chair('desk_chair',1.3,4.5,90,'dark');box('PC',[.23,4.7,0,.65,5.05,.64],'dark')
box('rug',[.85,1.1,.005,2.6,3.3,.017],'#9a9895','rug');table('lowtable',1.25,1.68,1.0,.75,.4);box('gamepads',[1.4,1.85,.4,1.7,2.1,.46],'dark','decor');box('wardrobe',[4.95,4.38,0,5.5,5.3,2.25],'wood');box('mirror',[5.45,3.73,.05,5.51,4.3,1.95],'#a7b9be')
for y in [3.08,3.65]:line('rackpost'+str(y),[5.15,y,0],[5.15,y,1.8],.025)
line('rackrail',[5.15,3.08,1.8],[5.15,3.65,1.8],.025)
for i in range(4):box('shirt'+str(i),[4.95,3.13+i*.12,.65,5.35,3.19+i*.12,1.67],['#687777','#c4c4bd','#3f494d','#777a79'][i],'decor')
ell('guitar_body',[4.72,2.98,.03,5.12,3.21,.64],'#b48b58');line('guitar_neck',[4.93,3.08,.55],[5.04,3.08,1.13],.035,'wood');
for i in range(3):
 a=i*math.tau/3;line('telescope_tripod'+str(i),[3.65+.4*math.cos(a),4.42+.4*math.sin(a),0],[3.65,4.42,1.2],.022,'#a8acae')
line('telescope_tube',[3.65,4.12,1.25],[3.65,4.81,1.49],.085,'white');plaque('logo',[5.45,3.05,2.02,5.48,4.05,2.32]);plant('TV_plant',.4,1.4,.55,.55)
camera('front','入口看床与望远镜',[2.3,.65,1.65],[2.8,4.1,1.1],22);camera('reverse','窗侧看入口电视工作区',[4.6,4.5,1.65],[1.1,1.7,1.0],22);camera('cut','去顶俯视',[2.8,2.7,11.5],[2.8,2.7,0],40,True)
check('床尾至小桌实际净距',3.25-2.25,.9,['M_bed_base','M_lowtable_top']);check('望远镜后方至床侧通路',(4.42-.4)-2.95,.9,['M_telescope_tripod','M_bed_base'])

module('Y','舒亚卧室 · 独立校准',5.0,4.8,['V3_009','V3_010','V3_011','V3_012','V3_013','V3_014'],'保留床头与书桌同侧、入口在书桌旁、窗下低柜和星形地毯。')
room(5,4.8,{'E':[(.4,1.0,0,2.2,'door')],'W':[(1.0,2.35,.72,2.65,'window')]})
box('bed_base',[2.35,3.35,.06,4.8,4.67,.35]);box('headboard',[4.76,3.3,.1,4.87,4.72,1.02]);box('mattress',[2.38,3.38,.35,4.75,4.64,.52]);box('duvet',[2.33,3.33,.52,4.23,4.69,.6],'#89939e','bed');ell('pillow',[4.16,3.55,.56,4.7,4.4,.76]);ell('toy_body',[3.55,3.74,.61,4.0,4.18,.76]);ell('toy_head',[3.48,3.78,.65,3.7,4.05,.88]);
table('desk',4.4,1.78,.55,1.48);box('drawers',[4.45,2.85,0,4.9,3.22,.7],'wood');box('laptop',[4.65,2.25,.75,4.83,2.78,1.07],'dark');chair('desk_chair',3.87,2.42,-90);plant('desk_plant',4.71,3.07,.75,.5);box('memo_board',[4.9,2.03,1.2,4.94,3.02,1.8],'#c7ad86','decor');plaque('logo',[4.91,2.12,2.0,4.94,3.05,2.3]);
box('wardrobe',[.1,3.8,0,.7,4.7,2.35],'wood');box('window_lowcab',[.1,1.12,0,.5,3.25,.63]);plant('window_plant',.32,1.32,.63,.6);box('bedside',[1.68,4.05,0,2.24,4.6,.6],'wood');plant('bedside_plant',1.95,4.35,.6,.6)
box('rug',[1.15,1.05,.006,3.55,3.13,.02],'#9d9cae','rug');star=[]
for i in range(10):
 a=math.pi/2+i*math.pi/5;r=.76 if i%2==0 else .32;star.append([2.35+r*math.cos(a),2.09+r*math.sin(a),.023])
o=box('star',[1.5,1.2,.021,3.2,3,.025],'#555263','decor');o.update(kind='mesh',vertices=star,faces=[list(range(10))])
box('collection_cab',[1.25,.08,0,3.9,.58,.65]);
for x in [1.35,3.75]:line('displaypost'+str(x),[x,.35,.65],[x,.35,2.15],.025)
for z in [1.05,1.6,2.1]:
 line('displayrail'+str(z),[1.35,.35,z],[3.75,.35,z],.023)
 for i in range(10):ell('collection'+str(z)+str(i),[1.42+i*.22,.26,z-.28,1.58+i*.22,.46,z-.05],['#c5a3b2','#d5c9bf','#9895b3'][i%3],'decor')
box('fullmirror',[4.0,.07,.03,4.55,.13,1.86],'#a6b4b8');
for i in range(7):box('bed_photo'+str(i),[2.1+i*.32,4.68,1.1+(i%2)*.22,2.33+i*.32,4.7,1.4+(i%2)*.22],'#b6a5a8','decor')
camera('front','窗侧看床书桌门',[.9,1.35,1.65],[4.6,3.0,1.0],22);camera('reverse','书桌侧看窗与收藏',[4.1,3.05,1.65],[1.0,2,1.0],23);camera('cut','去顶俯视',[2.5,2.4,10.5],[2.5,2.4,0],40,True)
check('窗下柜至星毯活动区',1.15-.5,.6,['Y_window_lowcab','Y_rug'],'地毯可行走；此为柜前间隙');check('床尾至衣柜前净距',2.35-.7,1.0,['Y_bed_base','Y_wardrobe'])

module('P','主卧与主卫 · 联合校准',6.0,5.6,['V3_064','V3_065','V3_067','V3_068','V3_070','V3_071','V3_072','V3_073'],'主卫附在床尾墙外，只经主卧进入；入口位于床头侧。主卫坐标Y为负，属于同一套房。')
room(6,5.6,{'N':[(1.25,1.0,0,2.2,'door')],'E':[(.95,3.8,.75,2.65,'window')],'S':[(4.6,.95,0,2.2,'door')]})
box('bed_base',[3.0,3.06,.08,5.0,5.29,.37],'#695443');box('headboard',[2.93,5.23,.1,5.07,5.43,1.25],'#695443');box('mattress',[3.03,3.1,.37,4.97,5.24,.58]);box('burgundy_duvet',[2.98,3.03,.58,5.02,4.83,.67],'#754754','bed');
for i,x in enumerate([3.08,4.04]):ell('pillow'+str(i),[x,4.72,.62,x+.88,5.2,.86],'#794b58')
for i,x in enumerate([2.3,5.18]):
 box('bedside'+str(i),[x,4.76,0,x+.5,5.34,.58],'#695443');cyl('lampbase'+str(i),x+.25,5.0,.58,.1,.22,'#898b8a');cyl('lampshade'+str(i),x+.25,5.0,.8,.16,.23,'#d8d2be','fixture')
# Open wardrobe facing +X, not a generic opaque cabinet.
box('wardrobe_back',[.05,3.0,0,.1,5.35,2.55]);
for y in [3.0,4.15,5.31]:box('wardrobe_partition'+str(y),[.05,y,0,.65,y+.04,2.55])
for z in [.05,.4,2.2,2.5]:box('wardrobe_shelf'+str(z),[.05,3,z,.65,5.35,z+.04])
for i in range(12):box('clothes'+str(i),[.19,3.12+i*.17,.62,.51,3.22+i*.17,1.98],['#c8b8a5','#dfd3bd','#bdb7af'][i%3],'decor')
box('vanity_top',[.12,1.22,.72,.66,2.45,.78],'#695443');box('vanity_base',[.15,1.3,0,.57,1.6,.72],'#695443');box('vanity_base2',[.15,2.1,0,.57,2.4,.72],'#695443');ell('oval_mirror',[.08,1.5,.8,.14,2.2,1.52],'#b2b9b7');cyl('vanity_stool',1.05,1.85,0,.26,.48,'#754754');plaque('logo',[2.4,5.47,1.65,3.7,5.51,1.98]);plant('vanity_plant',.4,2.32,.78,.45)
box('bath_floor',[2.9,-3.5,-.18,6.1,0,0],'#c6c0ae','floor');box('bath_ceiling',[2.9,-3.5,3.08,6.1,0,3.26],'white','ceiling');wall('bath_W','y',3,-3.4,0,color='#d4cbbb');wall('bath_E','y',6,-3.4,0,color='#d4cbbb');wall('bath_S','x',-3.4,3,6,[(3.45,2.05,1.65,2.2,'window')],color='#d4cbbb')
box('tub_outer',[3.38,-3.25,0,5.6,-2.35,.57]);box('tub_inner',[3.53,-3.13,.49,5.45,-2.47,.58],'#a9c0c5');box('bath_vanity',[3.1,-1.35,0,3.65,-.2,.83],'#695443');ell('basin',[3.12,-1.1,.8,3.63,-.48,.93]);ell('round_mirror',[3.08,-1.14,1.04,3.13,-.44,1.74],'#a8babf');ell('WC_base',[5.25,-1.5,0,5.87,-.65,.43]);box('WC_tank',[5.67,-1.4,.25,5.88,-.78,.9]);box('bath_glass',[3.48,-2.3,0,4.45,-2.27,2.1],'glass','glass');plaque('bath_logo',[5.89,-1.65,1.45,5.92,-.65,1.75])
camera('front','床尾看床头入口',[3.9,1.15,1.65],[3.5,5.25,1.1],25);camera('reverse','床头侧看主卫门',[3.6,4.9,1.65],[2.7,.5,1.1],22);camera('cut','套房去顶俯视',[3,1.1,20],[3,1.1,0],36,True)
check('床尾至主卫门墙通路',3.03,.95,['P_burgundy_duvet','P_S_0door']);check('床侧至衣柜外沿',3.0-.65,1.0,['P_bed_base','P_wardrobe_shelf0.4']);check('主卫柜与马桶间净宽',5.25-3.65,.9,['P_bath_vanity','P_WC_base'])

module('LA','洗衣房 · 独立校准',3.5,4.3,['V3_056','V3_057','V3_058'],'独立房间；双排柜之间净距按外沿计算，不再藏进楼梯旁小门。')
room(3.5,4.3,{'E':[(.18,1.0,0,2.2,'door')],'W':[(1.1,2.65,1.05,2.6,'window')]})
box('tallunit',[.12,.18,0,.72,.91,1.8]);box('washer',[.12,1.03,0,.78,1.72,.86]);ell('washer_door',[.76,1.14,.16,.82,1.61,.64],'dark');box('washcab',[.12,1.75,0,.78,4.12,.85]);box('washcounter',[.1,1.75,.85,.81,4.14,.9],'dark');box('foldcab',[2.78,1.48,0,3.38,4.12,.85]);box('foldcounter',[2.75,1.46,.85,3.4,4.14,.9],'dark');cyl('basket',1.28,3.7,0,.36,.55,'#c2b49d');ell('laundry',[.98,3.4,.45,1.58,4.0,.68],'#b4b9ba');box('stool',[2.25,3.32,0,2.67,3.74,.46],'wood');
for i in range(3):box('folded_towel'+str(i),[2.85,3.6,.9+i*.06,3.32,4.0,.95+i*.06],'#c2c7c7','decor')
plaque('logo',[.9,4.17,1.65,2.6,4.21,2.12]);camera('front','入口侧看洗衣双排柜',[2.4,.38,1.7],[1.6,2.8,.95],18);camera('cut','去顶俯视',[1.75,2.15,9.6],[1.75,2.15,0],40,True);check('双排台面实际净距',2.75-.81,1.2,['LA_washcounter','LA_foldcounter'])
