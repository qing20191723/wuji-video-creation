// NODE_PATH supplies Playwright; CHROME_PATH can override the local browser.
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');const {pathToFileURL}=require('url');
const R=path.resolve(__dirname,'..');
fs.mkdirSync(path.join(R,'预览/v5'),{recursive:true});
(async()=>{const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--allow-file-access-from-files']});
const page=await browser.newPage({viewport:{width:1600,height:1040}});const errors=[];const requests=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))requests.push(r.url())});
await page.goto(pathToFileURL(path.join(R,'打开V5校准模型.html')).href);await page.waitForFunction(()=>window.v5?.ready);await page.waitForTimeout(1200);
await page.screenshot({path:path.join(R,'预览/v5/交互模型_默认二楼.png')});const modules=await page.evaluate(()=>v5.D.modules.map(x=>x.id));
for(const id of modules){await page.selectOption('#module',id);await page.waitForTimeout(120);if(!await page.evaluate(()=>v5.objects.some(o=>o.visible)))throw Error('empty module '+id);}
await page.selectOption('#module','E');await page.selectOption('#camera','E_side');await page.waitForTimeout(300);await page.screenshot({path:path.join(R,'预览/v5/交互模型_大姐.png')});
await page.selectOption('#module','HOME');await page.selectOption('#camera','HOME_exterior');await page.waitForTimeout(300);await page.screenshot({path:path.join(R,'预览/v5/交互模型_全屋.png')});
const cameraCount=await page.evaluate(()=>v5.D.cameras.length);
await page.setViewportSize({width:2100,height:1330});await page.goto(pathToFileURL(path.join(R,'图纸/全屋两层同向平面_v5.svg')).href);await page.screenshot({path:path.join(R,'图纸/全屋两层同向平面_v5.png')});
const report={portable_file_loaded:true,modules_checked:modules,camera_count:cameraCount,page_errors:errors,external_requests:requests};fs.writeFileSync(path.join(R,'校验/v5_browser.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();if(errors.length||requests.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
