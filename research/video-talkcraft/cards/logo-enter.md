# Logo 登场 · logo-enter

类别：素材呈现；研究用途：卡内强调标注；输入：文, 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

本集确有一个产品或机构作为解释对象，需要短暂建立其标识与名称对应。

语义关系：图标与实体命名、身份收束

## 避免误用

把上游片头片尾规范当V5默认固定品牌包装，或在每张卡反复出现标识。

## 可见过程

1. 圆牌携标识一起缩放落定
2. 主名称从圆牌侧边稍后推出
3. 副行再错一拍补充
4. 描环合拢收口
5. 全部静止成为终帧

配音落点：标识入场对齐实体首次命名，名称与副行跟身份信息；收口对应介绍结束，不另制造高潮。

## 关键限制与适配

- 上游建议系列固定片头片尾，与V5无常驻品牌要求不等同，不能自动套用。
- 代码用backOut近似spring而非真实物理弹簧，替换求解器后时长过冲要重新检视。
- 只有圆牌应过冲，字标也弹会产生多个重音；环未合完就撤走则像加载未完成。

V5 适配提示：默认不采用品牌收尾；仅在语义上确需介绍对象且本集明确选择时，改成短暂实体标识卡。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 96 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/logo-enter.tsx#L96)：TSX用同一近似弹性进度驱动圆牌属性，并将透明度另行夹到合法范围。
  对照字串：`const badgeP = tw(t, C.lead, C.badgeDur, backOut(C.badgeBack));`
- [html 第 117 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/logo-enter/index.html#L117)：HTML描环长度比周长多3px防接缝，环有明确终态而非无限loading。
  对照字串：`const len = ring.getTotalLength() + 3;`

## 演示与来源

![上游演示三个取样状态](../previews/logo-enter.jpg)

[本地静音 HTML 演示](../upstream/demos/logo-enter/index.html?embed=1) · [完整配方](../upstream/references/cards/logo-enter.md) · [TSX](../upstream/template/cards/logo-enter.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
