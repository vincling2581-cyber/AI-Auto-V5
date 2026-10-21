# 长镜头世界画布 · long-take-world

类别：转场结构；研究用途：证据或卡片运镜；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

内容具有真实流程、地图或生态布局，观众需要知道节点相对位置和前往下一节点的方向时。

语义关系：空间化流程、相邻关系导航

## 避免误用

无空间依据的普通段落不应硬放大画布巡游；尤其不能将 V5 插画布成大世界后连续推拉横移。

## 可见过程

1. 第一站在画心建立起点
2. 相机沿二维路径接近下一站
3. 目标按距离提前显形，旧站随远离退去
4. 第三站接续出现，到站后仍有微漂

配音落点：运镜对应“下一步往哪里、由谁接手”的关系词；到站揭示应贴住节点被引入的含义，而不是句号固定换位置。

## 关键限制与适配

- 文档称站点到站成形，但实现是距离函数可逆显隐，离开后旧内容也会退去，非永久构建。
- HTML 微漂由独立 gsap.ticker 积时，未见移除监听，重播可能累积且与 speed 变化不同步。
- 上游“永不静止”的微漂规则不适用于 V5 信息卡阅读保持。

V5 适配提示：只把空间寻址用于确有布局含义的信息图候选，优先显式节点与连线；不继承无意义微漂，也不改变静态插画合同。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 104 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/long-take-world.tsx#L104)：显形进度取相机与站点距离，接近时上移放大成形，远离时反向退去。
  对照字串：`const dist = Math.hypot(cam.x - st.x`
- [html 第 93 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/long-take-world/index.html#L93)：微漂使用时间线以外的 ticker 时钟，和站点关键帧动画分属两种计时来源。
  对照字串：`gsap.ticker.add(() => { t += gsap.ticker.deltaRatio()`

## 演示与来源

![上游演示三个取样状态](../previews/long-take-world.jpg)

[本地静音 HTML 演示](../upstream/demos/long-take-world/index.html?embed=1) · [完整配方](../upstream/references/cards/long-take-world.md) · [TSX](../upstream/template/cards/long-take-world.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。

取样限制：跳转取样中后两态只见网格，HTML 使用独立 ticker；此取样不足以证明到站显形，也不能据此断言正常播放相同。需统一时钟后验证。
