# 光标锁定跟拍 · cursor-locked-zoom

类别：运镜；研究用途：证据或卡片运镜；输入：界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

小屏展示很长的一行命令、路径或代码，必须先保证当前字符清楚，再拉回完整上下文时。

语义关系：逐字跟随、细节到全貌

## 避免误用

插画和人物情境镜头不得采用该连续相机运动；多行阅读、比例字体或无真实长内容也不能只为动而跟拍。

## 可见过程

1. 终端局部放大，光标附近成为视点
2. 命令线性打出，画幅按已输入字符跟随
3. 打完保持供读当前内容
4. 只减小缩放量，画幅连续归回终端全景

配音落点：跟随阶段对应“这一条命令怎么写”，全景回收对应“完整命令在这里”，不把读到一半的命令提前缩小。

## 关键限制与适配

- 定位反解依赖左上原点与等宽字宽，改字体会积累横向偏差。
- 边界钳制生效时光标未必严格居中，文档“恒在正中”存在素材边界条件。
- 命令文本、行号和终端几何固定在 CONFIG，换真实截图须重新标定文本起点。

V5 适配提示：仅供 V5 命令或界面证据的可读性候选，使用可核对文本；不可移植到插画，完整命令另留足可读状态。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 118 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/cursor-locked-zoom.tsx#L118)：字符数乘等宽字宽生成光标世界坐标，打字进度直接决定相机目标。
  对照字串：`const charW = C.fontSize * C.charW`
- [html 第 158 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/cursor-locked-zoom/index.html#L158)：镜头平移由缩放与受边界钳制的光标坐标反解，不另排追赶位移。
  对照字串：`x: W / 2 - z * cx`

## 演示与来源

![上游演示三个取样状态](../previews/cursor-locked-zoom.jpg)

[本地静音 HTML 演示](../upstream/demos/cursor-locked-zoom/index.html?embed=1) · [完整配方](../upstream/references/cards/cursor-locked-zoom.md) · [TSX](../upstream/template/cards/cursor-locked-zoom.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
