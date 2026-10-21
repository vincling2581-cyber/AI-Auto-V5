# 冲击开场 · impact-open-title

类别：字幕花字；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实主题可用一个短承诺句概括，需要在片头或少数章节建立强题眼。

语义关系：主题钩子、整句到核心词的聚焦

## 避免误用

复杂定义、证据长引文，或已经连续使用多次重标题而仍想靠砸字维持注意。

## 可见过程

1. 整句一次缩落显现
2. 四角框同起但较慢向内收
3. 末词稍后换色并轻压到位
4. 点阵更淡地出现
5. 副题补足主题后整屏保持

配音落点：整句对齐首次完整提问或承诺，末词对齐真正题眼；副题承接范围，不把装饰动作逐一对应口播。

## 关键限制与适配

- 所谓一次主砸仍含末词补拍，不能让角框、网格再增加独立重音。
- 细密点阵若参与卡层缩放可能产生亚像素爬行，上游也明确提示；当前插画更禁止相机运动。
- 标题与末词源码固定拆分，换句必须重新评估字宽，末词放大可能压到前字。

V5 适配提示：仅提取一屏一个主重音的卡片编排，按本集文案改写题眼；装饰角框非固定品牌或栏目角标。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 130 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/impact-open-title.tsx#L130)：TSX末词在整句落定后再补一拍，和主标题并非同帧首次放大。
  对照字串：`const wordAt = CONFIG.lead + CONFIG.slamDur + CONFIG.wordDelay;`
- [html 第 156 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/impact-open-title/index.html#L156)：HTML先在补拍起点设置末词大比例，再与换色一起缓回，因此需检查该帧的字距。
  对照字串：`tl.set(last, { scale: CONFIG.wordScale }, wordAt);`

## 演示与来源

![上游演示三个取样状态](../previews/impact-open-title.jpg)

[本地静音 HTML 演示](../upstream/demos/impact-open-title/index.html?embed=1) · [完整配方](../upstream/references/cards/impact-open-title.md) · [TSX](../upstream/template/cards/impact-open-title.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
