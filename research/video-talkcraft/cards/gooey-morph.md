# 图块拼入 · gooey-morph

类别：素材呈现；研究用途：信息卡主体；输入：图, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

要一次建立几张独立案例、平台或对象属于同一组的印象，组内没有先后步骤。

语义关系：并列证据成组、多图汇聚

## 避免误用

按时间逐项解释的流程，或需要看清小图正文却把六张材料挤成一条。

## 可见过程

1. 多张图从远离人物的一侧错时进入
2. 每图先横移到所属列
3. 再竖直落到统一行位
4. 图块几乎相接成居中横排
5. 拼齐后保持原图清晰不再形变

配音落点：入场覆盖“这几个案例、这组平台”，拼齐落在集合名词之后；不是按左到右配逐项口播。

## 关键限制与适配

- 卡ID仍叫gooey-morph，但定版已无粘液融化或融字，不能由名称推断实现。
- 先后两轴若合并成同一插值会退成斜飞，失去归列再落行的拼入过程。
- 起飞次序刻意打乱，不适于表达步骤顺序；多图尺寸变小还可能损失证据可读性。

V5 适配提示：只在卡片中用于真实素材组汇聚；完整叙事插画仍逐张硬切，不能以缩略图拼入替代插画镜头。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 147 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/gooey-morph.tsx#L147)：TSX先完成x进度，再由后半段驱动y，路径是分轴L形而非液化滤镜。
  对照字串：`const kx = Math.min(1, k * 2);`
- [html 第 162 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/gooey-morph/index.html#L162)：HTML按虚拟时间求每张图的两轴位置，拼齐后没有后续融字处理。
  对照字串：`const ky = Math.max(0, k * 2 - 1);`

## 演示与来源

![上游演示三个取样状态](../previews/gooey-morph.jpg)

[本地静音 HTML 演示](../upstream/demos/gooey-morph/index.html?embed=1) · [完整配方](../upstream/references/cards/gooey-morph.md) · [TSX](../upstream/template/cards/gooey-morph.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
