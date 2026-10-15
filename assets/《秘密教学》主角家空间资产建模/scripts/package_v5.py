"""Build a portable viewer and reference comparison page, without image generation."""
import argparse,json,re,base64,html,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--reference-root',default=str(R/'参照/V3'));a=p.parse_args();S=Path(a.reference_root)
D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'))
url=lambda s:'data:text/javascript;base64,'+base64.b64encode(s.encode()).decode()
core=url((R/'vendor/three.core.js').read_text(encoding='utf8'));three=(R/'vendor/three.module.js').read_text(encoding='utf8').replace('./three.core.js',core)
imports={'three':url(three),'./vendor/OrbitControls.js':url((R/'vendor/OrbitControls.js').read_text(encoding='utf8'))}
page=(R/'V5校准检查.html').read_text(encoding='utf8');page=re.sub(r'<script type="importmap">.*?</script>','<script type="importmap">'+json.dumps({'imports':imports})+'</script>',page,flags=re.S)
js=(R/'v5-viewer.js').read_text(encoding='utf8').replace("await(await fetch('./模型/空间校准主数据_v5.json')).json()",json.dumps(D,ensure_ascii=False))
page=page.replace('<script type="module" src="./v5-viewer.js"></script>','<script type="module">'+js.replace('</script','<\\/script')+'</script>');(R/'打开V5校准模型.html').write_text(page,encoding='utf8')
out=R/'预览/v5';out.mkdir(parents=True,exist_ok=True);idx=json.loads((R/'制作记录/V3参考索引.json').read_text(encoding='utf8'))['files'];byid={x['id']:x for x in idx}
pairs=[('V3_042','E_side','双窗、床、书桌、梳妆台与阳台门'),('V3_043','E_cut','去顶俯视检查，不用于正式摄影'),('V3_040','KLD_K_front','厨房设备与水槽横窗'),('V3_041','KLD_K_reverse','厨房直接看餐厅；客厅位于侧面'),('V3_061','M_front','床、工作区与望远镜'),('V3_010','Y_cut','床、书桌、入口、收藏与星形地毯'),('V3_065','P_cut','主卧入口在床头侧，主卫仅从床尾侧进入'),('V3_057','LA_front','洗衣房体量与双排台面'),('V3_026','SITE_front','外部体量研究：车库、围墙与人行入口')]
body=['<h1>V3 参考与 v5 校准模型</h1><p>已按用户选择增加采光院并转折走廊，形成全屋拼接提案。中性几何用于查关系，不能作为最终场景图片。</p><p><a href="../../打开V5校准模型.html">打开可旋转模型</a></p>']
body.append('<h2>全屋拼接与实际外形</h2><div class="pair">'+''.join('<figure><img src="'+cid+'.png"><figcaption>'+title+'</figcaption></figure>' for cid,title in [('HOME_floor1','一楼去顶检查'),('HOME_floor2','二楼去顶检查'),('HOME_exterior','包含室内拼接的实际外形'),('HOME_stairs_up','B端向上看有支承的直跑楼梯')])+'</div>')
for rid,cid,title in pairs:
 f=S/byid[rid]['relative_path']
 if not f.exists():f=S/(rid+f.suffix)
 dest='参考_'+rid+f.suffix;shutil.copyfile(f,out/dest)
 body.append('<section><h2>'+html.escape(title)+'</h2><div class="pair"><figure><img src="'+dest+'"><figcaption>'+rid+' 用户指定 V3 原图</figcaption></figure><figure><img src="'+cid+'.png"><figcaption>'+cid+' 校准模型；材质为示意</figcaption></figure></div></section>')
body.append('<h2>仍需解决</h2><ul>'+''.join('<li><b>'+x['id']+'</b> '+html.escape(x['fact']+' '+x['decision'])+'</li>' for x in D['assembly_conflicts'])+'</ul>')
(out/'对照与复核.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>V3 与模型对照</title><style>body{font:16px/1.7 system-ui;margin:32px;background:#eef1ed;color:#263c34}h1{font-size:28px}h2{font-size:19px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:14px}figure{margin:0;background:white;padding:8px}img{width:100%;aspect-ratio:1.65;object-fit:contain;background:#e7eae9}section{margin:28px 0}a{color:#277461}li{margin:14px 0}</style>'+''.join(body)+'</html>',encoding='utf8')
# Real orthographic diagram from the same object coordinates. No hand-drawn room positions.
for m in D['modules']:
 if m['id']=='HOME':continue # two aligned storey plans are exported by plan_v5.py
 obs=[o for o in D['objects'] if o['module']==m['id'] and o['role'] not in ['ceiling','glass','decor','brand','fixture','frame']]
 bounds=[min(o['box'][k] for o in obs) for k in [0,1]]+[max(o['box'][k] for o in obs) for k in [3,4]];x0,y0,X,Y=bounds;scale=min(1000/(X-x0),800/(Y-y0));W=(X-x0)*scale+120;H=(Y-y0)*scale+140
 def px(x):return 60+(x-x0)*scale
 def py(y):return 80+(Y-y)*scale
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="#f5f4ef"/><g font-family="Microsoft YaHei, sans-serif"><text x="25" y="30" font-size="20">{html.escape(m["name"])}</text><text x="25" y="55" font-size="13">同一主数据俯视投影 · 影视设计参考尺寸 · 独立模块非全屋平面图</text>']
 for o in sorted(obs,key=lambda o:(o['box'][2]+o['box'][5])/2):
  b=o['box'];svg.append(f'<rect x="{px(b[0]):.2f}" y="{py(b[4]):.2f}" width="{(b[3]-b[0])*scale:.2f}" height="{(b[4]-b[1])*scale:.2f}" fill="{o["color"]}" stroke="#69716a" stroke-width="0.5"><title>{o["id"]}</title></rect>')
 for op in [v for v in D['openings'] if v['module']==m['id']]:
  x=op['start']+op['width']/2 if op['axis']=='x' else op['plane'];y=op['plane'] if op['axis']=='x' else op['start']+op['width']/2
  svg.append(f'<text x="{px(x):.1f}" y="{py(y):.1f}" text-anchor="middle" fill="#08627d" font-size="10">{op["width"]:.2f}m</text>')
 svg.append('</g></svg>');(out/(m['id']+'_平面.svg')).write_text(''.join(svg),encoding='utf8')
print('V5 portable viewer, source comparison and 7 projected plans created')
