# 逐字升起 · per-character-rise

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

需要单独立住六至十字的短判断，整句是一个语义单位且不用逐词解释。

语义关系：短论点立起、整句近同步揭示

## 避免误用

常规跟读字幕、长句定义，或误以为逐字升起本身就能说明因果和对象关系。

## 可见过程

1. 各字预置在自身下方
2. 以约一帧的密错峰同时感升起
3. 位移较早到位
4. 文字继续在原位变实
5. 整句静止供阅读

配音落点：整句起势对齐提出判断或结论，落定覆盖主张读完；不应按每字口播机械逐字排队。

## 关键限制与适配

- 位移与淡入共用曲线、同时完成会失去前段力道和后段余韵。
- 逐字Array.from按码点而非完整字素，组合符号、复合emoji需另处理，中文标点也占错峰位置。
- 横排nowrap超出安全宽度时不会自行合理换行；放大错峰会把短句变成波浪式字幕。

V5 适配提示：只用于卡内独立结论句，重测全句宽度；不施加于固定底部口播字幕，也不充当增强信息卡过程。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 95 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/per-character-rise.tsx#L95)：TSX淡入使用较长持续时间及专用缓动，位置另以TRAVEL_EASE提前落定。
  对照字串：`const fadeP = tw(t, at, CONFIG.dur, FADE_EASE);`
- [html 第 86 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/per-character-rise/index.html#L86)：HTML明确分离位移与透明度曲线，源码不依赖缩放或模糊制造入场。
  对照字串：`const TRAVEL_EASE = cubicBezier(0.2, 0.8, 0.6, 0.85);`

## 演示与来源

![上游演示三个取样状态](../previews/per-character-rise.jpg)

[本地静音 HTML 演示](../upstream/demos/per-character-rise/index.html?embed=1) · [完整配方](../upstream/references/cards/per-character-rise.md) · [TSX](../upstream/template/cards/per-character-rise.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
