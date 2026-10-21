# 缓拉全貌 · slow-pull-reveal

类别：运镜；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

静态证据的完整范围比局部更有信息，例如密集看板、清单或全景，先看一个细节再揭开规模时。

语义关系：细节扩展、规模揭示

## 避免误用

没有新增范围信息的普通图片不应缓拉凑时长；V5 插画严禁用该连续缩放，长表格精读也不能被运动替代。

## 可见过程

1. 从放大的兴趣点细节起手
2. 缩放和偏移同时向素材全貌回收
3. 主拉减缓后接线性余量拉完
4. 终点回到一倍且零偏移的完整素材

配音落点：起手局部对应具体数字或细节，范围逐渐展开对应“更惊人的是整张表都如此”，全貌应在归纳句出现时可见。

## 关键限制与适配

- 主拉只走 k 倍总量却用未乘 k 的 rate 接尾段，代码所称末速连续并不严格成立，接点需实看。
- 终点小于一倍会露出素材外舞台，失去范围揭示的完整性。
- 原实现含固定示意看板与兴趣点，真实长表需重新标定清晰度、起点及最终可读范围。

V5 适配提示：仅供 V5 外部证据从细节到全貌的条件候选；若信息靠读表而非看规模，应分区静置，插画继续硬切。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 121 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/slow-pull-reveal.tsx#L121)：TSX 把主拉位移缩短为 k 倍，但 camEase 的末速还会同乘 k，尾段 rate 并未同步缩放。
  对照字串：`const k = 1 - (rate * CONFIG.holdDur) / total`
- [html 第 232 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/slow-pull-reveal/index.html#L232)：HTML 尾段以线性补间回到原尺寸和零偏移，完成从细节到全貌的重构图。
  对照字串：`scale: CONFIG.zoomTo, x: 0, y: 0`

## 演示与来源

![上游演示三个取样状态](../previews/slow-pull-reveal.jpg)

[本地静音 HTML 演示](../upstream/demos/slow-pull-reveal/index.html?embed=1) · [完整配方](../upstream/references/cards/slow-pull-reveal.md) · [TSX](../upstream/template/cards/slow-pull-reveal.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
