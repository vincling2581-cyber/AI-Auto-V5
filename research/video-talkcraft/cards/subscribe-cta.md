# 多平台关注 CTA · subscribe-cta

类别：人物互动；研究用途：人物出镜互动；输入：人(可选), 界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

用户明确要求加入关注引导，且平台和操作含义已经确认时。

语义关系：移动与按压到关注状态、长按过程到依次完成的反馈

## 避免误用

没有 CTA 授权，或正片内容尚未完成却要常驻营销控件时。

## 可见过程

1. 所选平台控件入场
2. 光标沿可见路径移到操作目标
3. 点击或长按并显示进度
4. 按钮换态、图标或对勾确认
5. 结果短停后退出

配音落点：仅在真实邀请关注的句子上演示操作，不覆盖知识说明。

## 关键限制与适配

- 演示连续播放三种平台，不等于成片应全部加入。
- B 站版的长按进度和依次点亮不能误改成一次同时成功。
- 程序状态变化只是示意交互，不代表真实完成关注或订阅。

V5 适配提示：仅记录交互反馈链，V5 默认不采纳 CTA、品牌皮肤或次数要求；只有本集明确授权后选择单一场景，且不得作为固定角标或遮住字幕。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 277 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/subscribe-cta.tsx#L277)：订阅结果由点击后的独立阈值决定，状态变化跟在按压后。
  对照字串：`const subDone = t >= TC_A + 0.08;`
- [html 第 448 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/subscribe-cta/index.html#L448)：通用关注版用路径描出确认对勾，而非直接贴静态字符。
  对照字串：`tl.to(tickPath, { strokeDashoffset: 0`

## 演示与来源

![上游演示三个取样状态](../previews/subscribe-cta.jpg)

[本地静音 HTML 演示](../upstream/demos/subscribe-cta/index.html?embed=1) · [完整配方](../upstream/references/cards/subscribe-cta.md) · [TSX](../upstream/template/cards/subscribe-cta.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
