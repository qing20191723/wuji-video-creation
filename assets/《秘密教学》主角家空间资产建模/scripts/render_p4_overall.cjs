const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..','整体平面_P4_20261022');
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const files=fs.readdirSync(path.join(root,'图纸')).filter(f=>f.endsWith('.svg')).sort(),checks=[];
 for(const file of files){
  const page=await browser.newPage({viewport:{width:1800,height:1240},deviceScaleFactor:2});
  await page.goto(pathToFileURL(path.join(root,'图纸',file)).href);await page.evaluate(()=>document.fonts.ready);
  const outside=await page.evaluate(()=>[...document.querySelectorAll('text')].filter(t=>{const r=t.getBoundingClientRect();return r.left<0||r.top<0||r.right>innerWidth+1||r.bottom>innerHeight+1}).map(t=>t.textContent));
  await page.screenshot({path:path.join(root,'图纸',file.replace('.svg','.png'))});checks.push({file,outside});await page.close();
 }
 const data=JSON.parse(fs.readFileSync(path.join(root,'数据','整体空间方案_P4.json'),'utf8'));
 const cards=files.map(f=>`<article id="${esc(f)}"><h2>${esc(f.replace('.svg','').replaceAll('_',' / '))}</h2><a href="图纸/${esc(f.replace('.svg','.png'))}" target="_blank"><img src="图纸/${esc(f.replace('.svg','.png'))}" alt="${esc(f)}"></a><p><a href="图纸/${esc(f.replace('.svg','.png'))}" download>高清 PNG</a> · <a href="图纸/${esc(f)}" download>可编辑 SVG</a></p></article>`).join('');
 const nav=files.map(f=>`<a href="#${esc(f)}">${esc(f.replace('.svg','').replaceAll('_',' '))}</a>`).join('');
 const doc=`<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>秘密教学 P4 整体平面</title><style>*{box-sizing:border-box}body{margin:0;background:#f5f4ef;color:#253e40;font:16px/1.65 "Microsoft YaHei",sans-serif}main,header{max-width:1450px;margin:auto;padding:26px}h1{font-size:32px}nav{display:flex;gap:14px;flex-wrap:wrap}a{color:#2b7668}.intro{background:#e6eee3;padding:20px;border-left:4px solid #4e8069}article{background:white;border:1px solid #d6ded4;border-radius:10px;padding:18px;margin:28px 0}article img{width:100%;height:auto}h2{font-size:22px;margin:0 0 15px}.metrics{display:flex;gap:24px;flex-wrap:wrap;font-size:20px;font-weight:600}li{margin:6px 0}</style><header><p>2026-10-22 · P4 新外部设计稿</p><h1>从确认的室内，向右延展公共庭院</h1><div class="intro">二楼内部以 P3-R2 为确认基线，一楼沿用。原房间、家具、墙体和楼梯坐标保持。公共庭院从上平台按箭头向右扩展；庭院与大姐私人阳台分开。新增外部待审阅，尚未回写全屋模型。</div><p class="metrics"><span>公共庭院 36.34㎡</span><span>七张整体图纸</span><span>双车位 + 分离人行入口</span></p><nav>${nav}</nav></header><main>${cards}<article><h2>新增外部的确认边界</h2><ul>${data.unresolved.map(t=>'<li>'+esc(t)+'</li>').join('')}</ul><p><a href="设计说明.md">完整设计说明</a> · <a href="数据/整体空间方案_P4.json">完整空间数据</a> · <a href="数据/新增外部尺寸.csv">新增尺寸表</a> · <a href="检查/范围与通行检查.json">范围检查</a></p></article></main></html>`;
 fs.writeFileSync(path.join(root,'统一查看页.html'),doc);
 const page=await browser.newPage({viewport:{width:1440,height:1000}});await page.goto(pathToFileURL(path.join(root,'统一查看页.html')).href);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
 const broken=await page.evaluate(()=>[...document.images].filter(i=>!i.naturalWidth).map(i=>i.src));await browser.close();
 fs.writeFileSync(path.join(root,'检查','图纸输出检查.json'),JSON.stringify({checks,broken},null,2));
 const manifest=[];function scan(p){for(const name of fs.readdirSync(p)){const q=path.join(p,name);if(fs.statSync(q).isDirectory())scan(q);else if(name!=='交付文件校验.json')manifest.push({file:path.relative(root,q).replaceAll('\\','/'),bytes:fs.statSync(q).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(q)).digest('hex')});}}scan(root);
 fs.writeFileSync(path.join(root,'检查','交付文件校验.json'),JSON.stringify({revision:'P4-20261022',files:manifest},null,2));
 console.log(JSON.stringify({sheets:files.length,checks,broken,files:manifest.length}));if(broken.length||checks.some(c=>c.outside.length))process.exit(1);
})().catch(e=>{console.error(e);process.exit(1)});
