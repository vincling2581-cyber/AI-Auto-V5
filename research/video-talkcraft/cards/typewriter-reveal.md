# 打字机档案戳 · typewriter-reveal

类别：字幕花字；研究用途：信息卡主体；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

纪实、调查或事件回顾需要缓慢交代经过核验的时间地点和补充背景，逐条录入本身有叙事意义时。

语义关系：档案录入、时间地点交代

## 避免误用

高语速强调或普通整句字幕不宜逐字敲；默认日期、地点与巨大观看人数只是示例，不可带入新片。

## 可见过程

1. 主行以不等间隔逐字录入
2. 方块光标在行尾硬切闪三次
3. 延迟后光标移交第二行
4. 副信息录入，结尾光标继续闪烁

配音落点：主行对应“时间与地点”，副行对应该时刻的背景；打字结束后的空拍应服务档案停顿，而非迫使口播等待装饰。

## 关键限制与适配

- HTML 每次用 Math.random 重建时刻表，TSX 使用确定性随机，两个版本节奏不能视为逐帧等同。
- HTML 末尾无限 repeat，TSX 只给有限结束点加展示段，导出必须另定明确尾长。
- 等宽英文仍不保证中英全宽字符一致，混排和光标位置需按实际字体检查。

V5 适配提示：V5 可将其作为卡内档案字段的逐条建立方式，替换成已核验事实并限制尾部闪烁，不接管独立口播字幕。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 110 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/typewriter-reveal.tsx#L110)：TSX 预先生成时间表，逐帧数已到时刻控制文字数量，光标随后移交第二行。
  对照字串：`const n1 = TIMES1.filter((x) => t >= x).length`
- [html 第 68 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/typewriter-reveal/index.html#L68)：HTML 以每字随机偏差加入调用时刻，收尾光标另用无限 yoyo 闪烁。
  对照字串：`Math.random() * 2 - 1`

## 演示与来源

![上游演示三个取样状态](../previews/typewriter-reveal.jpg)

[本地静音 HTML 演示](../upstream/demos/typewriter-reveal/index.html?embed=1) · [完整配方](../upstream/references/cards/typewriter-reveal.md) · [TSX](../upstream/template/cards/typewriter-reveal.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
