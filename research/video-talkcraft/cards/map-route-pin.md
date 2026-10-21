# 地图路线图钉 · map-route-pin

类别：数据信息图；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

行程、迁移、供应链或事件链确实涉及从一地点到下一地点，且先后顺序需要可见时。

语义关系：地理转移、按序到达、路线接续

## 避免误用

抽象并列关系不宜画成真实地理旅行；无地点资料时不能沿用北京、上海、深圳坐标造成错误地理断言。

## 可见过程

1. 起点图钉先落定并显示地名
2. 一条弧线路线逐渐伸向下一地点
3. 飞机沿线前进，到达后新图钉砸下回弹
4. 标签出现，停一拍再生长下一段路线

配音落点：起点对齐“从这里出发”，路线对应“转移到”，落钉对齐目的地名；下一条路须等当前到达已被看清。

## 关键限制与适配

- 飞机朝向来自路径切线，替换形状后须重新设 planeAngle，否则会横着飞。
- 演示只预排两段路线，改变城市数不能只改标签；PIN_AT 和路线表需一起调整。
- 抽象底图用于示意，不等于精确地理证据，实际距离或时间要另给来源。

V5 适配提示：可作 V5 地点关系信息卡，使用经核对的地点和抽象坐标，保留出发、移动、到达及下一段；不在静态插画上加飞行动画。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 169 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/map-route-pin.tsx#L169)：落钉状态按下落、短暂横宽纵扁和回弹分段计算，标签在回弹前后接入。
  对照字串：`const squashAt = at + CONFIG.pinDrop`
- [html 第 223 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/map-route-pin/index.html#L223)：飞机与路线共用进度，取真实弧长点和邻近点计算位置及切线朝向。
  对照字串：`route.getPointAtLength(prog.p * L)`

## 演示与来源

![上游演示三个取样状态](../previews/map-route-pin.jpg)

[本地静音 HTML 演示](../upstream/demos/map-route-pin/index.html?embed=1) · [完整配方](../upstream/references/cards/map-route-pin.md) · [TSX](../upstream/template/cards/map-route-pin.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
