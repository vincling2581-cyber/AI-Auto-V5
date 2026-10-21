# 后拉冷却转场 · pullback-cool-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

信息段落需要明确降速和退一步思考，且不在知识继续密集推进的位置时。

语义关系：激烈论述到沉淀收束、旧内容退场到新内容出现

## 避免误用

需要连续推理的新步骤，或 V5 静态插画之间的常规切换时。

## 可见过程

1. 旧画面先收住镜头尺度
2. 旧内容本身压暗失焦
3. 新画面从较小尺度交叠出现
4. 新画面缓慢到工作尺度后进入下一段

配音落点：上一段讲完留出呼吸，再以“回过来看”之类真实转折接新信息。

## 关键限制与适配

- 名称叫后拉，但入场尺度从 0.90 到 0.99 实际在放大，不应描述成实拍后退镜头。
- 沉暗施加在内容层，若只整体淡出会丢掉主体退场层级。
- 小于一的尺度会漏画幅，需有足够扩边；全片唯一规则只是上游偏好。

V5 适配提示：仅研究卡片段落冷却的时序，是否采用需本集授权和适配；插画仍静态硬切，不采用强制慢漂、唯一尺度或固定交叠时长。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 85 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/pullback-cool-transition.tsx#L85)：入场从较小尺度逐步放大到落点，源码不等于实拍后拉。
  对照字串：`lerp(P.inScale, P.inSettle`
- [html 第 83 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/pullback-cool-transition/index.html#L83)：退场首先削弱内部内容，整镜交叠另由镜头层处理。
  对照字串：`tl.to(outBig, { opacity: P.outDim`

## 演示与来源

![上游演示三个取样状态](../previews/pullback-cool-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/pullback-cool-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/pullback-cool-transition.md) · [TSX](../upstream/template/cards/pullback-cool-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
