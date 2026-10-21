# 多图排版 + 焦点接力 · still-layout-relay

类别：素材呈现；研究用途：证据与素材呈现；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

三份真实材料关系可判断为一主两辅或平级并列，口播需要逐张解释后再合看。

语义关系：主图与佐证归属、并列对象焦点接力、局部回到整体

## 避免误用

关系未定就先套版式，或拿三张完整插画作缩放压暗接力来延长同景。

## 可见过程

1. 主图或首图先落，其他材料同向错峰跟入
2. 图注建立各材料身份
3. 当前材料保持亮，其他材料轻缩暗退后
4. 焦点随口播依次接力
5. 讲完全部复原，整组保持再退出

配音落点：各次接力对齐对应材料名及解说，全部复原对齐“综合这些证据”，避免最后一张被误认唯一结论。

## 关键限制与适配

- 默认tour连演两式，真实镜头应明确单选layout与durationFor。
- 主图内部还叠全段缓推，外部接力缩放与内部相机缩放是两层，可能累计裁切证据边缘。
- TABLE按固定秒数排站，替换材料和口播后必须一起调整relays、reset、exitAt，不能只换srcs。

V5 适配提示：仅对证据卡作关系排版与定位，必要时关闭主图内部缓推；上游全部同时淡入即坏的评价不写入工程标准。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 149 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/still-layout-relay.tsx#L149)：TSX将回位设为特殊站点，最后恢复全部材料而非一直强调最后一项。
  对照字串：`const stations: [number, number][] = [...L.relays, [L.reset, -1]];`
- [html 第 135 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/still-layout-relay/index.html#L135)：HTML主图内部另有从lead持续到退场的缩放轨，独立于外框焦点接力。
  对照字串：`if (heroPic) tl.to(heroPic, { scale: CONFIG.heroPush`

## 演示与来源

![上游演示三个取样状态](../previews/still-layout-relay.jpg)

[本地静音 HTML 演示](../upstream/demos/still-layout-relay/index.html?embed=1) · [完整配方](../upstream/references/cards/still-layout-relay.md) · [TSX](../upstream/template/cards/still-layout-relay.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
