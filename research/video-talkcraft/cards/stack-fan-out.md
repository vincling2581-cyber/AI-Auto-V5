# 卡堆扇形展开 · stack-fan-out

类别：素材呈现；研究用途：信息卡主体；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

少量图片来自同一明确集合，要先建立“一叠”再展开让成员可逐项辨认。

语义关系：集合拆分为成员、从汇总到可逐项阅读

## 避免误用

几张毫不相关的图，或把完整插画序列扇开飞动来替代叙事镜头。

## 可见过程

1. 微错位卡堆先出现，透露多张身份
2. 各卡沿共同弧心同时扇开
3. 扇形态停一拍，确认成员数量
4. 卡片旋转归零并缩为等距横排
5. 整排保持供说明后共同退场

配音落点：扇开对齐“收集了这些”，铺平承接“分别来看”，成员介绍从铺平后开始并按字数延长保持。

## 关键限制与适配

- 改srcs数量不会改变卡数，TSX由CONFIG.n决定；HTML还需同步DOM卡片数量。
- 扇开到铺平无停顿会把集合展开与整理两种意思合成乱飞，不能只压缩时长提速。
- 铺平后卡宽较小不适合密集截图正文，必要时另作证据定位而非声称已读清所有图。

V5 适配提示：仅在卡内展开真实图片或证据集合，保留两段中间状态与阅读；叙事插画本体仍满幅静态硬切。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 110 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/stack-fan-out.tsx#L110)：TSX以共同半径求扇形位置，同时配各卡旋转；铺平是另一独立目标态。
  对照字串：`const s1 = { x: Math.sin(a) * C.R`
- [html 第 88 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/stack-fan-out/index.html#L88)：HTML铺平时把卡统一缩到同宽、旋转归零并等距，和扇开动作分开排程。
  对照字串：`scale: C.flatW / cardW,`

## 演示与来源

![上游演示三个取样状态](../previews/stack-fan-out.jpg)

[本地静音 HTML 演示](../upstream/demos/stack-fan-out/index.html?embed=1) · [完整配方](../upstream/references/cards/stack-fan-out.md) · [TSX](../upstream/template/cards/stack-fan-out.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
