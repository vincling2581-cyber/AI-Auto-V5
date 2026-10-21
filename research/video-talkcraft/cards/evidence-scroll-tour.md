# 证据长页慢滚 · evidence-scroll-tour

类别：素材呈现；研究用途：证据与素材呈现；输入：截图, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

原始文档超过两屏，需要保留上下文连续并把关键条款带到稳定阅读位置。

语义关系：长文上下文连续、证据定位、巡览后聚焦

## 避免误用

短截图、重点本身不可辨认，或用连续滚动制造已展示全文的假象。

## 可见过程

1. 文档在页首先静置
2. 缓起后匀速浏览且预标记随页移动
3. 提前减速，把目标停到视口中线
4. 目标框轻呼吸并留足原文阅读
5. 再次加速浏览到页尾后减速停止

配音落点：匀速段对应材料背景，减速对齐“看这一条”，停点阅读覆盖原文引用和必要限定条件。

## 关键限制与适配

- TSX使用固定GEO而HTML实时量取文档；换长图须重测停点、页高及总时长。
- 停点靠页首或页尾太近时，虽然匀速距离被截零，加减速距离仍固定，可能出现超范围或反向段，须重新校核。
- 预置框与扫描过程不同，不能临时叠加划线抢夺定位注意力。

V5 适配提示：仅用于真实长图举证并保留出处；不把页面滚动或框呼吸迁移到插画层，阅读保持可超过2秒。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 149 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/evidence-scroll-tour.tsx#L149)：TSX按位移与速度排加减速时长，停点和短距离边界需随实际页面重算。
  对照字串：`const tDecel = (2 * C.decelDist) / v;`
- [html 第 153 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/evidence-scroll-tour/index.html#L153)：HTML把屏幕测量换回设计坐标再求停点，外壳缩放会参与几何换算。
  对照字串：`const sc = pr.width / page.offsetWidth;`

## 演示与来源

![上游演示三个取样状态](../previews/evidence-scroll-tour.jpg)

[本地静音 HTML 演示](../upstream/demos/evidence-scroll-tour/index.html?embed=1) · [完整配方](../upstream/references/cards/evidence-scroll-tour.md) · [TSX](../upstream/template/cards/evidence-scroll-tour.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
