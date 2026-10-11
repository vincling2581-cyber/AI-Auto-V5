/* C04/C05: episode-local deterministic scenes. All motion depends only on t. */
(function () {
  'use strict';
  const C = { dark:'#14271B', edge:'#31533B', paper:'#F0F3EC', ink:'#173523', accent:'#78EFA2', muted:'#A9BCAB', paperMuted:'#5D7463' };
  const lerp = (a,b,p) => a+(b-a)*p;
  const fade = (t,a,b) => H.phase(t,a,b-a);
  const rect = (x,y,w,h,fill,stroke='none',r=16) => H.box(x,y,w,h,fill,stroke,r);
  const txt = (s,x,y,size=36,color=C.paper,bold=false,anchor='start') => H.text(s,x,y,size,color,bold,anchor);
  const wrap = (s,x=0,y=0,o=1) => H.group(s,x,y,o,1);
  const cycle = (t,start,period) => Math.max(0,t-start)%period/period;
  const plainLine = (d,color,width=3,dash='') => H.mark('raw_path',`<path d="${d}" fill="none" stroke="${color}" stroke-width="${width}" stroke-linecap="round" stroke-linejoin="round"${dash?` stroke-dasharray="${dash}"`:''}/>`);
  const circle = (x,y,r,fill,stroke='none',width=3) => H.mark('raw_circle',`<circle cx="${x}" cy="${y}" r="${r}" fill="${fill}" stroke="${stroke}" stroke-width="${width}"/>`);

  function modelFile(letter,dy=0,dx=0,opacity=1) {
    return wrap(rect(210,489,116,94,C.paper,'none',12)
      +plainLine('M233 518H292M233 539H276',C.paperMuted,5)
      +txt(letter,310,569,34,C.ink,true,'end'),dx,dy,opacity);
  }

  function C04(t) {
    const download = H.ease(t,0.18,1.42);
    const runtime = H.phase(t,1.55,1.00);
    const browser = H.phase(t,2.65,1.00);
    const sever = H.ease(t,4.55,1.10);
    const localOnly = H.phase(t,5.65,0.40);
    const platforms = H.ease(t,7.10,0.65);
    const changeModel = H.ease(t,8.15,0.80);
    const firstLink = 'M400 547H463';
    const secondLink = 'M735 547H795';
    const localLoop = 'M600 676V710Q600 733 623 733H927Q951 733 951 710V676';
    let s = rect(90,280,1060,630,C.dark,C.edge,28)
      +rect(1190,280,640,630,C.paper,'none',28)
      +txt('模型下载后，在本机运行',137,335,42,C.paper,true)
      +txt('文件 → 推理 → 对话',139,379,34,C.muted)
      +rect(140,411,260,265,'#1C3525',C.edge,22)
      +rect(463,411,272,265,'#1C3525',runtime>=1?C.accent:C.edge,22)
      +rect(795,411,310,265,'#1C3525',browser>=1?C.accent:C.edge,22);
    s += txt(download<1?'下载模型':'本地模型',270,458,38,C.paper,true,'middle')
      +plainLine('M194 568V597H342V568',C.muted,5)
      +plainLine('M206 608H330',C.edge,5)
      +H.line('M206 608H330',C.accent,5,download)
      +modelFile('A',-67*(1-download),45*changeModel,1-changeModel)
      +modelFile('B',0,-45*(1-changeModel),changeModel)
      +txt(changeModel>0.7?'已下载模型 B':download<1?'正在下载':'文件就绪',270,648,34,C.paper,false,'middle');
    s += txt('Ollama',600,458,40,C.paper,true,'middle')
      +circle(600,535,57,'#14271B',runtime>=1?C.accent:C.edge,4)
      +circle(600,535,43,'none',C.edge,2)
      +txt('推理',600,548,36,C.paper,true,'middle')
      +txt('本地运行时',600,648,34,C.paper,false,'middle');
    s += txt('Open WebUI',950,458,36,C.paper,true,'middle')
      +rect(834,487,230,111,C.paper,'none',12)
      +rect(850,505,115,28,'#D1DCCD','none',7)
      +rect(900,551,146*H.phase(t,3.65,0.4),29,'#ACDDB7','none',7)
      +plainLine('M866 519H938',C.paperMuted,4)
      +txt('浏览器交互',950,648,34,C.paper,false,'middle');
    s += H.line(firstLink,C.accent,5,runtime)
      +H.line(secondLink,C.accent,5,browser)
      +wrap(plainLine('M452 538L462 547L452 556',C.accent,4),0,0,runtime)
      +wrap(plainLine('M783 538L793 547L783 556',C.accent,4),0,0,browser);
    if (t>=1.55 && t<3.0) s += H.dot(firstLink,H.phase(t,1.55,1.0),10,C.accent);
    if (t>=2.65 && t<4.25) s += H.dot(secondLink,H.phase(t,2.65,1.0),10,C.accent);
    s += H.line(localLoop,C.accent,4,H.phase(t,3.55,0.85));
    if (t>=3.9) {
      s += H.dot(localLoop,cycle(t,3.9,1.65),10,C.accent);
      const reply = cycle(t,3.9,1.65);
      s += rect(850,550,34+58*reply,8,C.ink,'none',4);
    }
    // External wire physically separates; the local circuit above never disconnects.
    const netOpacity = H.phase(t,4.00,0.45);
    const externalRight = `M${430+19*sever} 806H447Q465 806 465 788V712Q465 687 490 687H600V676`;
    const external = plainLine(`M369 806H${430-19*sever}`,sever>0.95?C.paperMuted:C.muted,4)
      +plainLine(externalRight,sever>0.95?C.paperMuted:C.muted,4)
      +rect(425-19*sever,797,9,18,C.paper,'none',2)
      +rect(432+19*sever,797,9,18,C.paper,'none',2)
      +rect(139,771,230,70,sever>0.95?'#27392E':'#1C3525',C.edge,18)
      +txt(sever>0.95?'外网断开':'外网连接',254,817,36,C.paper,true,'middle');
    s += wrap(external,0,0,netOpacity)
      +wrap(rect(665,772,391,68,C.paper,'none',18)
      +txt('本地对话继续',860,817,40,C.ink,true,'middle'),0,10*(1-localOnly),localOnly)
      +txt('本地流程示意',140,880,34,C.muted);
    // Official screenshot is explicitly separated from the offline diagram.
    s += txt('Open WebUI',1230,337,42,C.ink,true)
      +txt('官方界面示例',1230,381,34,C.paperMuted)
      +rect(1225,404,570,318,'#E1E7DD','#C7D3C3',14)
      +H.img('official/webui_demo.png',1235,414,550,298,'xMidYMid meet')
      +txt('示例画面含外部 API',1230,760,34,C.ink)
      +txt('离线需选择本地模型',1230,804,34,C.ink);
    s += wrap(rect(1228,830,190,53,'#DEE8D9','none',13)
      +txt('Windows',1323,868,34,C.ink,false,'middle')
      +rect(1430,830,171,53,'#DEE8D9','none',13)
      +txt('macOS',1515,868,34,C.ink,false,'middle')
      +rect(1613,830,170,53,'#DEE8D9','none',13)
      +txt('Linux',1698,868,34,C.ink,false,'middle'),0,15*(1-platforms),platforms);
    return s;
  }

  function metric(label,value,x,y,w,h,emphasis) {
    return rect(x,y,w,h,emphasis?'#DDEBDD':'#E4E8E0','#C8D4C4',14)
      +txt(label,x+20,y+43,34,C.paperMuted)
      +txt(value,x+20,y+h-19,54,C.ink,emphasis);
  }

  function C05(t) {
    const headline = H.ease(t,0.45,0.90);
    const m1 = H.ease(t,0.75,1.20);
    const m3up = H.ease(t,0.55,0.80);
    const m3across = H.ease(t,1.35,0.90);
    const m2across = H.ease(t,2.25,0.65);
    const align = H.ease(t,2.90,0.58);
    const emphasis = H.ease(t,3.05,0.45);
    const star = t>=3.6 && t<6.15;
    const example = H.ease(t,6.15,0.85);
    const ruleOpacity = H.phase(t,0.35,0.35)*(1-H.phase(t,3.35,0.35));
    let s = rect(90,280,1040,630,C.dark,C.edge,28)
      +rect(1165,280,665,630,C.paper,'none',28)
      +txt('同一界面，重排结构',135,338,42,C.paper,true)
      +txt(t<3.48?'移动位置 → 对齐 → 建立层级':'位置、间距与层级已统一',136,382,34,C.muted)
      +rect(135,404,950,434,C.paper,'none',22);
    let guides = '';
    for (const x of [180,462,744,1000]) guides += plainLine(`M${x} 431V816`,'#82AB87',2,'7 8');
    for (const y of [554,698,744]) guides += plainLine(`M162 ${y}H1041`,'#82AB87',2,'7 8');
    s += wrap(guides,0,0,ruleOpacity);
    s += txt('项目概览',lerp(200,180,headline),lerp(489,466,headline),lerp(39,52,headline),C.ink,headline>.5)
      +txt('本周进展',lerp(193,180,headline),lerp(531,515,headline),34,C.paperMuted);
    s += wrap(rect(880,432,153,53,'#D5E5D0','none',13)
      +txt('进行中',897,470,34,C.ink),0,0,align);
    // Three persistent metric objects take separate lanes, avoiding crossing through each other.
    s += metric('项目','12',lerp(175,180,m1),lerp(558,554,m1),lerp(220,256,m1),lerp(128,144,m1),emphasis>.5);
    const thirdX = lerp(457,744,m3across);
    const thirdY = lerp(lerp(678,572,m3up),554,align);
    s += metric('完成','8',thirdX,thirdY,lerp(235,256,align),lerp(130,144,align),emphasis>.5);
    const secondX = lerp(748,462,m2across);
    const secondY = lerp(425,554,align);
    s += metric('任务','36',secondX,secondY,lerp(250,256,align),lerp(120,144,align),emphasis>.5);
    const button = H.ease(t,0.45,0.70);
    s += rect(lerp(731,782,button),lerp(712,747,button),246,65,C.ink,'none',14)
      +txt('打开项目',lerp(854,905,button),lerp(756,791,button),36,C.paper,true,'middle')
      +wrap(txt('统一栅格',180,784,34,C.paperMuted),0,0,align);
    s += txt(t<3.48?'同一组元素持续移动':'元素身份保留，结构变清楚',136,880,34,C.muted);
    s += txt('Impeccable',1208,338,42,C.ink,true);
    if (t<3.6) {
      s += txt('设计语言进入工作流',1208,384,34,C.paperMuted);
      const rows = [ ['排版层级',0.45], ['对齐与间距',1.35], ['可读性检查',2.55] ];
      rows.forEach(([label,start],i) => {
        const p=H.ease(t,start,0.65), y=465+i*114;
        s += rect(1206,y-46,578,88,'#E1E9DD','none',18)
          +txt(label,1235,y+10,42,C.ink,true)
          +wrap(plainLine(`M1700 ${y-2}L1714 ${y+12}L1741 ${y-19}`,C.ink,5),0,0,p);
      });
    } else if (star) {
      s += txt('GitHub Stars',1208,423,36,C.paperMuted)
        +rect(1206,458,578,173,'#DDE9D7','none',22)
        +txt('★ 约7.85万',1495,566,66,C.ink,true,'middle')
        +txt('核查快照 · 非75万',1495,698,42,C.ink,true,'middle')
        +txt('以核查时页面显示为准',1495,772,34,C.paperMuted,false,'middle');
    } else {
      // Reveal the verified official case, not a fabricated live run.
      s += txt('官方案例',1208,384,36,C.paperMuted)
        +rect(1206,414,578,363,'#DEE6D9','#C7D3C3',15)
        +`<defs><clipPath id="c05-official-case"><rect x="1213" y="421" width="${564*example}" height="349" rx="9"/></clipPath></defs>`
        +`<g clip-path="url(#c05-official-case)">${H.img('official/impeccable_case.png',1213,421,564,349,'xMidYMid meet')}</g>`
        +txt('Neo Mirai · 页面设计',1208,830,36,C.ink,true)
        +txt('官方案例展示',1208,880,34,C.paperMuted);
    }
    return s;
  }

  window.SCENES = { ...(window.SCENES || {}), C04, C05 };
})();
