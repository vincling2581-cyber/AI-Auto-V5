# 五选一反黑 · chip-grid-single-select

类别：数据信息图；研究用途：信息卡主体；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

先让观众读完少量候选，再揭晓一个选择，随后解释选中它带来何种结果时。

语义关系：候选取舍、唯一选择、选择后的结果

## 避免误用

多个候选同时成立、逐项讲解或还会移动焦点的比较不应用单选反黑，因为它会暗示其他项已落选。

## 可见过程

1. 问题与候选芯片先铺开供读题
2. 一帧灰闪后选中项反黑并轻回弹
3. 其余项原位降权，选中态单独保持
4. 选中项上移归中，结果算式逐词加深

配音落点：反黑落在口播说出被选项的字上；收束等观众确认选择后，再对应“选了它之后……”的推论。

## 关键限制与适配

- 非选项移动或缩走会被读成消失而非未被选择。
- 上移必须补偿选中项原有横坐标，否则黑块留在原列。
- 选项建议不超过六项；selected 越界和过长文字没有自动适配，需改内容后复核。

V5 适配提示：适合 V5 决策到因果的信息卡，把候选、选中确认和后果分成连续状态，阅读时间随选项长度调整。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 116 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chip-grid-single-select.tsx#L116)：用正弦构造起止均为一的轻按压回弹，选中项再按同一 lift 进度移位。
  对照字串：`const bounce = 1 + Math.sin(pr * Math.PI)`
- [html 第 84 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chip-grid-single-select/index.html#L84)：用选择与收束两段时间界限，先保留原位落选项，再移走并显出算式。
  对照字串：`const FS = CONFIG.FS, LIFT = FS + CONFIG.lift`

## 演示与来源

![上游演示三个取样状态](../previews/chip-grid-single-select.jpg)

[本地静音 HTML 演示](../upstream/demos/chip-grid-single-select/index.html?embed=1) · [完整配方](../upstream/references/cards/chip-grid-single-select.md) · [TSX](../upstream/template/cards/chip-grid-single-select.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
