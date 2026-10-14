const fs=require('fs'),path=require('path');
const base=path.resolve(__dirname,'..');const libs=(process.env.HOME_ASSETS_NODE_MODULES || '');
const {chromium}=require(libs+'playwright');const sharp=require(libs+'sharp');
(async()=>{
 await sharp(path.join(base,'图纸/两层同向平面图.svg'),{density:170}).png().toFile(path.join(base,'图纸/两层同向平面图.png'));
 const browser=await chromium.launch({executablePath:process.env.HOME_ASSETS_BROWSER || undefined,headless:true,args:['--allow-file-access-from-files','--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1600,height:1000},deviceScaleFactor:1});const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto((process.env.HOME_ASSETS_BASE_URL || 'http://127.0.0.1:8766')+'/模型检查.html');await page.waitForFunction(()=>window.review?.ready);await page.waitForTimeout(1200);
 const results=[];
 for(const id of ['AX1','AX2','AXS','C01','C02','C03','EXT']){
  await page.evaluate(id=>review.setCamera(id),id);await page.waitForTimeout(450);await page.screenshot({path:path.join(base,'校验','浏览器_'+id+'.png')});
  results.push(await page.evaluate(()=>({camera:document.querySelector('#caption').textContent,geometryObjects:review.D.objects.length,canvas:[review.renderer.domElement.width,review.renderer.domElement.height],webgl:review.renderer.getContext().getParameter(review.renderer.getContext().VERSION)})));
 }
 for(const reverse of [false,true]){await page.evaluate(r=>{review.startWalk(r);review.pause();},reverse);for(const t of [0,.25,.5,.75,1])await page.evaluate(([t,r])=>review.showWalk(t,r),[t,reverse]);}
 await page.goto(require('url').pathToFileURL(path.join(base,'打开检查模型.html')).href);await page.waitForFunction(()=>window.review?.ready);await page.evaluate(()=>review.setCamera('AXS'));await page.waitForTimeout(600);await page.screenshot({path:path.join(base,'校验/离线模型检查.png')});
 const offline=await page.evaluate(()=>({ready:review.ready,objects:review.D.objects.length,protocol:location.protocol}));
 await page.goto((process.env.HOME_ASSETS_BASE_URL || 'http://127.0.0.1:8766')+'/验收说明.html');await page.evaluate(async()=>{for(const i of document.images)i.loading='eager';await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));});await page.waitForTimeout(300);const resources=await page.evaluate(()=>({images:[...document.images].map(i=>({src:i.getAttribute('src'),ok:i.complete&&i.naturalWidth>0})),videos:[...document.querySelectorAll('video')].map(v=>({src:v.getAttribute('src'),ready:v.readyState,width:v.videoWidth,height:v.videoHeight,duration:Number.isFinite(v.duration)?v.duration:'stream_metadata'}))}));
 fs.writeFileSync(path.join(base,'校验/browser_check.json'),JSON.stringify({errors,results,offline,resources,walkControls:'forward/reverse and scrub executed'},null,2));
 await browser.close();console.log(JSON.stringify({errors,views:results.length,offline,videos:resources.videos,brokenImages:resources.images.filter(i=>!i.ok)}));
})();
