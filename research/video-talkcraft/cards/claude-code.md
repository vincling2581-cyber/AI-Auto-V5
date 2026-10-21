# 编码智能体终端 · claude-code

类别：素材呈现；研究用途：证据与素材呈现；输入：界, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

材料足以展示一次真实编码智能体执行链，需解释读文件、改文件与结果的因果时。

语义关系：任务命令到工具调用、调用结果到代码改动再到结论

## 避免误用

只有产品名称或宣传口号，或无法核对示例执行记录时。

## 可见过程

1. 终端外壳与身份区域错峰就位
2. 用户命令逐字输入并提交
3. 工具调用和缩进返回成簇出现
4. 删除新增差异接上，末行给出结论

配音落点：命令对应任务，工具与返回各讲一件事，最后才说明结果。

## 关键限制与适配

- 逐字打机器日志会混淆人输入和 stdout 的语法。
- 结果不缩进会被读成无关的并列日志。
- 上游品牌、模型和 cwd 为示例，不能据此宣称本集实际用过该工具。

V5 适配提示：保留命令、调用、返回、差异、结果的结构，使用可核对记录或明确重演；不将终端皮肤、品牌吉祥物或示例成功状态变为 V5 必备项。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 338 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/claude-code.tsx#L338)：机器日志按固定块跳出，与用户命令逐字输入区分。
  对照字串：`Math.ceil(linear / CONFIG.logChunk) * CONFIG.logChunk`
- [html 第 373 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/claude-code/index.html#L373)：预留日志行位置，出现时不重排整个终端。
  对照字串：`row.row.style.visibility = on ? "visible" : "hidden";`

## 演示与来源

![上游演示三个取样状态](../previews/claude-code.jpg)

[本地静音 HTML 演示](../upstream/demos/claude-code/index.html?embed=1) · [完整配方](../upstream/references/cards/claude-code.md) · [TSX](../upstream/template/cards/claude-code.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
