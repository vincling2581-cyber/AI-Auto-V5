# 终端逐行推进 · terminal-typing-log

类别：素材呈现；研究用途：证据与素材呈现；输入：人(可选), 界

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

技术口播需清楚区分人输入命令、机器输出日志以及成功或失败结果，且有真实可核对记录时。

语义关系：命令触发、日志推进、执行结果

## 避免误用

自演日志不能当实际执行或测试通过的证据；面向不需要命令细节的观众，不必为了技术感逐行刷屏。

## 可见过程

1. 命令逐字符打出
2. 机器日志以小簇接续跳出
3. 溢出后缓冲区整行上跳
4. 省略号行冻结一段再继续
5. 末尾结果行出现，完成行光标撤去

配音落点：命令对应“我执行这个操作”，省略号对应仍在等待的真实阶段，末行对齐实际结果；不可拿合成悬停冒充耗时。

## 关键限制与适配

- 默认十一行内容在 CONFIG 内硬编码，演示的成功行不是当前环境运行结果。
- 滚动加平滑补间会变成网页阅读，和终端整行刷新机制不一致。
- 命令与日志若使用同样粒度，会混淆输入和输出；完成后继续闪光标也会制造仍在运行的误解。

V5 适配提示：V5 使用真实日志建立时序，可按需删掉无信息行但保存完整证据；最终状态与机器检查、正常速度审片分别记录。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 172 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/terminal-typing-log.tsx#L172)：每当可见行数外的新行开始，TSX 直接跳一整行高度，不插值滚动。
  对照字串：`const ty = -steps * CONFIG.lineHeight`
- [html 第 207 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/terminal-typing-log/index.html#L207)：HTML 按行的 chunk 将线性计数取整成簇，光标只在该行未完成时存在。
  对照字串：`Math.ceil(linear / s.chunk) * s.chunk`

## 演示与来源

![上游演示三个取样状态](../previews/terminal-typing-log.jpg)

[本地静音 HTML 演示](../upstream/demos/terminal-typing-log/index.html?embed=1) · [完整配方](../upstream/references/cards/terminal-typing-log.md) · [TSX](../upstream/template/cards/terminal-typing-log.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
