/* HUMAN 3.0 / v4.6 episode cards. Frame-time SVG only; no animation clock.
 * Contract: renderCard(assetName, sceneLocalSeconds, absoluteSeconds) => SVG inner markup.
 * All curved handoffs use the same sampled polyline for drawing and arc-length travel.
 */
(function () {
  'use strict';
  const C = { paper:'#F5F2E9', ink:'#16392F', muted:'#52685F', line:'#B8C7BD',
    green:'#285B47', mint:'#BFE8CD', coral:'#C8674F', coralSoft:'#F2DDD3',
    blue:'#427A99', blueSoft:'#DCE9EC', gold:'#A67A30', goldSoft:'#EEE4C7',
    dark:'#102D29', white:'#FFFDF5' };
  const F = 'Microsoft YaHei, sans-serif';
  const clamp = v => Math.max(0, Math.min(1, v));
  const p = (t,a,b) => clamp((t-a)/(b-a));
  const out = v => 1-Math.pow(1-clamp(v),3);
  const smooth = v => { v=clamp(v); return v*v*(3-2*v); };
  const mix = (a,b,v) => a+(b-a)*v;
  const n = v => Number(v.toFixed(3));
  const esc = s => String(s).replace(/[&<>\"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[c]));
  const size = key => Number((window.EFFECTIVE_DEFAULTS?.cards?.typography||{})[key+'_px']) || ({title:72,node:46,support:34}[key]);
  const txt = (x,y,s,z=34,c=C.ink,w=400,a='start',extra='') => `<text x="${n(x)}" y="${n(y)}" font-family="${F}" font-size="${z}" font-weight="${w}" fill="${c}" text-anchor="${a}" ${extra}>${esc(s)}</text>`;
  const line = (x1,y1,x2,y2,c=C.line,w=2,extra='') => `<line x1="${n(x1)}" y1="${n(y1)}" x2="${n(x2)}" y2="${n(y2)}" stroke="${c}" stroke-width="${w}" ${extra}/>`;
  const circle = (x,y,r,fill,stroke='none',w=0,extra='') => `<circle cx="${n(x)}" cy="${n(y)}" r="${n(r)}" fill="${fill}" stroke="${stroke}" stroke-width="${w}" ${extra}/>`;
  const rect = (x,y,w,h,fill,r=0,stroke='none',sw=0,extra='') => `<rect x="${n(x)}" y="${n(y)}" width="${n(w)}" height="${n(h)}" rx="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${extra}/>`;
  const grp = (body,extra='') => `<g ${extra}>${body}</g>`;
  const opacity = (body,v) => grp(body,`opacity="${n(clamp(v))}"`);
  const pathD = pts => pts.map((v,i)=>`${i?'L':'M'}${n(v[0])},${n(v[1])}`).join(' ');
  const path = (pts,c,w=3,progress=1,extra='') => `<path d="${pathD(pts)}" fill="none" stroke="${c}" stroke-width="${w}" stroke-linecap="round" stroke-linejoin="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="${n(1-clamp(progress))}" ${extra}/>`;
  function bezier(a,b,c,d,steps=80) {
    const pts=[];
    for(let i=0;i<=steps;i++){const u=i/steps,v=1-u;pts.push([v*v*v*a[0]+3*v*v*u*b[0]+3*v*u*u*c[0]+u*u*u*d[0],v*v*v*a[1]+3*v*v*u*b[1]+3*v*u*u*c[1]+u*u*u*d[1]]);}
    return pts;
  }
  function atLength(pts,q) {
    const lens=[0]; for(let i=1;i<pts.length;i++)lens.push(lens[i-1]+Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]));
    const target=lens[lens.length-1]*clamp(q); let k=1; while(k<lens.length-1&&lens[k]<target)k++;
    const u=(target-lens[k-1])/(lens[k]-lens[k-1]||1); return [mix(pts[k-1][0],pts[k][0],u),mix(pts[k-1][1],pts[k][1],u)];
  }
  function resample(pts,count=81){return Array.from({length:count},(_,i)=>atLength(pts,i/(count-1)));}
  function bg(id,dark=false) {
    const base=dark?C.dark:(window.EFFECTIVE_DEFAULTS?.cards?.palette?.background||C.paper);
    return `<defs><pattern id="${id}_paper" width="42" height="42" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="0.8" fill="${dark?'#86A89A':'#92A596'}" opacity="0.16"/></pattern></defs>`+
      rect(0,0,1920,1080,base)+rect(0,0,1920,1080,`url(#${id}_paper)`)+
      line(128,155,1792,155,dark?'#39584D':'#C8D1C6',1.5);
  }
  function heading(s,dark=false){return txt(128,268,s,size('title'),dark?C.white:C.ink,700);}
  // 100-unit icons. No portrait features: these are diagram symbols, not characters.
  function icon(kind,x,y,scale=1,color=C.ink,width=3.3){
    const paths={
      mind:'<path d="M30 81V66C15 54 17 29 34 20C51 10 72 18 76 35L84 49H74V65H59V81"/><path d="M34 38L48 31L62 40L48 51L34 38M48 31V51"/><circle cx="34" cy="38" r="3"/><circle cx="62" cy="40" r="3"/>',
      body:'<path d="M15 43V57M23 33V67M31 41V59M31 50H69M69 41V59M77 33V67M85 43V57"/><path d="M34 78H66"/>',
      spirit:'<path d="M50 76C37 65 20 53 20 39C20 24 39 20 50 34C61 20 80 24 80 39C80 53 63 65 50 76Z"/><path d="M8 55L18 57M82 57L92 55M50 8V18"/>',
      career:'<rect x="19" y="33" width="62" height="47" rx="5"/><path d="M36 33V21H64V33M19 48C38 60 62 60 81 48M45 49H55V62H45Z"/>',
      pin:'<path d="M50 84C39 67 24 52 24 36A26 26 0 0 1 76 36C76 52 61 67 50 84Z"/><circle cx="50" cy="36" r="9"/>',
      question:'<path d="M18 21H82V66H53L33 82V66H18Z"/><path d="M42 36C42 24 64 24 64 37C64 45 51 45 51 52M51 58V60"/>',
      step:'<path d="M17 78H37V60H57V42H77V23M66 23H77V34"/><circle cx="24" cy="24" r="6"/>',
      arrow:'<path d="M18 50H81M61 30L81 50L61 70"/>'
    };
    return grp(paths[kind]||paths.arrow,`transform="translate(${n(x)},${n(y)}) scale(${n(scale)})" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"`);
  }
  const dimensions=[
    {id:'mind',name:'心智',sub:'理解与思考',color:C.green,soft:'#DFEBDD'},
    {id:'body',name:'身体',sub:'健康与活力',color:C.coral,soft:C.coralSoft},
    {id:'spirit',name:'精神',sub:'意义与连接',color:C.blue,soft:C.blueSoft},
    {id:'career',name:'事业',sub:'价值与贡献',color:C.gold,soft:C.goldSoft}
  ];
  function titleRoute(t){
    const enter=out(p(t,0,.38)), morph=smooth(p(t,3.866,5.62));
    const tangled=Array.from({length:81},(_,i)=>{const u=i/80;return [1370+260*Math.sin(u*Math.PI*4.1-.9)+90*Math.sin(u*Math.PI*9),535+160*Math.cos(u*Math.PI*5.6)+45*Math.sin(u*Math.PI*11)];});
    const clean=resample(bezier([1050,690],[1260,680],[1430,365],[1730,365]));
    const current=tangled.map((v,i)=>[mix(v[0],clean[i][0],morph),mix(v[1],clean[i][1],morph)]);
    let s=bg('route');
    s+=grp(txt(134,244,'一个关于成长的框架',34,C.muted,400)+txt(122,430,'HUMAN',155,C.ink,700)+txt(128,616,'3.0',190,C.ink,700)+
      line(136,670,680,670,C.ink,2)+txt(136,732,'Dan Koe',49,C.ink,700)+txt(136,791,'人生进化框架',34,C.muted),`opacity="${n(enter)}" transform="translate(0,${n((1-enter)*24)})"`);
    s+=opacity(path(tangled,C.coral,3.5),(.3*(1-morph))*enter);
    s+=path(current,C.green,7,out(p(t,.25,1.2)));
    const dot=atLength(current,mix(.08,1,out(p(t,3.866,5.62))));
    s+=circle(dot[0],dot[1],13,C.coral,C.paper,5);
    [0,.5,1].forEach((u,i)=>{
      const v=atLength(clean,u),a=out(p(t,4.9+i*.18,5.55+i*.18));
      s+=opacity(circle(v[0],v[1],16,C.paper,C.green,5)+txt(v[0],v[1]+64,['盘点','定位','行动'][i],46,C.ink,700,'middle'),a);
    });
    s+=opacity(txt(1380,820,'路径示意',30,C.muted,400,'middle'),p(t,5.3,5.7));
    s+=opacity(txt(1380,820,'把混乱梳理清楚',38,C.ink,500,'middle'),p(t,3.866,4.1)*(1-p(t,5.0,5.3)));
    return s;
  }
  function quadrants(t){
    let s=bg('quadrants')+heading('从四个方向，看见自己');
    const cx=960,cy=577;
    s+=`<defs><clipPath id="quad_clip"><ellipse cx="960" cy="577" rx="710" ry="253"/></clipPath></defs>`;
    const coords=[[535,421],[1305,421],[535,711],[1305,711]];
    const slices=[[250,324,710,253],[960,324,710,253],[250,577,710,253],[960,577,710,253]];
    dimensions.forEach((d,i)=>{
      const a=out(p(t,2.166+i*.64,2.78+i*.64)); const [x,y,w,h]=slices[i];
      s+=grp(rect(x,y,w,h,d.soft),`clip-path="url(#quad_clip)" opacity="${n(.28+.72*a)}"`);
    });
    s+=line(960,324,960,830,C.paper,5)+line(250,577,1670,577,C.paper,5);
    dimensions.forEach((d,i)=>{
      const st=2.166+i*.64, q=out(p(t,st,st+.62)),[x,y]=coords[i];
      const dest=[i%2?1198:722,i<2?437:698];
      const pts=bezier([cx,cy],[mix(cx,dest[0],.35),cy],[dest[0],mix(cy,dest[1],.75)],dest);
      s+=path(pts,d.color,3.5,q);
      if(q>0&&q<1){const dot=atLength(pts,q);s+=circle(dot[0],dot[1],8,d.color,C.paper,3);}
      const a=out(p(t,st+.62,st+.84));
      s+=opacity(icon(d.id,x-160,y-71,1.02,d.color)+txt(x,y,d.name,46,C.ink,700)+txt(x,y+56,d.sub,34,C.muted),a);
    });
    s+=circle(cx,cy,79,C.white,C.paper,10)+circle(cx,cy,66,C.ink)+txt(cx,cy+19,'你',56,C.white,700,'middle');
    s+=opacity(txt(960,848,'四个维度 · 一次完整盘点',34,C.muted,400,'middle'),p(t,5.3,5.65));
    return s;
  }
  function promptDoc(x,y,scale,opacityValue=1){
    return grp(rect(0,0,490,428,'#001C17',15,'none',0, 'opacity=".18" transform="translate(9,12)"')+
      `<path d="M0 0H424L490 66V428H0Z" fill="${C.white}" stroke="#C6D9CB" stroke-width="2"/><path d="M424 0V66H490" fill="#E1EBDC" stroke="#C6D9CB" stroke-width="2"/>`+
      rect(32,32,9,55,C.coral,3)+txt(62,70,'HUMAN 3.0',40,C.ink,700)+txt(34,137,'结构化提示',46,C.ink,700)+
      line(34,165,454,165,'#BDCBC0',2)+txt(34,218,'围绕四个象限',34,C.ink)+txt(34,276,'逐项了解当前状态',34,C.ink)+txt(34,334,'结合回答继续追问',34,C.ink)+txt(34,392,'摘要示意',30,C.muted),
      `transform="translate(${n(x)},${n(y)}) scale(${n(scale)})" opacity="${n(opacityValue)}"`);
  }
  function prompt(t){
    let s=bg('prompt',true)+heading('把结构化提示交给 AI',true);
    const transfer=out(p(t,2.566,3.94));
    const route=bezier([405,568],[590,660],[720,650],[890,600]);
    const where=atLength(route,transfer),scale=mix(1,.37,transfer);
    s+=opacity(path(route,'#6E9E87',2),.5);
    // Back wall of the receiving tray; document remains visibly stored after arrival.
    s+=rect(742,392,306,338,'#1A4036',27,'#557C66',2)+txt(895,443,'AI 输入',42,C.white,700,'middle');
    s+=promptDoc(where[0]-245*scale,where[1]-214*scale,scale,out(p(t,0,.35)));
    // The foreground lip occludes the bottom of the arriving page only at the tray.
    s+=rect(758,660,274,53,'#285242',13,'#6F967F',2)+txt(895,697,transfer>=1?'提示已接收':'接收提示',29,'#D9EDDD',600,'middle');
    const endpoints=[[1312,375],[1420,508],[1420,643],[1312,776]];
    dimensions.forEach((d,i)=>{
      const dst=endpoints[i],start=4.4+i*.12,q=out(p(t,start,start+.72));
      const points=bezier([1048,565],[1175,565],[1170,dst[1]],dst);
      s+=opacity(path(points,'#547C6D',2.3),.8);
      s+=path(points,d.soft,3,q);
      if(q>0&&q<1){const at=atLength(points,q);s+=rect(at[0]-11,at[1]-13,22,26,d.soft,3,C.dark,1)+line(at[0]-5,at[1]-4,at[0]+5,at[1]-4,d.color,2);}
      const a=out(p(t,start+.72,start+.95));
      s+=circle(dst[0]+47,dst[1],43,'#24473D',d.soft,2)+icon(d.id,dst[0]+15,dst[1]-32,.64,d.soft,4);
      s+=txt(dst[0]+112,dst[1]-2,d.name,42,C.white,700);
      s+=opacity(txt(dst[0]+112,dst[1]+43,'基础定位',30,d.soft),a);
    });
    s+=txt(160,831,'画面示意 · 提示词为摘要',30,'#BDD4C7');
    s+=opacity(txt(895,786,'同一份提示，分别了解四个维度',32,'#D7E9DC',400,'middle'),p(t,5.66,6.0));
    return s;
  }
  function plan(t){
    let s=bg('plan')+heading('一份可以继续行动的指南');
    const a=out(p(t,.36,1.5)),b=out(p(t,1.16,2.55)),move=out(p(t,.36,2.55));
    const x=mix(700,240,move),y=348,w=480,h=420;
    const wa=w*mix(.035,1,a),wb=w*mix(.025,1,b),skewA=45*Math.sin(Math.PI*a),skewB=-45*Math.sin(Math.PI*b);
    const faces=[{x:0,width:w,skew:0,offset:0,fill:'#FEFCF3',i:0},{x:w,width:wa,skew:skewA,offset:0,fill:'#F4EEDC',i:1},{x:w+wa,width:wb,skew:skewB,offset:skewA,fill:'#FBF9EE',i:2}];
    s+=`<defs>${faces.map(f=>`<clipPath id="plan_face_${f.i}"><path d="M${n(x+f.x)} ${n(y+f.offset)}L${n(x+f.x+f.width)} ${n(y+f.offset+f.skew)}V${n(y+h+f.offset+f.skew)}L${n(x+f.x)} ${n(y+h+f.offset)}Z"/></clipPath>`).join('')}</defs>`;
    s+=`<path d="M${n(x+10)} ${y+16}H${n(x+w+wa+wb+10)}V${y+h+16}H${n(x+10)}Z" fill="#193C2A" opacity=".08"/>`;
    faces.forEach(f=>{
      const sx=f.width/w,xx=x+f.x,yy=y+f.offset;
      s+=`<path d="M${n(xx)} ${n(yy)}L${n(xx+f.width)} ${n(yy+f.skew)}V${n(yy+h+f.skew)}L${n(xx)} ${n(yy+h)}Z" fill="${f.fill}" stroke="#C9C6B3" stroke-width="2"/>`;
      if(f.i>0)s+=rect(xx,yy,Math.min(20,f.width),h,'#A6986A',0,'none',0,`opacity="${n(.12*(1-(f.i===1?a:b))+.03)}"`);
      const info=[['01','当前位置','四维状态','与现有习惯','pin',C.green],['02','关键问题','值得继续追问','的成长卡点','question',C.coral],['03','下一步行动','可以尝试的','具体小步骤','step',C.blue]][f.i];
      const inner=txt(40,60,info[0],33,info[5],700)+icon(info[4],42,91,1.03,info[5],3.5)+txt(42,259,info[1],44,C.ink,700)+txt(42,322,info[2],34,C.muted)+txt(42,370,info[3],34,C.muted);
      s+=grp(grp(inner,`transform="matrix(${n(sx)} ${n(f.skew/w)} 0 1 ${n(xx)} ${n(yy)})"`),`clip-path="url(#plan_face_${f.i})"`);
    });
    s+=txt(960,839,'输出结构示意 · 根据真实回答继续完善',32,C.muted,400,'middle');
    return s;
  }
  function choice(t){
    let s=bg('choice');
    const follow=out(p(t,5.466,5.85));
    s+=opacity(heading('你最想先升级哪一项？'),1-follow)+opacity(heading('继续探索 AI 新玩法'),follow);
    const xs=[390,770,1150,1530];
    dimensions.forEach((d,i)=>{
      const a=out(p(t,1.666+i*.55,2.13+i*.55));
      s+=circle(xs[i],448,95,d.soft,'none',0,`opacity="${n(.38+.62*a)}"`);
      s+=icon(d.id,xs[i]-68,380,1.36,d.color,3.7);
      s+=txt(xs[i],615,d.name,46,C.ink,700,'middle')+txt(xs[i],674,d.sub,32,C.muted,400,'middle');
      // The ring is a temporary spoken-label cue only. All four end equally weighted.
      const pulse=p(t,1.666+i*.55,1.94+i*.55)*(1-p(t,2.08+i*.55,2.38+i*.55));
      s+=circle(xs[i],448,106,'none',d.color,3,`opacity="${n(.6*pulse)}"`);
    });
    const collect=out(p(t,4.466,5.08));
    const bracket=[[390,705],[390,726],[960,726],[1530,726],[1530,705]];
    s+=path(bracket,C.green,2.8,collect);
    s+=line(960,726,960,mix(726,752,collect),C.green,2.8);
    const call=out(p(t,4.72,5.12));
    s+=opacity(rect(655,752,610,66,C.ink,33)+txt(960,797,'评论区 · 留下你的选择',37,C.white,700,'middle'),call);
    s+=opacity(txt(960,850,'关注，一起看看更多可能',34,C.muted,500,'middle'),follow);
    return s;
  }
  const renderers={title_route:titleRoute,quadrants,prompt,plan,choice};
  window.renderCard=function(assetName,t,absoluteT){
    const fn=renderers[assetName];
    if(!fn)throw new Error('Unknown HUMAN 3.0 card asset: '+assetName);
    const local=Number.isFinite(t)?Math.max(0,t):0;
    return `<g data-card="${assetName}" data-local-time="${n(local)}">${fn(local)}</g>`;
  };
  window.CARD_THEME={title_route:'paper',quadrants:'paper',prompt:'dark',plan:'paper',choice:'paper'};
})();
