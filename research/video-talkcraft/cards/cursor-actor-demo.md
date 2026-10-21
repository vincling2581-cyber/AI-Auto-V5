# 光标演员演示 · cursor-actor-demo

类别：素材呈现；研究用途：证据与素材呈现；输入：界, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

要解释真实软件里几次点击或拖拽的结果，能够重建目标控件状态并核验操作含义。

语义关系：操作与响应因果、顺序演示、拖拽归属

## 避免误用

只有一张不可响应截图，却想用假光标证明软件已经完成实际操作。

## 可见过程

1. 放大光标移向目标并短暂停留
2. 按压时目标即时变更状态
3. 离开后上一目标悬停高亮退去
4. 光标抓住缩略图沿同一路径拖动
5. 松手后落点出现缩略图并确认

配音落点：每个“点开、启用、拖入、放下”的动词对应一次操作，响应起在按下过程而不等抬手。

## 关键限制与适配

- TSX落点是POS常量，HTML按元素位置测量；换界面只改图而不改坐标会点偏。
- 状态响应与涟漪是人为编排，不能声称是实际软件运行或产品能力的实测。
- 拖件和光标轨迹必须同曲线，独立缓动会让抓持关系断开。

V5 适配提示：限真实界面证据的解释重建，替换假UI并区分演示与实测；去掉上游主持人角标和字幕。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 293 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/cursor-actor-demo.tsx#L293)：TSX开关状态在按压行程过半时启动，不等待松手；拖拽两轴另共享光标缓动。
  对照字串：`const tOn = pressAt + CONFIG.press * 0.55;`
- [html 第 379 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/cursor-actor-demo/index.html#L379)：HTML让拖件与光标共用时长和起点，落下后再切换插槽内的可见结果。
  对照字串：`moveTo(thumb, { x: dx, y: dy }, CONFIG.moveDrag, t);`

## 演示与来源

![上游演示三个取样状态](../previews/cursor-actor-demo.jpg)

[本地静音 HTML 演示](../upstream/demos/cursor-actor-demo/index.html?embed=1) · [完整配方](../upstream/references/cards/cursor-actor-demo.md) · [TSX](../upstream/template/cards/cursor-actor-demo.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
