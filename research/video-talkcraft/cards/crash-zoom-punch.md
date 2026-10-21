# 急推特写 · crash-zoom-punch

类别：强调标注；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

截图中的一处短文字确需由全景迅速切换为阅读焦点时。

语义关系：整页证据到单处关键文字、语音指认到目标特写

## 避免误用

要保持多个位置的对照，或对象是 V5 静态叙事插画时。

## 可见过程

1. 整页先显示以建立位置
2. 围绕目标文字中心急推并短暂模糊
3. 小幅回收至同一目标构图
4. 落定清晰后静置阅读

配音落点：“就是这一行”对应急推，随后停运动再讲该行含义。

## 关键限制与适配

- 目标应取文字块而非整行，否则容易推向空白。
- 相机只钳舞台边界，目标靠卡边会露出底色。
- 两档缩放必须共用目标中心；上游次数限制仅是来源偏好。

V5 适配提示：只列为证据截图的条件候选，先核对分辨率、目标坐标和阅读余量；禁止移植到插画图内，是否使用须经本集适配验证。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 88 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/crash-zoom-punch.tsx#L88)：冲入与回收使用相同目标中心，构成一次连续指认。
  对照字串：`const a = camTo(CONFIG.zoom, px, py), b = camTo(CONFIG.settle, px, py);`
- [html 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/crash-zoom-punch/index.html#L87)：推进集中在短促加速段，而非持续缓推。
  对照字串：`duration: CONFIG.punch, ease: "power3.in"`

## 演示与来源

![上游演示三个取样状态](../previews/crash-zoom-punch.jpg)

[本地静音 HTML 演示](../upstream/demos/crash-zoom-punch/index.html?embed=1) · [完整配方](../upstream/references/cards/crash-zoom-punch.md) · [TSX](../upstream/template/cards/crash-zoom-punch.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
