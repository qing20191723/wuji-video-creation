from pathlib import Path
import json,hashlib,html,re,csv
R=Path(__file__).resolve().parents[1]
records=json.loads((R/'制作记录/直接渲染首批.json').read_text(encoding='utf8'))
for item in records:
 p=R/'预览/直接渲染'/item['file'];item['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();item['bytes']=p.stat().st_size;item['status']='direct_render_prototype_not_final'
(R/'制作记录/直接渲染首批.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
# Explicitly retire the generative prototype pipeline, without promoting any trial.
for p in (R/'制作记录').glob('*attempt*.json'):
 d=json.loads(p.read_text(encoding='utf8'));d['status']='retired_by_user_direct_render_request';d['generated_path']='本地试制/'+Path(d['generated_path']).name;d['references']=['本地参考/'+Path(x).name for x in d['references']];p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
p=R/'制作记录/制作清单.json';items=json.loads(p.read_text(encoding='utf8'))
for item in items:item['status']='awaiting_direct_render_finish';item['method']='Blender Cycles direct render';item['model_version']='v4.3_pilot';item.pop('size',None)
p.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf8')
(R/'制作记录/流程变更.json').write_text(json.dumps({'date':'2026-10-14','reason':'用户要求直接对同一个模型设置多个摄影机并渲染，避免AI重绘导致空间变化','active_method':'Blender Cycles direct render','abandoned_method':'灰模参考 + imagegen整图重绘','formal_scene_ready':0,'formal_scene_target':95,'auxiliary_target':2,'pilot_renders':len(records),'quality_limit':'首批可验证固定机位、门牌和日夜状态；家具精度、布艺、照片收藏、生活陈设仍未达到原图质感'},ensure_ascii=False,indent=2),encoding='utf8')
intro='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>直接渲染首批检查</title><style>body{font:16px/1.7 system-ui;background:#eef1f2;color:#26333b;margin:0}main{max-width:1500px;margin:auto;padding:30px}h1{font-size:30px}a{color:#176a8a}.note{padding:20px;background:#fff1ce;border-radius:10px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:white;padding:12px}.card img{width:100%}small{color:#586771}</style><main><h1>同一模型，固定摄影机，直接渲染</h1><p>《秘密教学》主角家空间资产建模 · v4.3 首批技术样图</p><p class="note">本页全部画面来自 Blender Cycles，没有 AI 重绘。它们验证空间固定、标牌固定、日夜与不同机位的关系；目前仍是制作样图，家具、照片装饰与材质尚未达到原场景图的精细程度，不列为全屋终稿。</p><p><a href="模型/秘密教学_主角家_直接渲染_v4.3.blend">最新 Blender 样模</a> · <a href="打开检查模型.html">已认可结构交互查看</a> · <a href="制作记录/直接渲染首批.json">机位与文件记录</a></p><div class="grid">'''
cards=[]
for it in records:
 src='预览/直接渲染/'+it['file'];cards.append('<article class="card"><a href="'+src+'"><img src="'+src+'"></a><p>'+html.escape(it['file'])+'</p><small>'+('正交剖切关系图，不是走廊内普通机位' if '关系图' in it['file'] else '同一实体空间，未移动家具与门窗')+'</small></article>')
(R/'直接渲染首批检查.html').write_text(intro+'\n'.join(cards)+'</div></main></html>',encoding='utf8')
print('Packaged',len(records),'direct-render prototypes; 0 promoted to final.')
