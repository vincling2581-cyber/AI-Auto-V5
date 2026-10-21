# 准星咬合 · reticle-lock-on

类别：强调标注；研究用途：卡内强调标注；输入：截图, 图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真实截图中只需点名一个按钮、数字或条款，旁白有明确“就是它”的重音时。

语义关系：整页证据到单个指定对象、先到位再咬合的重音确认

## 避免误用

同镜要连续标很多处，或目标只是没有出处的演示按钮时。

## 可见过程

1. 整页先让观众建立位置
2. 四个角从远处同时飞到大框位置
3. 大框二次缩小过头后回弹锁住目标
4. 锁定帧目标微亮并出现解释标签
5. 整组静置留阅读

配音落点：四角飞入作准备，“就是这个”落在咬合与标签出现处。

## 关键限制与适配

- 飞入和收缩若合并就丢掉先到再锁的两拍。
- target 相对截图左上角，不能直接传舞台坐标。
- 目标常驻白色微亮可能冲淡原文字，使用真实图时须另查对比。

V5 适配提示：只作证据或卡内单对象的指认候选，验证坐标、标签留白和原文可读；不把四角锁定叠到叙事插画，也不替换实际证据内容。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 83 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/reticle-lock-on.tsx#L83)：锁定由飞入和收缩完成共同定义，标签重音共享该节点。
  对照字串：`const LOCK = CONFIG.at + CONFIG.fly + CONFIG.shrink;`
- [html 第 91 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/reticle-lock-on/index.html#L91)：收缩过头后再弹回标准框，产生一次咬合确认。
  对照字串：`duration: CONFIG.snap, ease: "back.out(2)"`

## 演示与来源

![上游演示三个取样状态](../previews/reticle-lock-on.jpg)

[本地静音 HTML 演示](../upstream/demos/reticle-lock-on/index.html?embed=1) · [完整配方](../upstream/references/cards/reticle-lock-on.md) · [TSX](../upstream/template/cards/reticle-lock-on.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
