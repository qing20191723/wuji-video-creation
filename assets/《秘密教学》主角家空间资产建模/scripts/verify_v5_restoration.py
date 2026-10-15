"""Compare a separate HTTPS restore against local v5 binaries and master data."""
import argparse,hashlib,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('restored_asset');p.add_argument('--commit',required=True);p.add_argument('--runtime-checked',action='store_true');a=p.parse_args();R=Path(__file__).resolve().parents[1];T=Path(a.restored_asset)
refs=json.loads((R/'制作记录/V5必要参考备份清单.json').read_text(encoding='utf8'))
paths=['模型/秘密教学_V3校准模块_v5.blend','模型/秘密教学_V3校准模块_v5.glb','图纸/全屋两层同向平面_v5.png']+[x['backup_path'] for x in refs];records=[]
for rel in paths:
 src=(R/rel).read_bytes();dst=(T/rel).read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest();records.append({'path':rel,'bytes':len(dst),'sha256':sha(dst),'matches_local':sha(src)==sha(dst)})
assert all(x['matches_local'] for x in records),'binary mismatch'
assert json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'))==json.loads((T/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'))
glb=(T/paths[1]).read_bytes();magic,version,length=struct.unpack_from('<III',glb);assert magic==0x46546c67 and version==2 and length==len(glb)
chunklen,chunktype=struct.unpack_from('<II',glb,12);g=json.loads(glb[20:20+chunklen]);assert len(g['meshes'])>1000
assert (T/paths[0]).read_bytes().startswith(b'BLENDER')
report={'version':'v5','commit':a.commit,'transport':'independent HTTPS clone and targeted Git LFS pull','binary_files_verified':len(records),'all_binary_hashes_match':True,'master_data_equal':True,'glb_mesh_count':len(g['meshes']),'blender_header_valid':True,'files':records,'scope':'Backup integrity only; scene proposal still requires user review.'}
if a.runtime_checked:
 report['restored_blender_open_check']=json.loads((T/'校验/v5_保存模型回读.json').read_text(encoding='utf8'))
 report['restored_browser_check']=json.loads((T/'校验/v5_browser.json').read_text(encoding='utf8'))
(R/'制作记录/远端恢复校验_v5.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({k:v for k,v in report.items() if k!='files'}))
