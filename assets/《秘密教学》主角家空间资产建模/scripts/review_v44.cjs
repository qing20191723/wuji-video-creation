const fs=require('fs'),path=require('path'),{pathToFileURL}=require('url');
const {chromium}=require(process.env.HOME_ASSETS_NODE_MODULES?path.join(process.env.HOME_ASSETS_NODE_MODULES,'playwright'):'playwright');
const R=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.HOME_ASSETS_BROWSER||undefined,headless:true,args:['--allow-file-access-from-files','--enable-webgl','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
 const page=await browser.newPage({viewport:{width:1700,height:1000}});let errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(path.join(R,'打开检查模型.html')).href);await page.waitForFunction(()=>window.review?.ready);
 const full=await page.evaluate(()=>{review.setCamera('AX2');return review.scene.children.flatMap(g=>g.children).filter(o=>o.userData.group==='F2_walls'&&o.visible).every(o=>o.scale.z===1)});
 await page.check('#cutWalls');const cut=await page.evaluate(()=>review.scene.children.flatMap(g=>g.children).some(o=>o.userData.group==='F2_walls'&&o.visible&&o.scale.z<1));
 await page.evaluate(()=>review.setCamera('H203'));
 const real=await page.evaluate(()=>({uncut:review.scene.children.flatMap(g=>g.children).filter(o=>o.userData.group==='F2_walls'&&o.visible).every(o=>o.scale.z===1),caption:document.querySelector('#caption').textContent,fov:review.camera.fov}));
 await page.screenshot({path:path.join(R,'预览/v4.4/离线检查器_H203.png')});
 for(const rev of [false,true]){await page.evaluate(r=>{review.startWalk(r);review.pause();review.showWalk(.5,r)},rev)}
 const report={default_full_height:full,explicit_cutaway:cut,real_camera_ignores_cutaway:real.uncut,real_camera:real,errors,pass:full&&cut&&real.uncut&&!errors.length};
 fs.writeFileSync(path.join(R,'校验/离线预览_v4.4.json'),JSON.stringify(report,null,2));
 // SVG diagnostics and plan are rendered as technical drawings, not photo edits.
 for(const [src,dst,w,h] of [['预览/v4.4/H203_门窗轮廓核对.svg','预览/v4.4/H203_门窗轮廓核对.png',1920,1080],['预览/v4.4/H203_文字位置核对.svg','预览/v4.4/H203_文字位置核对.png',1920,1080],['图纸/两层同向平面图_v4.4.svg','图纸/两层同向平面图_v4.4.png',1800,1260]]){await page.setViewportSize({width:w,height:h});await page.goto(pathToFileURL(path.join(R,src)).href);await page.screenshot({path:path.join(R,dst)});}
 await browser.close();console.log(JSON.stringify(report));if(!report.pass)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1});
