import {renderCard,cardState} from './cards.js';

const LOGICAL_W=1920,LOGICAL_H=1080;
const stage=document.getElementById('stage');
const visual=document.getElementById('visual');
const region=document.getElementById('caption-region');
const caption=document.getElementById('caption');
let config,defaults,scenes,subtitles,currentFrame=0,lastState=null;
const illustrationImages=new Map();
let visibleIllustration=null;

async function json(path){const r=await fetch(path);if(!r.ok)throw new Error(`加载失败 ${path}: ${r.status}`);return r.json();}
function fit(){const s=Math.min(innerWidth/LOGICAL_W,innerHeight/LOGICAL_H);stage.style.transform=`scale(${s})`;stage.style.left=`${(innerWidth-LOGICAL_W*s)/2}px`;stage.style.top=`${(innerHeight-LOGICAL_H*s)/2}px`;}
async function loadImage(path){
  const img=new Image();
  img.alt='';img.draggable=false;
  img.style.cssText='display:block;width:1920px;height:1080px;object-fit:cover;object-position:center';
  img.src=path;
  await img.decode();
  if(!img.naturalWidth)throw new Error(`插画加载失败: ${path}`);
  illustrationImages.set(path,img);
}

window.ready=(async()=>{
  [config,defaults,scenes,subtitles]=await Promise.all([
    json('../00_brief/episode.json'),json('../00_brief/effective_defaults.json'),
    json('../03_storyboard/scenes.json'),json('../02_timing/subtitles.json')
  ]);
  scenes=scenes.scenes;
  if(config.fps!==defaults.video.fps)throw new Error('配置帧率不一致');
  const paths=[...new Set(scenes.filter(s=>s.layer==='illustration').map(s=>'../'+s.asset_path))];
  await Promise.all(paths.map(loadImage));
  await document.fonts.load(`700 ${defaults.type.caption_px}px "${defaults.type.family}"`);
  await document.fonts.ready;
  const safe=defaults.layout.caption_safe;
  region.style.left=`${safe[0]}px`;region.style.top=`${safe[1]}px`;
  region.style.width=`${safe[2]-safe[0]}px`;region.style.height=`${safe[3]-safe[1]}px`;
  caption.style.fontFamily=`"${defaults.type.family}",sans-serif`;
  caption.style.fontSize=`${defaults.type.caption_px}px`;
  caption.style.fontWeight=defaults.type.caption_bold?'700':'400';
  caption.style.maxWidth=`${safe[2]-safe[0]}px`;
  caption.style.color=defaults.brand.text_on_dark;
  fit();
  window.renderFrame(0);
})();

window.renderFrame=function(frame){
  if(!Number.isInteger(frame)||frame<0||frame>=config.total_frames)throw new Error(`帧号超出范围: ${frame}`);
  currentFrame=frame;
  const clip=scenes.find(s=>frame>=s.start_frame&&frame<s.end_frame_exclusive);
  if(!clip)throw new Error(`时间轴缺帧: ${frame}`);
  const t=(frame-clip.start_frame)/config.fps,duration=(clip.end_frame_exclusive-clip.start_frame)/config.fps;
  if(clip.layer==='illustration'){
    // A complete still image; no transform, tween, opacity or camera motion.
    // Reuse the decoded HTML image node. Recreating an SVG <image> on each
    // frame can race its resource loading and produce a blank screenshot.
    if(visibleIllustration!==clip.id){
      visual.replaceChildren(illustrationImages.get('../'+clip.asset_path));
      visibleIllustration=clip.id;
    }
    lastState={frame,clip_id:clip.id,layer:'illustration',asset_path:clip.asset_path,motion:'none',transition:'hard_cut'};
  }else{
    visibleIllustration=null;
    const id=clip.card_id||clip.id;
    visual.innerHTML=renderCard(id,t,duration,defaults);
    lastState={frame,clip_id:clip.id,layer:'information_card',local_seconds:t,...cardState(id,t,duration,defaults)};
  }
  const sec=frame/config.fps;
  const sub=subtitles.find(s=>sec>=s.start&&sec<s.end);
  caption.textContent=sub?sub.text:'';
  caption.style.display=sub?'block':'none';
  lastState.caption=sub?{id:sub.id,text:sub.text}:null;
  return lastState;
};
window.getFrameState=()=>lastState;
window.getCurrentFrame=()=>currentFrame;
window.inspectTextBounds=()=>{
  const violations=[];
  for(const node of visual.querySelectorAll('svg text')){
    const style=getComputedStyle(node);if(Number(style.opacity)===0||style.display==='none'||style.visibility==='hidden')continue;
    const box=node.getBoundingClientRect(),stageBox=stage.getBoundingClientRect(),scale=stageBox.width/LOGICAL_W;
    const b={x:(box.left-stageBox.left)/scale,y:(box.top-stageBox.top)/scale,w:box.width/scale,h:box.height/scale};
    if(b.x < -1||b.y < -1||b.x+b.w>LOGICAL_W+1||b.y+b.h>LOGICAL_H+1)violations.push({text:node.textContent,...b});
  }
  if(caption.scrollWidth>caption.clientWidth+2)violations.push({text:caption.textContent,kind:'caption_overflow'});
  return violations;
};
addEventListener('resize',fit);
