# 界面流程剧场 · ui-flow-theater

类别：素材呈现；研究用途：信息卡主体；输入：界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

确需说明一套短操作流程，能准确建模每次点击、拖拽与结果，且明确示意界面时。

语义关系：操作动作到控件换态、多步操作到最终保存反馈

## 避免误用

需要原生实测证据，或假 UI 的功能与真实产品未经核对时。

## 可见过程

1. 界面和区块先揭示
2. 光标依脚本移动到开关并点击
3. 继续选分段并拖滑杆，值同步变化
4. 保存后按钮成功，稍晚系统 toast 回应

配音落点：一步旁白对应一次操作和一个状态变化，成功提示跟在最后操作之后。

## 关键限制与适配

- 上游首个光标 1.28 秒起步，而末区块约 1.93 秒才落定，存在入场与操作交叠。
- HTML 运行时反算 POS，TSX 是固定测量坐标，换布局必须重新测。
- 示意成功 toast 不能被当作真实软件测试通过。

V5 适配提示：可优先研究单一时间表驱动操作与结果的因果链，依据真实流程重建并标注示意；保留中间态及阅读，界面不采固定品牌，不对插画使用相机运动。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 267 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/ui-flow-theater.tsx#L267)：光标移动由同一 STEPS 操作时刻倒排，避免单独手数时间。
  对照字串：`moves.push({ t0: s.at - CONFIG.hoverHold - dur, dur, to: POS[s.target] });`
- [html 第 453 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/ui-flow-theater/index.html#L453)：控件响应读取同一操作步骤，点击和换态共享剧本。
  对照字串：`RESPOND[step.target](t, step);`

## 演示与来源

![上游演示三个取样状态](../previews/ui-flow-theater.jpg)

[本地静音 HTML 演示](../upstream/demos/ui-flow-theater/index.html?embed=1) · [完整配方](../upstream/references/cards/ui-flow-theater.md) · [TSX](../upstream/template/cards/ui-flow-theater.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
