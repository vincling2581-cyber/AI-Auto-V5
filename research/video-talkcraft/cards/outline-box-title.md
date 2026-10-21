# 描边框标题 · outline-box-title

类别：字幕花字；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

短语要被确认为定义、核心观点或段落结论，且偏理性条理表达，需要精确容器边界时。

语义关系：术语界定、结论框选

## 避免误用

情绪爆点或作者手写圈重点不宜用机器闭合框冒充；短标题框也不能承载长段正文和复杂关系。

## 可见过程

1. 描边沿一条路径绕完精确闭合
2. 闭合后实心标记从左展开
3. 标记内文字独立延迟显出
4. 三枚方向符号依次提亮后保持

配音落点：框选过程对应“我们把它定义为”，框闭合后术语或结论确认；装饰箭纹不必逐一对应口播词。

## 关键限制与适配

- 框和标签同时出现会丢失先界定后命名的关系。
- 标签背景若连字一起 scaleX，字形被压扁；正文需独立层保持原比例。
- 文档称近匀速机器感，实际使用 power2.inOut，节奏并非真正等速描线。

V5 适配提示：适合 V5 卡内术语或短结论的边界确认，先确定该框承担哪种关系，再选择有框或无框形式，不作为固定标题包装。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 109 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/outline-box-title.tsx#L109)：逐帧用闭合路径长度控制可见弧长，框完成后才计算 chip 展开。
  对照字串：`const dashOffset = BOX_LEN * (1 - boxP)`
- [html 第 129 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/outline-box-title/index.html#L129)：标签背景横展与文字透明度分开排程，内字延后 0.1 秒出现。
  对照字串：`t.to(chip, { scaleX: 1`

## 演示与来源

![上游演示三个取样状态](../previews/outline-box-title.jpg)

[本地静音 HTML 演示](../upstream/demos/outline-box-title/index.html?embed=1) · [完整配方](../upstream/references/cards/outline-box-title.md) · [TSX](../upstream/template/cards/outline-box-title.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
