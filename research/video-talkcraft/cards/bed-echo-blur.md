# 同源模糊底床 · bed-echo-blur

类别：素材呈现；研究用途：证据与素材呈现；输入：V, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实竖屏视频需置入横屏证据段，且标题、来源要与完整原比例画面共存时。

语义关系：单条竖屏证据与同源环境底床、前景内容与来源说明分区

## 避免误用

要逐字阅读密集长截图，或要给静态插画补运动时。

## 可见过程

1. 同源画面压暗模糊铺满底床
2. 清晰白边竖卡在一侧落位
3. 另一侧标题和来源逐行进入
4. 前景与底床异速保持后同收

配音落点：讲到“现场画面”时交代来源，再让证据承担说明。

## 关键限制与适配

- TSX src 只接视频，静图要改 Img，HTML 是占位漂移而非真实播放证明。
- 同源两层同速会形成重影；底床只降透明度会损害字的对比。
- TSX 标称 7.7 秒镜头但 meta 为 243 帧，含额外收尾。

V5 适配提示：只作真实证据的横竖画幅处理候选，现场确认来源和清晰度；不把异速缓推用于 V5 插画，不强制信息卡持续运动。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 83 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/bed-echo-blur.tsx#L83)：同一视频组件可按 rate 设置播放速率，前景和底床不必同步。
  对照字串：`muted playbackRate={rate}`
- [html 第 112 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/bed-echo-blur/index.html#L112)：HTML 用较慢的底床占位漂移演示异速关系，未证明真素材表现。
  对照字串：`CONFIG.driftSpeed * CONFIG.echoSpeed * CONFIG.end`

## 演示与来源

![上游演示三个取样状态](../previews/bed-echo-blur.jpg)

[本地静音 HTML 演示](../upstream/demos/bed-echo-blur/index.html?embed=1) · [完整配方](../upstream/references/cards/bed-echo-blur.md) · [TSX](../upstream/template/cards/bed-echo-blur.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
