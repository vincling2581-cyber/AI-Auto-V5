# 人后大字视差 · behind-text-title

类别：人物互动；研究用途：人物出镜互动；输入：人(必需), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有真实抠像主持人且开场只需一个题眼，标题与人形成可读遮挡时。

语义关系：人物遮挡标题、主题揭示

## 避免误用

无主持人的连环插画，或标题字少到遮挡后无法辨认的场面。

## 可见过程

1. 大字先在人物后方隐藏
2. 标题上升、显现且字距收紧
3. 副标稍晚落定
4. 标题与人物缓慢反向横移以维持前后层次

配音落点：标题升起对齐主题第一次被说出的词组，副标跟随限定条件，不把呼吸漂移当知识过程。

## 关键限制与适配

- 缺少透明通道人像或遮挡量不足时只剩普通叠字；遮挡过多又会伤及题眼可读性。
- HTML持续往返漂移，TSX只有95帧，不能据此认为已覆盖完整8秒周期。
- 漂移必须产生相对位移，搬到V5插画会直接违反静态插画约束。

V5 适配提示：仅作未来真实主持人合成的条件候选；当前插画层禁止移植人物与标题视差，也不复制栏目字幕。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 103 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/behind-text-title.tsx#L103)：TSX从标题落定后计算慢漂移，并非独立的镜头录像运动。
  对照字串：`const drift = CONFIG.driftPx * sineInOut`
- [html 第 95 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/behind-text-title/index.html#L95)：HTML重播将主持人横向位置清零，随后与标题分层做相对运动。
  对照字串：`gsap.set(host, { x: 0 });`

## 演示与来源

![上游演示三个取样状态](../previews/behind-text-title.jpg)

[本地静音 HTML 演示](../upstream/demos/behind-text-title/index.html?embed=1) · [完整配方](../upstream/references/cards/behind-text-title.md) · [TSX](../upstream/template/cards/behind-text-title.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
