# 名词解释悬浮卡 · info-term-card

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

首次提到专业名词，短释义能帮助观众继续理解且无需长篇展开时。

语义关系：首次出现的名词到简短释义、人物说明与侧边解释补充

## 避免误用

定义本身含多步因果，或释义太长需要缩字号挤进小卡时。

## 可见过程

1. 人物对侧的解释卡滑入并回稳
2. 图标、词条和短释义同卡可见
3. 短暂往返浮动保持层次
4. 讲完后原路退出

配音落点：名词首次出现时进卡，读完核心定义再收，避免重复解释。

## 关键限制与适配

- 文档称 ±6px 正弦浮动，TSX/HTML 默认实际在 0 与 +6px 间往返。
- TSX 的词条和释义在 JSX 内，hostSrc 并非文字参数接口。
- 图标也跟着摆动，可能分散定义阅读，不应把悬浮当语义过程。

V5 适配提示：采用名词到释义的层级，按本集内容决定是否需要示意关系；不强制浮动、投影或两行封顶，信息卡保持按阅读需要安排。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 114 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/info-term-card.tsx#L114)：位置由零到正幅值的 yoyo 进度控制，非对称上下正弦。
  对照字串：`const y = CONFIG.floatPx * fp;`
- [html 第 85 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/info-term-card/index.html#L85)：演示在落位后重复往返，属于装饰保持而非解释机制。
  对照字串：`yoyo: true, repeat: 3`

## 演示与来源

![上游演示三个取样状态](../previews/info-term-card.jpg)

[本地静音 HTML 演示](../upstream/demos/info-term-card/index.html?embed=1) · [完整配方](../upstream/references/cards/info-term-card.md) · [TSX](../upstream/template/cards/info-term-card.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
