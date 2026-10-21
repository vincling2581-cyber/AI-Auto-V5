# 金句大字卡 · quote-card

类别：字幕花字；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

前文已建立依据，需要让一句短结论独占阅读注意力时。

语义关系：完整论述到一句核心结论、关键词与其余句子的权重

## 避免误用

原句含许多限定条件却为了大字效果被截断，或多次替代实际讲解时。

## 可见过程

1. 实色底板先接管画面
2. 结论按行错峰进入
3. 少量关键词提高权重，出处稍后出现
4. 整句保持后底板轻量退去

配音落点：旁白完成论证后读出结论，按完整意思分行而非按固定字数切割。

## 关键限制与适配

- 半透明底板让原人物与大字争夺视线。
- TSX outAt 写死 3.40 秒，HTML 随逐行 timeline 接 hold，改行数后未必等时。
- 示例是观点卡，只有确有引文时才应使用人物署名或引号。

V5 适配提示：可作为卡内结论保持，保留全部必要限定与真实出处；不强制三至五行、颜色或人物遮罩，不把大字强调误作增强信息卡的完整过程。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 94 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/quote-card.tsx#L94)：TSX 退出固定排期，改字数和行数时需重新核对阅读长度。
  对照字串：`const outAt = 3.40;`
- [html 第 89 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/quote-card/index.html#L89)：结论以整行为节奏单位顺序呈现，行内不再逐字演出。
  对照字串：`stagger: CONFIG.lineStagger`

## 演示与来源

![上游演示三个取样状态](../previews/quote-card.jpg)

[本地静音 HTML 演示](../upstream/demos/quote-card/index.html?embed=1) · [完整配方](../upstream/references/cards/quote-card.md) · [TSX](../upstream/template/cards/quote-card.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
