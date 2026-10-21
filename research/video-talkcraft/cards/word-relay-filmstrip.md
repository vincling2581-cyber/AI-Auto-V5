# 动词接力胶片 · word-relay-filmstrip

类别：素材呈现；研究用途：证据与素材呈现；输入：图, 截图, 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

同一主体有多种能力或案例，每个动词都能配一张真实对应截图，需逐项解释并保留主体不变。

语义关系：同主体多能力列举、动词与证据一一对应

## 避免误用

每项主体不同、截图不支持对应动词，或用虚构作品图暗示本人已经完成项目。

## 可见过程

1. 名词固定，首个动词与首图建立对应
2. 旧词先变灰退出
3. 胶片同窗上移恰好一卡高度
4. 新动词在旧词消失后落位
5. 末词强调色收口，静置后图词同退

配音落点：每次换词起点对齐新的能力动词，步进跟随同一事件；实际截图可见内容应能支撑该动词。

## 关键限制与适配

- 文档称词期可不均匀，但当前swapAt是firstAt+i×period，非均匀时间需改成真实时刻表。
- verbs增加会自动延后退出，meta204帧却不自动增长；还需保证labels与srcs数量同步。
- 默认第五卡只是下方预露下一张，不是额外能力；胶片滚动只适用于卡片证据，不适于V5插画镜头。

V5 适配提示：把主体、能力、证据逐项核实并换成口播时刻表，阅读时胶片真静止，移除未有证据的默认AI能力宣告。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 107 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/word-relay-filmstrip.tsx#L107)：TSX所有切词点由均匀period计算，props没有直接接入不等间隔时刻。
  对照字串：`const swapAt = (i: number) => CONFIG.firstAt + i * CONFIG.period;`
- [html 第 99 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/word-relay-filmstrip/index.html#L99)：HTML只在换词窗口更新胶片位置，其他时间保持；旧词退出和新词落位存在明确先后。
  对照字串：`.to(strip, { y: CONFIG.startY - i * CONFIG.cardH`

## 演示与来源

![上游演示三个取样状态](../previews/word-relay-filmstrip.jpg)

[本地静音 HTML 演示](../upstream/demos/word-relay-filmstrip/index.html?embed=1) · [完整配方](../upstream/references/cards/word-relay-filmstrip.md) · [TSX](../upstream/template/cards/word-relay-filmstrip.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
