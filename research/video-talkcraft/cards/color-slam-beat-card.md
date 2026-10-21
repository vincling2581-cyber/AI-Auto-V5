# 纯色硬切节拍卡 · color-slam-beat-card

类别：转场结构；研究用途：卡内强调标注；输入：场, 文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

确有短而强的结论，需要纯色跳变标出一次口播重音，并接一张相关真实材料。

语义关系：观点断拍、判断与证据配对

## 避免误用

把整段知识关系都压成连续大字口号，或为追节拍过早撤走尚未读完的证据。

## 可见过程

1. 纯色底一帧切入
2. 大字稍后由同色淡字变实
3. 素材卡与副文错峰升入并清晰
4. 整组静止供阅读
5. 硬切回原场或卡层上移退出

配音落点：硬切对齐判断重音，显影与材料出现跟随后半句解释，保持按实际证据阅读量决定。

## 关键限制与适配

- HTML注释仍说保持时漂移，但配置driftPx为0，代码实际是静置，不能照注释宣称持续运动。
- 附带Shot1、Shot2是假截图，不构成来源证据。
- 上移退出只适于卡片层，不能照搬成静态插画的运动换景。

V5 适配提示：仅提取卡层重音及先结论后材料的错峰；替换假证据，去掉上游口播字幕与固定编号身份。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 199 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/color-slam-beat-card.tsx#L199)：TSX第一卡采用硬切状态，第二卡另选lift退出，不能统称全部零补间。
  对照字串：`const s1 = beatState(t, CONFIG.cards[0], at1, "cut");`
- [html 第 155 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/color-slam-beat-card/index.html#L155)：HTML默认保持期位移为零；显影完成后并无必要的常驻漂移动画。
  对照字串：`driftPx: 0,`

## 演示与来源

![上游演示三个取样状态](../previews/color-slam-beat-card.jpg)

[本地静音 HTML 演示](../upstream/demos/color-slam-beat-card/index.html?embed=1) · [完整配方](../upstream/references/cards/color-slam-beat-card.md) · [TSX](../upstream/template/cards/color-slam-beat-card.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
