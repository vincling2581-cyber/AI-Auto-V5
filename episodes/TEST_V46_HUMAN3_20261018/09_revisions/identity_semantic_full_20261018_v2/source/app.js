'use strict';
const escapeXML=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const imageElement=document.getElementById('illustration');
const graphics=document.getElementById('graphics');
const overlay=document.getElementById('overlay');
const textCanvas=document.createElement('canvas').getContext('2d');
let scenes=[],subtitles=[],images={},activeImage=null,config={};
function txt(x,y,text,size=44,color='#24362b',anchor='start',weight=600){return `<text x="${x}" y="${y}" fill="${color}" font-size="${size}" font-weight="${weight}" text-anchor="${anchor}">${escapeXML(text)}</text>`;}
function illustrationOverlay(scene){
  const o=config.opening;
  if(scene.start_frame<119){
    return `<defs><linearGradient id="hook_wash" x1="0" x2="1"><stop offset="0" stop-color="#fffaf0" stop-opacity=".86"/><stop offset=".55" stop-color="#fffaf0" stop-opacity=".65"/><stop offset="1" stop-color="#fffaf0" stop-opacity="0"/></linearGradient></defs><rect x="0" y="110" width="880" height="330" fill="url(#hook_wash)"/><g data-opening-hook="true">${o.lines.map(line=>txt(o.x,line.y,line.text,line.size,'#173b2e',o.anchor,700)).join('')}</g>`;
  }
  if(scene.asset==='open_study'){
    return `<g data-framework-label="true"><rect x="${o.study_x-24}" y="${o.study_y-66}" width="405" height="136" rx="22" fill="#fffaf0" fill-opacity=".93"/>${txt(o.study_x,o.study_y,'HUMAN 3.0',56,'#24443c','start',700)}${txt(o.study_x,o.study_y+48,'Dan Koe',30,'#52685f','start',500)}</g>`;
  }
  return '';
}
function subtitleOverlay(time){
  const s=subtitles.find(x=>time>=x.start&&time<x.end);
  if(!s)return '';
  const c=config.subtitle;
  textCanvas.font=`700 ${c.font_size}px "Microsoft YaHei"`;
  const w=Math.min(1700,Math.ceil(textCanvas.measureText(s.text).width)+76);
  return `<g data-subtitle-id="${s.id}"><rect data-subtitle-plate="true" x="${(1920-w)/2}" y="${c.plate_y}" width="${w}" height="${c.plate_height}" rx="22" fill="#10231d" fill-opacity=".88"/>${txt(c.x,c.baseline_y,s.text,c.font_size,'#fffdf4',c.anchor,700)}</g>`;
}
window.renderFrame=frame=>{
  if(!Number.isInteger(frame)||frame<0||frame>=config.total_frames)throw new Error('Frame outside timeline: '+frame);
  const time=frame/config.fps;
  const scene=scenes.find(s=>frame>=s.start_frame&&frame<s.end_frame_exclusive);
  if(!scene)throw new Error('No scene at frame '+frame);
  const local=(frame-scene.start_frame)/config.fps;
  if(scene.type==='illustration'){
    if(activeImage!==scene.asset){imageElement.src=images[scene.asset].src;activeImage=scene.asset;}
    imageElement.style.display='block';
    graphics.innerHTML=illustrationOverlay(scene);
  }else{
    imageElement.style.display='none';
    graphics.innerHTML=window.renderCard(scene.asset,local,time);
  }
  const ink=scene.asset==='prompt'?'#f5f2e9':'#24443c';
  const headerBg=scene.type==='illustration'?'<rect x="64" y="35" width="410" height="62" rx="31" fill="#fffaf0" fill-opacity=".85"/>':'';
  overlay.innerHTML=headerBg+txt(92,77,'ECHO / HUMAN 3.0',29,ink,'start',700)+subtitleOverlay(time);
  document.getElementById('stage').dataset.scene=scene.id;
  return {frame,time,scene:scene.id,asset:scene.asset,type:scene.type,local_seconds:local,
    subtitle:subtitles.find(x=>time>=x.start&&time<x.end)?.id??null};
};
window.ready=(async()=>{
  const read=path=>fetch(path).then(r=>{if(!r.ok)throw new Error('Missing '+path);return r.json();});
  [scenes,subtitles,window.EFFECTIVE_DEFAULTS,config]=await Promise.all([
    read('timeline.json'),read('subtitles.json'),read('effective_defaults.json'),read('config.json')]);
  await document.fonts.load('700 44px "Microsoft YaHei"');
  await document.fonts.ready;
  await Promise.all(scenes.filter(x=>x.type==='illustration').map(scene=>new Promise((resolve,reject)=>{
    const img=new Image();img.onload=()=>{images[scene.asset]=img;resolve();};
    img.onerror=()=>reject(new Error('Missing image '+scene.asset));img.src='../'+scene.asset_path;
  })));
  return window.renderFrame(0);
})();
