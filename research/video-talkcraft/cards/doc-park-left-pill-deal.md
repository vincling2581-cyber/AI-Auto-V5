# 文档驻留发牌 · doc-park-left-pill-deal

类别：素材呈现；研究用途：证据与素材呈现；输入：截图, 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

从一份真实报告提炼少量结论，需要持续保留来源身份并让各结论可回看。

语义关系：来源驻留、证据提炼结论、累计清单

## 避免误用

需要精读原文而驻留后正文过小，或来源并不能支持右侧提炼出的结论。

## 可见过程

1. 文档先较大展示并缓慢滚动
2. 文档以左边缘为锚退到左侧
3. 右侧逐条落下结论签
4. 各签的说明词逐步加深且不清除
5. 全量结论保留后一起收尾

配音落点：驻留对齐“从这份材料得到”，各结论起点分别对齐实际提炼句，不固定每1.3秒发一张。

## 关键限制与适配

- 默认报告、百分比与样本量均为演示文字，不能当事实沿用。
- noteDelay为0.30秒而pillLand为0.37秒，实际说明先于签完全落定约0.07秒，和文档“落定后”有差距。
- 露出35%只能保持来源身份，不能同时保证正文可读或证明全部结论有出处。

V5 适配提示：把真实来源和结论证据逐项关联；文档运动只在证据层，右侧保持可扩展，独立字幕仍固定底部中央。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 128 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/doc-park-left-pill-deal.tsx#L128)：TSX说明从发签起点加固定延迟计算，没有等待land完成的联动条件。
  对照字串：`const noteAt = t0 + CONFIG.noteDelay`
- [html 第 84 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/doc-park-left-pill-deal/index.html#L84)：HTML慢滚从镜头起点持续到收尾，与驻留和发签是并行轨。
  对照字串：`.to(inner, { y: CONFIG.scrollRate * end, duration: end, ease: "none" }, 0)`

## 演示与来源

![上游演示三个取样状态](../previews/doc-park-left-pill-deal.jpg)

[本地静音 HTML 演示](../upstream/demos/doc-park-left-pill-deal/index.html?embed=1) · [完整配方](../upstream/references/cards/doc-park-left-pill-deal.md) · [TSX](../upstream/template/cards/doc-park-left-pill-deal.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
