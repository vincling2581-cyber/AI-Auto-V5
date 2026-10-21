# 画中画放大 · pip-zoom-box

类别：运镜；研究用途：证据与素材呈现；输入：人(可选), 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

讲解截图、产品或动作的具体局部，需要把该处搬到旁侧长期看，同时保持原全景作为出处时。

语义关系：局部提取、全景与细节并存

## 避免误用

仅短暂巡视的放大镜需求、缺少足够分辨率的源图或叙事插画，不宜通过复制放大搬运制造动态镜头。

## 可见过程

1. 原素材上取景框先出现并瞄准一拍
2. 框与其中同源内容一起移向侧边放大
3. 落定时细框交接成白边卡和投影
4. 箭头回指关系建立，局部与全景共同保持

配音落点：取景框对齐“这一块”，搬运对齐“拎出来看”，落定后再解释细节；箭头只确认出处，不要先指向空白目的地。

## 关键限制与适配

- 框与内容分两条补间会失步，起始副本裁切也须与全景像素连续。
- HTML 用同步计时对齐双视频，但仍需验证实际帧一致，代码读取不等于同步播放通过。
- 默认 faceX/faceY 和目标几何固定，更换截图局部必须重算锚点与裁切边界。

V5 适配提示：V5 可用于真实界面证据的局部抽取，保留原图出处和足够清晰度；侧卡落定后静置，不对静态插画应用移动或放大。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 128 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/pip-zoom-box.tsx#L128)：TSX 用同一 pT 同时计算框的尺寸、中心与放大倍率，统一几何来源。
  对照字串：`const zoom = lerp(1, C.zoom, pT)`
- [html 第 186 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/pip-zoom-box/index.html#L186)：HTML 一次更新函数补偿局部副本位置，边框与内容随同一进度搬运。
  对照字串：`onUpdate: () => setPip(p.t)`

## 演示与来源

![上游演示三个取样状态](../previews/pip-zoom-box.jpg)

[本地静音 HTML 演示](../upstream/demos/pip-zoom-box/index.html?embed=1) · [完整配方](../upstream/references/cards/pip-zoom-box.md) · [TSX](../upstream/template/cards/pip-zoom-box.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
