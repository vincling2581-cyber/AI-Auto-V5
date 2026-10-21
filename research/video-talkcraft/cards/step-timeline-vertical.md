# 竖向步骤线 · step-timeline-vertical

类别：数据信息图；研究用途：信息卡主体；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

步骤确有先后依赖，需让观众理解次序并知道当前在第几步时。

语义关系：前一步完成到后一步启动、流程总貌到当前所在步骤

## 避免误用

几条可交换建议，或材料没有真实流程却硬加因果线时。

## 可见过程

1. 竖向连接线从上向下推进
2. 线到节点才弹出节点
3. 节点之后对应文字接上
4. 全部流程显示后单个节点升级为空心环
5. 保持完整流程与当前位置

配音落点：按真实步骤解释，当前环在概览结束后回答“现在做到哪”。

## 关键限制与适配

- 节点时刻要由缓动反解，手写 delay 会出现点早于线。
- 默认当前环永远选第一个节点，实际进度改变必须改实现。
- 三个点都升环会失去当前唯一性，清单也不能误用此卡。

V5 适配提示：可研究其顺序推进、节点接文和当前状态三层关系；按本集真实依赖编排，节点可停留解释，不强制固定三步、线长或时长。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 114 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/step-timeline-vertical.tsx#L114)：根据节点高度反解线条缓动时间，保证线到才亮。
  对照字串：`CONFIG.lead + CONFIG.lineDur * invPower1InOut(s.at / WRAP_H)`
- [html 第 166 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/step-timeline-vertical/index.html#L166)：当前位置确认安排在所有步骤就位之后，独立回答进度问题。
  对照字串：`const ringAt = lastEnd + CONFIG.ringDelay;`

## 演示与来源

![上游演示三个取样状态](../previews/step-timeline-vertical.jpg)

[本地静音 HTML 演示](../upstream/demos/step-timeline-vertical/index.html?embed=1) · [完整配方](../upstream/references/cards/step-timeline-vertical.md) · [TSX](../upstream/template/cards/step-timeline-vertical.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
