# 铅笔手绘揭示 · pencil-sketch-draw

类别：素材呈现；研究用途：信息卡主体；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

概念确能被分成有意义的几笔关系，逐笔生成有助理解而非只画装饰边框时。

语义关系：讲解次序到图形生成次序、笔尖位置到当前可见笔迹

## 避免误用

要把完整叙事插画做图内绘制，或材料只是已经画好的复杂照片时。

## 可见过程

1. 笔尖就位到第一条路径起点
2. 笔尖与线条共享进度同步描出
3. 每笔结束沿笔身方向抬笔
4. 下一笔接续，最后出现解释标签并保持

配音落点：每一句讲解对应一笔或一组关系，名称在相关结构形成后补出。

## 关键限制与适配

- TSX 使用采样路径点，HTML 用浏览器路径测量，两者要按最终路径核对而非假定逐像素一致。
- handSrc 更换后原有笔尖坐标与轴角会失效。
- 示例默认可退回矢量笔，不能把未交付照片素材视为已具备手绘效果。

V5 适配提示：可研究信息卡内关系图的逐笔过程；先按语义拆路径并核实笔尖，保留完成图阅读，不给插画加绘制、漂移或环境呼吸，也不采用上游全局运动底线。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 103 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/pencil-sketch-draw.tsx#L103)：笔的位置由当前已画路径长度求出，使笔尖跟在线条前端。
  对照字串：`const pt = pointAtLength(g, at);`
- [html 第 134 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/pencil-sketch-draw/index.html#L134)：同一个 state.p 同时驱动线条显示与 placePencil，避免二者脱节。
  对照字串：`path.style.strokeDashoffset = len * (1 - state.p);`

## 演示与来源

![上游演示三个取样状态](../previews/pencil-sketch-draw.jpg)

[本地静音 HTML 演示](../upstream/demos/pencil-sketch-draw/index.html?embed=1) · [完整配方](../upstream/references/cards/pencil-sketch-draw.md) · [TSX](../upstream/template/cards/pencil-sketch-draw.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
