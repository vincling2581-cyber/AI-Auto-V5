# 划线纠错替换 · strike-and-replace

类别：强调标注；研究用途：卡内强调标注；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一句话中只有一个旧数值、旧参数或旧理解需要被明确否定并改成新值，其他句干应保持稳定时。

语义关系：旧值否定、同位更正

## 避免误用

两个同时有效的指标或无证据的新旧说法不应划除；必须保留的历史原文与纠错依据不能用动画抹掉。

## 可见过程

1. 旧值在句子固定槽位中可读
2. 强调色横线从左快速划过旧值
3. 短间隔后旧值退去，新值从同一位置升入
4. 新值和句干保持供确认

配音落点：划线对齐口播否定旧值的含义，新值升入对齐正确值起音；两值仍属同一指标，不能将单位变化藏进替换。

## 关键限制与适配

- keepStrike 虽为 true，划线是旧值子节点，父层 opacity 归零后仍会消失，和文档“划线与新值同屏”不符。
- 隐形尺子按字符串长度选更长者，比例字体下字符多不一定更宽，需实测最大宽度。
- 新旧值分开排成两行会变成并列数据，失去对同一位置作更正的含义。

V5 适配提示：V5 可用于有来源的参数纠正卡，保留旧值辨认和新值确认；先决定划线应留旧值还是退出，不直接依赖 keepStrike。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 109 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/strike-and-replace.tsx#L109)：子层透明度虽保持一，仍受旧值父层透明度共同约束，不能独立常驻。
  对照字串：`const strikeOpacity = CONFIG.keepStrike ? 1 : fromOpacity`
- [html 第 90 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/strike-and-replace/index.html#L90)：HTML 用字符数量决定隐形尺子，令句干占位固定，但未比较真实渲染宽度。
  对照字串：`const longer = CONFIG.from.length >= CONFIG.to.length`

## 演示与来源

![上游演示三个取样状态](../previews/strike-and-replace.jpg)

[本地静音 HTML 演示](../upstream/demos/strike-and-replace/index.html?embed=1) · [完整配方](../upstream/references/cards/strike-and-replace.md) · [TSX](../upstream/template/cards/strike-and-replace.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
