# 逐行滑入 · line-by-line-slide

类别：字幕花字；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

三四行短要点属于同一组，先轻微带出次序再让观众通读整组。

语义关系：少量清单成组、行级先后列举

## 避免误用

每一行都需长篇解释的步骤流程，或五行以上的密集文字想在一次短动效中读完。

## 可见过程

1. 各行从左侧密集错峰滑入
2. 横向位移先停，文字再变实
3. 全叠保持可读
4. 各行先在原位变淡
5. 稍后朝右穿出且更密地一起收走

配音落点：入场可对齐“三件事”等集合预告；若逐项讲述较长，必须按各项语义重排而不是照0.13秒刷完。

## 关键限制与适配

- 这只是文字行入场次序，未建立步骤之间的因果或依赖，不能冒充过程关系图。
- 行内自动折行会破坏视觉行与动画索引的一一对应。
- 说明提到五行会入退重叠，但当前代码exitStart在全部入场后加hold，不会仅因行数多而自动重叠；主要风险是密度与时长。

V5 适配提示：保留整组与逐项兼顾的原则，按真实条目扩充中间状态及阅读保持，出场不移动独立口播字幕。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 96 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/line-by-line-slide.tsx#L96)：TSX先计算最后一行入场结束，再加保持，当前代码具备全叠入场完成的排程下界。
  对照字串：`const exitStart = enterEnd + CONFIG.hold;`
- [html 第 130 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/line-by-line-slide/index.html#L130)：HTML把退出位移安排在淡出之后才开始，但二者在同一收尾时刻结束。
  对照字串：`duration: CONFIG.exitDur - CONFIG.exitDelay,`

## 演示与来源

![上游演示三个取样状态](../previews/line-by-line-slide.jpg)

[本地静音 HTML 演示](../upstream/demos/line-by-line-slide/index.html?embed=1) · [完整配方](../upstream/references/cards/line-by-line-slide.md) · [TSX](../upstream/template/cards/line-by-line-slide.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
