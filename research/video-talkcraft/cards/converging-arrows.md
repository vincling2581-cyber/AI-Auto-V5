# 双箭头聚焦 · converging-arrows

类别：强调标注；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

已有文字中只有一个关键词需要被明确指认，并能在对角方向留下干净箭头路径时。

语义关系：双向指认、单一焦点

## 避免误用

同屏多个同等关键词、整行宽目标或缺乏空白跑道时不宜强夹，箭杆穿字会把指向误读成划除。

## 可见过程

1. 目标先以普通黑字存在
2. 两条不同弧度的箭杆近乎同时描出
3. 各自箭头须接续杆尾完成
4. 较慢箭尖到位后目标换色并保持

配音落点：箭杆起笔对应“注意这里”，箭尖完成对应具体词；目标换色只确认指向完成，不应先行吸引箭头。

## 关键限制与适配

- 文档称换色硬切，但 TSX lerpColor 和 HTML color tween 都用 0.1 秒插值，需按实际效果判断。
- HTML 量目标盒，TSX 将 CONFIG.box 固定；换文案后不能照用原箭尖坐标。
- 两箭错峰过大变成两次强调，镜像复制则失去手绘的不对等形态。

V5 适配提示：可作为 V5 信息卡已有关键词的定向标注；先测真实词框并留箭尖空隙，不把箭头叠进静态插画造成图内动效。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 166 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/converging-arrows.tsx#L166)：TSX 等最迟箭头完成才线性换色，实际有持续时间而非一帧硬切。
  对照字串：`const colorP = tw(t, allTipsAt, CONFIG.colorDur`
- [html 第 156 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/converging-arrows/index.html#L156)：HTML 运行时测量关键词盒，再生成弧形箭杆和按末端切线计算的箭须。
  对照字串：`const box = boxOf(word)`

## 演示与来源

![上游演示三个取样状态](../previews/converging-arrows.jpg)

[本地静音 HTML 演示](../upstream/demos/converging-arrows/index.html?embed=1) · [完整配方](../upstream/references/cards/converging-arrows.md) · [TSX](../upstream/template/cards/converging-arrows.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
