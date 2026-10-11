/* New-episode C02/C03 only. Local time is seconds; no wall clock or randomness.
 * C02: 0.35 goal -> 1.15 parallel dispatch -> 3.25 execution -> 4.65 returns
 *      -> 6.75 progress -> 8.45 budget constraint -> 10.55 official UI -> 12.55 inspection.
 * C03: 0.25 context -> 1.45 store copies -> 3.20 stored -> 4.35 query routes
 *      -> 6.15 candidates -> 7.80 selection -> 9.45 retrieval -> 11.10 reuse
 *      -> 12.85 integration -> 14.45 context handoff -> 16.15 received -> 17.05 boundary.
 * All illustrated relationships and counts are examples, not captured product runs.
 */
(function () {
  'use strict';
  const pathCache = new Map();
  const clamp = x => Math.max(0, Math.min(1, x));
  const lerp = (a, b, p) => a + (b - a) * p;
  const helper = () => window.H;
  const colors = H => ({dark: H.k.col('dark'), paper: H.k.col('paper'), accent: H.k.col('accent'),
    text: H.k.col('text'), ink: H.k.col('ink'), muted: H.k.col('muted'), line: H.k.col('line')});
  function point(d, progress) {
    let path = pathCache.get(d);
    if (!path) {
      path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      path.setAttribute('d', d);
      pathCache.set(d, path);
    }
    return path.getPointAtLength(path.getTotalLength() * clamp(progress));
  }
  function transfer(H, d, p, label, fill, ink, objectId) {
    if (p <= 0 || p >= 1) return '';
    const xy = point(d, p);
    return `<g data-object-id="${objectId}">` + H.box(xy.x - 36, xy.y - 26, 72, 52, fill, fill, 12)
      + H.text(label, xy.x, xy.y + 12, 34, ink, true, 'middle') + '</g>';
  }
  const idGroup = (id, body) => `<g data-object-id="${id}">${body}</g>`;
  function checked(H, x, y, p, color) {
    return H.line(`M ${x} ${y} l 13 13 l 26 -30`, color, 5, p);
  }
  function C02(t) {
    const H = helper(), C = colors(H);
    const dispatch = H.ease(t, 1.15, 1.20);
    const work = H.phase(t, 3.25, 1.35);
    const ui = H.ease(t, 10.55, 0.72);
    const uiFocus = H.ease(t, 12.55, 0.60);
    const goal = H.ease(t, 0.35, 0.55);
    const agentXs = [145, 465, 785], centers = agentXs.map(x => x + 125);
    const returnStarts = [4.65, 5.15, 5.65];
    const returns = returnStarts.map(start => H.ease(t, start, 1.10));
    const doneCount = returns.filter(p => p >= 1).length;
    let out = H.box(90, 270, 1000, 620, C.dark) + H.box(1130, 270, 700, 620, C.paper, C.paper);
    // A persistent goal fans out to equal peers. No Agent -> Agent dependency.
    const goalBody = H.box(380, 315, 420, 100, '#233E2C', '#54775E', 22)
      + H.text('一个目标', 590, 356, 34, C.muted, false, 'middle')
      + H.text('并行推进三项任务', 590, 398, 40, C.text, true, 'middle');
    out += idGroup('paperclip-goal', H.group(goalBody, 0, 16 * (1 - goal), goal));
    centers.forEach((cx, i) => {
      const d = `M 590 415 C 590 455 ${cx} 450 ${cx} 505`;
      out += H.line(d, C.line, 4, dispatch);
      out += transfer(H, d, dispatch, ['A', 'B', 'C'][i], C.accent, C.ink, `paperclip-task-${i + 1}-dispatch`);
    });
    // Return paths are below the agents, then terminate in the matching result row.
    const resultYs = [382, 492, 602];
    centers.forEach((cx, i) => {
      const railY = 702 + 28 * i;
      const destinationY = resultYs[i] + 41;
      const d = `M ${cx} 636 L ${cx} ${railY - 20} Q ${cx} ${railY} ${cx + 20} ${railY} L 1104 ${railY} Q 1147 ${railY} 1147 ${railY - 43} L 1147 ${destinationY + 20} Q 1147 ${destinationY} 1167 ${destinationY} L 1180 ${destinationY}`;
      out += H.group(H.line(d, C.accent, 4, returns[i])
        + transfer(H, d, returns[i], ['A', 'B', 'C'][i], C.accent, C.ink, `paperclip-task-${i + 1}-return`), 0, 0, 1 - ui);
    });
    agentXs.forEach((x, i) => {
      const arrived = dispatch >= 1;
      const settled = returns[i] >= 1;
      const body = H.box(x, 505, 250, 131, '#1D3426', arrived ? C.accent : C.line, 22)
        + H.text(`Agent ${['A', 'B', 'C'][i]}`, x + 125, 548, 40, C.text, true, 'middle')
        + H.text(settled ? '已回传' : (arrived ? '执行任务' : '等待派发'), x + 125, 595, 34, settled ? C.accent : C.muted, false, 'middle')
        + H.box(x + 24, 615, 202, 6, '#314D3A', 'none', 3)
        + H.box(x + 24, 615, 202 * work, 6, C.accent, 'none', 3);
      out += idGroup(`paperclip-agent-${i + 1}`, body);
    });
    let results = H.text('结果逐项回传', 1180, 337, 42, C.ink, true);
    resultYs.forEach((y, i) => {
      const received = returns[i] >= 1;
      results += idGroup(`paperclip-result-${i + 1}`, H.box(1180, y, 600, 82, received ? '#DAE9DC' : '#E2E7DF', '#C4CCC2', 18)
        + H.text(`任务 ${['A', 'B', 'C'][i]}`, 1210, y + 52, 38, C.ink, true)
        + H.text(received ? '结果已收到' : '等待接收', 1420, y + 52, 36, received ? '#23462E' : '#637166')
        + (received ? checked(H, 1710, y + 38, H.phase(t, returnStarts[i] + 1.10, 0.30), '#315B3B') : ''));
    });
    const progressReveal = H.ease(t, 6.75, 0.70);
    results += H.group(H.text('统一查看进度', 1180, 756, 38, C.ink, true)
      + H.text(`${doneCount} / 3`, 1750, 756, 42, C.ink, true, 'end')
      + H.box(1180, 790, 600, 15, '#CCD6C9', 'none', 7)
      + H.box(1180, 790, 600 * (doneCount / 3) * progressReveal, 15, '#548763', 'none', 7), 0, 0, progressReveal);
    out += H.group(results, 0, 0, 1 - ui);
    const budget = H.ease(t, 8.45, 0.80);
    out += H.group(H.box(142, 795, 895, 63, '#233E2C', '#54775E', 17)
      + H.text('进度回传', 170, 837, 34, C.text, true)
      + checked(H, 342, 824, progressReveal, C.accent)
      + H.text('预算约束', 492, 837, 34, C.text, true)
      + H.text('按配置执行', 750, 837, 34, C.accent, true), 0, 14 * (1 - budget), budget);
    // The screenshot is an official source view, not a fabricated successful run.
    const sourceView = [lerp(0, 760, uiFocus), lerp(0, 470, uiFocus), lerp(1440, 560, uiFocus), lerp(900, 350, uiFocus)];
    const shot = H.text('官方界面', 1180, 337, 42, C.ink, true)
      + H.box(1155, 368, 650, 407, '#101110', '#637166', 12)
      + `<svg x="1156" y="369" width="648" height="405" viewBox="${sourceView.join(' ')}" overflow="hidden">`
      + H.img('official/paperclip_home.png', 0, 0, 1440, 900) + '</svg>'
      + H.text(uiFocus > 0 ? '查看预算与待审批项' : '任务与运行状态总览', 1480, 843, 36, C.ink, true, 'middle');
    out += idGroup('paperclip-official-ui', H.group(shot, 12 * (1 - ui), 0, ui));
    return out;
  }

  function memoryChip(H, C, id, label, x, y, width, active = true, light = false) {
    return idGroup(id, H.box(x, y, width, 72, light ? (active ? '#D7E9D8' : '#DEE3DA') : '#294932', active ? C.accent : C.line, 15)
      + H.text(label, x + width / 2, y + 47, 34, light ? C.ink : C.text, true, 'middle'));
  }
  function C03(t) {
    const H = helper(), C = colors(H);
    const context = H.ease(t, 0.25, 0.60);
    const store = H.ease(t, 1.45, 1.35);
    const stored = H.ease(t, 3.20, 0.65);
    const query = H.ease(t, 4.35, 1.15);
    const candidates = H.ease(t, 6.15, 1.15);
    const select = H.ease(t, 7.80, 0.85);
    const retrieve = H.ease(t, 9.45, 1.20);
    const reuse = H.ease(t, 11.10, 0.65);
    const integration = H.ease(t, 12.85, 0.72);
    const handoff = H.ease(t, 14.45, 1.25);
    const received = H.ease(t, 16.15, 0.60);
    const boundary = H.ease(t, 17.05, 0.55);
    let out = H.box(90, 270, 750, 620, C.dark) + H.box(880, 270, 950, 620, C.paper, C.paper);
    // Original conversation and stored records stay visible throughout reuse.
    out += H.text('对话中的上下文', 140, 335, 42, C.text, true);
    out += H.box(140, 363, 650, 155, '#1D3426', '#54775E', 24);
    const chipXs = [158, 370, 582], labels = ['M1 偏好', 'M2 背景', 'M3 旧任务'];
    chipXs.forEach((x, i) => {
      out += H.group(memoryChip(H, C, `memory-source-M${i + 1}`, labels[i], x, 405, 188), 0, 12 * (1 - context), context);
      const d = `M ${x + 94} 477 C ${x + 94} 548 ${x + 94} 572 ${x + 94} 653`;
      out += H.line(d, C.line, 4, store);
      out += transfer(H, d, store, `M${i + 1}`, C.accent, C.ink, `memory-store-M${i + 1}`);
    });
    out += H.box(140, 582, 650, 248, '#10261A', '#54775E', 24)
      + H.text('持久记忆库', 180, 627, 42, C.text, true);
    chipXs.forEach((x, i) => {
      if (store >= 1) out += memoryChip(H, C, `memory-library-M${i + 1}`, labels[i], x, 653, 188);
    });
    out += H.group(H.text('来源保留，后续继续复用', 465, 787, 36, C.accent, true, 'middle'), 0, 0, stored);
    // Two retrieval routes are peers: neither one is a prerequisite of the other.
    let retrieval = H.text('后续对话 / 新任务', 950, 335, 42, C.ink, true)
      + H.box(1120, 365, 460, 76, '#DDE6D9', '#BACBB8', 19)
      + H.text(query > 0 ? '查询相关记忆' : '需要已有上下文', 1350, 415, 38, C.ink, true, 'middle');
    const laneXs = [945, 1405], laneCenters = [1140, 1600];
    laneXs.forEach((x, i) => {
      const d = `M 1350 441 C 1350 458 ${laneCenters[i]} 456 ${laneCenters[i]} 477`;
      retrieval += H.line(d, '#73977A', 4, query);
      retrieval += transfer(H, d, query, 'Q', '#3A6344', C.paper, `memory-query-${i}`);
      retrieval += H.box(x, 477, 390, 88, '#E2E9DE', '#B9CBB9', 18)
        + H.text(i === 0 ? '关键词检索' : '语义检索', laneCenters[i], 532, 38, C.ink, true, 'middle');
    });
    const candidateXs = [955, 1230, 1505];
    candidateXs.forEach((x, i) => {
      const origin = i === 2 ? 1600 : 1140;
      const d = `M ${origin} 565 C ${origin} 586 ${x + 112} 580 ${x + 112} 611`;
      retrieval += H.line(d, '#73977A', 4, candidates);
      retrieval += transfer(H, d, candidates, `M${i + 1}`, '#3A6344', C.paper, `memory-candidate-transfer-M${i + 1}`);
      if (candidates >= 1) {
        const muted = i === 2 && select > 0;
        retrieval += H.group(memoryChip(H, C, `memory-candidate-M${i + 1}`, labels[i], x, 611, 225, !muted, true), 0, 0, muted ? lerp(1, 0.42, select) : 1);
        if (i < 2) retrieval += checked(H, x + 172, 701, select, '#386B44');
        else retrieval += H.line(`M ${x + 78} 695 l 26 26 M ${x + 104} 695 l -26 26`, '#859184', 4, select);
      }
    });
    // Only selected M1/M2 travel into the receiving context; rejected M3 never does.
    [0, 1].forEach(i => {
      const d = `M ${candidateXs[i] + 112} 683 C ${candidateXs[i] + 112} 728 ${1280 + i * 180} 710 ${1280 + i * 180} 756`;
      retrieval += H.line(d, '#5A8962', 4, retrieve);
      retrieval += transfer(H, d, retrieve, `M${i + 1}`, '#3A6344', C.paper, `memory-retrieve-M${i + 1}`);
    });
    retrieval += H.box(1135, 751, 615, 93, '#D5E4D4', '#A9BFA7', 20);
    if (retrieve >= 1) {
      retrieval += idGroup('memory-received-context', H.text(reuse > 0 ? '复用相关上下文继续任务' : '已取回 M1 + M2', 1442, 810, 38, C.ink, true, 'middle'));
    } else {
      retrieval += H.text(select > 0 ? '筛选相关项，再取回' : '接收相关上下文', 1442, 810, 36, '#64735E', false, 'middle');
    }
    out += H.group(retrieval, 0, 0, 1 - integration);
    // Developer integration replaces the explanatory retrieval view, not the stored source.
    const apiD = 'M 790 790 C 860 790 845 582 945 582';
    const appD = 'M 1270 582 C 1350 582 1358 582 1430 582';
    let api = H.text('开发者接入应用', 950, 335, 44, C.ink, true)
      + H.text('通过接口把记忆接到任务中', 950, 404, 36, '#4F654E')
      + H.line(apiD, '#5A8962', 5, handoff)
      + H.line(appD, '#5A8962', 5, handoff)
      + H.box(945, 505, 325, 154, '#DBE7D7', '#AEC4AA', 23)
      + H.text('记忆接口', 1107, 559, 40, C.ink, true, 'middle')
      + H.text('调用 / 检索', 1107, 609, 34, '#4F654E', false, 'middle')
      + H.box(1430, 505, 345, 154, '#D5E4D4', '#AEC4AA', 23)
      + H.text('应用 / Agent', 1602, 559, 38, C.ink, true, 'middle')
      + H.text(received > 0 ? '已取得上下文' : '新任务', 1602, 609, 34, '#4F654E', false, 'middle');
    const wholeD = 'M 790 790 C 860 790 845 582 945 582 L 1430 582';
    api += '<defs><mask id="memory-front-mask" maskUnits="userSpaceOnUse" x="0" y="0" width="1920" height="1080"><rect width="1920" height="1080" fill="white"/><rect x="945" y="505" width="325" height="154" rx="23" fill="black"/><rect x="1430" y="505" width="345" height="154" rx="23" fill="black"/></mask></defs><g mask="url(#memory-front-mask)">' + transfer(H, wholeD, handoff, 'M1', '#3A6344', C.paper, 'memory-integration-copy-M1') + '</g>';
    api += H.group(H.box(945, 703, 830, 70, '#DAE8D6', '#AEC4AA', 17)
      + H.text('记忆仍在库中，任务获得副本', 1360, 750, 38, C.ink, true, 'middle'), 0, 0, received);
    api += H.group(H.text('应用接入后，用户才能在产品中使用', 1360, 836, 34, '#4F654E', false, 'middle'), 0, 0, boundary);
    out += H.group(api, 12 * (1 - integration), 0, integration);
    return out;
  }
  window.SCENES = {...(window.SCENES || {}), C02, C03};
})();
