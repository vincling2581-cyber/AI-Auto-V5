/* Group-preserving export; ownership is supplied from the audited full-frame catalog. */
(()=>{'use strict';
const xml=e=>new XMLSerializer().serializeToString(e);
const cache=new Map();
function clean(root){
 for(const e of [...root.querySelectorAll('g')].reverse())if(!e.children.length)e.remove();
 const defs=[...root.querySelectorAll('defs')],all=new Map();
 for(const d of defs)for(const e of d.children)if(e.id)all.set(e.id,e);
 defs.forEach(e=>e.remove());
 for(const e of [...root.querySelectorAll('g')].reverse())if(!e.children.length)e.remove();
 let body=[...root.children].map(xml).join(''),needed=new Set(),queue=[...body.matchAll(/url\(#([^\)]+)\)/g)].map(m=>m[1]);
 while(queue.length){const id=queue.pop();if(needed.has(id))continue;needed.add(id);const d=all.get(id);if(!d)throw Error('Missing SVG definition '+id);for(const m of xml(d).matchAll(/url\(#([^\)]+)\)/g))queue.push(m[1]);}
 let s='<defs>'+[...needed].sort().map(id=>xml(all.get(id))).join('')+'</defs>'+body;
 s=s.replace(/ data-[\w-]+="[^"]*"/g,'');
 const ids=[...new Set([...s.matchAll(/id="([^"]+)"/g)].map(m=>m[1]))];
 ids.forEach((id,i)=>s=s.split('id="'+id+'"').join('id="d'+i+'"').split('url(#'+id+')').join('url(#d'+i+')'));
 return s;
}
function c00Compensate(root){
 const marked=root.querySelector('[data-ekind="icon"]');if(!marked)return;
 let q=1;for(let p=marked.parentElement;p&&p!==root;p=p.parentElement){q*=+(p.getAttribute('opacity')??1);p.removeAttribute('opacity');}
 if(q>=1)return;
 for(const el of [marked,...marked.querySelectorAll('*')])for(const attr of ['fill','stroke']){
  const s=el.getAttribute(attr);if(!s||s==='none')continue;
  const m=s.match(/^#([0-9a-f]{6})$/i);if(!m)throw Error('Unsupported compensation color '+s);
  const c=[0,2,4].map(i=>parseInt(m[1].slice(i,i+2),16)),bg=[7,17,12];
  el.setAttribute(attr,`rgb(${c.map((v,i)=>v*q+bg[i]*(1-q)).join(',')})`);
 }
}
window.exportGroups=async(plan,reference=false)=>{
 const raw=await exportRaw(),root=document.querySelector('#root>svg'),items=[],keys=[];
 for(const l of plan){const r=root.cloneNode(true),ids=new Set(l.source_ids);
  r.querySelectorAll('text').forEach(e=>e.remove());
  for(const e of r.querySelectorAll('[data-export-final-id]'))if(!ids.has(e.dataset.exportFinalId))e.remove();
  if(currentShot.id==='C00'&&l.role==='graphics')c00Compensate(r);
  const svg=clean(r),cacheKey=l.id+'|'+svg;
  let key=cache.get(cacheKey);
  if(!key){key='p'+cache.size;cache.set(cacheKey,key);items.push({key,svg,x:l.crop[0],y:l.crop[1],width:l.crop[2],height:l.crop[3]});}
  keys.push({id:l.id,key});
 }
 if(reference)items.push({key:'reference',svg:raw.source});
 return {keys,images:await rasterizeSVGs(items)};
};
})();
