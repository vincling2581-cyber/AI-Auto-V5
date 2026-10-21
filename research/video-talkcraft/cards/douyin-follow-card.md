# 抖音主页关注卡 · douyin-follow-card

类别：人物互动；研究用途：人物出镜互动；输入：界, 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

介绍一个真实作者或账号，确需演示进入主页后关注的动作，并有可用身份材料时。

语义关系：人物来源介绍、关注状态改变

## 避免误用

单纯引用观点不应擅自加关注 CTA；合成主页、虚构粉丝或模仿点击不能作为已关注和社会认可的证据。

## 可见过程

1. 主页卡壳先弹入，头像与身份信息依次显清
2. 光标沿弧线到达关注按钮
3. 点击同帧按钮换态、涟漪出现，副按钮改为私信
4. 光标离开，主页数据保持不变

配音落点：身份出现对齐“这位作者是谁”，点击只在口播明确有关注动作时发生，不能给纯引用凭空附加背书。

## 关键限制与适配

- HTML 需在终态量按钮再减光标尖偏移，入场缩放态测量会点空。
- 文档说简介整块一层，TSX 注释仍写每行分档，替换多行简介须核对实际分层。
- 粉丝数固定不加一；样例账号和数据均是内容占位，不能继承为事实。

V5 适配提示：在 V5 默认仅保留真实作者来源的介绍结构，去除关注互动和产品固定装饰；明确需要关注演示的单集再另行适配。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 262 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/douyin-follow-card.tsx#L262)：TSX 以固定按钮目标减去光标尖偏移，点击位置随示例几何锁定。
  对照字串：`const target = { x: TARGET.x - TIP.x`
- [html 第 207 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/douyin-follow-card/index.html#L207)：点击时刻统一触发光标下压、按钮两态交叉和私信展开，粉丝数未参与动画。
  对照字串：`const tc = C.cursorStart + C.cursorMove + 0.08`

## 演示与来源

![上游演示三个取样状态](../previews/douyin-follow-card.jpg)

[本地静音 HTML 演示](../upstream/demos/douyin-follow-card/index.html?embed=1) · [完整配方](../upstream/references/cards/douyin-follow-card.md) · [TSX](../upstream/template/cards/douyin-follow-card.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
