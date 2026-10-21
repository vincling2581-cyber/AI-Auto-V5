# 章节标题卡 · chapter-title-card

类别：转场结构；研究用途：转场与章节结构；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

论述确有主题边界，需要先交代新章再进入内容时。

语义关系：上一主题到下一主题、章节编号与题名的层级

## 避免误用

只是换一句话或插画换景，尤其不能套到每个句号。

## 可见过程

1. 整片色板扫入接管画面
2. 大编号先建立章节身份
3. 题名从编号旁揭示并接短线
4. 内容相关线稿在后方描出
5. 读清题名后色板同向离场

配音落点：在上一段收束后说新章问题，题名承接这次语义转向。

## 关键限制与适配

- 文档说编号先落位，但源码题名在编号开始后 0.18 秒启动，存在交叠。
- 文档总时长上限约 2.5 秒，默认单卡参数相加约 2.55 秒，不能当锁定配额。
- 背景 motif 若与本章无关，只会制造第二视觉重点。

V5 适配提示：仅作信息卡章节结构候选，保留编号与主题关系；取消对静止的否定和强制漂移，也不移植固定章节时长或插画扫屏转场。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 147 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chapter-title-card.tsx#L147)：题名比编号晚起步但未等编号完成，实际是错峰交叠。
  对照字串：`at + CONFIG.wipeIn + 0.18`
- [html 第 159 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chapter-title-card/index.html#L159)：出场继续朝同一侧扫走，表达单向翻页。
  对照字串：`.to(card, { xPercent: 100`

## 演示与来源

![上游演示三个取样状态](../previews/chapter-title-card.jpg)

[本地静音 HTML 演示](../upstream/demos/chapter-title-card/index.html?embed=1) · [完整配方](../upstream/references/cards/chapter-title-card.md) · [TSX](../upstream/template/cards/chapter-title-card.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
