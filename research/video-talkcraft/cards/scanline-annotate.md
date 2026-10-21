# 扫描线逐处点名 · scanline-annotate

类别：强调标注；研究用途：证据与素材呈现；输入：截图, 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

同一真实截图有少量从上到下分布的点评点，需要统一扫描过程建立位置与标注的对应。

语义关系：多处证据定位、扫描到命名、累积标注

## 避免误用

把装饰扫描包装成实际AI识别完成，或多个同行目标的右侧标注会互相覆盖。

## 可见过程

1. 扫描线从截图上方匀速下降
2. 越过目标下缘后取景框收拢并轻确认
3. 标注稍晚在独立列出现
4. 已指出的标注保留且计数增加
5. 扫描结束后全部共同保持再收尾

配音落点：扫描速度按每个点评的实际口播反推，框对齐目标被提到，标注承接命名与解释。

## 关键限制与适配

- 触发有最小间隔钳制，后续框可能晚于扫描线实际越过目标，并非每次都严格同刻。
- labelLag0.17秒小于bkDur0.4秒，命名在框完全收稳前已开始，与“框稳了才命名”的字面要求有差距。
- done只按扫描结束加延迟判断，密集多目标被钳迟时可能先显示完成，不能当检测验证。

V5 适配提示：用真实截图、重测目标坐标，去掉会误导为实际分析结果的状态话术；标注保持到讲完，插画层不加扫描。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 106 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/scanline-annotate.tsx#L106)：TSX基于目标下缘算原始触发后又钳最小间距，密集目标的触发会被延后。
  对照字串：`fts.push(i ? Math.max(raw, fts[i - 1] + CONFIG.gap) : raw);`
- [html 第 83 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/scanline-annotate/index.html#L83)：HTML标签延后约五帧，但框收拢0.4秒，二者实际有重叠而非严格串行。
  对照字串：`labelLag: 0.17,`

## 演示与来源

![上游演示三个取样状态](../previews/scanline-annotate.jpg)

[本地静音 HTML 演示](../upstream/demos/scanline-annotate/index.html?embed=1) · [完整配方](../upstream/references/cards/scanline-annotate.md) · [TSX](../upstream/template/cards/scanline-annotate.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
