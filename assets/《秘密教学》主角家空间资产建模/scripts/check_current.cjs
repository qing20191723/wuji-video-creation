const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require('playwright'),sharp=require('sharp');
const R=path.resolve(__dirname,'..');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME_PATH||'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1600,height:1000}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto(pathToFileURL(path.join(R,'打开检查模型.html')).href);await p.waitForFunction(()=>window.review?.ready);
const results=[];for(const id of ['AX1','AX2','AXS','C01','C02','C03','EXT']){await p.evaluate(id=>review.setCamera(id),id);await p.waitForTimeout(150);results.push(id);}
await p.evaluate(()=>review.setCamera('AX2'));await p.screenshot({path:path.join(R,'校验/页面_当前二楼.png')});
const audit=await p.evaluate(()=>({version:review.D.version,objects:review.D.objects.length,bedrooms:review.D.rooms.filter(x=>['R201','R202','R203'].includes(x.id)).map(x=>({name:x.name,box:x.box})),links:[...document.querySelectorAll('a[href]')].map(x=>x.getAttribute('href'))}));
const missing=audit.links.filter(x=>!fs.existsSync(path.join(R,x)));if(missing.length)throw Error('Missing links: '+missing);
const q=await b.newPage({viewport:{width:1800,height:1260},deviceScaleFactor:2});await q.goto(pathToFileURL(path.join(R,'图纸/两层同向平面图.svg')).href);const png=path.join(R,'图纸/两层同向平面图.png');await q.screenshot({path:png});
for(const [name,left] of [['一楼平面图',0],['二楼平面图',1800]])await sharp(png).extract({left,top:190,width:1800,height:2330}).png().toFile(path.join(R,'图纸',name+'.png'));
fs.writeFileSync(path.join(R,'校验/当前入口检查.json'),JSON.stringify({errors,cameras:results,...audit,missing},null,2));await b.close();console.log(JSON.stringify({errors,cameras:results.length,missing,version:audit.version}));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
