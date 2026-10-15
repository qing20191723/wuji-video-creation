const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..','平面确认');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true});
 const errors=[],results=[];
 for(const name of fs.readdirSync(root).filter(n=>n.endsWith('.svg'))){
  const source=fs.readFileSync(path.join(root,name),'utf8'),size=source.match(/width="(\d+)" height="(\d+)"/);
  const page=await browser.newPage({viewport:{width:+size[1],height:+size[2]},deviceScaleFactor:2});
  page.on('pageerror',e=>errors.push({file:name,message:e.message}));
  await page.goto(pathToFileURL(path.join(root,name)).href);await page.evaluate(()=>document.fonts.ready);
  const outside=await page.evaluate(()=>[...document.querySelectorAll('text')].filter(t=>{const b=t.getBoundingClientRect();return b.left<0||b.top<0||b.right>innerWidth+1||b.bottom>innerHeight+1}).map(t=>t.textContent));
  await page.screenshot({path:path.join(root,name.replace('.svg','.png'))});
  results.push({file:name,width:+size[1]*2,height:+size[2]*2,text_outside_canvas:outside});await page.close();
 }
 const gallery=await browser.newPage();await gallery.goto(pathToFileURL(path.join(root,'打开平面图.html')).href);
 const galleryResults=[];for(const button of await gallery.locator('button[data-sheet]').all()){
   await button.click();await gallery.waitForFunction(()=>{const i=document.querySelector('#drawing');return i.complete&&i.naturalWidth>0});
   galleryResults.push(await gallery.locator('#drawing').getAttribute('src'));
 }
 const broken=await gallery.evaluate(async()=>{const links=[...document.querySelectorAll('a[href]')].map(a=>a.getAttribute('href'));return links;});
 for(const link of broken)if(!fs.existsSync(path.join(root,decodeURI(link))))errors.push('Missing gallery link '+link);
 await browser.close();fs.writeFileSync(path.join(root,'图纸输出检查.json'),JSON.stringify({errors,results,galleryResults},null,2));console.log(JSON.stringify({errors,results,galleryResults},null,2));
 if(errors.length||results.some(r=>r.text_outside_canvas.length))process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
