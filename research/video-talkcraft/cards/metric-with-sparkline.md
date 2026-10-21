# 数字带趋势 · metric-with-sparkline

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一个已核验指标既有确切终值又有同口径时间序列，需要同时交代大小和变化方向。

语义关系：指标与趋势合成、过程到结论

## 避免误用

只有孤立百分比却没有趋势数据，或用随意坐标造一条线来暗示未经证实的增长。

## 可见过程

1. 指标标签先出现
2. 数字计数与折线同刻启动
3. 数据点随线端逐个出现，折线先完成
4. 数字落定后单位和方向箭头出现
5. 指标与趋势一起静止供复述

配音落点：标签对齐对象，计数与折线跟变化描述，终值落定对齐报数；方向标记要与真实升降一致。

## 关键限制与适配

- 曲线点位是SVG坐标而非原始数据，需补时间、单位及可追溯换算，不能凭形状声称趋势成立。
- 点出现时刻依弧长与特定缓动反函数，换线型或缓动须一起重算。
- 将单位延后是演示修辞，不能因此隐去数量单位、统计期间等阅读必需信息。

V5 适配提示：接入本集真实终值和时间序列，核验口径与箭头；卡层过程和保持按讲述重排，数字不常驻漂移。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 109 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/metric-with-sparkline.tsx#L109)：TSX单位和箭头显现起点直接取计数结束，和大数字并非同时入场。
  对照字串：`const landAt = CONFIG.countAt + CONFIG.countDur;`
- [html 第 201 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/metric-with-sparkline/index.html#L201)：HTML按累计弧长比例反解时间来安排数据点，避免均分时间导致点线脱节。
  对照字串：`CONFIG.lineDur * invPower1InOut(cum[i] / acc)`

## 演示与来源

![上游演示三个取样状态](../previews/metric-with-sparkline.jpg)

[本地静音 HTML 演示](../upstream/demos/metric-with-sparkline/index.html?embed=1) · [完整配方](../upstream/references/cards/metric-with-sparkline.md) · [TSX](../upstream/template/cards/metric-with-sparkline.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
