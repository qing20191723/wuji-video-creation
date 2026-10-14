"""Fetch narrowly selected CC0 plant models and verify the provider's checksums."""
import hashlib, json, urllib.request, concurrent.futures
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'资源/PolyHaven'
def fetch(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'SecretTeachingAssetBuild/1.0'}),timeout=120) as f:return f.read()
records=[]
for asset in ['potted_plant_01','potted_plant_04']:
    data=json.loads(fetch('https://api.polyhaven.com/files/'+asset))
    b=data['blend']['2k']['blend']; folder=DEST/asset;folder.mkdir(parents=True,exist_ok=True)
    files=[(asset+'_2k.blend',b)]+list(b.get('include',{}).items())
    def download(item):
        name,info=item;p=(folder/name).resolve()
        if not p.is_relative_to(folder.resolve()):raise ValueError(name)
        p.parent.mkdir(parents=True,exist_ok=True)
        if not p.exists() or hashlib.md5(p.read_bytes()).hexdigest()!=info['md5']:
            blob=fetch(info['url'])
            if hashlib.md5(blob).hexdigest()!=info['md5']:raise ValueError('MD5 mismatch '+name)
            p.write_bytes(blob)
        return {'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':info['url'],'bytes':p.stat().st_size}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:downloaded=list(pool.map(download,files))
    records.append({'asset':asset,'license':'CC0','license_url':'https://polyhaven.com/license','source':'https://polyhaven.com/a/'+asset,'files':downloaded})
    print(asset,len(downloaded),'files verified',flush=True)
(DEST/'来源与许可.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf8')
