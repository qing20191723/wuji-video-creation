"""Package an inspected imagegen candidate; never promotes unverified text to final."""
import argparse,json,hashlib,shutil
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--first',required=True);p.add_argument('--repaired',required=True);p.add_argument('--output-root',required=True);a=p.parse_args()
out=Path(a.output_root).resolve();name='二楼走廊_后露台方向看三间卧室（高位日景）.png'
target=out/'待核对/楼梯与走廊'/name;target.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(a.repaired,target);shutil.copy2(a.first,R/'预览/v4.4/H203_材质初稿.png');shutil.copy2(a.repaired,R/'预览/v4.4/H203_材质修正版.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
refs=['预览/v4.4/H203_模型底图.png','参照/别墅二楼走廊.png','品牌/黄瓜短剧_无域名_透明底.png']
record={'id':'H203','model':'模型/秘密教学_主角家_v4.4.blend','model_sha256':sha(R/'模型/秘密教学_主角家_v4.4.blend'),'method':'built-in imagegen; model camera base; original material reference; one text repair','prompts':['制作记录/H203_实际提示词_v4.4.txt','制作记录/H203_门牌局部修正提示词_v4.4.txt'],'refs':[{'file':f,'sha256':sha(R/f)} for f in refs],'output_relative_to_scene_collection':str(target.relative_to(out)).replace('\\','/'),'sha256':sha(target),'resolution':list(Image.open(target).size),'status':'candidate_pending_distant_text_and_edge_review','formal_ready':False,'camera':'H203','issues':['远处子豪、薇亚门牌在实际输出尺寸下无法逐字可靠验清','生成图增加少量顶灯并细化门框，边线相对底图有少量变化，未达到逐像素锁定','房间比例尚未根据无标尺原图完成校准'],'reviewed':['三门数量与近远顺序','完整门墙与实体护栏高度区分','无前景门洞/门楣','单一无域名黄瓜短剧实体标牌','柔和明亮白天光线']}
(R/'制作记录/H203_制作与检查_v4.4.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf8')
manifest=json.loads((R/'制作记录/制作清单.json').read_text(encoding='utf8'))
for item in manifest:
    item['refs']=[];item['reference_selection_status']='select_and_inspect_for_this_camera; historical refs are not active inputs'
    if item['id'].startswith('H2'):item['logo']='二楼护栏B端朝后露台端墙，唯一无域名标牌，宽1.10m；原远端侧墙不再放置'
    if item['id']=='H203':item.update(status=record['status'],candidate_file=record['output_relative_to_scene_collection'],sha256=record['sha256'],actual_prompt_file=record['prompts'][0],review_file='制作记录/H203_制作与检查_v4.4.json')
    if item['id']=='H203':item.update(refs=refs,reference_selection_status='inspected; each role specified in actual prompt')
assert len(manifest)==97
(R/'制作记录/制作清单.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
# Real camera shows closed doors, while plan/walk keeps the explicitly open navigation state.
vp=R/'viewer.js';s=vp.read_text(encoding='utf8');needle=' for(const s of labels)s.visible='
insert=""" if(m==='all'&&!walking){for(const o of meshes){const d=o.userData;if(!['D203_leaf','D204_leaf','D205_leaf'].includes(d.id))continue;const op=D.openings.find(p=>p.id===d.id.slice(0,4)),b=d.box,bb=[3.377,op.s,3.3,3.423,op.s+op.w,5.46];for(let k=0;k<3;k++){const scale=(bb[k+3]-bb[k])/(b[k+3]-b[k]);o.scale.setComponent(k,scale);o.position.setComponent(k,bb[k]-b[k]*scale);}}}
"""
if insert not in s:
    assert needle in s;s=s.replace(needle,insert+needle);vp.write_text(s,encoding='utf8')
page='''<!doctype html><meta charset="utf-8"><title>秘密教学 v4.4 · 首张空间材质复核</title><style>body{font:16px/1.8 "Microsoft YaHei",sans-serif;background:#edf1f2;color:#25363a;max-width:1500px;margin:32px auto;padding:0 24px}h1{font-size:28px}.note{background:#fff3da;padding:18px;border-left:5px solid #b77b2b}.grid{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%;background:white}a{color:#245c66}figure{margin:0}figcaption{font-size:14px;padding:8px 0}li{margin:5px 0}</style>
<h1>《秘密教学》v4.4 · 后露台方向看三间卧室</h1><p class="note">待核对样图，不计入合格终稿。近→远：舒亚の窝 → 子豪の窝 → 薇亚的窝。远端两牌逐字可验性与少量边线差异尚未通过。</p>
<div class="grid"><figure><img src="预览/v4.4/H203_模型底图.png"><figcaption>同一模型摄影机底图：2.25 m 高、20 mm、俯角 15°，完整墙高。</figcaption></figure><figure><img src="预览/v4.4/H203_材质修正版.png"><figcaption>imagegen 材质修正版：1672×941；原浅墙、木色、黑窗框；唯一实体 Logo 在护栏端墙。</figcaption></figure></div>
<p><a href="打开检查模型.html">旋转检查 v4.4 模型</a> · <a href="图纸/两层同向平面图_v4.4.svg">同源两层平面图</a> · <a href="校验/空间复核_v4.4.md">尺寸问题与检查边界</a></p>
<ul><li>显示误导已修复：墙高 3.08 m；护栏含压顶 1.16 m。</li><li>走廊净宽约 1.48 m；门中心距维持 2.8 m / 4.9 m，未为构图搬门。</li><li>25 个空间可达，1,117 个路线采样点无碰撞。三间卧室比例及辅助区效率仍待进一步校准。</li><li>原始素材保留；本图未替换任何已合格场景。</li></ul>
<div class="grid"><figure><img src="预览/v4.4/H203_门窗轮廓核对.png"><figcaption>门扇包围框检查副本（模型投影，不是像素分割）。</figcaption></figure><figure><img src="预览/v4.4/H203_文字位置核对.png"><figcaption>精确模型文字位置；不代替成图小字验收。</figcaption></figure></div>'''
(R/'v4.4首张对照检查.html').write_text(page,encoding='utf8')
print('CANDIDATE_SAVED',str(target));print('RESOLUTION',record['resolution'])
