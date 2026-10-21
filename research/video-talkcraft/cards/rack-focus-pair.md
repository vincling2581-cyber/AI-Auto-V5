# 焦点接力 · rack-focus-pair

类别：素材呈现；研究用途：证据与素材呈现；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

两个对象在口播中交替被讨论，需要始终同屏但每一刻只有一个主要观察对象时。

语义关系：交替指认、前后景降权

## 避免误用

两图需要同时清楚精比、对象超过两个或需要表现先后因果时，不宜靠失焦交接代替结构关系。

## 可见过程

1. 两张略重叠卡片入场，一张清晰一张失焦
2. 口播切换对象时清晰、亮度和大小同步交换
3. 第二对象保持，原对象原位退为背景
4. 焦点再交回前张，最后两张一起退出

配音落点：转焦起点对应“再看另一款”，回转对应“回到刚才那一个”；两次之间覆盖当前对象完整解释，而非机械来回。

## 关键限制与适配

- 失焦只加 blur 不压亮度，后景仍可能比前景抢眼。
- 标签若被前卡遮住，观众失去对象身份；清晰度变化不能代替标签可读性。
- TSX 默认只用 Img，视频需另接同步播放；这是素材对焦效果，不能用于 V5 静态插画的缩放或失焦。

V5 适配提示：适合 V5 两份真实案例之间的注意力切换候选；要做细节对照时改用两者都可读的布局，并保留来源标识。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 88 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/rack-focus-pair.tsx#L88)：由一条焦点进度及其反值统一生成两卡的模糊、亮度和缩放，状态互补。
  对照字串：`const front = look(f), back = look(1 - f)`
- [html 第 78 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/rack-focus-pair/index.html#L78)：HTML 同一时刻把前卡变软、后卡变清，后续再对称交回，两个对象不消失。
  对照字串：`.to(pf, { ...soft, duration: CONFIG.shift`

## 演示与来源

![上游演示三个取样状态](../previews/rack-focus-pair.jpg)

[本地静音 HTML 演示](../upstream/demos/rack-focus-pair/index.html?embed=1) · [完整配方](../upstream/references/cards/rack-focus-pair.md) · [TSX](../upstream/template/cards/rack-focus-pair.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
