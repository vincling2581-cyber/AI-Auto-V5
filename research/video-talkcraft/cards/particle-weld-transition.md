# 粒子溶接转场 · particle-weld-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

前后两段确实是同一对象换形态，例如来源数据成为图表，且粒子隐喻有助说明转化时。

语义关系：形态转化、物质连续

## 避免误用

无因果关系的两张图、普通章节换页或 V5 插画之间不应溶粒；相似粒子也不能证明内容有实际转化关系。

## 可见过程

1. 旧主体轻升、失焦并逐渐消失
2. 主体范围内一批粒子错峰向上散开
3. 同种粒子从下方继续上升并收拢
4. 新主体在聚拢末段显形，粒子退出

配音落点：碎解对应“把这些信息拆开”，聚拢对应“重新组织成这个结果”；新结论应晚于主要收拢过程出现。

## 关键限制与适配

- 同 seed 保证两组尺寸落点一致，但只是视觉连续，生成盒仍是固定 HOME，并非真实文字或图形采样。
- 粒子与镜头同时大幅推拉会掩盖转化主语；上游还自带慢推需单独取舍。
- 换主体后不重建包围盒，粒子会从空处生出，无法表达对象真的被转化。

V5 适配提示：仅作为 V5 信息卡中同对象重组的条件候选；保留可核对对象映射优先于粒子效果，插画层继续静态硬切。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 57 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/particle-weld-transition.tsx#L57)：确定性种子按粒子序号生成稳定尺寸、位置与延迟，避免逐帧随机闪变。
  对照字串：`rnd(CONFIG.weld.seed * 1000 + i * 7 + k)`
- [html 第 97 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/particle-weld-transition/index.html#L97)：入场组复用同一生成函数和种子，从下方向上回到主体盒，主体滞后成形。
  对照字串：`const pIn = makeParticles()`

## 演示与来源

![上游演示三个取样状态](../previews/particle-weld-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/particle-weld-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/particle-weld-transition.md) · [TSX](../upstream/template/cards/particle-weld-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
