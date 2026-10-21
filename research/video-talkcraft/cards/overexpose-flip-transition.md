# 过曝翻页转场 · overexpose-flip-transition

类别：转场结构；研究用途：转场与章节结构；输入：场

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

信息卡或证据段确有郑重的语义翻页，且曝光处理不会遮掉重要材料时。

语义关系：一段论证结束到下一段、交接切点到曝光重音

## 避免误用

V5 插画之间的换景，或仅为了刺激而给普通句末闪屏时。

## 可见过程

1. 旧画面向证据物推进
2. 曝光重音在切点前升至峰值
3. 峰值处交叠换入新画面
4. 曝光回落，新画面清晰落定

配音落点：句末收束重音与交接峰值同拍，新段信息等清晰后再展开。

## 关键限制与适配

- 白底实际默认 peak 为 0.10 压暗，文档的 0.42–0.55 过曝不能跨极性照抄。
- 峰值不是对称 yoyo，若时刻错位会先看到新画面再闪。
- 上游“相机永不静止”和次数配额不适用于 V5 插画。

V5 适配提示：仅作信息卡或证据交接的低优先候选，须确认底色与可读性；V5 插画仍硬切，不导入强制曝光、镜头慢推或整片次数规则。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 89 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/overexpose-flip-transition.tsx#L89)：曝光升段以切点倒推，峰值锚定在内容交接处。
  对照字串：`tw(t, cut - B.rise, B.rise, power2In)`
- [html 第 61 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/overexpose-flip-transition/index.html#L61)：白底示例采用较轻压暗包络，与深底过曝数值不同。
  对照字串：`peak: 0.10, rise: 0.26, fall: 0.42`

## 演示与来源

![上游演示三个取样状态](../previews/overexpose-flip-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/overexpose-flip-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/overexpose-flip-transition.md) · [TSX](../upstream/template/cards/overexpose-flip-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
