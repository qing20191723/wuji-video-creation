"""Camera projection overlays for inspection only; never scene artwork."""
import json,html
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=json.loads((R/'校验/H203_文字与门窗投影.json').read_text(encoding='utf8'))
out=R/'预览/v4.4'
for typ in ['门窗轮廓核对','文字位置核对']:
    s=['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1920" height="1080" viewBox="0 0 1920 1080"><image href="H203_模型底图.png" width="1920" height="1080"/>']
    for key,v in P.items():
        if typ=='门窗轮廓核对' and not (key.endswith('_leaf') or key.startswith('OPENING_')):continue
        if typ=='文字位置核对' and not (key.startswith('TEXT_') or key=='BR_HALL_ART'):continue
        x,y,xx,yy=v['pixel_box'];name=v.get('exact_text') or key
        s.append(f'<rect x="{x}" y="{y}" width="{xx-x}" height="{yy-y}" fill="none" stroke="#e05824" stroke-width="3"/>')
        if v.get('pixel_corners'):s.append('<polygon points="'+' '.join(f'{a},{b}' for a,b in v['pixel_corners'])+'" fill="none" stroke="#1e71af" stroke-width="3"/>')
        s.append(f'<text x="{x}" y="{max(25,y-12)}" font-family="Microsoft YaHei" font-size="23" fill="#ad3515" stroke="white" stroke-width=".5">{html.escape(name)}</text>')
    s.append('<rect x="0" y="1020" width="1920" height="60" fill="white"/><text x="25" y="1060" font-family="Microsoft YaHei" font-size="26">检查副本 · 包围框来自同一模型摄影机投影（不是可见性或像素轮廓分割）；非正式场景</text></svg>')
    (out/f'H203_{typ}.svg').write_text('\n'.join(s),encoding='utf8')
