/* C05-C09: episode-local semantic scenes. All timings derive from cards.json.
 * Documents move along the exact SVG route's arc length (CardKit.packet).
 * Sender contents remain; receiver contents are gated by endpoint arrival.
 */
(function () {
  'use strict';
  const FPS = 30;
  const frame = t => t * FPS;
  const reached = (t, end) => frame(t) + 1e-7 >= end;
  const event = (c, i) => c.process_events[i];
  const progress = (t, start, end) => H.m(t, start / FPS, (end - start) / FPS);
  const phase = (t, e) => progress(t, e.start_frame, e.end_frame_exclusive);
  function wire(d, t, start, end, ink = 'accent') {
    const k = H.k, p = progress(t, start, end);
    return k.path(d, 1, 'line', 2, true) + k.path(d, p, ink, 4);
  }
  function payload(d, t, start, end, ink = 'accent') {
    return H.k.packet(d, progress(t, start, end), ink, 13, 'doc');
  }
  const mark = (id, s) => `<g data-node="${id}">${s}</g>`;
  function receivingRow(x, y, w, title, value, arrived) {
    const k = H.k;
    return k.box(x, y, w, 102, arrived ? '#D7E7D6' : '#E4EAE1', 'none', 16)
      + k.text(title, x + 24, y + 39, 30, 'ink')
      + (arrived ? k.text(value, x + 24, y + 82, 38, 'ink', 'start', true)
        : k.path(`M${x + 24} ${y + 74}H${x + w - 28}`, 1, 'paperLine', 3, true));
  }

  window.SCENES.C05 = (t, c) => {
    const k = H.k, e1 = event(c, 0), e2 = event(c, 1);
    const coreReady = reached(t, e1.end_frame_exclusive);
    let s = k.panel(100, 302, 670, 600, 'dark') + k.panel(900, 302, 910, 600, 'paper');
    s += k.text('项目入口', 145, 369, 38, 'muted');
    s += mark('repository', H.img('02_research/official/reverse-skill.png', 148, 413, 180, 180)
      + k.text('reverse-skill', 350, 484, 44, 'text', 'start', true)
      + k.text('技能路由包', 350, 542, 34, 'muted'));
    const coreRoute = 'M440 578C440 624 425 625 425 661';
    s += wire(coreRoute, t, e1.start_frame, e1.end_frame_exclusive);
    s += mark('router', k.panel(190, 661, 470, 176, 'soft')
      + k.icon('sliders', 219, 687, 67, coreReady ? 'accent' : 'line')
      + k.text('调度核心', 314, 727, 46, 'text', 'start', true)
      + (coreReady ? k.text('识别任务，选择路线', 225, 794, 34, 'muted')
        : k.path('M226 788H607', 1, 'line', 3, true)));
    s += k.text('数十个专业技能', 945, 370, 46, 'ink', 'start', true)
      + k.text('按需选用 · 下方展示代表项', 945, 419, 34, 'ink');
    const modules = [
      {id: 'apk', title: 'APK 分析', sub: 'Android 应用', y: 451, icon: 'doc'},
      {id: 'binary', title: '二进制分析', sub: 'EXE / DLL / ELF', y: 592, icon: 'grid'},
      {id: 'javascript', title: 'JS 分析', sub: '网页脚本与请求', y: 733, icon: 'search'}
    ];
    const routes = modules.map((m, i) => ({
      ...m, start: e2.start_frame + i * 4,
      end: e2.end_frame_exclusive - (2 - i) * 6,
      d: `M660 751C818 751 825 ${m.y + 56} 1083 ${m.y + 56}`
    }));
    routes.forEach(m => { s += wire(m.d, t, m.start, m.end, '#315B3B'); });
    routes.forEach(m => {
      const ready = reached(t, m.end);
      s += mark('modules-' + m.id, k.box(1083, m.y, 670, 123, ready ? '#D7E7D6' : '#E4EAE1', 'none', 18)
        + (ready ? k.icon(m.icon, 1105, m.y + 30, 64, 'ink')
          + k.text(m.title, 1193, m.y + 56, 46, 'ink', 'start', true)
          + k.text(m.sub, 1193, m.y + 110, 34, 'ink')
          : k.path(`M1113 ${m.y + 55}H1718`, 1, 'paperLine', 3, true)));
    });
    s += payload(coreRoute, t, e1.start_frame, e1.end_frame_exclusive);
    routes.forEach(m => { s += payload(m.d, t, m.start, m.end, '#315B3B'); });
    return s;
  };

  window.SCENES.C06 = (t, c) => {
    const k = H.k;
    const inputs = [
      {id: 'structure', title: '结构分析', sub: '模块与调用', y: 324, outY: 465, icon: 'grid', tone: 'dark', value: '模块 · 调用关系'},
      {id: 'risk', title: '风险排查', sub: '定位可疑位置', y: 515, outY: 601, icon: 'search', tone: 'soft', value: '风险线索 · 待验证'},
      {id: 'evidence', title: '证据核对', sub: '检查依据与限制', y: 706, outY: 737, icon: 'check', tone: 'accent', value: '依据 · 验证状态'}
    ];
    let s = k.panel(1110, 302, 700, 600, 'paper');
    s += k.text('同一份报告', 1150, 377, 46, 'ink', 'start', true)
      + k.text('三路汇总，各自保留来源', 1150, 427, 34, 'ink');
    const routes = inputs.map((n, i) => ({...n, e: event(c, i), d: `M705 ${n.y + 80}C880 ${n.y + 80} 924 ${n.outY + 44} 1148 ${n.outY + 44}`}));
    routes.forEach(n => {s += wire(n.d, t, n.e.start_frame, n.e.end_frame_exclusive);});
    routes.forEach(n => {
      const ready = reached(t, n.e.end_frame_exclusive);
      s += mark(n.id, H.node(n.title, n.sub, 110, n.y, 595, 154, n.tone, n.icon));
      s += mark('report-' + n.id, receivingRow(1148, n.outY, 620, n.title, n.value, ready));
    });
    s += k.text('来源保持可见，结果逐项累积', 1150, 871, 32, 'ink');
    routes.forEach(n => {s += payload(n.d, t, n.e.start_frame, n.e.end_frame_exclusive);});
    return s;
  };

  window.SCENES.C07 = (t, c) => {
    const k = H.k;
    let s = k.panel(100, 311, 500, 591, 'dark') + k.panel(815, 311, 995, 591, 'paper');
    s += mark('authorized', k.icon('check', 268, 380, 155, 'accent')
      + k.text('先确认范围', 350, 586, 46, 'text', 'middle', true)
      + k.text('自有 / 明确授权', 350, 650, 34, 'muted', 'middle')
      + k.path('M169 699H531', 1, 'line', 2)
      + k.text('按约定范围开展', 350, 759, 34, 'muted', 'middle'));
    s += k.text('四类用途', 869, 374, 46, 'ink', 'start', true);
    const tasks = [
      {id:'research', title:'合法研究', sub:'理解软件机制', x:875, y:450, icon:'search', d:'M600 594C735 594 724 527 875 527'},
      {id:'audit', title:'漏洞排查', sub:'检查风险线索', x:1360, y:450, icon:'target', d:'M600 594C737 594 713 397 925 397H1515Q1555 397 1555 437V450'},
      {id:'ctf', title:'CTF 竞赛', sub:'题目与靶场范围', x:875, y:680, icon:'grid', d:'M600 594C737 594 720 757 875 757'},
      {id:'pentest', title:'授权测试', sub:'约定目标与边界', x:1360, y:680, icon:'check', d:'M600 594C750 594 722 879 925 879H1515Q1555 879 1555 850'}
    ];
    tasks.forEach((n,i) => {const e = event(c,i);s += wire(n.d,t,e.start_frame,e.end_frame_exclusive,'#315B3B');});
    tasks.forEach((n,i) => {
      const ready = reached(t,event(c,i).end_frame_exclusive);
      s += mark(n.id, k.box(n.x,n.y,390,170,ready?'#D7E7D6':'#E4EAE1','none',20)
        + (ready ? k.icon(n.icon,n.x+25,n.y+24,62,'ink')
          + k.text(n.title,n.x+108,n.y+66,46,'ink','start',true)
          + k.text(n.sub,n.x+28,n.y+129,34,'ink')
          : k.path(`M${n.x+30} ${n.y+84}H${n.x+354}`,1,'paperLine',3,true)));
    });
    tasks.forEach((n,i) => {const e=event(c,i);s += payload(n.d,t,e.start_frame,e.end_frame_exclusive,'#315B3B');});
    return s;
  };

  window.SCENES.C08 = (t, c) => {
    const k = H.k, e1=event(c,0), e2=event(c,1), p=phase(t,e1);
    let s=k.panel(100,302,970,600,'dark')+k.panel(1180,302,630,600,'paper');
    s+=k.text('GitHub 官方仓库',142,368,42,'text','start',true);
    // Reframe the real, untouched screenshot. The source remains on screen.
    const vx=k.lerp(0,460,p),vy=k.lerp(0,220,p),vw=k.lerp(2880,1920,p),vh=vw*450/885;
    s+=mark('repository',`<svg x="142" y="399" width="885" height="450" viewBox="${vx} ${vy} ${vw} ${vh}" overflow="hidden">`
      +H.img('02_research/screenshots/github_repository.png',0,0,2880,1800,'none')+'</svg>'
      +k.text('来源：zhaoxuya520 / reverse-skill',142,883,32,'muted'));
    s+=k.text('先看这三项',1220,372,46,'ink','start',true);
    const r1='M1070 505C1132 505 1144 488 1218 488';
    const r2='M1070 651C1140 651 1128 661 1218 661';
    const r3='M1070 651C1150 651 1128 806 1218 806';
    s+=wire(r1,t,e1.start_frame,e1.end_frame_exclusive)
      +wire(r2,t,e2.start_frame,e2.end_frame_exclusive)
      +wire(r3,t,e2.start_frame,e2.end_frame_exclusive);
    const ready1=reached(t,e1.end_frame_exclusive),ready2=reached(t,e2.end_frame_exclusive);
    s+=mark('readme',k.box(1218,423,548,135,ready1?'#D7E7D6':'#E4EAE1','none',18)
      +(ready1?k.text('reverse-skill',1245,480,46,'ink','start',true)+k.text('README · 项目说明',1245,529,34,'ink')
        :k.path('M1245 490H1735',1,'paperLine',3,true)));
    s+=mark('skills',k.box(1218,601,548,125,ready2?'#D7E7D6':'#E4EAE1','none',18)
      +(ready2?k.text('技能目录',1245,653,46,'ink','start',true)+k.text('按任务选择专业方法',1245,700,34,'ink')
        :k.path('M1245 665H1735',1,'paperLine',3,true)));
    s+=mark('requirements',k.box(1218,755,548,125,ready2?'#D7E7D6':'#E4EAE1','none',18)
      +(ready2?k.text('运行条件',1245,807,46,'ink','start',true)+k.text('模型 · 工具 · 目标权限',1245,854,34,'ink')
        :k.path('M1245 819H1735',1,'paperLine',3,true)));
    s+=payload(r1,t,e1.start_frame,e1.end_frame_exclusive)
      +payload(r2,t,e2.start_frame,e2.end_frame_exclusive)
      +payload(r3,t,e2.start_frame,e2.end_frame_exclusive);
    return s;
  };

  window.SCENES.C09 = (t, c) => {
    const k=H.k,e1=event(c,0),e2=event(c,1),e3=event(c,2);
    const selectEnd=e2.start_frame+16,selected=reached(t,selectEnd);
    const routed=reached(t,e1.end_frame_exclusive),resultReady=reached(t,e2.end_frame_exclusive),humanReady=reached(t,e3.end_frame_exclusive);
    const d1='M410 574H530',d2='M870 574H990',dResult='M1019 651V676Q1019 714 1057 714H1094',d3='M1318 714C1420 714 1410 574 1490 574';
    let s=wire(d1,t,e1.start_frame,e1.end_frame_exclusive)
      +wire(d2,t,e2.start_frame,selectEnd)
      +wire(d3,t,e3.start_frame,e3.end_frame_exclusive);
    function stage(id,x,w,tone,icon,title,sub){
      const light=tone==='paper'||tone==='accent';
      return mark(id,k.panel(x,403,w,414,tone)+k.icon(icon,x+w/2-45,436,90,light?'ink':'accent')
        +k.text(title,x+w/2,582,46,light?'ink':'text','middle',true)
        +(sub?k.text(sub,x+w/2,636,34,light?'ink':'muted','middle'):''));
    }
    s+=stage('task',100,310,'dark','doc','分析任务','样本与目标');
    s+=stage('routing',530,340,'soft','sliders','任务路由','识别类型与范围');
    if(routed)s+=k.text('已接收任务',700,742,34,'muted','middle');
    s+=stage('skills',990,350,selected?'accent':'soft','grid','选择技能',selected?'匹配项已选择':'按任务匹配');
    // The second event contains a dispatch and then a result-return phase.
    s+=wire(dResult,t,selectEnd,e2.end_frame_exclusive,selected?'ink':'line');
    if(resultReady)s+=mark('result',k.box(1094,681,224,67,'paper','none',14)+k.text('分析结果',1206,727,36,'ink','middle',true));
    s+=stage('human',1490,320,'paper','person','人的判断',humanReady?'确认依据与限制':'接收后再复核');
    if(humanReady)s+=k.icon('check',1614,685,72,'ink');
    s+=payload(d1,t,e1.start_frame,e1.end_frame_exclusive)
      +payload(d2,t,e2.start_frame,selectEnd)
      +payload(dResult,t,selectEnd,e2.end_frame_exclusive,'ink')
      +payload(d3,t,e3.start_frame,e3.end_frame_exclusive);
    return s;
  };
})();
