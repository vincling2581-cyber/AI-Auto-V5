# 数字重音标题 · count-badge-title

类别：字幕花字；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

口播明确承诺后面有几种方法或几个风险，需要先让观众记住确切条数。

语义关系：数量承诺、数字主次强调

## 避免误用

把持续变化的指标、没有后续兑现的虚数承诺，或长列表内容塞进数字标题。

## 可见过程

1. 数量数字单独缩至落点
2. 到位附近才变强调色
3. 量词从数字右缘被揭示
4. 第二行补足主题
5. 数字轻补一拍后整组保持

配音落点：数字入场对齐报出条数的音节，量词跟随名目，补拍只在真实句尾重音有需要时使用。

## 关键限制与适配

- 配方称落定那帧换色，代码实际在落定前后跨0.14秒插值，不能当单帧开关。
- 量词裁切与横移不同步会分裂成刷字后再滑动，数量和名目失去从属。
- 数字一两位之外、长量词或多位小数会破坏共基线和两级字号布局。

V5 适配提示：用于真实分点前的数量预告并与后续条目核对，保持时长按主题读完决定，不替代关系卡。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 129 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/count-badge-title.tsx#L129)：TSX变色从落定前半个hueDur开始，落定并不是瞬间变色。
  对照字串：`const hueP = tw(t, tLand - CONFIG.hueDur * 0.5`
- [html 第 98 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/count-badge-title/index.html#L98)：HTML把量词起点放在数字到位之后，标题各语义成分并非同时淡入。
  对照字串：`const tRest = tLand + CONFIG.restLag;`

## 演示与来源

![上游演示三个取样状态](../previews/count-badge-title.jpg)

[本地静音 HTML 演示](../upstream/demos/count-badge-title/index.html?embed=1) · [完整配方](../upstream/references/cards/count-badge-title.md) · [TSX](../upstream/template/cards/count-badge-title.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
