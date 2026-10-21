from pathlib import Path
import json,hashlib,html,math
from PIL import Image,ImageDraw,ImageFont
import plan_svg as g
R=Path(__file__).resolve().parents[1];O=R/'白模当前';Q=O/'方位检查';Q.mkdir(exist_ok=True)
M=json.loads((O/'模型/空间数据.json').read_text(encoding='utf8'));D=M['plan'];g.OUT=Q;g.OPEN=D['openings']
for level in [1,2]:
 s=g.Sheet('P2.4-M2｜'+('一楼落脚与公共区' if level==1 else '二楼建模平面与机位'),'F4关系已确认；本图是按授权调整比例后的米制暂定实现。北↑；具体尺寸仍由用户校准。',[0,0,22,11],65,(100,870),(1800,1280))
 s.p=[x.replace('P2.3-R2 · 2026-10-21 · 走廊空间局部校核 · 同步 P2.3-M1 白模 · 影视参考，非施工图','P2.4-M2 · F4关系重建 / 尺寸暂定 / 同源模型数据 / 非施工图') for x in s.p]
 for r in D['rooms']:
  if r['level']==level:s.rect(r['box'],r.get('color','#e7eeea'),'#a9b9b4')
 if level==2:s.rect(D['architecture']['void'],'#d4e5ed','#6b909f');s.wt(13.1,1.7,'楼梯洞口',18,anchor='middle')
 for f in D['furniture']:
  if f['level']==level:g.furniture(s,f)
 for w in D['walls']:
  if w['level']==level:g.wall_draw(s,w,False)
 for i in range(22):s.line((9.4+i*.36,1.1),(9.4+i*.36,2.4),'#78939d',1)
 for r in D['rooms']:
  if r['level']==level:
   x,y,X,Y=r['box'];s.wt((x+X)/2,(y+Y)/2,r['name'],16,anchor='middle',weight=700)
 if level==2:
  for id,a,b in [('舒亚',7.8,11),('子豪',11.2,14.5),('薇亚',14.7,18.6)]:s.dim((a,10.9),(b,10.9),id+' '+f'{b-a:.2f}m')
  for cid in ['F4_DOWN','F4_REVERSE']:
   c=next(c for c in M['cameras'] if c['id']==cid);x,y,z=c['pos'];tx,ty,tz=c['target'];n=math.hypot(tx-x,ty-y);s.circ(x,y,.08,'#177d9e');s.line((x,y),(x+(tx-x)/n*.7,y+(ty-y)/n*.7),'#177d9e',2,arrow=True);s.wt(x,y-.38,cid,13,anchor='middle')
 else:
  pts=[[8.6,1.75],[8.6,3.4],[7.8,4],[7.8,6.5],[4.1,6.5]]
  for a,b in zip(pts,pts[1:]):s.line(a,b,'#3b887a',3,'6 4',True)
 s.notes(100,980,[('建模参数',['梯段7.56m，22级高差；层高3.30m，板厚0.22m。','C二楼地面位于B下平台上方；A在梯顶大窗前侧接走廊。'])],760)
 s.notes(930,980,[('本版范围',['二楼公卫、布草未定位置，不补造门或房间。','一楼主要家具保留；二楼家具重新定位，床保持物理尺寸。'])],760)
 s.finish('M2_'+('一楼建模平面' if level==1 else '二楼建模平面'))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',29);small=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',22)
titles={'F4_DOWN':'A上平台看舒亚端：楼梯与三道卧室门','F4_REVERSE':'舒亚端回看A平台：尽头为大窗','F4_C':'C二楼端部地面、高窗与洞口收头','F4_UP':'梯段向上：A平台与大窗','F4_STAIR_DOWN':'A平台下看：直梯到B下平台','F4_B_CONNECT':'B下平台侧转接一楼客厅','F4_PLAN':'二楼顶视检查：隐藏屋顶，墙体未截矮','B1_01':'薇亚卧室：大床与房间比例','B1_TOP':'薇亚卧室家具顶视检查','B2_TOP':'子豪卧室家具顶视检查','B3_TOP':'舒亚卧室家具顶视检查','EXT_01':'全屋外部：二楼体量已按授权调整'}
manifest=[]
for cid,title in titles.items():
 c=next(c for c in M['cameras'] if c['id']==cid);folder='方位检查' if c['kind']=='顶视检查' else '白模视角';p=O/'空间'/c['room']/folder/(cid+'.png')
 im=Image.open(p).convert('RGB');assert im.size==(1920,1080),(cid,im.size)
 out=Image.new('RGB',(1920,1410),'#edf2ef');out.paste(im,(0,100));draw=ImageDraw.Draw(out)
 draw.text((28,13),'P2.4-M2 | '+cid+' | '+title,font=font,fill='#233e48')
 draw.text((28,58),'顶视检查：隐藏屋顶及上层；保留完整墙高' if c['kind']=='顶视检查' else '真实机位：完整墙体、楼板与屋顶；'+str(c['lens'])+'mm等效参考',font=small,fill='#527077')
 draw.text((30,1210),'位置 '+str(c['pos'])+' m   →   观察点 '+str(c['target']),font=small,fill='#233e48')
 draw.text((30,1254),'A：二楼上平台  /  B：一楼下平台  /  C：二楼端部地面',font=small,fill='#233e48')
 draw.text((30,1300),'F4空间关系已确认；模型尺寸、家具布置为本轮暂定实现。',font=small,fill='#527077')
 # Mini map is drawn from the same plan; north always up.
 ox,oy,scale=1460,1380,18
 def xy(x,y):return ox+x*scale,oy-y*scale
 for w in D['walls']:
  if w['level']==(1 if c['room']=='B' else 2):draw.line([xy(*w['a']),xy(*w['b'])],fill='#7b9298',width=3)
 x,y,z=c['pos'];tx,ty,tz=c['target'];px,py=xy(x,y);draw.ellipse((px-5,py-5,px+5,py+5),fill='#187f9d');length=math.hypot(tx-x,ty-y)
 if length>.01:draw.line([(px,py),xy(x+(tx-x)/length*1.2,y+(ty-y)/length*1.2)],fill='#187f9d',width=3)
 draw.text((1480,1190),'机位定位 · 北↑',font=small,fill='#233e48')
 q=O/'空间'/c['room']/'方位检查'/(cid+'_标注.png');q.parent.mkdir(parents=True,exist_ok=True);out.save(q)
 manifest.append(dict(id=cid,title=title,kind=c['kind'],file=p.relative_to(O).as_posix(),annotated=q.relative_to(O).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
refs=json.loads((R/'平面确认/F4用户确认记录.json').read_text(encoding='utf8'))
cards=''.join('<section><h2>'+x['title']+'</h2><img class="markable" alt="'+x['id']+'" src="'+x['annotated']+'?v='+x['sha256'][:12]+'"><p><a href="'+x['file']+'">干净PNG</a> · <a href="'+x['annotated']+'">标注PNG</a> · <a href="查看白模.html?rev=M2&cam='+x['id']+'">跳到模型机位</a></p></section>' for x in manifest)
reference_cards=''.join('<section><h2>原始参考 · '+html.escape(f)+'</h2><img src="../平面确认/走廊原始参考/'+f+'"></section>' for f in ['别墅二楼到楼梯间参考图（俯拍图）.png','别墅二楼走廊.png','别墅楼梯间参考.png'])
page='''<!doctype html><html lang="zh"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>P2.4-M2｜F4重建对照</title><style>body{margin:0;background:#edf2ef;color:#243e48;font:17px "Microsoft YaHei",sans-serif}header,main{max-width:1440px;margin:auto;padding:24px}header{line-height:1.8}h1{font-size:28px}h2{font-size:22px}section{padding:20px;background:white;margin:22px 0}img{display:block;width:100%}a{color:#197280}#mark{position:fixed;right:12px;bottom:12px;padding:12px;background:white;border:2px solid #337f85;max-width:360px}.markable{cursor:crosshair}</style><header><h1>P2.4-M2 · 按已确认F4关系重建</h1><p>按你的授权调整二楼房间宽深比例：护栏仅沿实际梯段洞口；C为二楼端部地面，B在其下方，A在梯顶大窗前。二楼仅保留三道卧室木门。</p><p><a href="查看白模.html?rev=M2&cam=F4_DOWN">打开可旋转白模</a> · <a href="模型/秘密教学_P2.4-M2.blend">Blender</a> · <a href="模型/秘密教学_P2.4-M2.glb">GLB</a> · <a href="../平面确认/打开平面图.html?rev=P2.4-F4">已确认F4关系图</a></p><p>本轮为关系重建模型，尺寸暂定。二楼公卫、布草未定位，未补造房间。二楼缩窄产生西侧屋面露台，外立面需后续核对。连续路线可在模型中播放，完整视频与全空间无盲角验收尚未完成。</p></header><main><section><h2>本轮模型对应的二楼平面（尺寸暂定）</h2><img class="markable" alt="M2_F2_PLAN" src="方位检查/M2_二楼建模平面.svg"></section><section><h2>一楼衔接与落脚位置</h2><img class="markable" alt="M2_F1_PLAN" src="方位检查/M2_一楼建模平面.svg"></section>CARDSREFS</main><div id="mark">直接批注图片，或点击获取机位与百分比位置。</div><script>document.querySelectorAll('.markable').forEach(im=>im.onclick=e=>{const b=im.getBoundingClientRect();document.querySelector('#mark').textContent=im.alt+'：x='+((e.clientX-b.left)/b.width*100).toFixed(1)+'%，y='+((e.clientY-b.top)/b.height*100).toFixed(1)+'%。';});</script></html>'''.replace('CARDS',cards).replace('REFS',reference_cards)
(O/'F4建模对照.html').write_text(page,encoding='utf8')
(O/'查看白模.html').write_text((R/'scripts/view_m2.html').read_text(encoding='utf8'),encoding='utf8')
files=[O/'模型/秘密教学_P2.4-M2.blend',O/'模型/秘密教学_P2.4-M2.glb',O/'模型/建模方案.json',O/'模型/空间数据.json']
files += [O/x[k] for x in manifest for k in ['file','annotated']]
files += list(Q.glob('M2_*.svg'))
(O/'检查记录/M2交付清单.json').write_text(json.dumps(dict(revision=M['revision'],images=manifest,files=[dict(path=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in files]),ensure_ascii=False,indent=2),encoding='utf8')
print('M2 review packaged: 12 clean + 12 annotated PNG, 2 source-data plans.')
