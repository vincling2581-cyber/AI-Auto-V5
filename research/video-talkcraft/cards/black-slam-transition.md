# 黑震切转场 · black-slam-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

两段信息存在一次明确的最大反转，前段句末留停顿、后段给出答案时可研究其断裂节拍。

语义关系：悬念揭晓、强转折

## 避免误用

普通换景、连续讲解或静态插画切换不应直接套用整屏震位和推拉；上游“全片唯一静止”也不适合 V5。

## 可见过程

1. 前一画面缩放停住形成预备拍
2. 重音遮罩迅速冲顶
3. 前后画面同帧零交叠交接
4. 新画面递减震位并后拉刹住

配音落点：硬切落在“答案其实是……”的答案起音或前一悬念句后的停顿，不放在连续词组中间。

## 关键限制与适配

- 入场只是静图而没有对应主体，重音会变成无对象的抖屏。
- 上游后段继续慢漂，且固定说明角标随片存在，均不能作为 V5 默认规则。
- 用交叠淡化替代瞬切会改变此式的预备与兑现关系。

V5 适配提示：仅作为信息卡之间强转折的条件候选；保留断句思路，插画仍用普通静态硬切，不承接该相机或震动。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 81 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/black-slam-transition.tsx#L81)：逐帧按切点直接置零旧镜透明度，同时新镜从零变一。
  对照字串：`const aOpacity = t < cut ? 1 : 0`
- [html 第 89 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/black-slam-transition/index.html#L89)：GSAP 用 set 实现零交叠交接，随后只对入场镜安排三段递减震位。
  对照字串：`tl.set(out, { opacity: 0 }, cut)`

## 演示与来源

![上游演示三个取样状态](../previews/black-slam-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/black-slam-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/black-slam-transition.md) · [TSX](../upstream/template/cards/black-slam-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
