# 关键词弹出强调 · keyword-pop-highlight

类别：字幕花字；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

已有一行说明中某个数字、结论或反转词承担唯一信息峰值，需要短促视觉重音时。

语义关系：口播重音、单词强调

## 避免误用

不得把独立底部字幕随整屏移动，也不能把抖屏叠到静态插画；需要解释机制时单词弹大不构成语义过程。

## 可见过程

1. 正文先存在，关键词暂不出现
2. 关键词带底色快速放大并轻旋转
3. 放大峰值期间画面左右震动
4. 关键词回落到略大于正文的静止态

配音落点：关键词开始弹出的那帧对齐其口播重音；前面必须有可辨认的平淡句干，避免整句和重音同时砸入。

## 关键限制与适配

- stage 级震动会移动整个承载画面，直接复制会连人物及字幕一起横移。
- 关键词定格 1.15 倍会挤邻字，需按峰值 1.65 倍预留空间。
- 一句连续弹多个词会形成竞争重音，读不出哪一个承担结论。

V5 适配提示：V5 只考虑卡内独立关键词的重音确认，移除整屏震动并保护字幕固定位置；复杂含义仍用对象关系和连续过程说明。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 97 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/keyword-pop-highlight.tsx#L97)：TSX 把回落延至震动窗结束，关键词先到峰值再回到定格倍率。
  对照字串：`const settleAt = CONFIG.delay + 0.24`
- [html 第 73 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/keyword-pop-highlight/index.html#L73)：HTML 震动直接作用舞台容器，与关键词弹出同起，作用范围超出文字自身。
  对照字串：`.to(stage, {`

## 演示与来源

![上游演示三个取样状态](../previews/keyword-pop-highlight.jpg)

[本地静音 HTML 演示](../upstream/demos/keyword-pop-highlight/index.html?embed=1) · [完整配方](../upstream/references/cards/keyword-pop-highlight.md) · [TSX](../upstream/template/cards/keyword-pop-highlight.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
