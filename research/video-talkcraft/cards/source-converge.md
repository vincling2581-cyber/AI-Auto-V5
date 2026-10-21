# 多源汇聚 · source-converge

类别：数据信息图；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

多个明确来源通过各自通道进入同一结果，口播要解释收集、归并或汇总机制时。

语义关系：多对一汇聚、通路传递、结果收束

## 避免误用

普通共同指向某主题的论点不必装成数据管道；未经说明的合并不可暗示不同来源已去重或信息完全无损。

## 可见过程

1. 来源胶囊出现，各自曲线错峰接通
2. 强调色数据包沿通路滑动
3. 来源沿真实曲线缩小汇入同一中心
4. 结果脉冲确认，通路从起点擦除
5. 结果与说明归中静置

配音落点：通道接通对应来源建立，整体汇入对齐“汇到同一个地方”，结果脉冲对齐产出名称，归中后讲用途。

## 关键限制与适配

- 节点若用两点直线插值，会离开曲线，视觉上不再沿既有通道进入。
- 曲线必须等节点消失后才擦，逆向擦线容易被读成从结果吐出。
- TSX 来源数量可变，但连线时间与汇入点固定；多源时需避免末线未接通节点已动。

V5 适配提示：与 V5 机制图较契合，按真实来源和结果确定节点，保留通路、移动、吸收与成品四层含义，过程不受插画两秒上限。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 117 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/source-converge.tsx#L117)：节点缩小在膝点前缓到 0.34、末段归零，让靠近结果时的吞并显著。
  对照字串：`const size = Math.max(0, conv < CONFIG.shrinkKnee`
- [html 第 134 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/source-converge/index.html#L134)：HTML 在汇聚、脉冲和擦线后把结果胶囊移至画心，最后保留成品说明。
  对照字串：`.to(o, { cx: 480, duration: CONFIG.centerDur`

## 演示与来源

![上游演示三个取样状态](../previews/source-converge.jpg)

[本地静音 HTML 演示](../upstream/demos/source-converge/index.html?embed=1) · [完整配方](../upstream/references/cards/source-converge.md) · [TSX](../upstream/template/cards/source-converge.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
