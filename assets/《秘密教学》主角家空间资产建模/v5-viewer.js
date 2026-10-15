import * as THREE from 'three';
import {OrbitControls} from './vendor/OrbitControls.js';
const D=await(await fetch('./模型/空间校准主数据_v5.json')).json();
const scene=new THREE.Scene();scene.background=new THREE.Color('#e8eceb');
const renderer=new THREE.WebGLRenderer({antialias:true});renderer.setPixelRatio(Math.min(devicePixelRatio,2));document.querySelector('#stage').appendChild(renderer.domElement);
const camera=new THREE.PerspectiveCamera(48,1,.02,300);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xffffff,0x8b948a,2.1));const sun=new THREE.DirectionalLight(0xffffff,2.3);sun.position.set(8,-5,16);scene.add(sun);
const objects=[];let current='HOME',currentLens=40,currentLevel='all';const mats=new Map();
for(const d of D.objects){
 const b=d.box,dim=[b[3]-b[0],b[4]-b[1],b[5]-b[2]],center=new THREE.Vector3((b[0]+b[3])/2,(b[1]+b[4])/2,(b[2]+b[5])/2);let geo;
 if(d.kind==='mesh'){
  geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.Float32BufferAttribute(d.vertices.flat(),3));const indices=[];for(const f of d.faces)for(let i=1;i<f.length-1;i++)indices.push(f[0],f[i],f[i+1]);geo.setIndex(indices);geo.computeVertexNormals();center.set(0,0,0);
 }else if(d.kind==='bar'){
  const a=new THREE.Vector3(...d.a),v=new THREE.Vector3(...d.b).sub(a);geo=new THREE.CylinderGeometry(d.radius,d.radius,v.length(),12);center.copy(a).addScaledVector(v,.5);
 }else if(d.kind==='cylinder'){geo=new THREE.CylinderGeometry(d.radius,d.radius,dim[2],48);geo.rotateX(Math.PI/2);}
 else if(d.kind==='ellipsoid'){geo=new THREE.SphereGeometry(1,20,12);geo.scale(dim[0]/2,dim[1]/2,dim[2]/2);}
 else geo=new THREE.BoxGeometry(...dim);
 const glass=d.role==='glass'||d.role==='facade_glass';const key=d.color+glass;
 if(!mats.has(key))mats.set(key,new THREE.MeshStandardMaterial({color:d.color,roughness:.8,transparent:glass,opacity:glass?.2:1,depthWrite:!glass,side:THREE.DoubleSide}));
 const o=new THREE.Mesh(geo,mats.get(key));o.position.copy(center);if(d.kind==='bar')o.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0),new THREE.Vector3(...d.b).sub(new THREE.Vector3(...d.a)).normalize());o.userData=d;scene.add(o);objects.push(o);
}
const modsel=document.querySelector('#module'),camsel=document.querySelector('#camera');
for(const m of D.modules)modsel.add(new Option(m.name,m.id));
function visibility(){for(const o of objects){const d=o.userData;const shared=d.role==='stair'||d.id==='HOME_stair_separating_support';o.visible=d.module===current&&(d.role!=='ceiling'||document.querySelector('#ceiling').checked);if(current==='HOME'&&currentLevel==='F1'&&((d.level===2&&!shared)||d.zone==='site'))o.visible=false;if(current==='HOME'&&currentLevel==='F2'&&d.level!==2&&!shared)o.visible=false;}}
function setCamera(id){const c=D.cameras.find(x=>x.id===id);if(!c)return;current=c.module;currentLevel=c.level_mode||'all';document.querySelector('#level').value=currentLevel==='stairs'?'all':currentLevel;modsel.value=current;camera.position.set(...c.pos);currentLens=c.lens;camera.fov=2*Math.atan(36/(2*c.lens*camera.aspect))*180/Math.PI;camera.updateProjectionMatrix();controls.target.set(...c.target);document.querySelector('#ceiling').checked=!c.cutaway;visibility();camsel.value=id;document.querySelector('#viewtitle').textContent=c.name+' · '+(c.cutaway?'去顶检查，墙高不变':'真实高度机位');controls.update();}
function setModule(id){current=id;const m=D.modules.find(x=>x.id===id);camsel.innerHTML='';for(const c of D.cameras.filter(x=>x.module===id))camsel.add(new Option(c.name,c.id));document.querySelector('#description').textContent=m.note;document.querySelector('#refs').textContent='依据：'+(m.references.join('、')||'各独立房间模块 + 用户确认的采光院方向');document.querySelector('#checks').innerHTML=D.checks.filter(x=>x.module===id).map(x=>`<li><span>${x.name}</span><b>${x.actual_m.toFixed(2)} m</b></li>`).join('');document.querySelector('#measures').textContent=id==='SITE'?'早期体量研究：26 × 34 m；仅供对照':id==='HOME'?'采光院拼接提案 · 场地 26 × 42 m · 层高 3.3 m':`${m.width} × ${m.depth} m 局部范围 · 墙高 ${m.height} m`;const c=D.cameras.find(x=>x.id==='HOME_floor2'&&id==='HOME')||D.cameras.find(x=>x.module===id&&x.cutaway)||D.cameras.find(x=>x.module===id);setCamera(c.id);document.querySelector('#object').textContent='点击模型可查看对象编号与用途。';}
modsel.onchange=()=>setModule(modsel.value);camsel.onchange=()=>setCamera(camsel.value);document.querySelector('#ceiling').onchange=visibility;
document.querySelector('#level').onchange=e=>{currentLevel=e.target.value;visibility();};
document.querySelector('#reset').onclick=()=>setModule(current);
const ray=new THREE.Raycaster();renderer.domElement.addEventListener('click',e=>{const b=renderer.domElement.getBoundingClientRect();ray.setFromCamera(new THREE.Vector2((e.clientX-b.left)/b.width*2-1,-(e.clientY-b.top)/b.height*2+1),camera);const hit=ray.intersectObjects(objects.filter(x=>x.visible))[0];if(hit){const d=hit.object.userData;document.querySelector('#object').textContent=`${d.id}\n${d.label} · ${d.role}\n${d.box.slice(3).map((v,i)=>(v-d.box[i]).toFixed(2)).join(' × ')} m${d.note?'\n'+d.note:''}`;}});
function resize(){const r=document.querySelector('#stage').getBoundingClientRect();renderer.setSize(r.width,r.height);camera.aspect=r.width/r.height;camera.fov=2*Math.atan(36/(2*currentLens*camera.aspect))*180/Math.PI;camera.updateProjectionMatrix();}window.addEventListener('resize',resize);resize();setModule('HOME');renderer.setAnimationLoop(()=>{controls.update();renderer.render(scene,camera);});window.v5={ready:true,D,scene,camera,controls,setModule,setCamera,renderer,objects};
