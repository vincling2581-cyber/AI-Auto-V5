# 线条接力转场 · line-carry-transition

类别：转场结构；研究用途：转场与章节结构；输入：场, 图, 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

前一段的下划线、进度线或数据线确能成为后一段容器，两个信息图形有明确亲缘关系时。

语义关系：图形角色转换、章节承接

## 避免误用

没有图形继承关系的任意换景不应靠一条线强连；插画间的持续横移和画框动画不符合 V5 静态硬切。

## 可见过程

1. A 标题出现并画出下划线
2. 同一条线继续向右，视窗同步横移
3. 线拐直角围成 B 的闭合画框
4. 笔头卸下，B 内容出现并与框共同保持

配音落点：A 的信息在横移前讲完，线的延伸接“由此进入下一部分”，框闭合后再让 B 的主语登场。

## 关键限制与适配

- 线生长量与相机位移不一致，笔尖会在画面漂移或跑出边界。
- B 先于框闭合出现，图形转换的悬念与因果会被打断。
- 示例横移跨两屏且世界坐标固定，换画幅须一起计算 run、画框中心和笔头轨迹。

V5 适配提示：仅作为 V5 信息卡间有语义继承的条件转场候选，先确认下划线到容器的意义；不得用于插画镜头或固定品牌包装。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 108 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/line-carry-transition.tsx#L108)：已描画路径长度由下划线与相机位置共同推导，保持线头相对视窗的位置。
  对照字串：`const L = Math.min(TOTAL, Math.max(u, camL(c)))`
- [html 第 90 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/line-carry-transition/index.html#L90)：HTML 在同一 apply 中写入世界位移、路径显示长度和笔尖坐标，避免各自补间失步。
  对照字串：`world.style.transform = \`translateX(${-o.c}px)\``

## 演示与来源

![上游演示三个取样状态](../previews/line-carry-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/line-carry-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/line-carry-transition.md) · [TSX](../upstream/template/cards/line-carry-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
