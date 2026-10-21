# 金句停留 · quote-hold-arrow

类别：强调标注；研究用途：卡内强调标注；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

三行完整表述先铺垫后得出一行结论，需要观众先读语义再意识到最后一句最重要。

语义关系：铺垫到结论升级、整句内部层级

## 避免误用

一上屏即须高能量钩子的标题，或三行都同等重要、不存在末行结论。

## 可见过程

1. 三行均按普通样式错峰出现
2. 最后一行普通地停一拍
3. 荧光框从末行中心向两侧铺开
4. 框到位后末行轻压一下
5. 全组静止留出结论余味

配音落点：升级对齐口播语气真正转重的结论点，框与文字补拍分开；保持覆盖整句理解和回味。

## 关键限制与适配

- ID保留arrow但当前实现已去箭头，不能按名称补回外指方向。
- 末行起手就自带高亮会抹掉先读再发现的推进；框与补拍同起也会混淆范围和重音。
- 行外壳须为块级、内文字才inline-block，否则多行可能塌成同行并撑坏高亮宽度。

V5 适配提示：用于本集结论卡中的后置强调，保留先平淡后升级，不加CTA、品牌或箭头，阅读保持不套2秒上限。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 101 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/quote-hold-arrow.tsx#L101)：TSX末行补拍明确等待荧光框铺开结束，前面还计入plainHold。
  对照字串：`const punchAt = upAt + CONFIG.hlDur;`
- [html 第 71 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/quote-hold-arrow/index.html#L71)：HTML升级前另留普通态停顿，收尾再留2.2秒且没有重新导向下一目标的箭头。
  对照字串：`plainHold: 0.34,`

## 演示与来源

![上游演示三个取样状态](../previews/quote-hold-arrow.jpg)

[本地静音 HTML 演示](../upstream/demos/quote-hold-arrow/index.html?embed=1) · [完整配方](../upstream/references/cards/quote-hold-arrow.md) · [TSX](../upstream/template/cards/quote-hold-arrow.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
