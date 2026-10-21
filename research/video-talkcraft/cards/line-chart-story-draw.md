# 折线分段推演 · line-chart-story-draw

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有可核对的历史基准与清楚声明的情景假设，要边讲边比较分歧时。

语义关系：既成历史到未来假设、同一拐点下两种未来、区间标注到相关范围

## 避免误用

数据或轴单位不明，或只是把虚构增长线包装成事实时。

## 可见过程

1. 历史线段从开始就完整在场
2. 在拐点给出假设注释
3. 主方案逐段生长，完成后出现标签
4. 对比虚线从同一拐点岔出
5. 最后淡入区间色带标明范围

配音落点：“如果从这里开始……”触发推演，标签只在相应线段讲完后出现。

## 关键限制与适配

- 虚线不能直接用 dashoffset 描画，否则会变成原地流动。
- 历史与假设若同样生长会模糊二者证据等级。
- 示例百分比、坐标和区间是演示数据，不能直接作为 V5 事实。

V5 适配提示：可优先研究其事实基准、分支推演和中间标签过程；替换真实数据并明示假设，保留分段停顿和阅读，不套插画两秒上限。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 182 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/line-chart-story-draw.tsx#L182)：对比方案在主方案逐段结束后再启动，保留推理先后。
  对照字串：`const altAt = growAt1 + seg1.dur`
- [html 第 362 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/line-chart-story-draw/index.html#L362)：通过独立遮罩揭示虚线，避免改变虚线自身纹理位置。
  对照字串：`tl.to(maskPath, { strokeDashoffset: 0`

## 演示与来源

![上游演示三个取样状态](../previews/line-chart-story-draw.jpg)

[本地静音 HTML 演示](../upstream/demos/line-chart-story-draw/index.html?embed=1) · [完整配方](../upstream/references/cards/line-chart-story-draw.md) · [TSX](../upstream/template/cards/line-chart-story-draw.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
