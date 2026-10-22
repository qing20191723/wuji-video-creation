const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const deps='node_modules';
const {chromium}=require(path.join(deps,'playwright'));
const root=path.resolve(__dirname,'..','完整平面与品牌_P3_R2_20261022');
const tex=path.join(root,'品牌贴图');
const src=fs.readFileSync(path.resolve(__dirname,'..','品牌','黄瓜短剧_无域名_透明底.png'));
const uri='data:image/png;base64,'+src.toString('base64');
const h=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;');
function svg(w,H,body){return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${H}" viewBox="0 0 ${w} ${H}">${body}</svg>`}
const icon=`<svg x="65" y="65" width="370" height="430" viewBox="205 160 360 415"><image width="2172" height="724" href="${uri}"/></svg>`;
// Exact source artwork plus typeset domain. Mirror transforms the entire composition.
const plate=`<rect x="12" y="12" width="1576" height="736" rx="116" fill="#080a08" stroke="#e7c65e" stroke-width="16"/><image x="30" y="12" width="1540" height="514" href="${uri}"/><path d="M300 535H1300" stroke="#92783e" stroke-width="2"/><text x="800" y="664" text-anchor="middle" font-family="Arial,sans-serif" font-size="116" font-weight="600" letter-spacing="5" fill="#f3df9c">hgdju.com</text>`;
if(!process.argv.includes('--plans-only')){
for(const variant of ['normal','mirror']){
 const body=variant==='normal'?plate:`<g transform="translate(1600 0) scale(-1 1)">${plate}</g>`;
 fs.writeFileSync(path.join(tex,'HG_FULL_'+variant+'.svg'),svg(1600,760,body));
}
fs.writeFileSync(path.join(tex,'HG_ICON.svg'),svg(500,560,icon));
const names={NAME_B1:'薇亚の窝',NAME_B2:'子豪の窝',NAME_B3:'舒亚の窝',NAME_BW:'公共浴室'};
for(const [id,text]of Object.entries(names))fs.writeFileSync(path.join(tex,id+'.svg'),svg(1200,520,`<rect x="12" y="12" width="1176" height="496" rx="80" fill="#eee9dd" stroke="#423c31" stroke-width="12"/><text x="600" y="330" text-anchor="middle" font-family="Microsoft YaHei" font-size="188" font-weight="700" fill="#161b17">${h(text)}</text>`));
fs.writeFileSync(path.join(tex,'品牌文字源.json'),JSON.stringify({brand:'黄瓜短剧',domain:'hgdju.com',names,mirror:'整组水平翻转；不是倒排字符',source_sha256:crypto.createHash('sha256').update(src).digest('hex')},null,2));
}
(async()=>{
 const browser=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const checks=[];
 for(const dir of (process.argv.includes('--plans-only')?['图纸']:['图纸','品牌贴图']))for(const file of fs.readdirSync(path.join(root,dir)).filter(f=>f.endsWith('.svg'))){
  const source=fs.readFileSync(path.join(root,dir,file),'utf8');const [,w,H]=source.match(/width="(\d+)" height="(\d+)"/);
  const page=await browser.newPage({viewport:{width:+w,height:+H},deviceScaleFactor:dir==='图纸'?2:1});
  await page.goto(pathToFileURL(path.join(root,dir,file)).href);await page.evaluate(()=>document.fonts.ready);await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode().catch(()=>null))));
  const outside=await page.evaluate(()=>[...document.querySelectorAll('text')].filter(t=>{let r=t.getBoundingClientRect();return r.left<0||r.top<0||r.right>innerWidth+1||r.bottom>innerHeight+1}).map(t=>t.textContent));
  await page.screenshot({path:path.join(root,dir,file.replace('.svg','.png')),omitBackground:dir==='品牌贴图'});
  checks.push({file:dir+'/'+file,width:+w*(dir==='图纸'?2:1),height:+H*(dir==='图纸'?2:1),outside});await page.close();
 }
 await browser.close();fs.writeFileSync(path.join(root,'检查','图纸与贴图输出检查.json'),JSON.stringify(checks,null,2));console.log(JSON.stringify(checks));
})().catch(e=>{console.error(e);process.exit(1)});
