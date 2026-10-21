# 点阵比例图 · unit-grid-proportion

类别：数据信息图；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

统计以每一百个个体中若干个为核心，需要直观看到分子与总数关系，而非只读百分号时。

语义关系：部分与整体、个体计数、比例可视化

## 避免误用

非人数比例、样本量并非一百或有多组不确定范围时不能把百格当真实样本；示意单位必须写清。

## 可见过程

1. 一百格从中心分环显出，位置保持不变
2. 右侧指标与标签出现
3. 从左上按阅读顺序染色，计数同阶段上升
4. 图例补足一格含义与剩余部分，最终保持

配音落点：染色阶段对齐“每一百个里有三十七个”，图例出现时补上所统计对象、时间范围和示意单位，不能省掉分母。

## 关键限制与适配

- 默认图例固定写三十七和六十三，修改 target 不会自动更正文案，数字与图例必须成组替换。
- 同一时间窗并不保证计数等于已完全染色格数，格子有 fillDur 过渡且计数用 round，逐帧会有短差。
- 目标数增大后染色总时长增加，而退出时刻固定，必须检查图例阅读窗是否仍够。

V5 适配提示：很适合 V5 比例信息卡，锁定分母、统计来源和一格含义，保留铺满、染色、计数与结论阅读过程，不按两秒截断。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 103 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/unit-grid-proportion.tsx#L103)：TSX 让前 n 格依阅读序逐一染色，目标值先四舍五入并钳制到百格范围。
  对照字串：`const f = i < n ? tw(t, CONFIG.fillStart + i * CONFIG.fillEach`
- [html 第 97 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/unit-grid-proportion/index.html#L97)：HTML 以染色总窗安排线性数字计数和随后图例；格色过渡与数值取整仍是不同算法。
  对照字串：`const fillTotal = CONFIG.target * CONFIG.fillEach`

## 演示与来源

![上游演示三个取样状态](../previews/unit-grid-proportion.jpg)

[本地静音 HTML 演示](../upstream/demos/unit-grid-proportion/index.html?embed=1) · [完整配方](../upstream/references/cards/unit-grid-proportion.md) · [TSX](../upstream/template/cards/unit-grid-proportion.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
