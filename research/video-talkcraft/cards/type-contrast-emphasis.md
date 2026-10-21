# 字体对比重音 · type-contrast-emphasis

类别：字幕花字；研究用途：卡内强调标注；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一句短判断中只有一个核心词需要比普通词更有分量，且可以用字体或色彩落差直接辨认。

语义关系：一句内部重音、对照结论突出

## 避免误用

把两三个词都做大字重音，或把这种追加式花字直接替换V5固定底部口播字幕。

## 可见过程

1. 整句词位先占好版面
2. 普通词按真实语音轻显现
3. 重音词以不同字族和更大字号，或单一强调色落定
4. 后续词继续追加且前词保留
5. 全句完成后保持共同基线

配音落点：词级出现对齐真实语音时间，重音对齐语义焦点；先判断哪个词承担结论，再选择字形或色彩通道。

## 关键限制与适配

- 配方要求一句一个重音、两通道不叠用，但两端默认同时强调“流量”衬线和“信任”色彩，与自身纪律不一致。
- 中文斜体需显式skew并留外探空间，否则依赖合成斜体会跨端不稳或挤压邻字。
- CSS预占位可防回流，但长句仍会超宽；relay模式虽可撤前词，却会牺牲整句对照。

V5 适配提示：仅作为卡内短论点强调候选，删去默认双重音并按本集字体重测，不引入主持人角标或动态跟读字幕要求。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 28 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/type-contrast-emphasis.tsx#L28)：TSX默认对“流量”使用字形强调，后续“信任”又设色彩强调，实际有两个重音。
  对照字串：`{ w: "流量",       beat: 1.02, emph: "serif" },`
- [html 第 143 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/type-contrast-emphasis/index.html#L143)：HTML可在下一词到达时硬撤前词，默认append则所有已说词仍留在预占位置。
  对照字串：`if (CONFIG.mode === "relay" && i > 0)`

## 演示与来源

![上游演示三个取样状态](../previews/type-contrast-emphasis.jpg)

[本地静音 HTML 演示](../upstream/demos/type-contrast-emphasis/index.html?embed=1) · [完整配方](../upstream/references/cards/type-contrast-emphasis.md) · [TSX](../upstream/template/cards/type-contrast-emphasis.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
