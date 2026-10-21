# 素材弹入堆叠 · media-pop-in

类别：素材呈现；研究用途：证据与素材呈现；输入：图, 截图, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

几份真实截图或照片需快速建立“有多项材料”的集合，随后还能读关键证据时。

语义关系：多份证据到同一主张、逐项列举到同屏共存

## 避免误用

每份材料都有长文需要独立阅读，或要以堆叠数量替代证据质量时。

## 可见过程

1. 第一张证据带静态倾角弹入
2. 后续证据紧密错峰拍上
3. 后来材料压住前一张边角
4. 全组落位后留作证据集合

配音落点：旁白列举材料时逐张出现，核心证据需再留独立阅读段。

## 关键限制与适配

- 示例照片区在源码内，hostSrc 不是任意证据图片注入接口。
- 重叠不能遮住所引用的关键文字、日期或来源。
- 默认全组有循环呼吸，不能把示例的持续缩放当作 V5 必需保持。

V5 适配提示：可研究多证据集合的次序与共存关系，替换可核对原图并控制遮挡；必要时分卡讲清，去除无意义呼吸，不对插画做弹入缩放。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 94 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/media-pop-in.tsx#L94)：单张以带过冲的缩放落位表现拍放动作。
  对照字串：`const p = tw(t, at, CONFIG.popDur, backOut(CONFIG.overshoot));`
- [html 第 110 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/media-pop-in/index.html#L110)：演示落位后整组无限呼吸，属于需要取舍的装饰运动。
  对照字串：`repeat: -1, yoyo: true`

## 演示与来源

![上游演示三个取样状态](../previews/media-pop-in.jpg)

[本地静音 HTML 演示](../upstream/demos/media-pop-in/index.html?embed=1) · [完整配方](../upstream/references/cards/media-pop-in.md) · [TSX](../upstream/template/cards/media-pop-in.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
