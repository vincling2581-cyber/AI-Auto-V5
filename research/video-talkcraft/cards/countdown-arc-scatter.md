# 数字弧落标题 · countdown-arc-scatter

类别：字幕花字；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

数字本身构成开场悬念，例如时长承诺或数量揭晓，想先表现从相邻倒数里停在一个数时。

语义关系：数字揭晓、候选收束、标题组装

## 避免误用

统计量已经给定、精确数值证据或需要真实计时的倒计时不宜套用，转盘只是标题揭晓结构。

## 可见过程

1. 相邻递减数字沿弧扫入视野并急停
2. 被选数停在弧顶，其余数失焦淡出
3. 选中数平移回正进入标题首位
4. 后续词重叠解糊，末词换色并静置

配音落点：扫停锚定念出数字的音节，数字落入词组后紧接“分钟、做成什么”，动作应组成同一句承诺。

## 关键限制与适配

- pick 不在 numbers 时索引回退到零，但标题槽仍显示 pick，可能出现两个数不一致。
- 其余数若加位移散射，会与唯一选中数争夺动作方向。
- 标题宽度通过测量确定，换长词须确认落点与隐形数字槽，不以改字号掩盖溢出。

V5 适配提示：可作 V5 数量型标题的语义过程；只放信息卡文字，承诺数应有事实依据，落定后保留整句阅读保持。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 88 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/countdown-arc-scatter.tsx#L88)：索引决定弧顶选中对象，当前仅以零索引兜底，需保证 pick 实际存在。
  对照字串：`const pickIdx = Math.max(0, numbers.indexOf(pick))`
- [html 第 106 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/countdown-arc-scatter/index.html#L106)：同一 hand 进度同时移动与回正选中数，其他数字只执行失焦退出。
  对照字串：`.to(o, { hand: 1, duration: CONFIG.handDur`

## 演示与来源

![上游演示三个取样状态](../previews/countdown-arc-scatter.jpg)

[本地静音 HTML 演示](../upstream/demos/countdown-arc-scatter/index.html?embed=1) · [完整配方](../upstream/references/cards/countdown-arc-scatter.md) · [TSX](../upstream/template/cards/countdown-arc-scatter.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
