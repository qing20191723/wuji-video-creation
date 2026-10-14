// Offline structural viewer smoke test. Preview renders intentionally stay local.
const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require(process.env.HOME_ASSETS_NODE_MODULES ? path.join(process.env.HOME_ASSETS_NODE_MODULES,'playwright') : 'playwright');
const root=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.HOME_ASSETS_BROWSER||undefined,headless:true,args:['--allow-file-access-from-files','--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1500,height:1000}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(root,'打开检查模型.html')).href);
 await page.waitForFunction(()=>window.review?.ready);
 const views=[];
 for(const id of ['AX1','AX2','AXS','C01','C02','C03']){
  await page.evaluate(id=>review.setCamera(id),id);
  views.push(await page.evaluate(()=>({caption:document.querySelector('#caption').textContent,objects:review.D.objects.length})));
 }
 for(const reverse of [false,true]){await page.evaluate(r=>{review.startWalk(r);review.pause();},reverse);for(const t of [0,.25,.5,.75,1])await page.evaluate(([t,r])=>review.showWalk(t,r),[t,reverse]);}
 const report={offline:true,views,errors,walk:'forward and reverse sampled',pass:!errors.length};
 fs.writeFileSync(path.join(root,'校验/portable_preview.json'),JSON.stringify(report,null,2));
 await browser.close();console.log(JSON.stringify(report));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
