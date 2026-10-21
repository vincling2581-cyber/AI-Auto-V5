/* reference_cards_v1: reusable SVG drawing primitives only.
 * Derived from accepted card_style_v4_reference. No episode scene, text, timing, network fetch or wall clock.
 * Call createReferenceCardKit(effectiveDefaults) after loading local Flubber when morphing is required.
 */
(function(global){
  'use strict';
  global.createReferenceCardKit=function(effective){
    if(!effective?.video?.width||!effective?.video?.height||!effective?.video?.fps||!effective?.type?.family)
      throw new Error('Pass this episode effective defaults: video dimensions/fps and type.family are required');
    const cardConfig=effective.cards;
    if(!cardConfig?.palette||!cardConfig?.typography||!cardConfig?.geometry)
      throw new Error('Pass effective cards.palette, cards.typography and cards.geometry; no hidden episode fallback');
    const geometry=cardConfig.geometry,typography=cardConfig.typography;
    const motionSeconds=cardConfig.process_initial_seconds??0.55;
    for(const key of ['background','dark','soft','paper','accent','text','ink','muted','line','edge','paperLine'])
      if(!cardConfig.palette[key])throw new Error('Missing palette role: '+key);
    for(const key of ['panel_border_px','panel_radius_px','connection_stroke_px','icon_stroke_local_px'])
      if(!Number.isFinite(geometry[key]))throw new Error('Missing geometry value: '+key);
    for(const key of ['title_px','node_px','support_px'])
      if(!Number.isFinite(typography[key]))throw new Error('Missing typography value: '+key);
    if(geometry.icon_viewbox_units!==100)
      throw new Error('reference_cards_v1 icons use a fixed 100-unit coordinate system; icon_viewbox_units must be 100');
    const easingFunctions={linear:p=>p,quadratic_out:p=>1-Math.pow(1-p,2),cubic_out:p=>1-Math.pow(1-p,3)};
    const easingAliases={quadratic:'quadratic_out',cubic:'cubic_out'};
    function easing(name){
      const canonical=Object.prototype.hasOwnProperty.call(easingAliases,name)?easingAliases[name]:name;
      if(!Object.prototype.hasOwnProperty.call(easingFunctions,canonical))
        throw new Error('Unknown easing '+String(name)+'; supported: linear, quadratic_out, cubic_out');
      return easingFunctions[canonical];
    }
    const objectCurve=cardConfig.frame_time_easing?.object_default;
    const morphCurve=cardConfig.frame_time_easing?.morph_default;
    easing(objectCurve);easing(morphCurve);
  const clamp=x=>Math.max(0,Math.min(1,x)),lerp=(a,b,p)=>a+(b-a)*p;
  const phase=(t,s,d)=>clamp((t-s)/d),m=(t,s,d=motionSeconds,curve=objectCurve)=>easing(curve)(phase(t,s,d));
  let serial=0;
  const C={...cardConfig.palette};
  const col=s=>C[s]||s,esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
  const mix=(a,b,p)=>'#'+[1,3,5].map(i=>Math.round(lerp(parseInt(col(a).slice(i,i+2),16),parseInt(col(b).slice(i,i+2),16),p)).toString(16).padStart(2,'0')).join('');
  const box=(x,y,w,h,fill='dark',stroke='edge',r=geometry.panel_radius_px)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${col(fill)}" stroke="${col(stroke)}" stroke-width="${geometry.panel_border_px}"/>`;
  function panel(x,y,w,h,tone='dark',r=geometry.panel_radius_px){const themes={dark:['dark','edge'],soft:['soft','edge'],paper:['paper','none'],accent:['accent','accent'],outline:['soft','line']};const a=themes[tone]||themes.dark;return box(x,y,w,h,a[0],a[1],r)}
  const text=(s,x,y,size=typography.node_px,ink='text',anchor='start',bold=false)=>`<text x="${x}" y="${y}" font-family="${esc(effective.type.family)}" font-size="${size}" fill="${col(ink)}" text-anchor="${anchor}" font-weight="${bold?700:400}">${esc(s)}</text>`;
  const group=(s,p=1,dx=0,dy=0,scale=1,rotation=0,cx=0,cy=0)=>`<g opacity="${clamp(p)}" transform="translate(${dx},${dy}) translate(${cx},${cy}) rotate(${rotation}) scale(${scale}) translate(${-cx},${-cy})">${s}</g>`;
  function clip(s,p,x,y,w,h,axis='x'){const id='clip_'+serial++;return `<defs><clipPath id="${id}"><rect x="${x}" y="${y}" width="${axis==='x'?w*clamp(p):w}" height="${axis==='y'?h*clamp(p):h}"/></clipPath></defs><g clip-path="url(#${id})">${s}</g>`}
  function settle(s,t,start,d,cx,cy,opt={}){const p=m(t,start,d);return group(s,1,(opt.dx||0)*(1-p),(opt.dy??25)*(1-p),lerp(opt.scale??.94,1,p),(opt.rotate??-2)*(1-p),cx,cy)}
  function path(d,p=1,ink='line',width=geometry.connection_stroke_px,dashed=false){const id='stroke_'+serial++;return `<defs><mask id="${id}" maskUnits="userSpaceOnUse" x="0" y="0" width="${effective.video.width}" height="${effective.video.height}"><path d="${d}" fill="none" stroke="white" stroke-width="${width+4}" stroke-linecap="round" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="${1-clamp(p)}"/></mask></defs><path d="${d}" fill="none" stroke="${col(ink)}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round" ${dashed?'stroke-dasharray="12 10"':''} mask="url(#${id})"/>`}
  const iconPaths={chat:['M15 17H85V64H49L29 82V64H15Z','M30 34H69M30 47H58'],doc:['M25 12H59L77 30V89H25Z','M59 12V31H77M37 46H65M37 59H65M37 72H57'],clipboard:['M33 21H20V89H80V21H66M36 16H64V31H36Z','M34 48H66M34 62H66M34 76H57'],folder:['M12 30V18H40L50 31H88V82H12Z','M13 43H87'],target:['M83 50A33 33 0 1 1 17 50A33 33 0 1 1 83 50','M69 50A19 19 0 1 1 31 50A19 19 0 1 1 69 50','M50 50L83 16M73 17H84V29'],grid:['M15 15H43V43H15ZM57 15H85V43H57ZM15 57H43V85H15ZM57 57H85V85H57Z'],sliders:['M22 15V85M50 15V85M78 15V85','M13 28H31V43H13ZM41 57H59V72H41ZM69 31H87V46H69Z'],check:['M21 52L40 72L80 28'],person:['M65 31A15 15 0 1 1 35 31A15 15 0 1 1 65 31','M22 84V72A28 28 0 0 1 78 72V84M32 84H68'],play:['M12 17H88V85H12Z','M41 35L64 52L41 69Z'],plus:['M13 18H87V85H13Z','M13 35H87M50 47V72M37 60H63'],copy:['M33 28H82V87H33Z','M63 28V14H15V73H33M46 46H69M46 59H69M46 72H61'],search:['M65 42A23 23 0 1 1 19 42A23 23 0 1 1 65 42','M59 59L84 84'],arrow:['M15 50H84M66 32L84 50L66 68'],question:['M32 32C32 8 72 8 72 32C72 49 50 48 50 63M50 79V81']};
  function icon(name,x,y,size=90,ink='accent',p=1){return `<g transform="translate(${x},${y}) scale(${size/100})" fill="none" stroke="${col(ink)}" stroke-width="${geometry.icon_stroke_local_px}" stroke-linecap="round" stroke-linejoin="round">${(iconPaths[name]||iconPaths.doc).map(d=>`<path d="${d}" pathLength="1" stroke-dasharray="1 1" stroke-dashoffset="${1-clamp(p)}"/>`).join('')}</g>`}
  const routeCache=new Map();
  function onPath(d,p){let el=routeCache.get(d);if(!el){el=document.createElementNS('http://www.w3.org/2000/svg','path');el.setAttribute('d',d);routeCache.set(d,el)}return el.getPointAtLength(el.getTotalLength()*clamp(p))}
  function packet(d,p,ink='accent',r=8,kind='dot'){if(p<=0||p>=1)return '';const xy=onPath(d,p);return kind==='dot'?`<circle cx="${xy.x}" cy="${xy.y}" r="${r}" fill="${col(ink)}"/>`:icon(kind,xy.x-24,xy.y-24,48,ink)}
  const shapes={bubble:'M17 8H83Q94 8 94 20V65Q94 77 82 77H48L22 96V77H17Q6 77 6 65V20Q6 8 17 8Z',paper:'M6 0H94Q100 0 100 6V94Q100 100 94 100H6Q0 100 0 94V6Q0 0 6 0Z',doc:'M25 12H59L77 30V89H25Z',clipboard:'M20 21H36V16H64V21H80V89H20Z',folder:'M12 30V18H40L50 31H88V82H12Z'};
  const morphCache=new Map();
  function morph(a,b,t,start,d,from,to,fillFrom='paper',fillTo='paper',stroke='accent',arc=65,lines=true,lineInk='ink'){const raw=phase(t,start,d);if(raw<=0||raw>=1)return '';const p=m(t,start,d,morphCurve),key=a+'>'+b;if(!morphCache.has(key))morphCache.set(key,global.flubber.interpolate(shapes[a],shapes[b],{maxSegmentLength:3}));const [x,y,w,h]=from.map((v,i)=>lerp(v,to[i],p));const opacity=1-m(t,start+d-.10,.10);return `<g opacity="${opacity}" transform="translate(${x},${y-arc*Math.sin(raw*Math.PI)}) scale(${w/100},${h/100})"><path d="${morphCache.get(key)(p)}" fill="${mix(fillFrom,fillTo,p)}" stroke="${col(stroke)}" stroke-width="1"/>${lines?`<path d="M34 45H65M34 58H65M34 71H57" fill="none" stroke="${col(lineInk)}" stroke-width="1.8" stroke-linecap="round"/>`:''}</g>`}
  function folder(x,y,size=120,open=0,ink='accent',fill='none'){return `<g transform="translate(${x},${y}) scale(${size/100})"><path d="M12 30V18H40L50 31H88V82H12Z" fill="${col(fill)}" stroke="${col(ink)}" stroke-width="${geometry.icon_stroke_local_px}" stroke-linejoin="round"/><path d="M12 ${43-12*open}H88L${88-6*open} 82H${12+6*open}Z" fill="${col(fill)}" stroke="${col(ink)}" stroke-width="${geometry.icon_stroke_local_px}" stroke-linejoin="round"/></g>`}

    return {clamp,lerp,phase,m,col,mix,box,panel,text,group,clip,settle,path,icon,packet,morph,folder,
      beginFrame:()=>{serial=0;},
      profile:()=>JSON.parse(JSON.stringify({video:effective.video,type:effective.type,cards:cardConfig}))};
  };
})(typeof window!=='undefined'?window:globalThis);
