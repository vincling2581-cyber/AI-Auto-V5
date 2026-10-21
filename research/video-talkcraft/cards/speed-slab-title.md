# 速度块标题 · speed-slab-title

类别：字幕花字；研究用途：卡内强调标注；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

内容真实表达提速、抢先或效率，且是短标题的语义重音时。

语义关系：速度主题到视觉惯性线索、先立主标题再给副题重音

## 避免误用

冷静结论、长句阅读，或没有速度含义却只想套一个动感标题时。

## 可见过程

1. 主标题先轻量落位
2. 斜切副题块从画外冲入
3. 块内文字滞后追赶到位
4. 停止帧短速度线展开后迅速淡尽
5. 完整标题静置

配音落点：先说主题词，提速相关副题在色块冲入时落重音。

## 关键限制与适配

- 块起点不够远会一开始就在画内，失去冲入前提。
- 文字滞后需要父子两层坐标与裁切，不能同一 transform 上相加。
- 残影线留下太久会变装饰符号；源码颜色不能当作固定 V5 品牌色。

V5 适配提示：只研究文字块内部的速度表意，不套用底部字幕或叙事插画；保留短标题阅读，速度线按本集内容决定，不能用动感替代论证过程。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 137 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/speed-slab-title.tsx#L137)：块内文字有独立追赶位移，使色块和文字出现惯性差。
  对照字串：`const slabTX = lerp(-CONFIG.lagPx, 0,`
- [html 第 165 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/speed-slab-title/index.html#L165)：速度线在块到位时才启动，表达残影而非全程装饰。
  对照字串：`const lineAt = slabAt + CONFIG.slabDur;`

## 演示与来源

![上游演示三个取样状态](../previews/speed-slab-title.jpg)

[本地静音 HTML 演示](../upstream/demos/speed-slab-title/index.html?embed=1) · [完整配方](../upstream/references/cards/speed-slab-title.md) · [TSX](../upstream/template/cards/speed-slab-title.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
