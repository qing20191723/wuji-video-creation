"""Remove obsolete tool transport hints; retain creative prompts and asset provenance."""
from pathlib import Path, PureWindowsPath
import json
R=Path(__file__).resolve().parents[1]
def clean(v):
    if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k!='output_hint'}
    if isinstance(v,list):return [clean(x) for x in v]
    if isinstance(v,str) and len(v)>2 and v[1]==':' and v[2] in '/\\':return '本地历史来源/'+PureWindowsPath(v).name
    return v
for p in (R/'制作记录').glob('*.json'):
    p.write_text(json.dumps(clean(json.loads(p.read_text(encoding='utf8'))),ensure_ascii=False,indent=2),encoding='utf8')
