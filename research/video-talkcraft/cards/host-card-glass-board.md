# 人物竖卡玻璃台 · host-card-glass-board

类别：人物互动；研究用途：人物出镜互动；输入：人(必需), 文, 界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

已经有需要持续出镜的竖屏讲解人，同时右侧要按口播展开两到四步短流程或工具链时。

语义关系：人物持续讲解、步骤接力、流程结果

## 避免误用

无主持人需求、长段正文或需要精读的界面截图不宜放进透视玻璃板；不能为套样式凭空加入人物。

## 可见过程

1. 人物竖卡与透视板入场，板面反光扫一次
2. 板头建立流程主题
3. 步骤块逐个出现，线条连接相邻位置
4. 结果胶囊落下后整体保持并同收

配音落点：每块道具出现对齐步骤名，结果胶囊对齐流程产出；先讲清节点再确认关系，不能让装饰反光占据关键口播。

## 关键限制与适配

- 文档要求两端 tile 落定再连线，实际首线 2.05 秒起而第二块 2.5 秒才起，存在先指空处的差异。
- 示例默认含 TALKCRAFT 期数和装饰水印，不能随组件带入 V5。
- 三步时刻与结果固定，扩成四步时结果可能早于末块完成，须重排时间表。

V5 适配提示：仅在本集确需讲解人时借用人与流程同台结构，去品牌和期数；流程节点、关系与产出另按 V5 语义过程锁定。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 176 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/host-card-glass-board.tsx#L176)：连线只依据前一块时刻加 0.45 秒，并未等待下一块落定。
  对照字串：`const connAt = tileAt(i) + CONFIG.connDelay`
- [html 第 126 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/host-card-glass-board/index.html#L126)：玻璃板独立绕轴显影，人物卡正面滑入，sheen 另排一次扫光。
  对照字串：`.to(board, { rotateY: CONFIG.rot`

## 演示与来源

![上游演示三个取样状态](../previews/host-card-glass-board.jpg)

[本地静音 HTML 演示](../upstream/demos/host-card-glass-board/index.html?embed=1) · [完整配方](../upstream/references/cards/host-card-glass-board.md) · [TSX](../upstream/template/cards/host-card-glass-board.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
