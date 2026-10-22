"""Make the local review entry and reproducible deliverable inventory."""
from pathlib import Path
import json,html,hashlib
R=Path(__file__).resolve().parents[1];O=R/'完整平面与品牌_P3_R2_20261022'
D=json.loads((O/'数据/空间方案_P3.json').read_text(encoding='utf8'))
esc=html.escape
sections=[]
for group,folder in [('平面图纸','图纸'),('品牌与门牌贴图','品牌贴图'),('独立模型','独立模型')]:
 cards=[]
 for p in sorted((O/folder).glob('*.png')):
  rel=p.relative_to(O).as_posix();stem=p.stem.replace('_预览','');links=[]
  for ext in ['.png','.svg','.blend','.glb']:
   q=p if ext=='.png' else p.parent/(stem+ext)
   if q.exists():links.append(f'<a href="{esc(q.relative_to(O).as_posix())}" download>{ext[1:].upper()}</a>')
  cards.append(f'<article><h3>{esc(stem)}</h3><a href="{esc(rel)}" target="_blank"><img src="{esc(rel)}?r=R1" loading="lazy" alt="{esc(stem)}"></a><div>{" · ".join(links)}</div></article>')
 sections.append(f'<section id="{folder}"><h2>{group}</h2><div class="grid">{"".join(cards)}</div></section>')
 rows=[]
 for b in D['brands']:
  rows.append('<tr>'+''.join(f'<td>{esc(str(v))}</td>' for v in [b['room'],b['carrier'],b['variant'],b['position'],b['size'],b['light']])+'</tr>')
 datalinks=' · '.join(f'<a href="数据/{esc(p.name)}">{esc(p.name)}</a>' for p in sorted((O/'数据').iterdir()))
 document='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>秘密教学 P3-R1 平面与独立资产</title><style>
*{box-sizing:border-box}body{margin:0;background:#f6f5f0;color:#263e42;font:16px/1.65 "Microsoft YaHei",sans-serif}header,main{max-width:1440px;margin:auto;padding:28px}h1{font-size:30px;margin:8px 0}h2{margin-top:40px}a{color:#256b63}nav{display:flex;gap:24px;flex-wrap:wrap}.note{padding:18px 24px;background:#e8eee6;border-left:4px solid #548c74}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:22px}article{background:white;padding:16px;border:1px solid #d5dfd7;border-radius:10px}article img{width:100%;height:auto;max-height:620px;object-fit:contain;background:#efeee7}h3{margin:0 0 12px;font-size:18px}table{border-collapse:collapse;font-size:13px;width:100%}td,th{text-align:left;padding:8px;border-bottom:1px solid #d5dfd7}section{scroll-margin-top:20px}.scroll{overflow:auto}@media(max-width:600px){.grid{display:block}article{margin-bottom:16px}header,main{padding:16px}}</style>
<header><h1>《秘密教学》P3-R1 平面与独立资产</h1><p>2026-10-22 · 家具 → 使用空间 → 房间 → 楼层 → 外轮廓 → 地块</p><nav><a href="#图纸">平面图纸</a><a href="#品牌贴图">品牌贴图</a><a href="#独立模型">独立模型</a><a href="#台账">固定台账</a></nav></header><main>
<div class="note"><b>本次三处修订</b><br>子豪门移至指定位置，入口小柜避开门扇；大姐床长延至3.90m、宽2.52m，床尾距电脑桌侧边0.20m；二姐床贴右墙。原M3与7张认可图均保留。<br><b>状态：</b>平面设计稿待验收；独立标识资产已输出。全屋模型尚未同步，机位遮挡、镜面反射及最终场景露出仍待整模检查。</div>
'''+''.join(sections)+f'<section id="台账"><h2>固定品牌台账</h2><p>位置单位m；朝向、母版、机位见下方数据。N/M为独立正向及整组镜像实物，房间门牌保持正向。</p><div class="scroll"><table><thead><tr><th>空间</th><th>载体</th><th>版本</th><th>固定位置</th><th>尺寸</th><th>发光</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div><p>{datalinks}</p><h2>待核实</h2><ul>'+''.join(f'<li>{esc(t)}</li>' for t in D['unresolved'])+'</ul></section></main></html>'
document=document.replace('P3-R1','P3-R2').replace('?r=R1','?r=R2').replace('<b>本次三处修订</b>','<b>R2新增修订：C02小书架对齐C01床尾，尺寸与间距保持。</b><br><b>此前三处修订</b>')
(O/'统一查看页.html').write_text(document,encoding='utf8')
(O/'交付说明.md').write_text('''# P3-R1 平面与独立标识资产

本版为独立设计稿，不替换P2.4-M3及7张已认可日景图。先内部后外部，原楼道长度和外轮廓不是内部限制条件。

## 最新三处修订

- 子豪门中心横坐标9.65m，对应用户图示x38.5%；门洞宽1.00m。入口小柜移至门右，尺寸保持。
- 大姐床向电脑桌延长至3.90×2.52m；床尾与电脑桌侧边净距0.20m，南段通行不通过该窄缝。此条为最新局部指示，覆盖初稿1.20倍等比床方案。
- 二姐床向右贴墙，床尺寸1.50×2.20m保持；其他家具尺寸保持。

## 内容

图纸包含一楼、二楼、卧室及浴室放大、屋顶、楼梯剖面、外部总平面、两层品牌布置；每张提供可编辑SVG和3600×2480 PNG。数据包含家具/房间尺寸、品牌固定变换及机位预检。

独立模型包含4块门牌、正向及镜像实体品牌牌、霓虹牌、立体图标摆件，共10套Blend/GLB，另附总资产库Blend。完整版包含hgdju.com；小摆件使用简化图标。门牌保持正常方向。SVG和文字JSON为可编辑排版源，模型中文字为固定网格字形，贴图已嵌入GLB及Blend。

霓虹文字和图标本体自发光；背光为独立可选关闭层。镜像是完整母版/模型的水平翻转，不能用字符倒排替代。

## 验证范围

见检查目录：家具范围、门扇扫掠、房内代表通路、镜像像素、原始交付SHA-256、图纸边界。通行检查使用0.50m直径参考体和0.10m网格，不能等同最终家具细部、结构梁底净空或无障碍验收。

仍待用户确认平面；全屋模型、真实镜面反射、最终摄影机遮挡和AI场景图逐张验收尚未实施。品牌覆盖表是设计布点与机位预检，不能视为最终镜头可见率验收。
'''.replace('P3-R1','P3-R2').replace('## 最新三处修订','## R2新增修订\n\nC02床尾小书架向右平移0.80m，与贴墙后的C01床尾横向居中对齐；原尺寸0.70×0.60m和床尾间距0.20m保持。\n\n## 此前三处修订'),encoding='utf8')
manifest=[]
for p in sorted(O.rglob('*')):
 if p.is_file() and p.name!='交付文件校验.json' and p.suffix!='.log':manifest.append(dict(file=p.relative_to(O).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
(O/'检查/交付文件校验.json').write_text(json.dumps(dict(revision=D['revision'],files=manifest),ensure_ascii=False,indent=2),encoding='utf8')
print('Packaged',len(manifest),'files')
