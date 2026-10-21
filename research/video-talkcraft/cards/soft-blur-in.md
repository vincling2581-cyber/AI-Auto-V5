# 柔焦淡入 · soft-blur-in

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一个短结论需要轻缓进入画面，语气平稳且允许观众等文字清晰后再读。

语义关系：短句从未明到清晰、低权重结论呈现

## 避免误用

核心证据必须立即可读，或把多句连续口播字幕反复模糊来追求所谓轻盈。

## 可见过程

1. 各字以低透明、模糊和轻下沉预置
2. 逐字以约一帧密错峰开始
3. 位移只用前段便归位
4. 后段继续解糊并变实
5. 整句清晰后保持

配音落点：开始对齐新判断的起句，清晰终点需早于关键阅读时刻；低能量出现不能拖过口播结论。

## 关键限制与适配

- HTML开头注释残留blur9/rise12，但CONFIG实际为12/16，研究以执行参数为准。
- Array.from保住代理对却不处理完整复合字素，文档“emoji不会切坏”对连接符序列并不成立。
- 文字nowrap和逐字滤镜需实测输出可读性，不能照6~12字范围便保证不同字体都装得下。

V5 适配提示：只适于卡内短句的轻入场，不动独立字幕或插画；清晰后按实际阅读保持，不以模糊代替语义过程。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 104 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/soft-blur-in.tsx#L104)：TSX位移与主轨共用缓动但持续更短，剩余时间字留在原位解糊。
  对照字串：`const pTravel = tw(t, at, CONFIG.travel, EASE);`
- [html 第 60 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/soft-blur-in/index.html#L60)：HTML实际配置与旧注释不同，72px字配12px起始模糊，需依实际参数判断。
  对照字串：`blur: 12,`

## 演示与来源

![上游演示三个取样状态](../previews/soft-blur-in.jpg)

[本地静音 HTML 演示](../upstream/demos/soft-blur-in/index.html?embed=1) · [完整配方](../upstream/references/cards/soft-blur-in.md) · [TSX](../upstream/template/cards/soft-blur-in.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
