# 双色块对句 · alt-block-lines

类别：字幕花字；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

口播提出两句短而对等的策略、前后状态或判断，需要观众同时读到它们的对应关系。

语义关系：两项对照、对等论点成组

## 避免误用

三项以上清单、主论点配注释，或两句之间没有可说明的对照关系。

## 可见过程

1. 第一行贴字宽色块从左铺开
2. 文字落后块边缘约两帧被裁切揭示
3. 第二行紧接同样展开，明暗与第一行相反
4. 两行一起保持，完成整组对照阅读

配音落点：第一块对齐第一项判断，第二块对齐与之对应的转折或后半句，保持覆盖两句说完。

## 关键限制与适配

- 字层与底块共缩放会压扁字形，省略裁切则出现字先于底块露出。
- 等宽或居中会变成表格、标志组，失去贴字宽且左对齐的对句骨架。
- 固定0.12秒错峰只属样例手感，真实两句间隔较长时须按口播重排。

V5 适配提示：作为双项关系卡候选，仅保留块与字的过程；换成单集真实文案并另留双句阅读时段。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 114 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/alt-block-lines.tsx#L114)：字的揭示进度独立计算且滞后底块，不是整块带字一起缩放。
  对照字串：`const txtP = tw(t, at + CONFIG.textLag`
- [html 第 101 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/alt-block-lines/index.html#L101)：HTML重播先把字完全裁去，再用同曲线揭示，块宽由原始排版决定。
  对照字串：`gsap.set(txts, { clipPath: "inset(0 100% 0 0)" });`

## 演示与来源

![上游演示三个取样状态](../previews/alt-block-lines.jpg)

[本地静音 HTML 演示](../upstream/demos/alt-block-lines/index.html?embed=1) · [完整配方](../upstream/references/cards/alt-block-lines.md) · [TSX](../upstream/template/cards/alt-block-lines.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
