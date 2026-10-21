/* HUMAN 3.0 · episode-local, deterministic SVG information cards.
 * t and duration are seconds within the card. No clock, DOM, randomness or imports.
 * Every motion value used by renderCard is also exposed through cardState.
 */
const clamp = (v, lo = 0, hi = 1) => Math.max(lo, Math.min(hi, v));
const lerp = (a, b, p) => a + (b - a) * p;
const out = p => 1 - (1 - clamp(p)) ** 3;
const smooth = p => { p = clamp(p); return p * p * (3 - 2 * p); };
const progress = (t, at, d, curve = out) => curve(clamp((t - at) / d));
const n = v => Number(v.toFixed(4));
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&apos;' }[c]));

export const CARD_TIMELINE = Object.freeze({
  C01: [119,312], C02: [312,525], C03: [525,744], C04: [744,876],
  C05: [876,1102], C06: [1198,1319], C07: [1319,1446], C08: [1446,1678],
});
const themes = {
  blue: { background:'#ECF2F7', dark:'#14271B', soft:'#DDE8F2', paper:'#F8FAFC', accent:'#4384B8', text:'#243A4C', ink:'#243A4C', muted:'#597183', line:'#94AFC1', edge:'#B9CAD7', paperLine:'#D1DFE8' },
  peach: { background:'#F8EDE4', dark:'#14271B', soft:'#EFDBCA', paper:'#FFF9F2', accent:'#B86A42', text:'#4D352A', ink:'#4D352A', muted:'#876A5A', line:'#C29D83', edge:'#DCC4B1', paperLine:'#EAD9C9' },
};
const form = { C01:'paper', C02:'blue', C03:'paper', C04:'paper', C05:'blue', C06:'paper', C07:'dark', C08:'peach' };
function config(id, defaults = {}) {
  const c = defaults.cards || {}, p = c.palette || {};
  const paper = { background:'#F5F2E9', dark:'#14271B', soft:'#E8EEDC', paper:'#F0F3EC', accent:'#78EFA2', text:'#24362B', ink:'#12251A', muted:'#526454', line:'#54775E', edge:'#B1C1AE', paperLine:'#C4CCC2', ...p };
  const key = form[id];
  const palette = key === 'dark' ? { ...paper, background:'#07110C', soft:'#101F16', text:'#F0F3EC', muted:'#A9B9AC', edge:'#33533B', ...(c.palette_presets?.dark || {}) } : { ...paper, ...(themes[key] || {}), ...(c.palette_presets?.[key] || {}) };
  return {
    palette, theme:key, family:defaults.type?.family || 'Microsoft YaHei',
    title:c.typography?.title_px ?? 72, node:c.typography?.node_px ?? 46, support:c.typography?.support_px ?? 34,
    radius:c.geometry?.panel_radius_px ?? 28, border:c.geometry?.panel_border_px ?? 2,
    connection:c.geometry?.connection_stroke_px ?? 3,
    iconStroke:c.geometry?.icon_stroke_local_px ?? 3.5,
    entry:Math.min(...(c.entry_seconds || [.25,.4])),
    rise:Math.min(...(c.entry_translation_px || [16,32])),
    highlight:Math.min(...(c.highlight_seconds || [.15,.3])),
    initial:c.process_initial_seconds ?? .55,
    contentSafe:defaults.layout?.content_safe || [64,110,1856,880],
    captionSafe:defaults.layout?.caption_safe || [160,920,1760,1040],
  };
}
const text = (s,x,y,size,color,weight=500,anchor='start',extra='') => `<text x="${n(x)}" y="${n(y)}" font-size="${n(size)}" fill="${color}" font-weight="${weight}" text-anchor="${anchor}" ${extra}>${esc(s)}</text>`;
const rect = (x,y,w,h,r,fill,stroke='none',sw=0,extra='') => `<rect x="${n(x)}" y="${n(y)}" width="${n(w)}" height="${n(h)}" rx="${n(r)}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${extra}/>`;
const line = (x1,y1,x2,y2,color,sw=3,extra='') => `<path d="M${n(x1)} ${n(y1)} L${n(x2)} ${n(y2)}" stroke="${color}" stroke-width="${sw}" fill="none" stroke-linecap="round" ${extra}/>`;
const group = (svg,opacity=1,transform='') => `<g opacity="${n(clamp(opacity))}" transform="${transform}">${svg}</g>`;
const circle = (x,y,r,fill,stroke='none',sw=0,extra='') => `<circle cx="${n(x)}" cy="${n(y)}" r="${n(r)}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" ${extra}/>`;
function heading(label,c,sub='') { const p=c.palette; return text(label,128,184,c.title,p.text,700)+(sub?text(sub,132,253,c.support,p.muted):''); }
function chip(label,x,y,w,h,c,fill=c.palette.paper,color=c.palette.text) { return rect(x,y,w,h,c.radius,fill,c.palette.edge,c.border)+text(label,x+w/2,y+h/2+c.node*.34,c.node,color,600,'middle'); }
function icon(kind,x,y,size,color,c) {
  const paths = {
    mind:'M30 67 C14 58 18 34 33 31 C31 15 52 12 61 24 C78 17 90 36 79 48 C89 62 74 78 62 72 L62 88 M47 34 L47 70 M32 48 L62 48 M62 33 L62 57',
    body:'M40 25 C40 11 62 11 62 25 C62 39 40 39 40 25 M25 56 L39 44 L61 44 L76 56 M43 48 L37 74 L28 90 M58 48 L64 74 L73 90 M43 68 L58 68',
    spirit:'M50 42 C30 19 10 39 25 55 L50 79 L75 55 C90 39 70 19 50 42 M13 76 Q25 93 43 91 M87 76 Q75 93 57 91',
    vocation:'M23 36 H77 Q85 36 85 44 V80 Q85 87 77 87 H23 Q15 87 15 80 V44 Q15 36 23 36 M34 35 V22 H66 V35 M15 55 Q50 73 85 55 M43 61 H57',
    doc:'M27 12 H63 L79 29 V88 H27 Z M63 12 V30 H79 M39 44 H66 M39 57 H66 M39 70 H58',
    arrow:'M17 50 H80 M61 29 L82 50 L61 71',
  };
  return `<g transform="translate(${x} ${y}) scale(${size/100})" stroke="${color}" stroke-width="${c.iconStroke}" fill="none" stroke-linecap="round" stroke-linejoin="round"><path d="${paths[kind] || paths.doc}"/></g>`;
}
function bezier(points,p) { const q=1-p; return {x:q**3*points[0][0]+3*q*q*p*points[1][0]+3*q*p*p*points[2][0]+p**3*points[3][0],y:q**3*points[0][1]+3*q*q*p*points[1][1]+3*q*p*p*points[2][1]+p**3*points[3][1]}; }
// A fixed 80-piece arc-length table keeps the visual packet on its actual curve.
function along(points,p) { let len=0,prev=bezier(points,0); const table=[0]; for(let i=1;i<=80;i++){const q=bezier(points,i/80);len+=Math.hypot(q.x-prev.x,q.y-prev.y);table.push(len);prev=q;} const target=clamp(p)*len; let i=1;while(i<80&&table[i]<target)i++; return bezier(points,((i-1)+(target-table[i-1])/(table[i]-table[i-1]||1))/80); }
const curveD = ps => `M${ps[0][0]} ${ps[0][1]} C${ps[1][0]} ${ps[1][1]} ${ps[2][0]} ${ps[2][1]} ${ps[3][0]} ${ps[3][1]}`;
function curve(ps,color,c,extra='') { return `<path d="${curveD(ps)}" fill="none" stroke="${color}" stroke-width="${c.connection}" stroke-linecap="round" ${extra}/>`; }
const quadNames=['心智','身体','精神','事业'];
const quadIcons=['mind','body','spirit','vocation'];
const quadDescriptions=['想法 · 信念','健康 · 习惯','关系 · 归属','工作 · 价值'];
function focusAt(t,begin,interval,end,c) { if(t<begin||t>=end+.4)return {index:null,weights:[1,1,1,1],restore:t>=end?1:0,ring:0}; const idx=Math.min(3,Math.floor((t-begin)/interval)); const restore=progress(t,end,.4); const weights=[0,1,2,3].map(i=>lerp(i===idx?1:.48,1,restore)); return {index:t>=end?null:idx,weights,restore,ring:(1-restore)*progress(t,begin,c.highlight)}; }

export function cardState(rawId,t,duration,defaults={}) {
  const id=String(rawId).toUpperCase();
  if(!CARD_TIMELINE[id])throw new Error(`Unknown card ${rawId}`);
  const c=config(id,defaults); const nominal=(CARD_TIMELINE[id][1]-CARD_TIMELINE[id][0])/30;
  duration=Number.isFinite(duration)&&duration>0?duration:nominal;t=clamp(Number(t)||0,0,duration);
  const s={id,t:n(t),duration:n(duration),absoluteTime:n(CARD_TIMELINE[id][0]/30+t),theme:c.theme,config:c,sourcePreserved:true,activeNodes:[],visibleSteps:[],readingHold:false};
  if(id==='C01') {
    s.titleReveal=progress(t,1.6,c.entry);s.demote=progress(t,3.15,.68,smooth);
    s.sourceReveal=progress(t,3.50,c.entry);
    s.transfers=[0,1,2].map(i=>{const p=progress(t,3.8667+i*.10,.92,smooth);return {id:['目标','卡点','行动'][i],progress:n(p),arrived:p===1,sourcePreserved:true};});
    s.guideRows=s.transfers.map(q=>q.arrived);s.guideReady=s.guideRows.every(Boolean);
    s.activeNodes=s.guideReady?['清晰指南']:s.transfers.filter(q=>q.progress>0&&!q.arrived).map(q=>q.id);
    s.visibleSteps=['Dan Koe',...(s.titleReveal>0?['HUMAN 3.0']:[]),...(s.sourceReveal>0?['目标','卡点','行动']:[]),...(s.guideReady?['清晰指南']:[])];
    s.readingHold=t>=5.1;
  } else if(id==='C02') {
    s.distribution=[0,1,2,3].map(i=>({id:quadNames[i],progress:n(progress(t,.55+i*.13,.9,smooth)),equalWeight:true}));
    s.focus=focusAt(t,2.1667,.7833,5.3,c);s.activeNodes=s.focus.index===null?quadNames:[quadNames[s.focus.index]];
    s.visibleSteps=['自己',...s.distribution.filter(q=>q.progress>0).map(q=>q.id)];s.readingHold=t>=5.7;s.noScores=true;
  } else if(id==='C03') {
    s.rail=progress(t,c.initial,1.3,smooth);
    s.levels=[0,1,2].map(i=>({id:`L${i+1}`,progress:n(progress(t,c.initial+i*.65,c.entry)),notPersonalRating:true}));
    s.planning=progress(t,3.2667,.7,smooth);s.nextStep=progress(t,4.1,.55,smooth);
    s.activeNodes=t>=4.1?['下一步行动']:t>=3.2667?['当前位置']:s.levels.filter(q=>q.progress>0).map(q=>q.id);
    s.visibleSteps=[...s.levels.filter(q=>q.progress>0).map(q=>q.id),...(s.planning>0?['当前位置']:[]),...(s.nextStep>0?['下一步行动']:[])];
    s.personalLevel=null;s.readingHold=t>=4.7;
  } else if(id==='C04') {
    const transfer=progress(t,1.38,1.27,smooth);
    s.copy=progress(t,1.10,.22);s.transfer={identity:'prompt-copy',progress:n(transfer),arrived:transfer===1,sourcePreserved:true,path:'cubic_bezier_arc_length'};
    s.pasted=t>=2.65;s.sent=t>=3.05;s.received=t>=3.45;s.inputPlaceholderVisible=!s.pasted&&transfer<.5;
    s.status=s.received?'已收到提示词':s.sent?'发送中':s.pasted?'已粘贴 · 待发送':'等待输入';
    s.activeNodes=[s.received?'AI 已收到':s.sent?'发送':s.pasted?'AI 输入区':transfer>0?'提示词副本':'提示词原文'];
    s.visibleSteps=['提示词原文',...(s.copy>0?['复制']:[]),...(s.pasted?['粘贴']:[]),...(s.sent?['发送']:[]),...(s.received?['收到']:[])];s.readingHold=t>=3.65;
  } else if(id==='C05') {
    const schedule=[2.3667,3.56,4.70,5.80];
    s.messages=schedule.map((at,i)=>({id:`message-${i+1}`,role:i%2===0?'AI 提问':'示例回答',visible:progress(t,at,c.entry),typing:t>=at-.38&&t<at,source:'illustrative_not_real_chat'}));
    s.pendingQuadrants=quadNames;s.estimatedLevels=null;s.extract=progress(t,6.35,.5,smooth);s.extractionArrived=s.extract===1;
    s.activeNodes=s.extract>0?['待验证卡点']:s.messages.filter(q=>q.visible>0).map(q=>q.id);
    s.visibleSteps=['四象限待了解',...s.messages.filter(q=>q.visible>0).map(q=>q.id),...(s.extract>0?['待验证卡点']:[])];s.readingHold=t>=6.85;
  } else if(id==='C06') {
    s.fields=[.35,1.08,1.81].map((at,i)=>{const p=progress(t,at,.5,smooth);return{id:['当前状态','主要卡点','下一步行动'][i],progress:n(p),arrived:p===1,sourcePreserved:true};});
    s.complete=s.fields.every(q=>q.arrived);s.activeNodes=s.complete?['成长指南']:s.fields.filter(q=>q.progress>0&&!q.arrived).map(q=>q.id);
    s.visibleSteps=s.fields.filter(q=>q.arrived).map(q=>q.id);s.readingHold=t>=2.45;
  } else if(id==='C07') {
    s.strike=progress(t,1.50,.20);s.replacement=progress(t,2.5667,.42,smooth);
    s.archive=progress(t,2.5667,.42,smooth);s.strikeIsIndependentSibling=true;s.struckOriginalRetained=true;
    s.oldValue='答案';s.newValue='系统提问';s.activeNodes=s.replacement>.5?['系统提问']:['答案'];
    s.visibleSteps=['缺少答案',...(s.strike>0?['否定旧理解']:[]),...(s.replacement>0?['缺少系统提问']:[])];s.readingHold=t>=3.1;
  } else if(id==='C08') {
    s.focus=focusAt(t,1.6667,.65,4.2667,c);s.selected=null;s.winner=null;s.equalOptions=true;
    s.activeNodes=s.focus.index===null?quadNames:[quadNames[s.focus.index]];
    s.cta=t>=5.4667?'关注，继续了解 AI 用法':t>=4.4667?'评论区，聊聊你的选择':'';
    s.ctaReveal=progress(t,t>=5.4667?5.4667:4.4667,c.entry);s.visibleSteps=[...quadNames,...(s.cta?[s.cta]:[])];s.readingHold=t>=4.67;
  }
  return s;
}

function c01(s,c) {
  const p=c.palette,d=s.demote;let outSvg='';
  outSvg+=group(text('Dan Koe',960,lerp(475,352,s.titleReveal),lerp(c.title,c.node,s.titleReveal),p.muted,600,'middle'),1-d);
  const titleWidth=lerp(c.title*5.6,c.node*5.6,d);
  outSvg+=text('HUMAN 3.0',lerp(960,128+c.node*5.6/2,d),lerp(475,174,d),lerp(c.title,c.node,d),p.text,700,'middle',`opacity="${n(s.titleReveal)}" textLength="${n(titleWidth)}" lengthAdjust="spacingAndGlyphs"`);
  // The shared progress moves the visual centre and its width without an anchor snap.
  outSvg+=group(text('人生进化框架',128,244,c.support,p.muted),d);
  const ys=[410,575,740],labels=['目标','卡点','行动'];
  const lines=['想往哪里走','被什么卡住','接下来做什么'];
  for(let i=0;i<3;i++){
    // Each source enters the corresponding guide row. Separate entrances keep
    // simultaneous packet identities readable instead of stacking at one hub.
    const entryY=536+i*85;
    const ps=[[565,ys[i]],[820,ys[i]],[950,entryY],[1215,entryY]];
    outSvg+=group(curve(ps,p.edge,c),s.sourceReveal);
    outSvg+=group(rect(180,ys[i]-55,385,110,c.radius,p.paper,p.edge,c.border)+text(labels[i],220,ys[i]+16,c.node,p.text,600)+text(lines[i],330,ys[i]+14,c.support,p.muted),s.sourceReveal);
    const q=s.transfers[i],pt=along(ps,q.progress);
    if(q.progress>0&&q.progress<1)outSvg+=circle(pt.x,pt.y,16,p.accent,p.ink,1.5)+text(labels[i],pt.x-28,pt.y-30,c.support,p.text,600,'end');
  }
  outSvg+=group(rect(1215,350,530,440,c.radius,p.paper,p.edge,c.border)+icon('doc',1250,383,74,p.line,c)+text('成长指南',1350,438,c.node,p.text,700),s.sourceReveal);
  const rowText=['明确目标','识别卡点','安排下一步'];
  s.guideRows.forEach((shown,i)=>{outSvg+=group(line(1270,500+i*85,1685,500+i*85,p.paperLine,c.border)+circle(1285,536+i*85,8,p.accent)+text(rowText[i],1314,549+i*85,c.node,p.text,500),shown?1:0);});
  outSvg+=group(text('把松散信息，理成可回看的路径',960,860,c.support,p.muted,500,'middle'),s.guideReady?1:0);
  return outSvg;
}
function c02(s,c) {
  const p=c.palette;let outSvg=heading('从「自己」到四个象限',c);
  const cx=960,cy=538,R=318,r=112;
  const sectors=[[-180,-90],[-90,0],[90,180],[0,90]];
  const centers=[[740,382],[1180,382],[740,693],[1180,693]];
  const fills=['#DCE9F5','#DCEDE9','#F0E5F0','#EFE7D9'];
  sectors.forEach(([a,b],i)=>{
    const pt=(rr,ang)=>[cx+rr*Math.cos(ang*Math.PI/180),cy+rr*Math.sin(ang*Math.PI/180)];
    const v=[pt(R,a),pt(R,b),pt(r,b),pt(r,a)];
    const d=`M${v[0]} A${R} ${R} 0 0 1 ${v[1]} L${v[2]} A${r} ${r} 0 0 0 ${v[3]} Z`;
    const dist=s.distribution[i].progress,[x,y]=centers[i],w=s.focus.weights[i];
    outSvg+=group(`<path d="${d}" fill="${fills[i]}" stroke="${p.background}" stroke-width="10"/>`,dist*.95);
    const ps=[[cx,cy],[cx+(x-cx)*.3,cy],[x,cy+(y-cy)*.7],[x,y]];
    if(dist>0&&dist<1){const q=along(ps,dist);outSvg+=circle(q.x,q.y,13,p.accent);}
    outSvg+=group(icon(quadIcons[i],x-34,y-82,68,p.line,c)+text(quadNames[i],x,y+18,c.node,p.text,700,'middle')+text(quadDescriptions[i],x,y+76,c.support,p.muted,500,'middle'),progress(s.t,1.45+i*.13,c.entry)*w);
  });
  outSvg+=circle(cx,cy,106,p.paper,p.edge,c.border)+text('自己',cx,cy+16,c.node,p.text,700,'middle');
  outSvg+=group(text('四个平等视角，一起盘点',960,866,c.support,p.muted,500,'middle'),s.focus.restore);
  return outSvg;
}
function c03(s,c) {
  const p=c.palette;let outSvg=heading('每个象限，都可以继续成长',c,'三层结构示意 · 各象限可以处于不同位置');
  const ys=[730,550,370],names=['顺从','自主','整合'],detail=['较依赖既定规则与外部权威','主动选择自己的目标与方法','容纳多种视角，识别联系'];
  const reached=lerp(730,370,s.rail);
  outSvg+=line(202,730,202,reached,p.line,c.connection);
  s.levels.forEach((q,i)=>{
    const a=q.progress;outSvg+=group(circle(202,ys[i],35,p.paper,p.line,c.connection)+text(`L${i+1}`,202,ys[i]+10,c.support,p.text,700,'middle')+text(names[i],280,ys[i]+12,c.node,p.text,700)+text(detail[i],280,ys[i]+65,c.support,p.muted),a);
  });
  outSvg+=group(line(1075,390,1075,760,p.paperLine,c.border),s.planning);
  outSvg+=group(text('从你的位置出发',1165,387,c.node,p.text,700)+chip('当前位置',1190,448,485,106,c,p.soft)+text('基于回答进行参考判断',1432,604,c.support,p.muted,500,'middle'),s.planning);
  outSvg+=group(line(1432,628,1432,677,p.line,c.connection)+`<path d="M1420 664 L1432 680 L1444 664" fill="none" stroke="${p.line}" stroke-width="${c.connection}"/>`+chip('下一步行动',1190,697,485,106,c,p.dark,p.paper),s.nextStep);
  outSvg+=text('描述发展方式，不评价人的价值',128,868,c.support,p.muted);
  return outSvg;
}
function c04(s,c) {
  const p=c.palette;let outSvg=heading('把结构化提示词交给 AI',c,'操作流程示意');
  // Exactly two large panels: dark source, paper destination.
  outSvg+=rect(130,333,630,460,c.radius,p.dark)+rect(1100,333,690,460,c.radius,p.paper,p.edge,c.border);
  outSvg+=icon('doc',170,366,74,p.accent,c)+text('提示词原文',265,422,c.node,p.paper,700);
  outSvg+=text('HUMAN 3.0',185,509,c.node,p.paper,600)+text('结构化自我探索提示词',185,574,c.support,p.paper)+line(185,620,680,620,p.line,c.border)+line(185,654,605,654,p.line,c.border);
  outSvg+=text('原文保留',185,749,c.support,p.accent,600);
  outSvg+=text('AI 对话',1150,422,c.node,p.text,700);
  outSvg+=rect(1150,470,590,182,18,p.background,p.edge,c.border);
  if(s.pasted){outSvg+=text('HUMAN 3.0 提示词',1184,535,c.support,p.text,600)+text('已粘贴到输入区',1184,594,c.support,p.muted);}
  else if(s.inputPlaceholderVisible)outSvg+=text('等待粘贴提示词…',1184,561,c.support,p.muted);
  outSvg+=rect(1555,688,185,70,22,s.pasted?p.dark:p.soft)+text(s.sent?'已发送':'发送',1647,736,c.support,s.pasted?p.paper:p.muted,600,'middle');
  outSvg+=text(s.status,1150,747,c.support,s.received?p.ink:p.muted,600);
  // Keep the 126×160 copy below the AI title and entirely within the input
  // well at arrival; the shallow lower arc also clears the status/button row.
  const ps=[[710,560],[870,620],[1045,620],[1435,560]];
  if(s.copy>0&&s.transfer.progress<1)outSvg+=curve(ps,p.edge,c,'stroke-dasharray="9 12"');
  if(s.transfer.progress>0&&s.transfer.progress<1){const pt=along(ps,s.transfer.progress);outSvg+=group(rect(pt.x-63,pt.y-80,126,160,13,p.paper,p.line,c.border)+icon('doc',pt.x-43,pt.y-64,82,p.ink,c)+text('副本',pt.x,pt.y+61,c.support,p.ink,600,'middle'));}
  if(s.copy>0&&s.transfer.progress===0)outSvg+=group(text('复制',818,650,c.support,p.muted,600,'middle'),s.copy);
  if(s.received)outSvg+=text('收到之后，再开始访谈',960,866,c.support,p.muted,500,'middle');
  return outSvg;
}
function c05(s,c) {
  const p=c.palette;let outSvg=heading('先了解，再一层层追问',c,'访谈示意 · 非真实聊天记录 · 非专业诊断');
  outSvg+=text('四个方面',148,341,c.node,p.text,700);
  quadNames.forEach((name,i)=>{
    const y=394+i*112;outSvg+=line(148,y+78,490,y+78,p.paperLine,c.border)+icon(quadIcons[i],144,y-15,60,p.line,c)+text(name,220,y+26,c.node,p.text,600)+text(i===0&&s.t>=2.3667?'示例追问':'待了解',360,y+24,c.support,p.muted);
  });
  const content=['最近一次卡住，发生了什么？','想换方向，却总停在准备阶段。','那次最具体的顾虑是什么？','怕选错，也不知道先做哪一步。'];
  s.messages.forEach((q,i)=>{
    const y=310+i*118,answer=i%2===1,x=answer?720:585,w=answer?1070:1100;
    if(q.typing)outSvg+=group(rect(x,y,w,91,24,p.soft)+text(answer?'正在回想具体经历…':'正在组织下一个问题…',x+30,y+58,c.support,p.muted),.72);
    outSvg+=group(rect(x,y,w,91,24,answer?'#F4E7DA':p.paper,p.edge,c.border)+text(answer?'回答':'AI',x+24,y+56,c.support,p.muted,600)+text(content[i],x+122,y+57,c.node-6,p.text,500),q.visible,`translate(0 ${n(c.rise*(1-q.visible))})`);
  });
  const ex=s.extract;
  if(ex>0){
    outSvg+=rect(833,680,140,53,12,'none',p.accent,c.connection);
    outSvg+=rect(711,812,1079,62,18,p.soft)+text('待验证卡点',740,855,c.support,p.muted,600);
    if(s.extractionArrived)outSvg+=text('选择风险 · 下一步不清楚',980,855,c.support,p.text,600);
    else {const ps=[[903,728],[965,794],[1090,782],[1225,839]],pt=along(ps,ex);outSvg+=curve(ps,p.edge,c)+rect(pt.x-85,pt.y-27,170,54,15,p.paper,p.line,c.border)+text('怕选错',pt.x,pt.y+11,c.support,p.text,600,'middle');}
  }
  return outSvg;
}
function c06(s,c) {
  const p=c.palette;let outSvg=heading('依据回答，组装成长指南',c);
  outSvg+=rect(570,294,1150,540,c.radius,p.paper,p.edge,c.border)+text('成长指南',630,368,c.node,p.text,700)+text('示意结构',1640,365,c.support,p.muted,500,'end');
  const ys=[454,598,742],src=['事实','约束','意愿'],values=['事实与习惯','限制与反复模式','可尝试的具体动作'];
  outSvg+=text('你的具体回答',150,355,c.node,p.text,600);
  s.fields.forEach((q,i)=>{
    outSvg+=chip(src[i],155,ys[i]-38,245,88,c,p.soft);
    const ps=[[400,ys[i]],[470,ys[i]],[490,ys[i]],[615,ys[i]]];
    if(q.progress>0&&!q.arrived){outSvg+=curve(ps,p.edge,c);const pt=along(ps,q.progress);outSvg+=rect(pt.x-33,pt.y-21,66,42,11,p.accent);}
    outSvg+=line(630,ys[i]-53,1660,ys[i]-53,p.paperLine,c.border);
    outSvg+=group(text(q.id,635,ys[i]+11,c.node,p.text,600)+text(values[i],1085,ys[i]+8,c.support,p.muted),q.arrived?1:0);
  });
  outSvg+=text('内容取决于你的回答，行动建议仅供参考',960,868,c.support,p.muted,500,'middle');
  return outSvg;
}
function c07(s,c) {
  const p=c.palette;let outSvg=heading('重新理解迷茫',c,'一种自我反思的视角');
  const baseY=507,slotX=1000,a=s.archive;
  outSvg+=text('缺少',620,baseY,c.title,p.text,700);
  // The old word and the strike are independent siblings. Both are archived by
  // explicit geometry; the strike is never hidden by an old-word opacity parent.
  const ox=slotX,oy=lerp(baseY,704,a),oldSize=lerp(c.title,c.support,a);
  outSvg+=text('答案',ox,oy,oldSize,p.muted,600);
  const oldW=oldSize*2;
  if(s.strike>0)outSvg+=line(ox-8,oy-oldSize*.36,ox-8+(oldW+16)*s.strike,oy-oldSize*.36,'#E09778',6);
  outSvg+=group(text('先前的判断',720,704,c.support,p.muted),a);
  outSvg+=group(text('系统提问',slotX,baseY+c.rise*(1-s.replacement),c.title,p.accent,700),s.replacement);
  outSvg+=group(text('跟着问题，梳理想法与卡点',960,851,c.node,p.text,500,'middle'),progress(s.t,3.1,c.entry));
  return outSvg;
}
function c08(s,c) {
  const p=c.palette;let outSvg=heading('你想先从哪里开始？',c,'四个平等方向，聊聊最想改变的一项');
  const boxes=[[250,335,665,178],[1005,335,665,178],[250,581,665,178],[1005,581,665,178]];
  boxes.forEach(([x,y,w,h],i)=>{outSvg+=group(rect(x,y,w,h,c.radius,p.paper,p.edge,c.border)+icon(quadIcons[i],x+35,y+40,90,p.line,c)+text(quadNames[i],x+157,y+83,c.node,p.text,700)+text(quadDescriptions[i],x+157,y+137,c.support,p.muted),s.focus.weights[i]);});
  if(s.focus.ring>0){let i=Math.min(3,Math.max(0,Math.floor((s.t-1.6667)/.65))),b=boxes[i];if(i>0){const q=progress(s.t,1.6667+i*.65,.18,smooth);b=boxes[i-1].map((v,k)=>lerp(v,boxes[i][k],q));}outSvg+=group(rect(b[0]-7,b[1]-7,b[2]+14,b[3]+14,c.radius+6,'none',p.accent,4),s.focus.ring);}
  if(s.cta)outSvg+=group(text(s.cta,960,860,c.node,p.text,600,'middle'),s.ctaReveal);
  return outSvg;
}
const renderers={C01:c01,C02:c02,C03:c03,C04:c04,C05:c05,C06:c06,C07:c07,C08:c08};
export function renderCard(id,t,duration,defaults={}) {
  const s=cardState(id,t,duration,defaults),c=s.config,p=c.palette;
  const [x0,y0,x1,y1]=c.contentSafe;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1080" viewBox="0 0 1920 1080" role="img" aria-label="${esc(s.id)}" style="font-family:'${esc(c.family)}',sans-serif"><defs><clipPath id="semantic-safe-${s.id}"><rect x="${x0}" y="${y0}" width="${x1-x0}" height="${y1-y0}"/></clipPath></defs><rect width="1920" height="1080" fill="${p.background}"/><g clip-path="url(#semantic-safe-${s.id})">${renderers[s.id](s,c)}</g></svg>`;
}
