# 墨迹下划线 · ink-underline

类别：强调标注；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一句已在场的短句里，需要先后指出一两个词或区分两个对应概念。

语义关系：关键词精确标记、双词对照

## 避免误用

三个以上同级重点，或下划词跨行、基线不清而无法准确量取词盒。

## 可见过程

1. 句子先完整在场
2. 墨线沿第一个词下方由左向右生长
3. 线宽从起笔厚到收笔细
4. 按口播节拍再划第二词
5. 两条线落定静置供对照

配音落点：每次起笔对齐点名关键词，第二条跟第二个概念；划完保持以便回看整句，不能替口播改写原意。

## 关键限制与适配

- 填充缎带不能用轮廓dashoffset替代，否则会绕外边跑而非笔尖前行。
- taper若按已画部分归一化，会使线条事后膨胀，破坏落笔即终宽。
- TSX使用固定BOXES而HTML测真实基线，换字体或文案须重测；颗粒seed应固定避免抖动。

V5 适配提示：在卡片文字下保留笔压和静置，重测中文基线；不在完整插画上加动态笔划以规避静态规则。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 159 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/ink-underline.tsx#L159)：TSX每帧以被截短的脊线重算填充路径，字下线不是固定宽度描边。
  对照字串：`d: ribbon(spineOf(BOXES[m.target], m), m, v),`
- [html 第 189 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/ink-underline/index.html#L189)：HTML在同次更新直写SVG路径，完成后没有持续沸腾或随机重绘。
  对照字串：`onUpdate: () => p.setAttribute("d", ribbon(spine, m, st.v))`

## 演示与来源

![上游演示三个取样状态](../previews/ink-underline.jpg)

[本地静音 HTML 演示](../upstream/demos/ink-underline/index.html?embed=1) · [完整配方](../upstream/references/cards/ink-underline.md) · [TSX](../upstream/template/cards/ink-underline.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
