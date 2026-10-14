"""Run existing geometry checks against v4.4 without overwriting v4 results."""
from pathlib import Path
R=Path(__file__).resolve().parents[1]
s=(R/'scripts/check_and_draw.py').read_text(encoding='utf8').replace('空间主数据_v4.json','空间主数据_v4.4.json').replace('几何检查结果.json','几何检查结果_v4.4.json').replace('两层同向平面图.svg','两层同向平面图_v4.4.svg').replace('模型 v4 ·','模型 v4.4 ·')
exec(compile(s,str(R/'scripts/check_and_draw.py'),'exec'),{'__file__':str(R/'scripts/check_and_draw.py'),'__name__':'__main__'})
