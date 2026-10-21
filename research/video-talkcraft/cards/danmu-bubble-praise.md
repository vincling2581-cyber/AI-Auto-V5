# 弹幕气泡 · danmu-bubble-praise

类别：人物互动；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有依据的多条简短反馈需作轻量补充，且不承担主要论证时。

语义关系：多条独立短评到群体在场感、一条重点与其余背景反馈

## 避免误用

评论必须逐条准确阅读，或根本没有评论材料却要制造共识时。

## 可见过程

1. 第一条短评从近侧边缘进入
2. 后续气泡按固定错峰接续
3. 早到气泡在后续进入时上移退出
4. 最后一条离场后回到主体内容

配音落点：“有几条反馈提到……”触发短评，重点内容仍由旁白说明。

## 关键限制与适配

- 四条同时进出会变成标签墙，丢掉独立反馈流。
- 停留短，只适合短评，不能据此压缩必读证据的阅读。
- 固定数组保证复现，但示例文字不能当真实公众反馈。

V5 适配提示：仅在有真实评论来源且适合节奏时候选；必要信息改用可读证据卡，避免遮脸、独立字幕和关键图形，不采用固定 CTA 或共识营销。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 104 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/danmu-bubble-praise.tsx#L104)：每枚拥有自己的退出时刻，支持进出交叠。
  对照字串：`const tOut = tIn + CONFIG.inDur + CONFIG.hold;`
- [html 第 73 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/danmu-bubble-praise/index.html#L73)：气泡由其所在侧决定入场方向，而非全体同向弹入。
  对照字串：`const dir = b.classList.contains("side-l") ? -1 : 1;`

## 演示与来源

![上游演示三个取样状态](../previews/danmu-bubble-praise.jpg)

[本地静音 HTML 演示](../upstream/demos/danmu-bubble-praise/index.html?embed=1) · [完整配方](../upstream/references/cards/danmu-bubble-praise.md) · [TSX](../upstream/template/cards/danmu-bubble-praise.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
