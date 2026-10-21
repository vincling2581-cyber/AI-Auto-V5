# 荧光笔高亮扫过 · highlighter-sweep

类别：强调标注；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有可核验的完整短引句，口播正在指出原文关键结论，需要把这一句从周围段落中提出来。

语义关系：完整引句定位、前景与语境降权

## 避免误用

只有截断的半句，或高亮会遮住证据字形、使关键限定条件不可见。

## 可见过程

1. 引用文字卡先在场
2. 半透明笔块由左扫过整句
3. 周边文字同时减弱
4. 扫完后关键句轻浮起并保持可读

配音落点：扫笔起点对齐“这一句”的引用开头，长度覆盖实际朗读；浮起在完整句意到齐后确认。

## 关键限制与适配

- 模板是DOM重排引文，不能当原始截图；需要保留真实来源和重排标识。
- 默认60帧总长只留很短尾段，长引句必须改扫速、阅读保持和整卡时长。
- multiply适用于浅底，深底需另验混合方式；不透明笔块会涂掉证据。

V5 适配提示：只在引文卡层做语义高亮，完整保留限定条件；不继承上游假报告、旧年份或相机缓推。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 84 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/highlighter-sweep.tsx#L84)：TSX将关键句浮起安排在扫笔结束之后，而周围降权与扫笔同起。
  对照字串：`const liftP = tw(t, CONFIG.startDelay + CONFIG.sweep`
- [html 第 91 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/highlighter-sweep/index.html#L91)：HTML同步降低其他行透明度，不只是单独加一块黄色矩形。
  对照字串：`.to(dims, { opacity: CONFIG.dimTo`

## 演示与来源

![上游演示三个取样状态](../previews/highlighter-sweep.jpg)

[本地静音 HTML 演示](../upstream/demos/highlighter-sweep/index.html?embed=1) · [完整配方](../upstream/references/cards/highlighter-sweep.md) · [TSX](../upstream/template/cards/highlighter-sweep.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
