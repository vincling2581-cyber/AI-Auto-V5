# 时间线照片带 · timeline-photo-strip

类别：素材呈现；研究用途：证据与素材呈现；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

三至五个已核实时间点有图片和日期，口播逐站解释后需要回顾整段演进。

语义关系：时间先后、逐站查看与全貌回顾

## 避免误用

三个平级案例，或把没有时间依据的材料硬排成前后因果。

## 可见过程

1. 首站居中，其余沿时间线上下交错
2. 相机横移到下一站并真实停靠
3. 当前站轻亮，其他站减弱
4. 走完后拉远恢复全部站点
5. 全貌有意停留，日期与图片共同收尾

配音落点：每站停靠覆盖日期与该阶段变化的解释，拉远对齐“回看整个过程”的综合结语。

## 关键限制与适配

- 改变hold、站数或tailHold后，相机排程会延长，但END和meta仍固定，需另重算总时长防截断。
- 文档称相机唯一transform，实际照片也会局部scale到1.03；不能据此当插画无图内运动。
- 全貌0.62倍率下日期明显变小，需检查实际输出可读性，日期存在不等于已读清。

V5 适配提示：借用真实时间结构和最后全貌保持，仅用于证据照片卡；V5插画不能横移、拉远或亮暗运动，时间关系可另做纯信息卡。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 36 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/timeline-photo-strip.tsx#L36)：TSX从目标点反解画心位置，倍率变化与停站位置共享同一坐标公式。
  对照字串：`const camTo = (z: number, px: number, py: number): Cam =>`
- [html 第 85 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/timeline-photo-strip/index.html#L85)：HTML拉远时同时把照片焦点缩放、亮度全部恢复，确有相机以外的局部transform。
  对照字串：`photos.forEach((p) => tl.to(p, { filter: "brightness(1)", scale: 1`

## 演示与来源

![上游演示三个取样状态](../previews/timeline-photo-strip.jpg)

[本地静音 HTML 演示](../upstream/demos/timeline-photo-strip/index.html?embed=1) · [完整配方](../upstream/references/cards/timeline-photo-strip.md) · [TSX](../upstream/template/cards/timeline-photo-strip.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
