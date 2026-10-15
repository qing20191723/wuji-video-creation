"""Copy only indexed, actually used references; verify hashes before copying."""
import argparse,json,hashlib,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('source');a=p.parse_args();S=Path(a.source)
D=json.loads((R/'模型/空间校准主数据_v5.json').read_text(encoding='utf8'));idx=json.loads((R/'制作记录/V3参考索引.json').read_text(encoding='utf8'))['files'];needed={r for m in D['modules'] for r in m['references']}
needed.update(['V3_026','V3_042','V3_043','V3_040','V3_041','V3_061','V3_010','V3_065','V3_057']);out=R/'参照/V3';out.mkdir(parents=True,exist_ok=True);records=[]
for r in idx:
 if r['id'] not in needed:continue
 src=S/r['relative_path'];assert hashlib.sha256(src.read_bytes()).hexdigest()==r['sha256'],r['id'];dst=out/(r['id']+src.suffix);shutil.copyfile(src,dst);records.append({**r,'backup_path':dst.relative_to(R).as_posix(),'bytes':dst.stat().st_size})
(R/'制作记录/V5必要参考备份清单.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps({'count':len(records),'bytes':sum(x['bytes'] for x in records)}))
