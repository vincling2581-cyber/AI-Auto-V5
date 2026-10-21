# 标题降格成标签 · title-demote-to-label

类别：字幕花字；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

小节标题先需要被宣布，随后同一标题应留作内容的定位标签，下面还有少量要点待展开时。

语义关系：主题让位、小节路标、内容接续

## 避免误用

固定品牌、栏目或集数角标不属于这种语义路标；没有后续内容时标题无需缩到角落制造空动作。

## 可见过程

1. 章节标题居中由糊变清
2. 站稳后标题同时缩小并飞向内容栏左上
3. 降格后半程，要点块已在下面逐项长出
4. 小标题与要点共同保持，最终同收

配音落点：标题显影对齐章节名，降格对应“下面展开”，内容每条的开始对齐对应要点；先立路标再让出主阅读区。

## 关键限制与适配

- 位置与缩放分两段执行会显出先缩后飞的断裂。
- 居中修正量需随进度归零，否则落点偏移半个标题宽。
- TSX 内容数量影响退出时刻，但模板总帧数固定；增加要点必须同步更新合成时长，避免尾条被截。

V5 适配提示：适合 V5 卡内标题转为语义小节标签，保留要点逐步建立与阅读保持；标签随本段结束退出，不成为固定栏目角标。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/title-demote-to-label.tsx#L87)：居中修正、缩放与目标位置共用 d，在终点消除横向半宽修正。
  对照字串：`translate(${-(1 - d) * 50}%, -50%) scale(${s})`
- [html 第 72 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/title-demote-to-label/index.html#L72)：内容起点由降格起点延迟推出，允许标题后半程与首条内容短暂接力重叠。
  对照字串：`const growAt = demoteAt + CONFIG.growDelay`

## 演示与来源

![上游演示三个取样状态](../previews/title-demote-to-label.jpg)

[本地静音 HTML 演示](../upstream/demos/title-demote-to-label/index.html?embed=1) · [完整配方](../upstream/references/cards/title-demote-to-label.md) · [TSX](../upstream/template/cards/title-demote-to-label.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
