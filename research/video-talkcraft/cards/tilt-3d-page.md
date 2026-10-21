# 3D 立面展示 · tilt-3d-page

类别：运镜；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实网页或 UI 的整体外观本身是展示对象，且不必逐字读倾斜后的正文时。

语义关系：页面信息到产品物件的身份转换、正视阅读到立面展示

## 避免误用

要核查条款细字、图表精确数值，或对象是 V5 插画时。

## 可见过程

1. 页面正视停留建立内容身份
2. 页面在父级透视空间倾斜并略缩
3. 投影同步加深并向反侧偏移
4. 立面形态保持，示例续转展示

配音落点：“这是完成后的页面”先给正视，转向整体作品介绍再立起。

## 关键限制与适配

- 倾角过大会让远端正文不可读，不能同时承诺细节阅读。
- 变换元素自身加 perspective 与父空间透视含义不同。
- hostSrc 参数未用；立起后的持续微转是上游偏好，非 V5 保持要求。

V5 适配提示：只作证据页面或产品卡的条件候选，先区分阅读与外观展示；不要给插画做透视或视差，是否保留续转需经本集适配，不作为默认镜头。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 148 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/tilt-3d-page.tsx#L148)：投影浓度与立起进度共享变化，构成物件浮起感。
  对照字串：`shOp = lerp(C.shadowFrom, C.shadowTo, p);`
- [html 第 182 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/tilt-3d-page/index.html#L182)：倾斜时同时后退尺度，避免页面角点顶出画幅。
  对照字串：`rotateY: CONFIG.rotYTo, rotateX: CONFIG.rotXTo, scale: CONFIG.scaleTo`

## 演示与来源

![上游演示三个取样状态](../previews/tilt-3d-page.jpg)

[本地静音 HTML 演示](../upstream/demos/tilt-3d-page/index.html?embed=1) · [完整配方](../upstream/references/cards/tilt-3d-page.md) · [TSX](../upstream/template/cards/tilt-3d-page.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
