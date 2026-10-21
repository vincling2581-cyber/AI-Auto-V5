# 照片墙推轨 · gallery-wall-dolly

类别：素材呈现；研究用途：证据或卡片运镜；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

三项平级案例需要逐一讲完，再回到共同全貌确认它们并列关系时。

语义关系：平级案例巡览、局部到整体

## 避免误用

因果链或时间阶段不宜挂成同等照片墙；V5 叙事插画不能以三维透视墙、相机推轨或图内微推播放。

## 可见过程

1. 全景先交代三张素材的并列位置
2. 镜头对准第一张并推近，其余压暗失焦
3. 依次停靠其他案例，目标内部保持微推
4. 拉回全景，三图恢复清晰后共同退出

配音落点：每次到站对齐案例名称，停靠时长覆盖该案例的解释；拉回全貌对齐“这三种都属于……”的归纳。

## 关键限制与适配

- 墙面旋转后必须使用投影中心，未变换的平面坐标会让每站偏心。
- 演示要求停靠期内部微推以防静止，这是上游审美偏好，不能覆盖 V5 信息阅读保持。
- 全景缩放应按投影边界校核，否则近端第三张会被裁切。

V5 适配提示：仅作为 V5 多份外部证据的条件化巡览候选；普通对比优先保持可读平面，取消无语义微推并重新审片。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 107 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/gallery-wall-dolly.tsx#L107)：目标先经墙旋转坐标修正，再反解缩放和平移把每张素材送至画心。
  对照字串：`camTo(C.stopZ, wallX(cx), 270)`
- [html 第 93 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/gallery-wall-dolly/index.html#L93)：HTML 在停靠时仍放大目标内部图像，区别于单纯移动相机到站后静置。
  对照字串：`tl.to(phs[i], { scale: C.push`

## 演示与来源

![上游演示三个取样状态](../previews/gallery-wall-dolly.jpg)

[本地静音 HTML 演示](../upstream/demos/gallery-wall-dolly/index.html?embed=1) · [完整配方](../upstream/references/cards/gallery-wall-dolly.md) · [TSX](../upstream/template/cards/gallery-wall-dolly.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
