# 界面道具剧场 · ui-prop-theater

类别：数据信息图；研究用途：信息卡主体；输入：界, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

需要解释一个有明确阶段与完成条件的流程，能够给每阶段确定真实口播锚点并区分示意进度。

语义关系：流程状态推进、动作后确认、完成项累积

## 避免误用

用编排百分比伪装真实安装或处理记录，或不同事件的进度、状态、清单被硬塞在同一拍。

## 可见过程

1. 界面以初始状态在场
2. 重音处进度跳一段，读数同步变化
3. 旧状态退去，新状态换入
4. 对应清单稍后划勾并留下完成态
5. 收尾完成勾出现，界面稳定保持

配音落点：每拍对齐“下载、解压、安装完成”等对应事件，阶段间静置让观众读到目前状态。

## 关键限制与适配

- 分段百分比是写在beats里的示意值，非真实软件进度，不能凭非等距就声称真实。
- 状态开始退场与进度同拍，但新文本在swapOut之后才换，不是新文字与跳进严格同帧。
- 完成图标默认在done拍加0.16秒出现，早于0.30秒进度跳到100%的终点；需协调完成宣告。

V5 适配提示：重建为本集确有依据的流程状态卡，百分比无实据时改阶段名；保留中间静置，去掉假安装UI和主持人角标。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 211 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/ui-prop-theater.tsx#L211)：TSX每拍用同一个prog代理呈现填充与数值，状态推进是分段而不是一条匀速加载。
  对照字串：`if (t >= b.at) prog = lerp(prev, b.pct`
- [html 第 264 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/ui-prop-theater/index.html#L264)：HTML勾选及完成确认都用拍点加固定延迟，与进度0.30秒完成时刻不是同一终点。
  对照字串：`const at = b.at + CONFIG.tickDelay;`

## 演示与来源

![上游演示三个取样状态](../previews/ui-prop-theater.jpg)

[本地静音 HTML 演示](../upstream/demos/ui-prop-theater/index.html?embed=1) · [完整配方](../upstream/references/cards/ui-prop-theater.md) · [TSX](../upstream/template/cards/ui-prop-theater.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
