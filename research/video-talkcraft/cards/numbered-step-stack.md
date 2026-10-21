# 编号步骤堆入 · numbered-step-stack

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

内容确是顺序可交换的几条建议，需在同屏形成清楚、可保存的集合时。

语义关系：并列方法到完整清单、编号与对应条目的一一对应

## 避免误用

后一步依赖前一步结果，或每条还需展开完整过程时。

## 可见过程

1. 等宽横条从侧面均匀错峰进入
2. 每条落定时只给编号块一次确认
3. 所有横条就位后整组轻微上收
4. 整份清单保持供阅读

配音落点：“可以记这几条”先建立集合，再按编号解释各项。

## 关键限制与适配

- 有依赖的流程若去掉连接线会误传为可交换清单。
- 编号 punch 若作用整条，会变成整体没停稳。
- TSX 根据 STEPS.length 排总收束，但 meta 时长固定，增加条目必须延长保持。

V5 适配提示：可采用并列清单结构，条目数由材料决定；密集入场不等于已经读完，须给完整阅读与必要的逐项解释，不采纳固定四条或错峰配额。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 131 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/numbered-step-stack.tsx#L131)：各条由索引推导均匀错峰，形成一组而非随机入场。
  对照字串：`const at = CONFIG.lead + i * CONFIG.barStagger;`
- [html 第 107 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/numbered-step-stack/index.html#L107)：确认缩放只施加于编号块，横条正文落位后保持稳定。
  对照字串：`.fromTo(nos[i],`

## 演示与来源

![上游演示三个取样状态](../previews/numbered-step-stack.jpg)

[本地静音 HTML 演示](../upstream/demos/numbered-step-stack/index.html?embed=1) · [完整配方](../upstream/references/cards/numbered-step-stack.md) · [TSX](../upstream/template/cards/numbered-step-stack.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
