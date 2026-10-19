'use strict';
const escapeXML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const clamp=x=>Math.max(0,Math.min(1,x));
const ease=x=>1-Math.pow(1-clamp(x),3);
const imageElement=document.getElementById('illustration');
const graphics=document.getElementById('graphics');
const overlay=document.getElementById('overlay');
const textCanvas=document.createElement('canvas').getContext('2d');
let scenes=[],subtitles=[],images={},activeImage=null;
function txt(x,y,text,size=44,color='#24362b',anchor='start',weight=600){return `<text x="${x}" y="${y}" fill="${color}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}">${escapeXML(text)}</text>`;}
function paperLabel(x,y,label,width=330){return `<rect x="${x}" y="${y}" width="${width}" height="66" rx="33" fill="#fffaf0" fill-opacity=".95"/>${txt(x+width/2,y+44,label,30,'#24413d','middle',600)}`;}
function illustrationOverlay(scene,t){
  if(scene.asset==='ascent'){
    const points=[[847,661,'L1',0],[1238,377,'L2',.58],[1738,179,'L3',1.15]];
    let s=paperLabel(100,140,'各象限分别定位',340);
    // The terrain is a planning metaphor. No numeric score or personal rank is assigned.
    const route=ease((t-3.25)/1.8);
    s+=`<path d="M847 773 C1040 830 1320 675 1400 630 S1340 510 1440 440 S1710 390 1738 288" fill="none" stroke="#fff8df" stroke-opacity=".85" stroke-width="16" pathLength="1" stroke-dasharray="${route} 1" stroke-linecap="round"/>`;
    s+=`<path d="M847 773 C1040 830 1320 675 1400 630 S1340 510 1440 440 S1710 390 1738 288" fill="none" stroke="#2f6d5e" stroke-width="6" pathLength="1" stroke-dasharray="${route} 1" stroke-linecap="round"/>`;
    for(const [x,y,label,start] of points){const p=ease((t-start)/.45);s+=`<g opacity="${p}">${txt(x,y+10,label,30,'#24483b','middle',700)}</g>`;}
    if(t>3.25)s+=`<g opacity="${ease((t-3.25)/.5)}">${paperLabel(1180,785,'制定下一步行动',420)}</g>`;
    return s;
  }
  if(scene.asset==='conversation_listen')return paperLabel(100,800,t<2.33?'一次问清一个问题':'把隐藏的卡点说具体',420);
  if(scene.asset==='conversation_answer')return paperLabel(100,800,'从真实经历开始回答',420);
  if(scene.asset==='clarity')return paperLabel(100,145,'让下一步变得清楚',390);
  return '';
}
function subtitleOverlay(time){
  const s=subtitles.find(x=>time>=x.start&&time<x.end);
  if(!s)return '';
  textCanvas.font='700 44px "Microsoft YaHei"';
  const w=Math.min(1700,Math.ceil(textCanvas.measureText(s.text).width)+76);
  return `<rect x="${(1920-w)/2}" y="947" width="${w}" height="83" rx="22" fill="#10231d" fill-opacity=".88"/>${txt(960,1004,s.text,44,'#fffdf4','middle',700)}`;
}
window.renderFrame=frame=>{
  if(!Number.isInteger(frame)||frame<0||frame>=1678)throw new Error('Frame outside sample timeline: '+frame);
  const time=frame/30;
  const scene=scenes.find(s=>frame>=s.start_frame&&frame<s.end_frame_exclusive);
  if(!scene)throw new Error('No scene at frame '+frame);
  const local=(frame-scene.start_frame)/30;
  const dark=scene.asset==='prompt';
  if(scene.type==='illustration'){
    if(activeImage!==scene.asset){imageElement.src=images[scene.asset].src;activeImage=scene.asset;}
    imageElement.style.display='block';
    graphics.innerHTML=illustrationOverlay(scene,local);
  }else{
    imageElement.style.display='none';
    graphics.innerHTML=window.renderCard(scene.asset,local,time);
  }
  const ink=dark?'#f5f2e9':'#24443c';
  const headerBg=scene.type==='illustration'?`<rect x="64" y="35" width="410" height="62" rx="31" fill="#fffaf0" fill-opacity=".85"/>`:'';
  overlay.innerHTML=headerBg+txt(92,77,'ECHO / HUMAN 3.0',29,ink,'start',700)+subtitleOverlay(time);
  document.getElementById('stage').dataset.scene=scene.id;
  return {frame,time,scene:scene.id,asset:scene.asset};
};
window.ready=(async()=>{
  const [s,sub,d]=await Promise.all([
    fetch('../03_storyboard/scenes.json').then(r=>{if(!r.ok)throw new Error('Missing scenes');return r.json();}),
    fetch('../02_timing/subtitles.json').then(r=>{if(!r.ok)throw new Error('Missing subtitles');return r.json();}),
    fetch('../00_brief/effective_defaults.json').then(r=>{if(!r.ok)throw new Error('Missing defaults');return r.json();})
  ]);
  scenes=s;subtitles=sub;window.EFFECTIVE_DEFAULTS=d;
  await document.fonts.load('700 44px "Microsoft YaHei"');
  await document.fonts.ready;
  await Promise.all(s.filter(x=>x.type==='illustration').map(scene=>new Promise((resolve,reject)=>{
    const img=new Image();img.onload=()=>{images[scene.asset]=img;resolve();};img.onerror=()=>reject(new Error('Missing image '+scene.asset));img.src='../04_assets/illustrations/'+scene.asset+'.png';
  })));
  return window.renderFrame(0);
})();
