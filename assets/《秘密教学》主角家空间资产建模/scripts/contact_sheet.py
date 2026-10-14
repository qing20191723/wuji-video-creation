from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
items=json.loads((R/'制作记录/直接渲染首批.json').read_text(encoding='utf8'))
for page,start in enumerate(range(0,len(items),8)):
    out=Image.new('RGB',(1600,4*475),'#e7e9eb');draw=ImageDraw.Draw(out)
    for k,it in enumerate(items[start:start+8]):
        im=Image.open(R/'预览/直接渲染'/it['file']).convert('RGB');im.thumbnail((800,450));x=(k%2)*800;y=(k//2)*475
        out.paste(im,(x,y));draw.text((x+10,y+452),f'{start+k+1:02d} {it["time"]} {it["camera"].split("_")[0]}',fill='#151515')
    out.save(R/'预览'/f'contact_{page+1}.jpg',quality=90)
print('sheets',page+1)
