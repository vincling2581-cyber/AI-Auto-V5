# 数字弹出 · number-slab-pop

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一个已经确定的数值就是本句结论，需要先立住整数再补上小数、单位和说明时。

语义关系：单点结论、整数与精度补充

## 避免误用

计算过程、动态累积或多项比较不能用一次弹数代替；小数单位的延迟不能使结论被误读为另一量纲。

## 可见过程

1. 空实色块先从上方落到位
2. 巨大整数随后一次弹出
3. 预占位置的小数与单位延后显现
4. 说明行最后上浮，完整结论静置

配音落点：整数弹出对齐口播主数，精度与单位紧随其后，说明行对齐“这是哪一年的什么指标”，全值读完再切走。

## 关键限制与适配

- 色块与数字同时入场只剩整张贴图运动，结论主次消失。
- 小数单位必须从头占宽，临时插入 DOM 会推动整数横跳。
- 默认数字和说明在源码常量里，换数必须连同单位、来源、时间范围一起核对。

V5 适配提示：V5 可作单数值结论卡，先给指标语境并保留完整数值阅读；弹入只属于卡内排版，禁止带动插画和底部字幕。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 102 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/number-slab-pop.tsx#L102)：TSX 以色块落定时间作为数字起点，随后分别计算精度与说明行的出现。
  对照字串：`const numAt = CONFIG.lead + CONFIG.slabDur`
- [html 第 107 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/number-slab-pop/index.html#L107)：小数和单位保持节点占位只改透明度，整数出现时行宽已固定。
  对照字串：`gsap.set([dec, pct], { opacity: 0 })`

## 演示与来源

![上游演示三个取样状态](../previews/number-slab-pop.jpg)

[本地静音 HTML 演示](../upstream/demos/number-slab-pop/index.html?embed=1) · [完整配方](../upstream/references/cards/number-slab-pop.md) · [TSX](../upstream/template/cards/number-slab-pop.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
