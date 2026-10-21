# 色块扫屏转场 · shape-wipe-transition

类别：转场结构；研究用途：转场与章节结构；输入：场, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

信息卡之间确有章节切分，且需要一个明显翻页信号时。

语义关系：上个话题到下个话题、遮挡完成到内容替换

## 避免误用

静态插画切换、细密推理中间，或只为掩盖前后语义不连贯时。

## 可见过程

1. 旧场景先保持
2. 同方向多层色块错峰扫入
3. 全遮挡窗口内替换下一场景
4. 色块同向扫走后新内容再展开

配音落点：上一话题说完再扫屏，下一话题等完全揭示后开始。

## 关键限制与适配

- 换场时刻必须落在真正覆盖区，层宽不足会从缝里露出画面。
- 三色随意跨色系会比内容更显眼。
- TSX sceneB 在阈值后持续存在，HTML 用一次 call 切换，交互跳播语义不能直接等同。

V5 适配提示：仅保留信息卡边界和遮挡时刻的研究，选用须本集另验；插画层只硬切，不新增固定扫屏、品牌色条或按句号触发的换景规则。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 131 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/shape-wipe-transition.tsx#L131)：内容替换用确定阈值判断，遮挡层与场景显示分开控制。
  对照字串：`const sceneBOn = t >= swapAt;`
- [html 第 158 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/shape-wipe-transition/index.html#L158)：换场安排在中层色块经过中心的覆盖窗口。
  对照字串：`CONFIG.layerDelay + CONFIG.wipeDur / 2`

## 演示与来源

![上游演示三个取样状态](../previews/shape-wipe-transition.jpg)

[本地静音 HTML 演示](../upstream/demos/shape-wipe-transition/index.html?embed=1) · [完整配方](../upstream/references/cards/shape-wipe-transition.md) · [TSX](../upstream/template/cards/shape-wipe-transition.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
