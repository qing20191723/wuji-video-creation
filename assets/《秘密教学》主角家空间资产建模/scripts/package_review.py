"""Rebuild the offline geometry viewer using bundled local assets only."""
from pathlib import Path
import json,re,base64
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'模型/空间主数据_v4.4.json').read_text(encoding='utf8'))
dataurl=lambda s:'data:text/javascript;base64,'+base64.b64encode(s.encode('utf8')).decode()
core=dataurl((R/'vendor/three.core.js').read_text(encoding='utf8'))
three=(R/'vendor/three.module.js').read_text(encoding='utf8').replace('./three.core.js',core)
imports={'three':dataurl(three),'./vendor/OrbitControls.js':dataurl((R/'vendor/OrbitControls.js').read_text(encoding='utf8'))}
page=(R/'模型检查.html').read_text(encoding='utf8')
page=re.sub(r'<script type="importmap">.*?</script>','<script type="importmap">'+json.dumps({'imports':imports})+'</script>',page,flags=re.S)
js=(R/'viewer.js').read_text(encoding='utf8').replace("await(await fetch('./模型/空间主数据_v4.4.json')).json()",json.dumps(D,ensure_ascii=False))
page=page.replace('<script type="module" src="./viewer.js"></script>','<script type="module">'+js.replace('</script','<\\/script')+'</script>')
(R/'打开检查模型.html').write_text(page,encoding='utf8')
print('Portable accepted-geometry viewer rebuilt.')
