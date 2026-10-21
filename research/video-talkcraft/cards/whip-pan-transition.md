# 横甩转场 · whip-pan-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

信息卡或真实证据段由一个并列对象转到另一个对象，方向有明确含义时。

语义关系：并列案例 A 到案例 B、横向交接到同向速度连续

## 避免误用

推理是深入同一对象，或 V5 插画的静态换景时。

## 可见过程

1. 旧镜从已建立的画面向侧面加速甩出
2. 新镜从另一侧带模糊进入
3. 新镜减速刹到中心并解模糊
4. 剩余旋转单独回稳再读新内容

配音落点：“再看另一边”之类真实并列转折对应横向交接。

## 关键限制与适配

- 出场方向与入场来源配反会读作相互迎撞，旋转也要同向翻转。
- CSS blur 为各向同性失焦，并非真实定向运动模糊。
- 示例用扩大画幅防露底；上游回稳后必须续推不适用于 V5 插画。

V5 适配提示：只留作信息卡或证据交接的条件候选，优先让方向服务比较；禁止用于静态插画图内或镜头转场，不采永不静止要求，另验可读性与露边。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 82 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/whip-pan-transition.tsx#L82)：新镜从正侧回中心，与旧镜向负侧离开的空间方向连贯。
  对照字串：`const bX = lerp(W.dist, 0, tw(t, cut, W.brake, power3Out));`
- [html 第 88 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/whip-pan-transition/index.html#L88)：刹车结束后另排轻量回稳，只处理残留旋转。
  对照字串：`duration: W.recover, ease: "sine.out"`

## 演示与来源

![上游演示三个取样状态](../previews/whip-pan-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/whip-pan-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/whip-pan-transition.md) · [TSX](../upstream/template/cards/whip-pan-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
