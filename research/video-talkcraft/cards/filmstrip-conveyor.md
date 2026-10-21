# 传送带列举 + 减速停靠 · filmstrip-conveyor

类别：素材呈现；研究用途：证据与素材呈现；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

至少五个素材需按次序经过，并且其中一个对象值得稍慢讲解而其余只需辨认时。

语义关系：有序列举、重点停靠

## 避免误用

要同时精读各图、比较精细差异或仅有两三个对象时，传送带会削弱可读性，也不用于移动插画场景。

## 可见过程

1. 一列素材匀速通过中心参照位
2. 靠近中心的素材连续提亮放大
3. 目标项经过中心时减速至非零慢速
4. 恢复速度，让后续项目通过后整组退出

配音落点：把减速结束时目标居中对齐“其中第四个最关键”，以目标讲解长度决定慢速段，而不是任意停一拍。

## 关键限制与适配

- 中心权重由距离连续求值，到点才触发放大会突然闪跳。
- 所谓停靠仍保持四分之一速度，长解释会把目标送离中线，必须反推讲解窗。
- 示例复制第二组以补齐带尾，生产有限时长须避免观众误数重复项。

V5 适配提示：V5 可用于真实案例或截图的有序索引，先确认每项无需精读；若输入是叙事插画，则改成独立静态硬切。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 53 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/filmstrip-conveyor.tsx#L53)：用离中心距离的平方衰减连续计算放大、亮度及层级，强调来自经过中心。
  对照字串：`return (1 - d) * (1 - d)`
- [html 第 84 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/filmstrip-conveyor/index.html#L84)：位移按分段积分求出，慢速段仍保持非零速度，时间线只作为线性时钟。
  对照字串：`if (t < t3) return x0 + dDecel + v * r`

## 演示与来源

![上游演示三个取样状态](../previews/filmstrip-conveyor.jpg)

[本地静音 HTML 演示](../upstream/demos/filmstrip-conveyor/index.html?embed=1) · [完整配方](../upstream/references/cards/filmstrip-conveyor.md) · [TSX](../upstream/template/cards/filmstrip-conveyor.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
