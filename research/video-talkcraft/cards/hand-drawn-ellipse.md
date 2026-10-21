# 手绘圈重点 · hand-drawn-ellipse

类别：强调标注；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

旁白明确要圈住一个短语并提高一次强调强度时。

语义关系：短语指认到重要性确认、圈定位置先于文字重音

## 避免误用

要框住整段，或标注对象没有独立短语盒、圈会切进邻字时。

## 可见过程

1. 短语先完整在场
2. 不规则椭圆一笔描出并过头交叉
3. 圈画完后短语轻微放大回落
4. 圈与文字一起静置供阅读

配音落点：“记住这几个字”先触发圈，语音重音落在圈后的短语确认。

## 关键限制与适配

- TSX 用预生成 ELLIPSE，换文字必须重算几何，HTML 会现场量墨迹盒。
- 完美 ellipse 会丢失过头交叉与外扩特征。
- 圈和字同时动会把指认与确认混成一次碰撞，横向留白也须防切字。

V5 适配提示：可用于卡内短语强调，保留两拍先后与阅读保持；不为追求手绘添加静帧抖动，不把圈叠到禁止图内动效的叙事插画。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 101 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/hand-drawn-ellipse.tsx#L101)：文字 punch 在描圈结束并留出间隙后启动。
  对照字串：`CONFIG.startDelay + CONFIG.draw + CONFIG.punchGap`
- [html 第 163 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/hand-drawn-ellipse/index.html#L163)：HTML 依实际字形墨迹盒生成圈，换词后需重新适配位置。
  对照字串：`ellipsePath(inkBoxOf(word), CONFIG)`

## 演示与来源

![上游演示三个取样状态](../previews/hand-drawn-ellipse.jpg)

[本地静音 HTML 演示](../upstream/demos/hand-drawn-ellipse/index.html?embed=1) · [完整配方](../upstream/references/cards/hand-drawn-ellipse.md) · [TSX](../upstream/template/cards/hand-drawn-ellipse.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
