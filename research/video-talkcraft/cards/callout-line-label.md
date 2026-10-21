# 标注引出线 · callout-line-label

类别：强调标注；研究用途：卡内强调标注；输入：图, 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

旁白明确点到截图、产品图或地图的某个部位，且附近有标签留白时。

语义关系：截图具体部位到名称解释、多个目标的先后指认

## 避免误用

标签只是无定位的观点，或多个长标签会遮住证据本体时。

## 可见过程

1. 圆点在目标位置弹亮
2. 折线从圆点沿拐点向外描出
3. 线端标签展开并补入文字
4. 下一目标错峰指认，阅读后反向收回

配音落点：“这里”“这个部位”触发圆点，名称在标签揭示时说出。

## 关键限制与适配

- 标签先出会让答案抢在视线引导之前。
- 45 度与水平折线要据真图重新布点，不能原样套手机占位坐标。
- 标签只淡入会失去从线端展开的方向关系。

V5 适配提示：保留点到线再到字的指认过程；替换真实对象并绑定坐标，给信息卡足够阅读保持，底部字幕另留空间，不采纳上游固定颜色。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 145 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/callout-line-label.tsx#L145)：线条起点由圆点时长推导，支持先定位再引线。
  对照字串：`const tLine = t0 + CONFIG.dotIn;`
- [html 第 73 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/callout-line-label/index.html#L73)：标签有独立揭示阶段，不能把点线文字当作整组淡入。
  对照字串：`labelIn: 0.25`

## 演示与来源

![上游演示三个取样状态](../previews/callout-line-label.jpg)

[本地静音 HTML 演示](../upstream/demos/callout-line-label/index.html?embed=1) · [完整配方](../upstream/references/cards/callout-line-label.md) · [TSX](../upstream/template/cards/callout-line-label.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
