# 关键词隧道 · flying-words

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

仅需表达概念密集、信息不断涌来的气氛，前景已有明确主旨时。

语义关系：多个概念到信息涌入的感受、背景词群与前景主旨的主次

## 避免误用

必须读清词间逻辑或逐个名词，或要给 V5 插画加纵深运动时。

## 可见过程

1. 深底中心建立静态光晕
2. 词群从远处按分散相位推进
3. 临近观众时向外散开并模糊
4. 词越过相机平面，整圈循环后收尾

配音落点：只承接“概念很多”的整体表意，关键知识仍应另卡说明。

## 关键限制与适配

- 无前景时词群没有阅读焦点，不能把气氛误当信息提炼。
- 非整数圈会让首尾跳变；过长词在近处容易相互遮挡。
- 上游深底和彩色光晕是这版的条件，不是 V5 统一样式。

V5 适配提示：作为低优先候选记录，若词间存在关系优先重做成可读结构卡；不移植到静态插画，不照搬次数配额，不能用飞词取代语义过程。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 73 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/flying-words.tsx#L73)：词按相位均分并循环推进，组织的是数量感而非逻辑顺序。
  对照字串：`const u = ((Math.min(t, CONFIG.dur) / CONFIG.dur) * CONFIG.cycles + i / N) % 1;`
- [html 第 69 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/flying-words/index.html#L69)：深度由同一生命进度驱动，从负 z 推进到正 z。
  对照字串：`z = lerp(CONFIG.zFrom, CONFIG.zTo, u);`

## 演示与来源

![上游演示三个取样状态](../previews/flying-words.jpg)

[本地静音 HTML 演示](../upstream/demos/flying-words/index.html?embed=1) · [完整配方](../upstream/references/cards/flying-words.md) · [TSX](../upstream/template/cards/flying-words.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
