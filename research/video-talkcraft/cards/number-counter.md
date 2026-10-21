# 数字滚动计数 · number-counter

类别：数据信息图；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

口播给出一个较大的真实数量，需要在短时间内建立量级并明确最终读数。

语义关系：数量级呈现、数值收敛确认

## 避免误用

低至个位数的简单数量、逐笔账目差值，或将滚动误说成实际实时计算过程。

## 可见过程

1. 对象标签先建立
2. 主数字从零先快后慢趋近终值
3. 到达终值后轻压一拍
4. 单位或涨跌说明稍后落定
5. 滚轮变体由高位先停、低位补圈后收敛

配音落点：计数结束对齐报出最终金额或数量；滚轮应在同一句中完成，不能让讲述等数字转完。

## 关键限制与适配

- TSX轻压与涨跌起点写死在1.6、1.69秒，改countDur不会自动跟随，HTML则顺序衔接。
- 文档说字符串保位，但两端实现先Number(odoTarget)再格式化，前导零会丢失且超大整数有精度边界。
- 滚轮步长必须与行高一致，额外步数需整十圈，否则最终停错位。

V5 适配提示：仅将其作为数据卡的结论强调，重连时序并核验值、单位、期间，不把计数动画当计算证据。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 95 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/number-counter.tsx#L95)：TSX落定强调使用绝对秒数，计数时长参数改变后可能提前或延后强调。
  对照字串：`const scale = t < 1.69`
- [html 第 133 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/number-counter/index.html#L133)：HTML通过Number转换构造位数组，字符串输入不保证保留前导零。
  对照字串：`const groups = Number(numStr).toLocaleString("en-US").split("");`

## 演示与来源

![上游演示三个取样状态](../previews/number-counter.jpg)

[本地静音 HTML 演示](../upstream/demos/number-counter/index.html?embed=1) · [完整配方](../upstream/references/cards/number-counter.md) · [TSX](../upstream/template/cards/number-counter.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
