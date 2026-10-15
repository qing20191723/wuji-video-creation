"""Read-only V3 inventory and labeled inspection contact sheets."""
import json,hashlib,argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
p=argparse.ArgumentParser();p.add_argument('source');a=p.parse_args();S=Path(a.source);R=Path(__file__).resolve().parents[1]
out=R/'预览/V3参考盘点';out.mkdir(parents=True,exist_ok=True)
files=sorted(f for f in S.rglob('*') if f.suffix.lower() in ['.png','.jpg','.jpeg','.webp']);rows=[];groups={}
for i,f in enumerate(files):
 im=Image.open(f);r={'id':f'V3_{i+1:03}','relative_path':f.relative_to(S).as_posix(),'size':list(im.size),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()};rows.append(r);groups.setdefault(f.parent.relative_to(S).as_posix(),[]).append((f,r))
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',21)
for group,items in groups.items():
 for page in range(0,len(items),4):
  sheet=Image.new('RGB',(1680,1040),'#edf0ed');d=ImageDraw.Draw(sheet)
  for n,(f,r) in enumerate(items[page:page+4]):
   x=n%2*840;y=n//2*520;im=Image.open(f).convert('RGB');im.thumbnail((828,465));sheet.paste(im,(x+6,y+48));d.text((x+8,y+5),r['id']+' '+f.name,font=font,fill='#111111')
  sheet.save(out/(group.replace('/','_')+f'_{page//4+1}.jpg'),quality=92)
(R/'制作记录/V3参考索引.json').write_text(json.dumps({'source_label':'用户指定 场景图V3版','files':rows},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'images':len(rows),'groups':{g:len(v) for g,v in groups.items()},'sheets':[str(f) for f in out.glob('*.jpg')]},ensure_ascii=False))
