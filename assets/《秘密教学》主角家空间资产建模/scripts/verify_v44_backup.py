"""Verify fresh remote restore of v4.4 files; run model and viewer checks first."""
import json,hashlib,subprocess,argparse
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R.parents[1]
p=argparse.ArgumentParser();p.add_argument('--clone',required=True);a=p.parse_args();clone=Path(a.clone).resolve();cr=clone/R.relative_to(repo)
def git(*args):return subprocess.check_output(['git','-C',str(clone),*args],encoding='utf8').strip()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=['模型/秘密教学_主角家_v4.4.blend','模型/秘密教学_空间结构_v4.4.glb','图纸/两层同向平面图_v4.4.png']
checks=[]
for rel in paths:
    full=R.relative_to(repo)/rel;pointer=git('show','HEAD:'+full.as_posix());oid=next(l.split(':',1)[1] for l in pointer.splitlines() if l.startswith('oid sha256:'))
    cache=clone/'.git/lfs/objects'/oid[:2]/oid[2:4]/oid
    assert cache.is_file() and sha(cache)==oid,(rel,'remote downloaded LFS object mismatch')
    assert sha(R/rel)==oid,(rel,'local asset differs from remote')
    checks.append({'file':rel,'sha256':oid,'bytes':cache.stat().st_size,'remote_download_verified':True,'checkout_identical':sha(cr/rel)==oid})
model=json.loads((cr/'校验/模型回读_v4.4.json').read_text(encoding='utf8'));viewer=json.loads((cr/'校验/portable_preview.json').read_text(encoding='utf8'))
assert not model['issues'] and viewer['pass'] and all(i['packed'] for i in model['image_dependencies'])
report={'date':'2026-10-14','remote':git('remote','get-url','origin'),'verified_commit':git('rev-parse','HEAD'),'branch':git('branch','--show-current'),'fresh_clone':True,'v44_files':checks,'saved_model_open_and_structure_check':True,'structural_objects_checked':model['checked_structural_objects'],'all_used_textures_packed':True,'offline_preview_pass':True,'scope':'仅v4.4新增模型、结构GLB及图纸PNG远端恢复；正式场景图不在仓库内。原始依赖的全量恢复检查见旧记录。','candidate_is_final':False}
(R/'制作记录/远端恢复校验_v4.4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(report,ensure_ascii=True))
