# 章节进度 · chapter-progress-list

类别：转场结构；研究用途：信息卡主体；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

较长内容需要交代总共有几段、当前讲哪一段及后续还剩什么时，用目录中的单项升级建立坐标。

语义关系：整体目录、当前位置、剩余路径

## 避免误用

只有一句短标题或两个简单分句时不必撑出完整目录；高亮多行也不能再称为当前章节。

## 可见过程

1. 章节名与多行目录错峰进入
2. 所有条目站定，保留未激活文字可读
3. 当前行换色、圆点出现并前进少许
4. 四角标记收入，目录保持供阅读

配音落点：目录先随“分成四部分”出现，单行高亮对齐“现在到第二部分”，不在目录尚未成形时抢先点名。

## 关键限制与适配

- 未选行再叠低透明度会损失目录全貌，需用足够对比的实色。
- TSX 的 ROWS 与当前项在源码中固定，不是任意章节表的即插即用组件。
- 暗场和电影角框服务章节停顿，但不能把它们转成全片固定栏目装饰。

V5 适配提示：可用于 V5 长语义段的章节信息卡，保留当前项唯一性；仅在需要目录坐标时采用，去掉无语义的角框也应复核层级。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 121 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chapter-progress-list.tsx#L121)：高亮时刻由最后条目进入完成后再加延迟算出，先建立全集再定位。
  对照字串：`CONFIG.rowStagger * (ROWS.length - 1)`
- [html 第 127 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chapter-progress-list/index.html#L127)：重播先还原当前行颜色，再在 hlAt 换色并单独让当前行前进。
  对照字串：`gsap.set([curNo, curName], { color: CONFIG.dim })`

## 演示与来源

![上游演示三个取样状态](../previews/chapter-progress-list.jpg)

[本地静音 HTML 演示](../upstream/demos/chapter-progress-list/index.html?embed=1) · [完整配方](../upstream/references/cards/chapter-progress-list.md) · [TSX](../upstream/template/cards/chapter-progress-list.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
