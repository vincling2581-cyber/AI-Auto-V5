# 对角角框 · corner-bracket-frame

类别：强调标注；研究用途：卡内强调标注；输入：文, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

需要给一块短论点定题，强调的是整句话而非截图坐标时。

语义关系：整句观点与其强调边界、先划范围再给题名

## 避免误用

必须点到证据里的具体按钮，或需要强烈命中感时。

## 可见过程

1. 两个对角 L 从外侧同步进入
2. 角框先建立一块阅读范围
3. 两行题名按顺序进入框内
4. 整组静置供阅读

配音落点：旁白提出本段论点时出现边界，关键词随后落在框内。

## 关键限制与适配

- 四角框会改变为取景或锁定语义，与此卡的整句定题不同。
- 文字在框起步后 0.22 秒进，框本身用 0.3 秒，文档“先立住”并非严格串行。
- 加下划线或多种强调色会产生互相竞争的边界信号。

V5 适配提示：可保留同步对角边界和分行阅读，按本集文字块重算尺寸；标题属于卡内语义，不作为固定栏目角标，静置保持不受插画两秒规则限制。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 106 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/corner-bracket-frame.tsx#L106)：两个角框共享同一进度，避免左右错拍。
  对照字串：`const brP = tw(t, t0, CONFIG.brIn, power3Out);`
- [html 第 106 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/corner-bracket-frame/index.html#L106)：HTML 用单一 tween 同时把两个角框送到位。
  对照字串：`t.to([tl, br], { opacity: 1, x: 0, y: 0`

## 演示与来源

![上游演示三个取样状态](../previews/corner-bracket-frame.jpg)

[本地静音 HTML 演示](../upstream/demos/corner-bracket-frame/index.html?embed=1) · [完整配方](../upstream/references/cards/corner-bracket-frame.md) · [TSX](../upstream/template/cards/corner-bracket-frame.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
