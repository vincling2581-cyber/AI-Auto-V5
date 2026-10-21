# 环绕微漂 · orbit-drift

类别：运镜；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

证据页面需长时在场且正文不需逐字精读，可考虑极小透视变化维持展示空间感。

语义关系：证据页持续在场、前后空间层次

## 避免误用

V5任何完整插画，或密集小字截图、需要稳定对照数值的阅读任务。

## 可见过程

1. 页面以既定倾角在场
2. 横纵旋转以四分之一周期差缓慢变化
3. 前后距离叠加另一相位呼吸
4. 投影沿反方向随页面移动
5. 有限演示周期结束后停在终态

配音落点：没有固有单次口播落点，只能覆盖同一份材料的持续讲述；重点词仍需独立证据定位。

## 关键限制与适配

- 文档称可无限持续，但当前TSX将时间夹在orbit×cycles，HTML也只排有限圈，续长必须改时长与周期。
- 基准角加振幅才是最坏透视，默认Y可到约负14.2度，不能仅按振幅6.2度判断文字可读性。
- 异周期可减少重复却不保证循环点连续；不可通约周期直接拼loop会跳姿态。

V5 适配提示：仅列为证据页或卡片的条件相机候选，当前不应用到插画，不把上游永不停机纪律写成V5标准。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 138 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/orbit-drift.tsx#L138)：TSX实际在有限圈数后冻结时间，并非无条件无限运动。
  对照字串：`const t = Math.min(rawT, C.orbit * C.cycles);`
- [html 第 211 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/orbit-drift/index.html#L211)：HTML投影横移与页面横向相位反号，空间层次靠多层相对变化而非随机抖动。
  对照字串：`x: -sy * CONFIG.shadowShift,`

## 演示与来源

![上游演示三个取样状态](../previews/orbit-drift.jpg)

[本地静音 HTML 演示](../upstream/demos/orbit-drift/index.html?embed=1) · [完整配方](../upstream/references/cards/orbit-drift.md) · [TSX](../upstream/template/cards/orbit-drift.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
