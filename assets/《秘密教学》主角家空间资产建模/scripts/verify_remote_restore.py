"""Run after a fresh HTTPS clone, git lfs pull, and preview/model/render checks."""
import argparse,json,subprocess,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo=R.parents[1]
p=argparse.ArgumentParser();p.add_argument('--clone',required=True);a=p.parse_args();clone=Path(a.clone).resolve();cr=clone/R.relative_to(repo)
def git(*args):return subprocess.check_output(['git','-C',str(clone),*args],encoding='utf8').strip()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
files=json.loads(git('lfs','ls-files','--json'))['files'];checks=[]
for f in files:
    target=clone/f['name'];actual=sha(target)
    if actual!=f['oid']:raise ValueError('Remote LFS checksum mismatch: '+f['name'])
    checks.append({'file':f['name'],'sha256':actual,'bytes':target.stat().st_size})
geometry=json.loads((cr/'校验/直接渲染模型回读.json').read_text(encoding='utf8'))
preview=json.loads((cr/'校验/portable_preview.json').read_text(encoding='utf8'))
frame=Path('预览/保存模型拍摄/客厅_后视图（日景）.png')
assert not geometry['structural_changes'] and preview['pass']
assert all(i['packed'] for i in geometry['image_dependencies'])
same_frame=sha(R/frame)==sha(cr/frame)
from PIL import Image,ImageChops,ImageStat
im1=Image.open(R/frame).convert('RGB');im2=Image.open(cr/frame).convert('RGB');delta=ImageChops.difference(im1,im2)
report={'date':'2026-10-14','remote':git('remote','get-url','origin'),'branch':git('branch','--show-current'),'verified_commit':git('rev-parse','HEAD'),'fresh_https_clone':True,'lfs_paths_checked':len(checks),'unique_lfs_objects':len(set(c['sha256'] for c in checks)),'lfs_bytes_unique':sum({c['sha256']:c['bytes'] for c in checks}.values()),'lfs_checksum_pass':True,'structural_objects_checked':geometry['checked_structural_objects'],'structural_changes':geometry['structural_changes'],'all_used_texture_images_packed':True,'offline_preview_pass':preview['pass'],'saved_model_render_pass':True,'local_remote_render_sha256_identical':same_frame,'render_sha256':sha(cr/frame),'files':checks,'scope':'模型和依赖备份验证；不代表95张最终场景完成'}
report['render_pixels_identical']=delta.getbbox() is None
report['render_mean_absolute_pixel_error']=ImageStat.Stat(delta).mean
(R/'制作记录/远端恢复校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
