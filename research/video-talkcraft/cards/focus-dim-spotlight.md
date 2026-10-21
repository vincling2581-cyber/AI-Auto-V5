# 聚焦压暗切换 · focus-dim-spotlight

类别：强调标注；研究用途：证据与素材呈现；输入：截图, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

已有多行表格或清单，口播逐行解释，需要保留上下文又控制观众当前视线。

语义关系：版面证据定位、逐项焦点接力、局部回归整体

## 避免误用

目标还需放大才能读清，或把压暗当删除上下文以隐去不利比较。

## 可见过程

1. 原版面完整在场
2. 目标周围渐暗、目标框亮起
3. 焦点连同尺寸滑向下一行
4. 行窗口扩大到整卡
5. 描边先退，整屏恢复原亮度

配音落点：初次压暗对齐第一项目名，滑动跟随“下一行、这一项”，整卡恢复承接综合结论。

## 关键限制与适配

- 目标内容应保持原状；再做放大换色会混淆证据与强调效果。
- TSX矩形是TARGETS/WIDE固定几何，换内容必须重测；压暗过重会让上下文失去可比性。
- 配方带发光描边和持续呼吸，只是上游样式，不能未经本集选择就全套套用。

V5 适配提示：在证据或关系卡层重测焦点并评估克制边框，字幕独立位于蒙层之上，绝不压暗或运动插画内容。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 184 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/focus-dim-spotlight.tsx#L184)：TSX在行级焦点结束后另留整卡阶段，再执行恢复，不是讲完一行就直接切走。
  对照字串：`const tRestore = tWide + C.morph + C.wideHold;`
- [html 第 148 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/focus-dim-spotlight/index.html#L148)：HTML焦点窗口相对实测行保留几何内外边距，框应围绕内容而非压住文字。
  对照字串：`focusInsetX: 12,`

## 演示与来源

![上游演示三个取样状态](../previews/focus-dim-spotlight.jpg)

[本地静音 HTML 演示](../upstream/demos/focus-dim-spotlight/index.html?embed=1) · [完整配方](../upstream/references/cards/focus-dim-spotlight.md) · [TSX](../upstream/template/cards/focus-dim-spotlight.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
