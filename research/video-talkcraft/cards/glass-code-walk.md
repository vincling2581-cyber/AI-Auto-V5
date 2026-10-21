# 玻璃代码走读 · glass-code-walk

类别：素材呈现；研究用途：证据与素材呈现；输入：界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实代码或配置较短，每个停靠行都值得对应一句解说时。

语义关系：代码整体结构到逐行解释、当前语句与上下文的邻接

## 避免误用

大段日志、几百行源码，或必须始终读完整长行却放大后裁切时。

## 可见过程

1. 代码块和各行就位
2. 推到走读焦距并压暗非当前行
3. 高亮带与视点同步逐行滑动、停读
4. 末行完成后回到全景解除压暗

配音落点：一句旁白对应一个停靠行，讲完再滑至下一句。

## 关键限制与适配

- 行号若取整切换会使高亮跳格，无法表达视线连续转移。
- TSX 的 hostSrc 参数未使用，不能宣称已支持人物同屏。
- 中文注释按整字宽估算；放大后最长行若超边界会丢信息。

V5 适配提示：真实代码证据才采用走读候选，保持缩进、上下文和阅读；相机只作用代码卡，不进入插画，玻璃装饰及上游持续运动要求不作为标准。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 235 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/glass-code-walk.tsx#L235)：浮点行位置在两次停靠间连续变化，而非整数行跳转。
  对照字串：`linePos = lerp(STOPS[k - 1], STOPS[k],`
- [html 第 303 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/glass-code-walk/index.html#L303)：逐段 tween 以统一行位置推进，停靠间另外保留 dwell。
  对照字串：`linePos: stops[k], duration: C.stepDur`

## 演示与来源

![上游演示三个取样状态](../previews/glass-code-walk.jpg)

[本地静音 HTML 演示](../upstream/demos/glass-code-walk/index.html?embed=1) · [完整配方](../upstream/references/cards/glass-code-walk.md) · [TSX](../upstream/template/cards/glass-code-walk.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
