const fs=require('fs'),path=require('path'),{chromium}=require('playwright');
const R=path.resolve(__dirname,'..'),O=path.join(R,'白模当前'),base='http://127.0.0.1:8879/白模当前/';
(async()=>{const b=await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe',headless:true,args:['--enable-webgl','--ignore-gpu-blocklist']});const p=await b.newPage({viewport:{width:1600,height:1000}}),errors=[];p.on('pageerror',e=>errors.push(e.message));
await p.goto(base+'查看白模.html?rev=P2.4-M3&cam=F4_DOWN');await p.waitForFunction(()=>window.p23?.ready);if(await p.evaluate(()=>p23.D.revision)!=='P2.4-M3')throw Error('Stale model');
const count=await p.evaluate(()=>p23.D.objects.length);for(const id of ['F4_DOWN','F4_REVERSE','F4_UP','F4_PLAN','EXT_01']){await p.selectOption('#cam',id);await p.waitForTimeout(150);}
await p.selectOption('#cam','F4_REVERSE');await p.screenshot({path:path.join(O,'检查记录/M3浏览器回看.png')});
await p.click('#door');const moved=await p.evaluate(()=>Math.abs(p23.meshes.get('2-B2S_D204_leaf').quaternion.z)>.1);if(!moved)throw Error('Door did not open');
await p.click('#walk');await p.waitForTimeout(600);const walkStart=await p.evaluate(()=>p23.camera.position.toArray());await p.click('#stop');if(Math.abs(walkStart[2]-4.9)>.01)throw Error('Walk start wrong level');
await p.goto(base+'F4建模对照.html?rev=P2.4-M3');await p.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0));
const images=await p.locator('img').count();await p.locator('.markable').first().click({position:{x:100,y:100}});const annotation=await p.locator('#mark').innerText();if(!annotation.includes('M3_F2_PLAN'))throw Error('Annotation failed');
const refs=await p.locator('a[href]').evaluateAll(as=>as.map(a=>a.getAttribute('href'))),missing=refs.filter(x=>!fs.existsSync(path.resolve(O,x.split('?')[0])));if(missing.length)throw Error('Broken links: '+missing);
for(const f of ['M3_一楼建模平面.svg','M3_二楼建模平面.svg']){await p.goto(base+'方位检查/'+f);await p.setViewportSize({width:1800,height:1280});await p.screenshot({path:path.join(O,'检查记录',f.replace('.svg','.png'))});}
const result={revision:'P2.4-M3',passed:!errors.length,objects:count,images,door_switch:moved,walkStart,annotation,missing,errors};fs.writeFileSync(path.join(O,'检查记录/M3浏览器检查.json'),JSON.stringify(result,null,2));await b.close();console.log(JSON.stringify(result));if(errors.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exit(1)});
