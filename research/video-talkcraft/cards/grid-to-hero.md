# 网格收成主角 · grid-to-hero

类别：素材呈现；研究用途：证据与素材呈现；输入：图, V

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

四个候选先建立并列关系，再突出其中一个，同时仍需看见落选对象作参照时。

语义关系：并列候选、主次重排、回到对照

## 避免误用

若没有真实候选选择关系，或目标只需单图说明，不应先造四格；插画素材不能随网格重排缩放。

## 可见过程

1. 四格按短错峰落位，观众先辨认全集
2. 目标长成左侧主图，其余同步收为右列
3. 主图承担讲解，小图保留对照
4. 全部同曲线回到四格，再共同退出

配音落点：重排起点对齐“我们最后选了这一版”，回网格对齐说明选取依据后的整体回顾，主图保持覆盖解释句。

## 关键限制与适配

- 主图长大与其余收缩必须同起同止，否则被读成两个无关动作。
- 示例主图还执行内部缓推，不属于选择关系必需机制，不能沿用到 V5 插画。
- 尺寸变化会裁掉素材局部，真实封面、评论或界面需检查主图与小图两种取景。

V5 适配提示：V5 可用于封面、截图等真实候选的选取说明，保留小图列和回到全体的过程；去掉未授权装饰性缓推。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 118 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/grid-to-hero.tsx#L118)：主图与小图从同一重排进度计算矩形，再用第二条进度还原网格。
  对照字串：`const p1 = tw(t, T1, C.reflow, power3InOut)`
- [html 第 90 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/grid-to-hero/index.html#L90)：HTML 对每格使用统一时长与缓动同步换位换尺寸，落选格保留右列。
  对照字串：`tiles.forEach((el, i) => tl.to(el, { ...target(i)`

## 演示与来源

![上游演示三个取样状态](../previews/grid-to-hero.jpg)

[本地静音 HTML 演示](../upstream/demos/grid-to-hero/index.html?embed=1) · [完整配方](../upstream/references/cards/grid-to-hero.md) · [TSX](../upstream/template/cards/grid-to-hero.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
