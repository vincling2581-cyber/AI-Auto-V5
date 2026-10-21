# 关注卡弹出 · x-follow-card

类别：人物互动；研究用途：人物出镜互动；输入：界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

介绍真实作者或账号时确需资料上下文，且用户明确要求演示关注交互时。

语义关系：人物资料到来源身份、点击关注到按钮与计数反馈

## 避免误用

用虚构粉丝数制造社会证明，或只是引用观点却强加关注动作时。

## 可见过程

1. 资料卡外壳弹入
2. 内容按阅读顺序错峰揭示
3. 光标移动到关注按钮并按下
4. 按钮两态交叉、涟漪与计数纸带更新
5. 短暂读结果后结束

配音落点：先说明这个人是谁，再在获准的关注引导处演示操作。

## 关键限制与适配

- 文档称壳完全到位后内容才落，实际内容 0.34 秒起入，早于 0.62 秒壳落定。
- TSX 使用固定 TARGET/TIP，HTML 需在终态量按钮；改资料布局会影响命中。
- 粉丝数加一只是演示状态，不能当成实际发生的关注事实。

V5 适配提示：只保留资料层次和可见反馈链的研究；V5 默认不采用 X 品牌、CTA 或伪计数，真实人物可另做来源卡，交互仅在本集明确授权后适配验证。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 259 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/x-follow-card.tsx#L259)：资料内容从外壳动画进行中起步，实际是交叠错峰而非全串行。
  对照字串：`const p = tw(t, 0.34 + i * C.layerStagger, C.layerDur, power2Out);`
- [html 第 378 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/x-follow-card/index.html#L378)：固定窗口内推动计数字带，表现演示计数更新而非真实网络操作。
  对照字串：`tl.to(strip, { y: -20, duration: C.rollDur`

## 演示与来源

![上游演示三个取样状态](../previews/x-follow-card.jpg)

[本地静音 HTML 演示](../upstream/demos/x-follow-card/index.html?embed=1) · [完整配方](../upstream/references/cards/x-follow-card.md) · [TSX](../upstream/template/cards/x-follow-card.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
