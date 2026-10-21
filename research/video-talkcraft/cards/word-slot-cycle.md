# 词槽轮换 · word-slot-cycle

类别：字幕花字；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一串短语共用相同句干，口播按节拍列举后收于一句更高层结论，且无需同时逐项比较时。

语义关系：共同句干、并列枚举、总结升格

## 避免误用

长短语、需要回看所有选项的对比或没有真实收束关系时，不宜快速翻词；不能把功能枚举夸成未证实全能。

## 可见过程

1. 固定句干与第一个词槽出现
2. 胶囊上翻换词，宽度随词长改变
3. 上下淡幽灵项暗示仍有后续
4. 列举槽上飞退出，结论落入同位并保持

配音落点：每次翻词起点对齐新的枚举短语，结论过冲对齐“因此能做到什么”；中间词稳住供读，结论获得更长保持。

## 关键限制与适配

- 整句 flex 居中会因词宽改变拖动句干，须先按句干加结论总宽求左锚点。
- 词数影响最后时刻，模板 meta 却固定，扩展到六项需同步合成帧长。
- 空 words 虽有测量兜底，动画仍会索引 ws[0]，不是可靠空列表支持；至少提供一个有效词。

V5 适配提示：V5 可采用共同句干到总结的信息卡过程，按口播留足每词静置，限制幽灵项干扰；不用它替代需要保留所有项的对照图。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 101 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/word-slot-cycle.tsx#L101)：用句干与最终结论总宽只确定一次左锚点，翻词时宽度变化不牵动句干。
  对照字串：`const left = Math.round((960 - (stemW + CONFIG.gap + finW)) / 2)`
- [html 第 114 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/word-slot-cycle/index.html#L114)：HTML 让胶囊和槽宽随同一换词窗口插值，结论另有唯一过冲入场。
  对照字串：`.to([pill, slot], { width: WIDTHS[i]`

## 演示与来源

![上游演示三个取样状态](../previews/word-slot-cycle.jpg)

[本地静音 HTML 演示](../upstream/demos/word-slot-cycle/index.html?embed=1) · [完整配方](../upstream/references/cards/word-slot-cycle.md) · [TSX](../upstream/template/cards/word-slot-cycle.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
