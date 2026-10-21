# 首词占满补句 · lead-word-zoom-assemble

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一句短主张的语义重心确在首词，且后续词能自然补全关系时。

语义关系：先出现的核心词到完整主张、主句让位到副句补充

## 避免误用

首词过长、句子需多行，或要用大字冲击替代事实论证时。

## 可见过程

1. 首词先以大尺度独占画面
2. 首词缩回同时整行横移归位
3. 后续词按槽位接续推入
4. 主句上移同时补入副行
5. 整句落定后保持再同收

配音落点：先念首词立住概念，再随着补词完成主张，副行给限定说明。

## 关键限制与适配

- 首词中心必须按真实字宽测量，否则缩放会漂移。
- 缩放和位移同起但时长不同，不能误改成先缩再移。
- 固定 meta 时长未随任意长文案自动延长，换词后必须重排。

V5 适配提示：只用于卡内短主张的组句，不用于独立底部字幕；保留副行限定条件与静置阅读，不能用字号变化冒充推理或照搬示例结论。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/lead-word-zoom-assemble.tsx#L87)：测量首词中心在整行的占比，计算归位位移。
  对照字串：`setM({ ratio, slide: L * (0.5 - ratio) });`
- [html 第 78 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/lead-word-zoom-assemble/index.html#L78)：横移与缩小从同一时刻起步，保留位置延后落定的尾段。
  对照字串：`duration: CONFIG.slide, ease: "power3.inOut" }, shrinkAt)`

## 演示与来源

![上游演示三个取样状态](../previews/lead-word-zoom-assemble.jpg)

[本地静音 HTML 演示](../upstream/demos/lead-word-zoom-assemble/index.html?embed=1) · [完整配方](../upstream/references/cards/lead-word-zoom-assemble.md) · [TSX](../upstream/template/cards/lead-word-zoom-assemble.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
