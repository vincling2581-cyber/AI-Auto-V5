# 推穿转场 · push-through-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

证据或卡片素材之间确需从概念推进到具体细节，且另行允许相机尺度变化时。

语义关系：概念推进到证据、跨素材景别承接

## 避免误用

V5连环插画换景，或为了不静止而在所有边界默认推拉、交叉淡化。

## 可见过程

1. 旧素材先缓慢推近
2. 旧层加速放大并失焦
3. 新层在交叠期由模糊高倍率显现
4. 新层倍率回落且解糊
5. 到位后接一小段缓推保持

配音落点：交叠对齐“具体来看、进入这个细节”等语义推进，展示结果后须让细节重新清晰可读。

## 关键限制与适配

- 两侧同属推近轴是叙述命名，代码实际旧层倍率增加而新层回落，不能据此声称连续单镜头。
- 转场使用重叠、失焦与保持期慢推，整套与V5静态插画硬切冲突。
- 放大裁边会改变证据可见范围，关键单位或来源不能在转场后被裁掉。

V5 适配提示：只保留为证据或卡层的条件转场候选，不移植上游硬切必坏、相机永不停的判断到V5。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 79 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/push-through-transition.tsx#L79)：TSX将像素交叉淡化进度与倍率、模糊进度分开计算。
  对照字串：`const bOpacity = tw(t, cut, P.overlap, power1InOut);`
- [html 第 79 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/push-through-transition/index.html#L79)：HTML在旧层放大完成前开始新层交叠，而入场沉降另用settle时长。
  对照字串：`const cut = at + P.out - P.cutLead;`

## 演示与来源

![上游演示三个取样状态](../previews/push-through-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/push-through-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/push-through-transition.md) · [TSX](../upstream/template/cards/push-through-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
