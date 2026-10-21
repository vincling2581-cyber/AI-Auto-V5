# 信息卡逐字段自建 · info-card-assemble

类别：素材呈现；研究用途：信息卡主体；输入：图, 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

介绍一本书、工具或人物，信息由封面、名称、标签、价格和要点分组构成，且口播按这些字段推进时。

语义关系：字段分组、结构化生成、重点抽取

## 避免误用

真实网页证据或复杂计算不能被自建卡替代；无内容依据的价格、标签和色卡不可为填满模板而保留。

## 可见过程

1. 封面与标题以小幅上移建立对象
2. 标签等小字段接续弹出，价格普通落位
3. 要点分行长出，关键行底块刷过
4. 色卡收齐，整卡保持后退出

配音落点：将字段落位收成“对象名称、属性、要点、结论”几组对齐口播，组内密错峰表现填充，不能逐字段机械点名。

## 关键限制与适配

- 示例帧表是按 60 帧配方换算的时间基，直接当 30fps 帧号会改变整段节奏。
- 整卡内置 1 到 1.06 前推，属于附加相机行为，不是字段结构化的必要部分。
- 相邻字段过密时只看见涌入而读不到内容，应按真实口播加组间阅读间隔。

V5 适配提示：适合 V5 对象信息卡的分字段构建，保留字段层级与高亮因果，删除无依据字段，取消无语义前推并留足阅读。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 104 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/info-card-assemble.tsx#L104)：以六十帧配方位置映射至秒，字段表不是当前 Remotion 的帧号。
  对照字串：`const F = (f: number) => (f / 60) * CONFIG.D`
- [html 第 89 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/info-card-assemble/index.html#L89)：大字段采用轻上移，小标签另用 scale 弹出，高亮行用 scaleX 刷过。
  对照字串：`const rise = (el, at) => tl.fromTo`

## 演示与来源

![上游演示三个取样状态](../previews/info-card-assemble.jpg)

[本地静音 HTML 演示](../upstream/demos/info-card-assemble/index.html?embed=1) · [完整配方](../upstream/references/cards/info-card-assemble.md) · [TSX](../upstream/template/cards/info-card-assemble.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
