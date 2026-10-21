# 聊天记录自演 · chat-message-flow

类别：素材呈现；研究用途：信息卡主体；输入：界, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有真实可引用的两到四条对话，需解释先问什么、等到什么回答时。

语义关系：我方提问到对方回应、消息发送到延迟反馈

## 避免误用

完整聊天档案很长，或没有依据却要模拟真实客户证言时。

## 可见过程

1. 我方文字在输入框逐字完成
2. 短停后消息弹入对话区
3. 对方三点输入提示等待
4. 回复气泡替换提示，随后反应表情出现

配音落点：提问配输入与发送，回答落屏时再读出核心回应。

## 关键限制与适配

- 提示气泡应退出后再显回复，重叠会像状态故障。
- 用 display 随意切换整行会造成历史消息突然跳位。
- 重演对话不能冒充原始截图或实际发生时间。

V5 适配提示：用来表达问答、委托与反馈链，保留身份区分、等待和阅读；内容来自本集材料并标明重演，时刻表按旁白重排，不照搬品牌皮肤。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 263 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chat-message-flow.tsx#L263)：我方输入按字符显示，不是直接弹出已完成气泡。
  对照字串：`comp = s.text.slice(0, Math.floor(p * s.len));`
- [html 第 357 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chat-message-flow/index.html#L357)：输入提示由独立进出包络控制，可在回复前清退。
  对照字串：`r.ind.style.opacity = inP * outP;`

## 演示与来源

![上游演示三个取样状态](../previews/chat-message-flow.jpg)

[本地静音 HTML 演示](../upstream/demos/chat-message-flow/index.html?embed=1) · [完整配方](../upstream/references/cards/chat-message-flow.md) · [TSX](../upstream/template/cards/chat-message-flow.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
