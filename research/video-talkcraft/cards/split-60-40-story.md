# 60/40 主从分屏 · split-60-40-story

类别：素材呈现；研究用途：信息卡主体；输入：人(可选), V, 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

一段真实录屏或实拍是主信息，旁边少量要点补充观看任务而非与左侧平等比较。

语义关系：主素材与辅助要点、同步解释列举

## 避免误用

两个同等对象的对比，或完整V5插画被放在左侧并照模板持续缓推。

## 可见过程

1. 左侧主素材先在60%区域展示
2. 右栏标题升入
3. 要点签按口播逐枚落下
4. 素材与要点同时保留供来回核对
5. 标题、要点和素材以尾对齐方式收齐

配音落点：要点出现对齐“完成了什么、注意哪项”，主素材中的事件要能对应说明，不能任意配三条卖点。

## 关键限制与适配

- 说明允许四条，但当前CHIP_TOP只有三项且n取最小值，直接传第四条会被静默舍弃。
- src只走视频组件，静态图须另改适配，hostSrc还会优先覆盖src。
- 模板左格全程缓推会裁边并改变证据范围；上游的必须不断运动不能成为V5插画规则。

V5 适配提示：提取主从关系布局，左格真实素材按任务决定是否运动；要点与来源一致，去掉占位亮带及演示文案。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 101 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/split-60-40-story.tsx#L101)：TSX实际最多渲染三个签，第四条不会因props数组增长而自动有位置。
  对照字串：`const n = Math.min(chips.length, CHIP_TOP.length);`
- [html 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/split-60-40-story/index.html#L87)：HTML按文字数量反算退场起点，最后一项和素材在同一end收完。
  对照字串：`const textOut0 = CONFIG.end - CONFIG.exit - chips.length * CONFIG.stagger;`

## 演示与来源

![上游演示三个取样状态](../previews/split-60-40-story.jpg)

[本地静音 HTML 演示](../upstream/demos/split-60-40-story/index.html?embed=1) · [完整配方](../upstream/references/cards/split-60-40-story.md) · [TSX](../upstream/template/cards/split-60-40-story.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
