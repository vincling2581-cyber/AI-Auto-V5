# 缓推特写 · slow-push-in

类别：运镜；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实证据截图较清晰，长句解释中确需缓慢收拢到一处且仍保留足够上下文时。

语义关系：整份截图到兴趣点的收拢、主推阶段到末速延续

## 避免误用

密集文字必须全页阅读，或对象是 V5 叙事插画时。

## 可见过程

1. 页面以原始尺度和固定兴趣点出现
2. 主阶段轻缓推进并小幅修正构图
3. 以主推末速延续剩余保持
4. 整段单向结束，不中途折返

配音落点：完整说明一页证据时只用一条视线曲线，不按每个词追加缩放。

## 关键限制与适配

- 固定 transform-origin 改变会造成页面跳位。
- 低分辨率截图放大后文字发虚，运动不能弥补原图质量。
- 上游把静止判作失败是自身系统规则，V5 信息卡可以保持，不能泛化。

V5 适配提示：只作证据截图或卡片的条件镜头候选，必须优先可读性和来源完整；不强制常动，不移动底部字幕，更不能给静态插画施加缩放。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 113 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/slow-push-in.tsx#L113)：保持阶段仍以末速延伸尺度，区别于普通缓出后停住。
  对照字串：`const holdZoom = CONFIG.zoomTo + rate * CONFIG.holdDur;`
- [html 第 162 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/slow-push-in/index.html#L162)：兴趣点通过页面几何计算并作为固定推进支点。
  对照字串：`transformOrigin: ox + "px " + oy + "px"`

## 演示与来源

![上游演示三个取样状态](../previews/slow-push-in.jpg)

[本地静音 HTML 演示](../upstream/demos/slow-push-in/index.html?embed=1) · [完整配方](../upstream/references/cards/slow-push-in.md) · [TSX](../upstream/template/cards/slow-push-in.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
