# 并列句排版（人物在场） · parallel-items-with-host

类别：人物互动；研究用途：人物出镜互动；输入：人(必需), 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实主持人需要继续在场，同时介绍三件可明确命名的对象，能选定一种稳定版式。

语义关系：人物旁并列列举、三项累计或轮换

## 避免误用

配音插画片、无人视频，或三个对象关系其实是依赖流程却只摆成并列图。

## 可见过程

1. 主持人以对应版式保持在场
2. 第一项连大标签进入或恢复彩色
3. 第二、第三项按讲述依次出现
4. 当前版式保留成组关系或明确轮换
5. 讲完三项后一同退场

配音落点：各项起点对齐各对象首次点名，非固定0.6秒强行刷完；每镜只选一式以维持句法一致。

## 关键限制与适配

- 默认tour会连演七式，成片须选layout及durationFor，不能把样式巡演直接当一个镜头。
- CONFIG.hold未参与排程，延长保持应改per；第三项落定到退场实际约0.65秒。
- 背景轮换式带缩放交叉淡化，只能在证据素材或主持人合成条件下评估，插画禁用。

V5 适配提示：仅真实主持人任务中保留词图同属和累计原则；不接受人必须永远在场的上游要求，不移植演示式名标签。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 161 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/parallel-items-with-host.tsx#L161)：TSX退场起点由per计算而非CONFIG.hold决定，改hold不产生预期阅读延长。
  对照字串：`const t1 = CONFIG.lead, tOut = CONFIG.per - CONFIG.exit - 0.05;`
- [html 第 184 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/parallel-items-with-host/index.html#L184)：HTML依次演示七种不同列举语法，巡演顺序只是演示，不是每段口播的默认流程。
  对照字串：`const PRESETS = ["p-head", "p-band", "p-side", "p-stack", "p-strip", "p-diag", "p-swap"];`

## 演示与来源

![上游演示三个取样状态](../previews/parallel-items-with-host.jpg)

[本地静音 HTML 演示](../upstream/demos/parallel-items-with-host/index.html?embed=1) · [完整配方](../upstream/references/cards/parallel-items-with-host.md) · [TSX](../upstream/template/cards/parallel-items-with-host.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
