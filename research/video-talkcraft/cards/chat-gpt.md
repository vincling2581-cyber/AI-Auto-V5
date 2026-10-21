# ChatGPT 对话框 · chat-gpt

类别：素材呈现；研究用途：证据与素材呈现；输入：界, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

讲解一段短提示词如何输入、提交并得到分块回答，且需要展示该产品界面状态变化时。

语义关系：输入到响应、提交状态转换、界面过程例证

## 避免误用

长对话历史、完整测评证据或未经实际运行的回答不宜用这张一问一答自演代替；演示动画不证明模型真实输出。

## 可见过程

1. 问候、药丸输入框与建议依阅读顺序出现
2. 提示词逐字输入，语音键换成发送键
3. 建议退场，发送后问候让位给用户消息
4. 短暂思考后回答成簇揭示

配音落点：输入起点对齐“我这样问”，提交对齐“发给它”，首批回答对齐“它开始回答”；不要把合成等待时间当真实耗时。

## 关键限制与适配

- chips 退场必须使用不回退进度，否则按钮回语音态时建议会重现。
- 源码内的产品外观和回答文案是快照，不能据此宣称当前 UI 或实测结果。
- 中文输入速率与分块输出是两种节拍，全部改成逐字匀速会抹掉人机区别。

V5 适配提示：V5 可借用输入、提交、响应的状态结构，内容使用有来源的真实录屏或明确标作示意，独立底部字幕不随界面移动。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 267 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chat-gpt.tsx#L267)：提交是明确的状态边界，输入内容清空并转交用户消息显示。
  对照字串：`const sent = t >= S.sendAt`
- [html 第 404 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chat-gpt/index.html#L404)：回答按 chunk 向上取整成簇出现，单条线性时钟统一驱动全部状态。
  对照字串：`Math.ceil(linear / CONFIG.streamChunk)`

## 演示与来源

![上游演示三个取样状态](../previews/chat-gpt.jpg)

[本地静音 HTML 演示](../upstream/demos/chat-gpt/index.html?embed=1) · [完整配方](../upstream/references/cards/chat-gpt.md) · [TSX](../upstream/template/cards/chat-gpt.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
