# 人物缩位让台 · host-shrink-to-chip

类别：人物互动；研究用途：人物出镜互动；输入：人(必需), 文, 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

明确采用真人讲解且有连续视频，需从人物主画面交接到证据图时。

语义关系：讲者主体到图形主体的交接、同一讲者连续存在与舞台让位

## 避免误用

V5 当前只有静态角色插画，或没有获准的人物同屏交互需求时。

## 可见过程

1. 人物全屏口播先建立主体
2. 人物缩放与裁切同步收成角落圆窗
3. 图形稍晚从另一侧接位
4. 圆窗位置锁定，图形成为阅读中心

配音落点：“我把图摆出来”触发人物先让位，图进入后说明证据。

## 关键限制与适配

- 只缩人物而不裁窗会成为角上悬浮小人。
- 裁切与位移分开排期会让人脸在中途挤出圆窗。
- 占位与真实 hostSrc 不等价，静态头像不能证明口型连续。

V5 适配提示：只作额外真人路线的条件研究，不纳入本集插画默认；不新增固定头像角标，若授权使用需避开字幕和图形，验证取景连续性。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 108 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/host-shrink-to-chip.tsx#L108)：裁切与人物几何共享同一缩位进度，形成连续交接。
  对照字串：`const p = tw(t, CONFIG.startDelay, CONFIG.shrink, power2InOut);`
- [html 第 186 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/host-shrink-to-chip/index.html#L186)：图形入场晚于人物启动，避免双方同时争夺注意。
  对照字串：`CONFIG.startDelay + CONFIG.gfxLag`

## 演示与来源

![上游演示三个取样状态](../previews/host-shrink-to-chip.jpg)

[本地静音 HTML 演示](../upstream/demos/host-shrink-to-chip/index.html?embed=1) · [完整配方](../upstream/references/cards/host-shrink-to-chip.md) · [TSX](../upstream/template/cards/host-shrink-to-chip.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。

取样限制：本地取样缩位后圆内未见人物，不能据此确认裁剪和锚点正确；使用真实人物素材时需单独核对。
