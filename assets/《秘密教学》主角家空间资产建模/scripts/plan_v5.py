"""Aligned plans derived directly from HOME objects, never a second geometry source."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'));out=R/'图纸';out.mkdir(exist_ok=True)
S=44;W=2100;H=1330
v=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><marker id="arr" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6" fill="#b55531"/></marker></defs><rect width="100%" height="100%" fill="#f4f3ee"/><g font-family="Microsoft YaHei, sans-serif"><text x="55" y="52" font-size="29" fill="#263f37">《秘密教学》V5 · 原房间优先 / 采光院拼接提案</text><text x="55" y="84" font-size="17">同向、同尺度；临街端在下方。墙线按离地 1 米剖面投影，仅供检查；实际模型墙高 3.08 米。</text>']
labels={1:[('客厅',6.5,3.6),('餐厅',12.5,4.6),('厨房',12.0,8.8),('主卧',7.2,14.5),('主卫',5.3,19.0),('洗衣房',14.9,13.6),('客卫',14.3,17.2),('入口廊',8,-1),('采光院',5.8,7.9),('主卧通路',6.4,10.3),('服务通道',17.4,10.7)],2:[('薇亚 / 大姐',7.0,3.0),('子豪',6.8,14.1),('舒亚 / 二姐',14.8,11.5),('公用浴室',1.8,13.1),('后露台',13.7,17.5),('采光院',5.8,7.9),('转折走廊',7.0,10.3),('临街阳台',6.3,-.9)]}
for level,origin in [(1,65),(2,1110)]:
 z=(level-1)*3.3
 def px(x):return origin+(x+.4)*S
 def py(y):return 1180-(y+2)*S
 def rect(b,fill,stroke='#6c756e',sw=.5):
  x,y,zz,X,Y,Z=b;x-=3.8;X-=3.8;y-=15.2;Y-=15.2
  return f'<rect x="{px(x):.2f}" y="{py(Y):.2f}" width="{(X-x)*S:.2f}" height="{(Y-y)*S:.2f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
 v.append(f'<text x="{origin}" y="135" font-size="24" fill="#263f37">{level}F · '+('一楼' if level==1 else '二楼')+'</text>')
 obs=[o for o in D['objects'] if o['module']=='HOME' and o.get('zone')!='site']
 for o in obs:
  if o['role']=='floor' and abs(o['box'][5]-z)<.04:v.append(rect(o['box'],'#e9e0d3'))
 for o in obs:
  b=o['box'];role=o['role']
  if role in ('floor','ceiling','decor','brand','fixture','landscape','site','frame'):continue
  shared=role=='stair' or o['id']=='HOME_stair_separating_support'
  if o.get('level')!=level and not shared:continue
  if role in ('wall','support') and not(b[2]<=z+1<b[5]):continue
  if role not in ('wall','support','stair') and (b[2]>=z+1.5 or b[5]<=z):continue
  fill='#66756d' if role in ('wall','support') else '#b6d6db' if role=='glass' else o['color']
  v.append(rect(b,fill))
 # Short opening IDs correspond to a complete CSV ledger.
 for i,o in enumerate([o for o in D['openings'] if o['module']=='HOME' and o.get('level')==level],1):
  x=o['start']+o['width']/2 if o['axis']=='x' else o['plane'];y=o['plane'] if o['axis']=='x' else o['start']+o['width']/2
  v.append(f'<text x="{px(x-3.8):.1f}" y="{py(y-15.2)-5:.1f}" font-size="9" fill="#2b566b">{level}-{i:02}</text>')
 for text,x,y in labels[level]:
  ww=len(text)*15+14
  v.append(f'<rect x="{px(x)-ww/2:.1f}" y="{py(y)-15:.1f}" width="{ww}" height="25" rx="4" fill="#ffffff" opacity=".91"/><text x="{px(x):.1f}" y="{py(y)+3:.1f}" text-anchor="middle" font-size="15" fill="#214c3e">{html.escape(text)}</text>')
 v.append(f'<path d="M{px(.9)},{py(1)} L{px(.9)},{py(8)}" fill="none" stroke="#b55531" stroke-width="3" marker-end="url(#arr)"/><text x="{px(.1)}" y="{py(5)}" font-size="13" fill="#a34f30">A→B 下</text>')
 v.append(f'<text x="{origin}" y="1220" font-size="16">建筑局部最大范围约 18.3 × 22.0 m；尺寸为影视设计参考。</text>')
 v.append(f'<path d="M{origin},1250 h{5*S}" stroke="#263f37" stroke-width="3"/><text x="{origin}" y="1274" font-size="13">0</text><text x="{origin+5*S}" y="1274" font-size="13">5 m</text>')
v.append('<text x="55" y="1310" font-size="14">保留房间家具关系；新增连接处需人工复核。门扇按关闭状态示意，尚未完成全门扇扫掠。上楼方向为 B→A。</text></g></svg>')
(out/'全屋两层同向平面_v5.svg').write_text(''.join(v),encoding='utf8')
import csv
with (out/'门窗编号_v5.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['图纸短编号','模型对象编号','楼层','类型','宽度m','窗台相对地面m','开口高度m'])
 for level in (1,2):
  for i,o in enumerate([o for o in D['openings'] if o['module']=='HOME' and o.get('level')==level],1):w.writerow([f'{level}-{i:02}',o['id'],level,o['type'],o['width'],round(o['sill']-(level-1)*3.3,3),round(o['head']-o['sill'],3)])
print('aligned SVG + opening ledger written')
