# 光标擦除转场 · caret-wipe-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

两段真实代码、编辑器或文档的版本替换，边界确实代表重写、撤销或改稿。

语义关系：文本版本替换、新旧互补揭示

## 避免误用

人物镜头、完整静态插画之间的一般换景，或与文字编辑无关的任意切换。

## 可见过程

1. 旧版本保持可辨认
2. 细光标向一侧移动，走过处露出新版本
3. 新层轻沉降解糊，旧层轻上浮失焦
4. 边界扫完，光标退出，新版本完整保持

配音落点：扫描开始对齐“重写、换成、改为”，结束落到改完后的结果句，方向对应写入或撤销。

## 关键限制与适配

- 新旧裁切和光标若使用不同进度、宽度基准，会在边界露缝或追帧。
- 两侧内容为空白或文字都居中时，中段难辨旧新甚至文字混读。
- 微位移与失焦属于内容编辑隐喻，不可作为V5插画转场许可。

V5 适配提示：限证据文档或卡片版本比较层候选，保留互补边界；插画镜头继续只硬切。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 115 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/caret-wipe-transition.tsx#L115)：TSX让新旧裁切共享同一横向进度，方向分支成互补。
  对照字串：`const clipNew = (x: number)`
- [html 第 137 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/caret-wipe-transition/index.html#L137)：HTML在同次更新直写裁切与光标位置，以减少异步更新导致的边缘错位。
  对照字串：`out.style.clipPath = clipOld(p.x);`

## 演示与来源

![上游演示三个取样状态](../previews/caret-wipe-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/caret-wipe-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/caret-wipe-transition.md) · [TSX](../upstream/template/cards/caret-wipe-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
