# 引号夹句 · quote-bracket-pull

类别：字幕花字；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

需要把一句确有来源的引文、留言或作者自己的结论立成引文，同时不必遮住原主体时。

语义关系：引用边界、引文内重点

## 避免误用

未经核验的名言、断章取义或需要整屏让位的长引用不应硬套；大引号本身不能提供出处可信度。

## 可见过程

1. 两枚大引号从对角同步向内夹出引文区
2. 引号移动过半时多行文字密错峰出现
3. 最后一行到位后关键短语底色扫过
4. 符号、引文与重点共同静置

配音落点：引号起点对齐“他曾这样说”，正文随引文起句进入，高亮对齐真正承担论点的末行短语，避免先框后空等。

## 关键限制与适配

- 双引号错峰会读成两个装饰标点而非一次夹句。
- TSX 以固定三行计算 markerAt，换为其他行数须连同时间表改写；HTML 则按 lines.length 推导。
- 引文块固定宽度会拉远引号与文字，最长行须决定实际容器宽，原出处需另给。

V5 适配提示：V5 可用于有核验出处的短引文信息卡，保留原意和必要限定，不继承人物占位；高亮只标论证关键处且供完整阅读。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 128 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/quote-bracket-pull.tsx#L128)：TSX 高亮时刻固定按第三行完成计算，行数变化时需要显式重算。
  对照字串：`CONFIG.lineStagger * 2 + CONFIG.lineDur`
- [html 第 112 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/quote-bracket-pull/index.html#L112)：HTML 将两枚引号放进同一补间同步收拢，正文在引号进程中段开始出现。
  对照字串：`tl.to([open, close], {`

## 演示与来源

![上游演示三个取样状态](../previews/quote-bracket-pull.jpg)

[本地静音 HTML 演示](../upstream/demos/quote-bracket-pull/index.html?embed=1) · [完整配方](../upstream/references/cards/quote-bracket-pull.md) · [TSX](../upstream/template/cards/quote-bracket-pull.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
