# 动态人名条 · chevron-lower-third

类别：人物互动；研究用途：人物出镜互动；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有真实嘉宾首次发言，需要短暂交代姓名及经核验的单行身份。

语义关系：人物身份归属、姓名与资历配对

## 避免误用

无人物的视频固定品牌角标、长期栏目条，或把未经核验资历当信任背书。

## 可见过程

1. 姓名从左推出
2. 身份底签稍后展开，签内文字再落下
3. 三枚箭头在底签成形后密集扫亮
4. 姓名与头衔完整保持
5. 整组更快地从左收回

配音落点：姓名出现对齐介绍人物或其首次开口，资历跟随确有依据的身份句，撤回让出正文阅读。

## 关键限制与适配

- 签内文字若跟背景一起scaleX会变形，必须独立于背景缩放层。
- 箭头早于底签完成或错峰过稀，会从延伸收尾变成零散装饰。
- 下方位置必须按本集字幕安全区重新计算；上游固定底部数值不能直接继承。

V5 适配提示：只在本集确有嘉宾身份任务时重做为临时人物说明，不渲染栏目、品牌或集数常驻角标。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 120 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/chevron-lower-third.tsx#L120)：TSX把箭头收尾锁在身份底签完成之后，再统一计算撤回时刻。
  对照字串：`const chevAt = chipAt + CONFIG.chipDur;`
- [html 第 130 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/chevron-lower-third/index.html#L130)：HTML将签内文字比签背景延后约两帧，姓名、底签与箭头分工明确。
  对照字串：`chipAt + CONFIG.chipTxtLag`

## 演示与来源

![上游演示三个取样状态](../previews/chevron-lower-third.jpg)

[本地静音 HTML 演示](../upstream/demos/chevron-lower-third/index.html?embed=1) · [完整配方](../upstream/references/cards/chevron-lower-third.md) · [TSX](../upstream/template/cards/chevron-lower-third.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
