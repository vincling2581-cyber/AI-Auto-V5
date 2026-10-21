# 打字改口 · error-retype

类别：字幕花字；研究用途：卡内强调标注；输入：文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

原材料本身含有一次误解、更正或自我修正，且前后短语字数相近时。

语义关系：错误判断到修正结论、犹豫与果断纠错的时间差

## 避免误用

需要同时比较新旧两项，或不应先展示错误说法的严肃信息时。

## 可见过程

1. 固定句干先在场
2. 错误半句按字打出
3. 停顿闪光标后更快退字
4. 正确半句重打，光标退去后保持

配音落点：旁白先说误解，再在退字处完成转折，正确说法落定后解释。

## 关键限制与适配

- 固定宽槽位针对相近字数，长短差太大容易留下异常空隙。
- TSX 用 Math.floor 阶梯显示，加入缓动淡入会变成加载感。
- 文档写条件摘除光标，TSX 实际保留 span 并将 opacity 归零，属于视觉消失。

V5 适配提示：只表达已有的纠错关系，不能为了动画编一个错误观点；保持正确结论阅读，不用于底部口播字幕，也不把示例反转文案当本集事实。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 93 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/error-retype.tsx#L93)：删除按离散字符阶梯进行，速度与首次输入分开。
  对照字串：`first.length - 1 - Math.floor((t - tDel) / CONFIG.del)`
- [html 第 83 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/error-retype/index.html#L83)：犹豫和完稿分别安排两次短闪，而非光标全程循环。
  对照字串：`const blink2 = (t0)`

## 演示与来源

![上游演示三个取样状态](../previews/error-retype.jpg)

[本地静音 HTML 演示](../upstream/demos/error-retype/index.html?embed=1) · [完整配方](../upstream/references/cards/error-retype.md) · [TSX](../upstream/template/cards/error-retype.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
