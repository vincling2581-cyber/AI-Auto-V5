# 逐字裂升 · split-text-stagger

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一行短章节题或要点标题需要明确的版式化入场，随后有完整阅读时间时。

语义关系：字符接续到完整标题、基线生长与末字落定同步

## 避免误用

连续口播字幕、多行长文，或要把逐字动画当成信息解释时。

## 可见过程

1. 基线与首字从同一时刻启动
2. 各字在自己的行高裁切盒内接续升起
3. 基线长满与末字落定对齐
4. 副标补出，整组静置后同收

配音落点：标题短语完整读出，副标只补充必要限定，不逐字追着口播跑。

## 关键限制与适配

- HTML over 参数注释称约 10% 过冲，文档与计算曲线约为 5.3%，不能据注释承诺视觉强度。
- 裁切盒高过大就退化成普通位移，基线失去生成关系。
- 基线时长随字数计算，但副标和退出固定，长标题会挤掉阅读保持。

V5 适配提示：可用于卡内短标题，不改独立口播字幕；标题与副标保留事实限制，按实际字数重新安排保持，不把纯入场效果视作增强卡的语义过程。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 75 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/split-text-stagger.tsx#L75)：基线总时长覆盖每字错峰和最后一字行程。
  对照字串：`const growDur = CONFIG.dur + CONFIG.stagger * (chars.length - 1);`
- [html 第 61 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/split-text-stagger/index.html#L61)：每字从裁切盒下方起升，呈现被基线逐渐露出的效果。
  对照字串：`yPercent: 115`

## 演示与来源

![上游演示三个取样状态](../previews/split-text-stagger.jpg)

[本地静音 HTML 演示](../upstream/demos/split-text-stagger/index.html?embed=1) · [完整配方](../upstream/references/cards/split-text-stagger.md) · [TSX](../upstream/template/cards/split-text-stagger.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
