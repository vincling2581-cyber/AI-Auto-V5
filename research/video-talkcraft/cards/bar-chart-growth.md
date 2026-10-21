# 柱状增长 · bar-chart-growth

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

口播概括一段连续区间的增长或下滑，观众需要先看整体斜率再记住一个结论数时。

语义关系：时序趋势、整体量级、结果归纳

## 避免误用

逐项精确比较、异常点解释或需要逐月读数时，应另用带数值的图表，不能只留下趋势外形。

## 可见过程

1. 标题建立话题，横向基线先画出
2. 同色柱从底部密集错峰升起
3. 最后一根到顶后结论胶囊出现
4. 柱、坐标与结论共同静置

配音落点：把整组升起对齐“这几个月持续增长”，把结论胶囊对齐总增幅；结论应在数据形状完成后出现。

## 关键限制与适配

- 柱顶补满数字或独立高亮某柱，会把整体趋势变成逐项点名。
- 结论位置必须由最高柱高度计算；换数据仍用固定落点会压住柱顶。
- BARS 与月份为源码常量，替换后须同步量程和标签，不能只改胶囊百分数。

V5 适配提示：可作 V5 趋势信息卡，按真实数据重建柱高与固定量程，保留完整升起和阅读保持，不套插画两秒限制。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 119 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/bar-chart-growth.tsx#L119)：用末柱起点加生长时长推导结论出现时刻，保证先数据后判断。
  对照字串：`const lastTop = CONFIG.barsAt`
- [html 第 155 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/bar-chart-growth/index.html#L155)：运行时从真实最高柱计算结论位置，柱体以 scaleY 从基线上升。
  对照字串：`chip.style.bottom = (maxH + CONFIG.chipGap)`

## 演示与来源

![上游演示三个取样状态](../previews/bar-chart-growth.jpg)

[本地静音 HTML 演示](../upstream/demos/bar-chart-growth/index.html?embed=1) · [完整配方](../upstream/references/cards/bar-chart-growth.md) · [TSX](../upstream/template/cards/bar-chart-growth.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
