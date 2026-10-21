# 手绘圈注箭头 · scribble-annotation

类别：强调标注；研究用途：卡内强调标注；输入：截图, 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

截图或图表上已经存在具体目标，需要按口播依次指出价格、限定条款或按钮位置时。

语义关系：位置指认、逐处圈注

## 避免误用

没有确切目标或想凭空增加解释时不宜画圈；圈注并不验证截图内容，静态叙事插画也不得靠描线变成动态图。

## 可见过程

1. 原素材先完整可见
2. 歪斜马克笔圈按一笔描出第一个目标
3. 短暂停顿后下划线描出第二处
4. 箭杆与箭头须分两笔指出操作位置，墨迹保持

配音落点：每笔起点对齐“看这个价格、再看这行条件、点这里”的具体指认，笔间留观看目标的时间。

## 关键限制与适配

- HTML 按字形墨迹盒取位置，TSX 的 STROKES 却是示例实测死值，换素材必须重算。
- 文本行盒包含上下留白，直接拿行盒画圈会把线放在字上方。
- 手绘感来自确定路径与起收节奏，画完继续抖动只会损害证据可读性。

V5 适配提示：V5 可用于界面或证据卡的精确标注；绑定真实目标坐标，保留限定条款与原截图，不把圈注当成语义展开的全部。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 101 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/scribble-annotation.tsx#L101)：TSX 按固化路径表逐笔计算 dashoffset，坐标并不会随文案自动更新。
  对照字串：`{STROKES.map((s, i) => (`
- [html 第 207 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/scribble-annotation/index.html#L207)：HTML 圆圈从目标的墨迹盒生成，箭头另采用先杆后头的笔顺。
  对照字串：`circlePath(inkBoxOf(el), m)`

## 演示与来源

![上游演示三个取样状态](../previews/scribble-annotation.jpg)

[本地静音 HTML 演示](../upstream/demos/scribble-annotation/index.html?embed=1) · [完整配方](../upstream/references/cards/scribble-annotation.md) · [TSX](../upstream/template/cards/scribble-annotation.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
