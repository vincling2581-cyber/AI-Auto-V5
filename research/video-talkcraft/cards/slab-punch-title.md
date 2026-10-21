# 重点放大 · slab-punch-title

类别：字幕花字；研究用途：卡内强调标注；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

两段短标题有明确铺垫与重点，需用空色块先成形再让结论词落定。

语义关系：铺垫与重点结论、介质差分层

## 避免误用

两句对等比较，或长句被装进斜块导致阅读困难并把必要限定条件删掉。

## 可见过程

1. 第一行小幅缩落显现
2. 稍停后空色块从中心撑开
3. 色块完全到位
4. 白字硬现并在块内轻压到终态
5. 两行保持形成铺垫与重点

配音落点：第一行跟铺垫词，空块准备发生在转折，白字出现对齐真正结论词；不在块铺开中先漏出字。

## 关键限制与适配

- 第一行虽被文档叫硬现，实际仍有0.18秒透明度过渡，真正零帧切换仅白字。
- 块和字同scaleX会扭曲字形；从左刷块再落字还会混成两种不同语法。
- 斜切是静态形状，不能把回正或抖动当手作；块padding需与第一行文字基线一起校正。

V5 适配提示：只取卡层铺垫到结论的串行，使用真实语义短词；保持足量阅读，斜块不得变成栏目常驻包装。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 118 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/slab-punch-title.tsx#L118)：TSX白字透明度采用条件硬切，其起点等于色块动画结束。
  对照字串：`const l2Opacity = t < punchAt ? 0 : 1;`
- [html 第 125 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/slab-punch-title/index.html#L125)：HTML在punchAt以set露字，再做5帧左右缩落；块与文字独立控制。
  对照字串：`tl.set(l2, { opacity: 1 }, punchAt);`

## 演示与来源

![上游演示三个取样状态](../previews/slab-punch-title.jpg)

[本地静音 HTML 演示](../upstream/demos/slab-punch-title/index.html?embed=1) · [完整配方](../upstream/references/cards/slab-punch-title.md) · [TSX](../upstream/template/cards/slab-punch-title.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
