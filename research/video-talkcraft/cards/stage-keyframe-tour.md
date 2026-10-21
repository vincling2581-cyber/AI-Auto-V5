# 长页兴趣点巡游 · stage-keyframe-tour

类别：运镜；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一份真实长页面或长截图包含几个已知重点，观众需要知道各重点在同一文档中的位置时。

语义关系：长页分区阅读、兴趣点导航

## 避免误用

长页全文精读、无明确兴趣点的自动漫游或 V5 插画连续运镜不适用；三维舞台不能代替证据真实性。

## 可见过程

1. 长页作为整体落在透视台面上
2. 相机按兴趣点路径到达首处重点
3. 重复同姿态关键帧留出局部讲解
4. 依次转到其他重点后拉开离场

配音落点：每个关键帧落点对齐“这里的这一栏”，重复姿态的时间覆盖解释，转移对应口播从一个版块进入另一版块。

## 关键限制与适配

- 动态原点须等于当前兴趣点，固定中心再凑位移会让缩放时横漂。
- 兴趣点横向偏离太大且放得过近会暴露纸边，长文本透视也会降低可读性。
- TSX 演示是源码绘制的假落地页，hostSrc 不代表通用长截图入口，换成真图要另做素材接入。

V5 适配提示：V5 只作为长文档证据的导航候选，优先保证原文与出处可读；可取消透视和装饰台面，不延伸到插画镜头。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 209 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/stage-keyframe-tour.tsx#L209)：TSX 从路径表插值兴趣点、缩放和倾角，相同姿态的连续项自然形成停留。
  对照字串：`let px = C.moves[0].px, py = C.moves[0].py`
- [html 第 294 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/stage-keyframe-tour/index.html#L294)：HTML 每帧把目标兴趣点设为变换原点并搬到画心，缩放与旋转围绕它发生。
  对照字串：`transformOrigin: ox + "px " + oy + "px"`

## 演示与来源

![上游演示三个取样状态](../previews/stage-keyframe-tour.jpg)

[本地静音 HTML 演示](../upstream/demos/stage-keyframe-tour/index.html?embed=1) · [完整配方](../upstream/references/cards/stage-keyframe-tour.md) · [TSX](../upstream/template/cards/stage-keyframe-tour.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
