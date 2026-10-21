# 局部放大镜 · magnifier-detail

类别：强调标注；研究用途：证据与素材呈现；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实截图上的细小数字、条款或按钮需要放大，同时必须让观众知道它来自原图哪处。

语义关系：细节放大与出处对应、局部证据定位

## 避免误用

原图本已清晰，或旁边没有空位使镜面必须遮住目标出处。

## 可见过程

1. 截图先显示整体
2. 目标原位框显现且底图减亮
3. 圆镜从目标点缩放移到旁侧空处
4. 连接线描回原位置
5. 镜内轻扫视并保持细节可读

配音落点：起镜对齐“看这个数字/按钮”，连线完成承接具体解释；镜内扫视不应移出正在引用的词。

## 关键限制与适配

- 副本需按同一原图坐标对位，额外容器缩放或重复裁切容易放错位置。
- 文档建议镜径不超屏高三分之一，但默认210/540约39%，移植时须按内容重审而非照数值。
- 镜内轻平移是证据呈现候选，不意味着V5插画允许局部运镜。

V5 适配提示：使用真实高分辨截图、重测目标与空白落位；视情况关闭镜内扫视，字幕仍在独立固定层。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 108 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/magnifier-detail.tsx#L108)：TSX用截图位置加截图内目标坐标求原位起跳点与连接线起点。
  对照字串：`const tx = SHOT.x + px, ty = SHOT.y + py;`
- [html 第 105 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/magnifier-detail/index.html#L105)：HTML副本偏移由镜径、放大倍数和目标坐标计算，放大内容应严格对应原处。
  对照字串：`x: CONFIG.magSize / 2 - CONFIG.zoom * px,`

## 演示与来源

![上游演示三个取样状态](../previews/magnifier-detail.jpg)

[本地静音 HTML 演示](../upstream/demos/magnifier-detail/index.html?embed=1) · [完整配方](../upstream/references/cards/magnifier-detail.md) · [TSX](../upstream/template/cards/magnifier-detail.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
