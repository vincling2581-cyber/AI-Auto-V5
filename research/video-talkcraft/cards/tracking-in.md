# 字距收拢 · tracking-in

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一行短标题需要一次庄重归位，背景足够清楚且随后能保持阅读时。

语义关系：分散字符到完整标题、字距收拢到视觉聚焦

## 避免误用

多行解释、常规字幕，或内容需要讲对象关系而非标题情绪时。

## 可见过程

1. 大字以松字距和模糊态出现
2. 同一弹簧进度同时收字距与解模糊
3. 较短的独立淡入先完成
4. 字距缓慢咬到终态后静置

配音落点：完整题名出现时强调主题，不需要让每字对应一个口播音节。

## 关键限制与适配

- 字距与模糊分两条曲线会读成先排好再对焦。
- 初始松字距很宽，长标题可能被画幅裁两端。
- 源码 spring 接近临界阻尼但并非数学上的严格零过冲，文档“零回弹”是观感描述。

V5 适配提示：可研究卡内短标题的聚焦手感，不作用底部字幕或静态插画；字数、字距、字号按本集可读性决定，不采纳固定一片次数和品牌落版。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 75 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/tracking-in.tsx#L75)：字距和模糊都读取同一个 spring 变量 s，形成一次归位。
  对照字串：`const blur = CONFIG.startBlur * (1 - s);`
- [html 第 99 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/tracking-in/index.html#L99)：以 em 手动写字距，保持换字号后的比例关系。
  对照字串：`el.style.letterSpacing = sp.toFixed(4) + "em";`

## 演示与来源

![上游演示三个取样状态](../previews/tracking-in.jpg)

[本地静音 HTML 演示](../upstream/demos/tracking-in/index.html?embed=1) · [完整配方](../upstream/references/cards/tracking-in.md) · [TSX](../upstream/template/cards/tracking-in.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。

取样限制：跳转取样的后段仍有模糊；源码弹簧存在轻微过冲且 blur 未钳制，随机跳转不能证明最终清晰度。正式适配应统一进度并检查逐帧清晰度。
