"""Executed by build_v5_modules.py; one coordinate source for the L-shaped module.
Living and dining sit SIDE BY SIDE across the TV wall, kitchen behind dining.
"""
module('KLD','客厅—餐厅—厨房 · 连续校准',12.5,10.2,['V3_038','V3_039','V3_040','V3_041','V3_048','V3_049','V3_051','V3_079','V3_080','V3_081'],'客厅与餐厅并排，厨房在餐厅后方。L形外墙保留客厅侧窗，公共连接端待全屋拼接。')
box('floor_living',[-.1,-.1,-.18,5.7,6.1,0],'floor','floor');box('floor_dining_kitchen',[5.7,-.1,-.18,12.6,10.3,0],'floor','floor');box('floor_stub',[4.15,6,-.18,5.7,7.65,0],'floor','floor')
box('ceiling_living',[-.1,-.1,3.08,5.7,6.1,3.26],'white','ceiling');box('ceiling_dining_kitchen',[5.7,-.1,3.08,12.6,10.3,3.26],'white','ceiling')
wall('S','x',0,0,12.5,[(6.05,1.1,0,2.2,'door')]);wall('W','y',0,0,6);wall('living_N','x',6,0,5.7,[(.55,2.9,.55,2.65,'window'),(4.4,1.05,0,2.2,'door')]);wall('E','y',12.5,0,10.2,[(1.05,3.2,.6,2.65,'window'),(7.5,1.05,0,2.2,'door')]);wall('kitchen_N','x',10.2,5.7,12.5,[(6.85,2.75,1.2,1.77,'window')]);wall('kitchen_W','y',5.7,6,10.2);wall('stub_W','y',4.15,6,7.65);wall('stub_N','x',7.65,4.15,5.7)
wall('TV_partition','y',5.7,1.2,4.8)
# Sofa against solid west wall; window on perpendicular north wall.
box('sofa_base',[.2,.9,.12,1.18,4.8,.46],'#b8b9ba');box('sofa_back',[.15,.9,.46,.43,4.8,1.02],'#bababa');box('chaise',[.4,3.8,.18,2.4,4.8,.48],'#b8b9ba')
for i in range(3):box('sofa_cushion'+str(i),[.45,1.05+i*.94,.46,1.1,1.91+i*.94,.57],'#cacaca')
box('sofa_arm',[.2,.8,.3,1.23,1.05,.75],'#b8b9ba');box('throw',[.46,.91,.58,1.16,1.41,.6],'#909aa3','decor');box('living_rug',[1.28,.75,.005,4.5,4.95,.015],'#a6a39a','rug');table('coffee',2.55,1.7,.85,1.8,.43,True);box('coffee_books',[2.7,2.65,.43,3.1,3.1,.49],'#d8c8b6','decor');plant('living_plant',3.98,5.4,0,1.4)
box('TV',[5.56,1.85,.95,5.64,4.15,2.28],'dark');box('TV_cab',[5.11,1.45,0,5.55,4.55,.44]);box('TV_cab_top',[5.09,1.42,.44,5.58,4.58,.48],'wood')
for y in [1.1,4.7]:box('speaker'+str(y),[5.19,y,0,5.46,y+.22,1.2],'dark')
plaque('living_logo',[5.56,2.35,2.46,5.6,3.65,2.79])
# Dining is east of partition. Two long-side chairs per side + two end chairs.
table('dining',8.2,1.65,1.4,2.25,.77,True)
for i,y in enumerate([2.18,3.36]):chair('dining_left'+str(i),7.78,y,-90,'wood');chair('dining_right'+str(i),10.02,y,90,'wood')
chair('dining_endS',8.9,1.24,180,'wood');chair('dining_endN',8.9,4.31,0,'wood')
plant('dining_flowers',8.9,2.78,.77,.6);cyl('pendant',8.9,2.78,2.18,.34,.2,'#7d8184','fixture');line('pendant_cord',[8.9,2.78,2.38],[8.9,2.78,3.08],.012)
plaque('dining_logo',[11.3,5.91,1.5,12.3,5.96,1.8]);wall('kitchen_front_right','x',6,10.82,12.5,[(10.95,1.1,0,2.3,'door')]);wall('kitchen_right','y',10.82,6,10.2);shelf('hall_bookcase',11.0,9.75,1.25,.35,2.45);shelf('stub_bookcase',4.3,7.15,1.15,.35,2.45)
def counter(id,b):
 x,y,z,X,Y,Z=b;box(id+'_cab',[x,y,z,X,Y,Z-.04]);box(id+'_top',[x-.015,y-.015,Z-.04,X+.015,Y+.015,Z],'#373b40','counter')
counter('K_back',[5.8,9.54,0,10.7,10.1,.91]);counter('K_left',[5.8,7.25,0,6.45,9.54,.91]);counter('K_right',[10.05,6.25,0,10.7,9.54,.91]);counter('K_peninsula',[7.7,6.25,0,10.05,6.95,.91])
box('fridge',[5.83,6.17,0,6.7,7.03,1.94],'#b2b5b6');box('fridge_split',[5.83,6.15,1.18,6.7,6.18,1.2],'dark');box('stove',[5.81,7.7,.91,6.44,8.65,.94],'dark');box('oven',[6.4,7.75,.18,6.46,8.61,.77],'dark');box('hood',[5.78,7.63,1.65,6.5,8.7,1.85],'#b3b7b7');box('hood_duct',[5.8,7.94,1.85,6.2,8.38,2.8],'#b3b7b7')
for y in [7.95,8.39]:
 for x in [5.98,6.25]:cyl('burner'+str(x)+str(y),x,y,.94,.085,.015,'dark')
box('backsplash_W',[5.78,7.25,.91,5.81,10.1,1.65],'#8296a3','finish')
for id,b in [('tilebelow',[5.82,10.1,.91,10.7,10.13,1.2]),('tileleft',[5.82,10.1,1.2,6.85,10.13,1.92]),('tileright',[9.6,10.1,1.2,10.7,10.13,1.92]),('tileabove',[6.85,10.1,1.77,9.6,10.13,1.92])]:box(id,b,'#8296a3','finish')
for i in range(6):box('upper_cab'+str(i),[5.83+i*.8,9.7,1.93,6.6+i*.8,10.12,2.8])
for i,x in enumerate([7.42,8.15]):box('sink'+str(i),[x,9.64,.91,x+.58,10.0,.93],'#a7b2b4')
line('tap_vertical',[8.04,10.03,.91],[8.04,10.03,1.2],.022,'#a2aaad');line('tap_spout',[8.04,10.03,1.2],[8.04,9.81,1.2],.022,'#a2aaad')
box('microwave',[10.09,8.65,.91,10.66,9.32,1.24],'dark');ell('rice_cooker',[10.1,8.09,.91,10.66,8.54,1.24]);box('coffee_machine',[10.13,7.25,.91,10.64,7.7,1.26],'dark');plant('herbs',9.34,9.8,.91,.45);plaque('kitchen_logo',[8.3,6.225,.36,9.4,6.25,.66])
camera('L_front','沙发侧看电视及餐厅',[1.5,1.55,1.65],[5.65,3.75,1.2],22);camera('L_reverse','电视侧回看沙发',[4.8,2.8,1.65],[.4,3.0,1.1],23);camera('D_front','餐厅看厨房及左侧客厅',[8.9,.7,1.65],[8.7,7.7,1.2],22);camera('K_front','餐厅入口看水槽横窗',[8.4,4.7,1.65],[8.2,9.7,1.25],24);camera('K_reverse','水槽侧回看餐厅及右侧客厅',[9.2,9.1,1.65],[7.7,2.2,1.1],22);camera('cut','去顶俯视客餐厨关系',[6.25,5.1,22],[6.25,5.1,0],40,True)
check('厨房两侧台面实际净距',(10.05-.015)-(6.45+.015),1.2,['KLD_K_left_top','KLD_K_right_top']);check('半岛入口实际净宽',(7.7-.015)-6.7,.9,['KLD_K_peninsula_top','KLD_fridge']);check('半岛至后排台面实际净深',(9.54-.015)-(6.95+.015),1.2,['KLD_K_back_top','KLD_K_peninsula_top']);check('餐椅后移后至电视隔断通路',7.78-.25-.35-(5.7+.09),.9,['KLD_dining_left0_seat','KLD_TV_partition_end']);check('餐桌端椅后移至半岛',6.235-(4.31+.25+.35),1.2,['KLD_dining_endN_seat','KLD_K_peninsula_top']);check('客厅北端开口净宽',6-.09-4.8,1.0,['KLD_TV_partition_end','KLD_living_N_end'])
