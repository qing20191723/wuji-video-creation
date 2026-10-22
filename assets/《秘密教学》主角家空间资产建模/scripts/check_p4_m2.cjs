const fs=require('fs'),path=require('path'),crypto=require('crypto');
const {pathToFileURL}=require('url');
const {chromium}=require(path.join(process.env.CODEX_NODE_MODULES||'node_modules','playwright'));
const root=path.resolve(__dirname,'..','全屋模型_P4-M2_20261022');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const page=await browser.newPage({viewport:{width:1800,height:1240},deviceScaleFactor:2});
 for(const name of fs.readdirSync(path.join(root,'图纸')).filter(n=>n.endsWith('.svg'))){
  await page.goto(pathToFileURL(path.join(root,'图纸',name)).href);await page.evaluate(()=>document.fonts.ready);
  await page.locator('svg').screenshot({path:path.join(root,'图纸',name.replace('.svg','.png'))});
 }
 await page.setViewportSize({width:1440,height:1000});const errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto(pathToFileURL(path.join(root,'统一查看页.html')).href);
 await page.evaluate(()=>{for(const i of document.images)i.loading='eager'});
 await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
 const state=await page.evaluate(()=>({images:[...document.images].map(i=>({src:i.getAttribute('src'),width:i.naturalWidth,height:i.naturalHeight})),links:[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href')),overflow:document.documentElement.scrollWidth>innerWidth}));
 await page.locator('#flip').click();const flipped=await page.locator('main img').first().evaluate(i=>getComputedStyle(i).transform==='matrix(-1, 0, 0, 1, 0, 0)');
 await page.locator('#flip').click();await page.setViewportSize({width:390,height:844});const mobileOverflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
 const missing=state.links.filter(h=>!h.startsWith('#')&&!fs.existsSync(path.join(root,h)));
 await browser.close();
 const report={images:state.images,missing,overflow:state.overflow,mobileOverflow,errors,horizontalFlipToggle:flipped};
 fs.writeFileSync(path.join(root,'检查','查看页检查.json'),JSON.stringify(report,null,2));
 if(missing.length||state.overflow||mobileOverflow||errors.length||!flipped||state.images.length!==20)throw Error('M2 delivery page check failed');
 const files=[];function walk(p){for(const n of fs.readdirSync(p)){const q=path.join(p,n);if(fs.statSync(q).isDirectory())walk(q);else if(n!=='交付文件校验.json')files.push({file:path.relative(root,q).replaceAll('\\','/'),bytes:fs.statSync(q).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(q)).digest('hex')});}}walk(root);
 fs.writeFileSync(path.join(root,'检查','交付文件校验.json'),JSON.stringify({revision:'P4-M2',files},null,2));
 console.log(JSON.stringify({images:state.images.length,missing,errors,files:files.length}));
})().catch(e=>{console.error(e);process.exit(1)});
