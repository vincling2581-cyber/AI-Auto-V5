# 图表生长 · chart-grow

类别：数据信息图；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有来源明确且口径一致的多期或多对象数值，口播按项目逐一比较。

语义关系：定标数量比较、逐项列举

## 避免误用

单位、统计口径不一致的数据，或只有情绪性大小判断而没有可核验数值。

## 可见过程

1. 坐标轴与图题先建立量纲
2. 柱子依列举次序从共同底线长出
3. 各柱接近到顶时显示数值
4. 关键柱着色，图形轻压一拍后保留全量比较

配音落点：柱子起长对齐各对象名称，数值出现对齐报数，强调落在结论而非每根柱子都抢拍。

## 关键限制与适配

- 量程必须全程固定，动画高度不能暗中变换分母或隐藏单位。
- 实现的lastTop按最后一列排程，最高柱移到中间后，轻压时刻仍跟最后一列而非最高柱。
- 上游68帧演示仅留很短读数尾段，不可直接当真实数据卡阅读时长。

V5 适配提示：数据、单位、来源改用本集材料并延长比较保持；整图轻压仅属卡片候选，绝不作用于插画。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 85 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chart-grow.tsx#L85)：收尾强调依最后一列索引排程，并未查找最大值或hot列。
  对照字串：`const lastTop = 0.55 + (COLS.length - 1)`
- [html 第 131 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chart-grow/index.html#L131)：HTML用固定maxVal换算每根柱高，生长只改变scaleY。
  对照字串：`const h = (parseFloat(col.dataset.v) / CONFIG.maxVal) * 100;`

## 演示与来源

![上游演示三个取样状态](../previews/chart-grow.jpg)

[本地静音 HTML 演示](../upstream/demos/chart-grow/index.html?embed=1) · [完整配方](../upstream/references/cards/chart-grow.md) · [TSX](../upstream/template/cards/chart-grow.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
