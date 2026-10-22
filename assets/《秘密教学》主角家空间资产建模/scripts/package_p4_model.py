"""Package the approved-plan model and publish current local entry points."""
from pathlib import Path
import json,hashlib,shutil,html
R=Path(__file__).resolve().parents[1];repo=R.parents[1];O=R/'全屋模型_P4-M1_20261022';P4=R/'整体平面_P4_20261022';A=R/'完整平面与品牌_P3_R2_20261022'
for p in (A/'品牌贴图').iterdir():
 if p.is_file():shutil.copy2(p,O/'贴图'/p.name)
checks=json.loads((O/'检查/模型回读与几何核对.json').read_text('utf8'))
assert checks['passed']==checks['total'],checks['failed']
description='''# P4-M1 全屋空间模型

2026-10-22，用户确认 P4 整体平面正确，授权据此重新建模并同步 GitHub。新模型独立保存，不覆盖 P2.4-M3。

## 内容

- 一楼、二楼、公共庭院、私人阳台、屋顶楼梯间及外部庭院、车库、围墙。
- 78 件既定室内家具与 7 件庭院家具；全部平面坐标沿用 P4。大姐床 3.90×2.52m；二姐床贴墙、C02 位于床尾；子豪门中心 x=9.65m。
- 公共浴室玻璃门、舒亚门对面落地窗、直梯及上屋顶双跑楼梯。
- 4 块准确字形门牌、40 个固定品牌位置；完整版含 hgdju.com，镜像版整组翻转。
- 8 张直接模型检查渲染。基础材质与简化家具用于核对空间，不等同最终写实场景图。

## 打开

打开 `模型/秘密教学_P4-M1.blend`，所有贴图已经内嵌。通用交换文件为同名 GLB，包含材质、贴图、相机与构件属性。
Blender 集合按楼层与类型命名；隐藏 F3 屋顶相关集合可检查二楼，隐藏 F2/F3 可检查一楼。预览页提供这两种剖开视图。
`贴图/` 保留正向、整组镜像、图标与门牌 PNG/SVG 和文字源；固定字形已在模型中转为网格。

## 依据与边界

P4 图纸已获用户确认，模型仍待用户从立体视角验收。房间、家具和楼梯数据保持原样；实际墙体合并共线重叠部分，补齐未单独标注的通路边界。公共庭院门按图纸建为双扇玻璃门。
品牌图纸是点位规划。建模时避开门窗并贴到真实墙面，落地标识使用支承，摆件落到柜顶，织物图标固定到床面。逐项原点位、实际点位、朝向、尺寸和载体见 `数据/品牌固定变换.json`，未改变家具布局。
屋顶梯间顶面建模到 +9.42m（图纸 +9.20m 墙顶加 0.22m 盖板）；没有新增整层三楼住宅。
本交付为影视空间模型，梁柱、荷载、防水与机电不是工程施工设计；软装和植物为基础表现。未自动生成新 AI 场景图。

## 校核

模型已回读 Blend 和 GLB，对照确认数据检查家具占地、用户指定床位与门位、洞口、楼梯踏步和中心垂直净空、公共通路、门牌字形、品牌域名、内嵌贴图和导出坐标。详细结果见检查 JSON。
原 7 张认可图与 M3 文件逐一 SHA-256 校验不变；B6 不恢复。
'''
(O/'交付说明.md').write_text(description,'utf8')
notes={
'01_完整外观':'P4 完整体量、前庭、车库和围墙。屋顶灰色体量仅为出屋面楼梯间。',
'02_二楼剖开总览':'隐藏屋顶查看三间卧室、公共浴室、楼道与公共庭院；墙体保持完整高度。',
'03_一楼剖开总览':'隐藏二楼及屋顶；一楼室内布置保持，新增庭院下方檐下空间。',
'04_公共庭院':'从公共走廊经双扇玻璃门进入，花槽、座椅与主通道分开。',
'05_走廊朝浴室':'尽头为公共浴室玻璃门；短护栏、直梯及采光窗关系保留。',
'06_大姐卧室':'床按确认图延长，其余家具尺寸不变。当前为基础材质检查渲染。',
'07_二楼正投影':'可直接与 P4 二楼总平面对照家具位置和外部庭院。',
'08_屋顶楼梯剖开':'局部隐藏东、南墙及屋顶，显示二楼至屋顶双跑楼梯。'}
cards=''.join(f'<section id="{n}"><h2>{html.escape(n.replace("_"," / "))}</h2><p>{v}</p><a href="预览/{n}.png" target="_blank"><img loading="lazy" src="预览/{n}.png" alt="{n}"></a></section>' for n,v in notes.items())
nav=''.join(f'<a href="#{n}">{n.replace("_"," ")}</a>' for n in notes)
doc=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>秘密教学 · P4-M1 全屋模型</title><style>*{{box-sizing:border-box}}body{{margin:0;background:#f4f2ec;color:#253b3b;font:16px/1.7 'Microsoft YaHei',sans-serif}}header,main{{max-width:1450px;margin:auto;padding:28px}}h1{{font-size:34px}}h2{{font-size:22px}}a{{color:#256b5c}}.status{{background:#e2ebe1;padding:20px;border-left:4px solid #54846d}}nav,.actions{{display:flex;gap:12px;flex-wrap:wrap;margin:20px 0}}.actions a{{background:#294c44;color:white;padding:9px 16px;border-radius:5px;text-decoration:none}}section{{background:white;padding:20px;margin:28px 0;border:1px solid #d4ddd5;border-radius:9px}}img{{display:block;width:100%;height:auto}}small{{color:#566965}}</style><header><small>2026-10-22 · P4-M1 · 基于用户确认的完整平面</small><h1>《秘密教学》全屋空间模型</h1><div class="status">P4 平面已确认，本轮已据此重建全屋。房间与家具坐标保持；公共庭院、屋顶楼梯间、门牌和固定品牌资产已纳入。当前展示基础材质模型检查图，立体效果待用户审阅。</div><div class="actions"><a href="模型/秘密教学_P4-M1.blend" download>下载 Blender 模型</a><a href="模型/秘密教学_P4-M1.glb" download>下载 GLB 模型</a><a href="交付说明.md">交付说明</a><a href="检查/模型回读与几何核对.json">{checks['passed']} 项检查结果</a></div><nav>{nav}</nav></header><main>{cards}<section><h2>配套文件</h2><p><a href="数据/模型空间数据.json">构件、房间、机位与确认平面数据</a> · <a href="数据/品牌固定变换.json">品牌实际贴装位置</a> · <a href="贴图/HG_FULL_normal.png">正向品牌母版</a> · <a href="贴图/HG_FULL_mirror.png">整组镜像母版</a></p><p>三间卧室门牌和公共浴室标识保持正常阅读。完整版品牌含 hgdju.com；镜像包含图标、中文字与域名。所有贴图内嵌在模型中，也在贴图目录提供独立文件。</p><p>原 M3 和 7 张认可图片继续保留。没有批量生成新的 AI 场景图。</p></section></main></html>'''
(O/'统一查看页.html').write_text(doc,'utf8')
accept=dict(date='2026-10-22',user_statement='整体已经正确，就按照这个平面图，重新建模吧，同步更新一下GitHub仓库',plan='P4-20261022',model='P4-M1',plan_geometry_sha256=hashlib.sha256((P4/'数据/整体空间方案_P4.json').read_bytes()).hexdigest(),note='方案JSON中的待审阅文字是生成时历史状态，本验收记录更新其状态，几何源文件不改写。')
(P4/'数据/用户确认记录.json').write_text(json.dumps(accept,ensure_ascii=False,indent=2),'utf8')
p=P4/'统一查看页.html';s=p.read_text('utf8').replace('P4 新外部设计稿','P4 已确认整体平面').replace('新增外部待审阅，尚未回写全屋模型。','整体平面已获用户确认，已据此输出 P4-M1 全屋模型。').replace('新增外部的确认边界','设计与工程深化边界');p.write_text(s,'utf8')
p=P4/'设计说明.md';s=p.read_text('utf8');s=s.replace('# P4 整体平面构思','# P4 整体平面（已确认）\n\n2026-10-22 最新状态：用户已确认整体正确，授权按本平面重建模型并同步 GitHub。新模型为独立的 P4-M1。下文保留设计依据；空间 JSON 的生成时状态由数据/用户确认记录.json 覆盖。');s=s.replace('全部外部仍属设计提案，未更新全屋Blend/GLB，也未生成实际场景图。','本整体平面已确认，已按图独立输出P4-M1全屋Blend/GLB；未生成新的AI场景图。');p.write_text(s,'utf8')
base='assets/《秘密教学》主角家空间资产建模'
p=repo/'当前资产交付.md';s=p.read_text('utf8');old=s.index('## 本地新增设计稿');tail=s[old:];tail=tail.replace('## 本地新增设计稿：P3-R1（待验收，尚未远端上传）','## 历史设计稿：P3-R1（已由P3-R2/P4替代）').replace('## 建模文件','## 原M3历史建模文件（保留对照）');p.write_text(f'''# 《秘密教学》当前资产交付

## 最新模型：P4-M1

用户已确认 P4 整体平面正确，并授权据此重新建模、同步 GitHub。模型新建为独立 P4-M1，原 M3 和 7 张认可图保留。

- [全屋模型统一查看页]({base}/全屋模型_P4-M1_20261022/统一查看页.html)
- [Blender完整模型]({base}/全屋模型_P4-M1_20261022/模型/秘密教学_P4-M1.blend)
- [GLB通用模型]({base}/全屋模型_P4-M1_20261022/模型/秘密教学_P4-M1.glb)
- [模型交付说明]({base}/全屋模型_P4-M1_20261022/交付说明.md)
- [确认的P4整体平面]({base}/整体平面_P4_20261022/统一查看页.html)
- [回读与几何检查]({base}/全屋模型_P4-M1_20261022/检查/模型回读与几何核对.json)

已整合全屋、公共庭院、屋顶梯间、门牌、正向/镜像含 hgdju.com 品牌。基础材质模型和直接检查渲染供立体审阅；不代表最终写实场景图验收。Blend/GLB与图片经Git LFS保存于现有工作分支，不合并main。

下方为历史版本背景；涉及“尚未重建”的句子仅描述当时状态，当前入口以上方P4-M1为准。

'''+tail,'utf8')
p=repo/'README.md';s=p.read_text('utf8');a=s.index('本地最新平面入口：');b=s.index('`wuji-video-creation`');s=s[:a]+f'''当前空间基线：[已确认的P4整体平面]({base}/整体平面_P4_20261022/统一查看页.html)；新模型入口：[P4-M1全屋模型]({base}/全屋模型_P4-M1_20261022/统一查看页.html)。模型按确认平面重建，含公共庭院、屋顶楼梯间、准确门牌与固定品牌资产，提供Blend、GLB和检查渲染。

当前交接：[第7集场景交接](docs/episode7-scenes/新对话交接.md)。原7张认可日景图及P2.4-M3作为历史资产原样保留；平面确认不等同新模型与最终场景图已获验收。

'''+s[b:];p.write_text(s,'utf8')
entry=f'''## 2026-10-22 P4已确认，按图重建P4-M1全屋模型

用户最新授权：“整体已经正确，就按照这个平面图，重新建模吧，同步更新一下GitHub仓库”。P4完整平面现为确认基线，覆盖此前新增外部待审阅状态。负责人Codex。

独立输出 `{base}/全屋模型_P4-M1_20261022`：全屋Blend/GLB、8张直接检查渲染、统一查看页、贴图与可编辑文字源、空间数据及品牌固定变换。保留78件室内家具坐标，加入7件庭院家具；公共浴室玻璃门、舒亚对面落地窗、直梯、公共庭院双扇门及出屋面楼梯间均落实。

两格式各1124网格（最终以检查报告为准），回读坐标误差不超过2mm；{checks['total']}项检查通过。直梯踏步中心最小垂直净空3.23m，上屋顶梯2.75m。4块门牌文字转网格；40处品牌固定，完整版含hgdju.com，正向与整组镜像；实际贴装避让门窗并记录坐标。原M3及7张认可图SHA-256不变。

新模型是基础材质的影视空间模型，立体表现待用户审阅；没有批量生成AI场景图。梁柱与防水等不是施工验算。同步现有分支 `codex/20261014-secret-teaching-home-assets`，不合并main；后续应读取P4-M1，不再把M3当作当前几何基线。

'''
p=repo/'docs/project-state.md';s=p.read_text('utf8');p.write_text(s.split('\n',1)[0]+'\n\n'+entry+s.split('\n',1)[1].lstrip(),'utf8')
p=repo/'docs/episode7-scenes/新对话交接.md';s=p.read_text('utf8');p.write_text(s.split('\n',1)[0]+'\n\n'+entry+'以下保留历史交接；与上方新状态冲突时以上方为准。\n\n'+s.split('\n',1)[1].lstrip(),'utf8')
for folder in [O,P4]:
 files=[dict(file=p.relative_to(folder).as_posix(),bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(folder.rglob('*')) if p.is_file() and p.name!='交付文件校验.json']
 (folder/'检查/交付文件校验.json').write_text(json.dumps(dict(revision='P4-M1' if folder==O else 'P4-20261022',files=files),ensure_ascii=False,indent=2),'utf8')
print('PACKAGED',checks['passed'],len(list(O.rglob('*'))))
