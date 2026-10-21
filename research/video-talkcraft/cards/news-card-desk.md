# 新闻卡片划重点 · news-card-desk

类别：素材呈现；研究用途：证据与素材呈现；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

有原始报道或可靠截图，旁白需先给出处再标出某句报道内容时。

语义关系：报道来源到被引用重点、第一份报道到补充报道

## 避免误用

用新闻外壳装自写判断，或截图低清到重点不可辨认时。

## 可见过程

1. 第一张报道卡从下方落位
2. 读到关键词时扫出下划线
3. 第二张报道从侧面压叠补充
4. 两份材料保持，来源与重点仍可读

配音落点：先说“这篇报道提到”，读到目标句才画线，后续材料再接上。

## 关键限制与适配

- 标题与来源文字是示例，必须替换并核对，不能只换大标题保留虚构媒体。
- 第二张会压住第一张，需检查引用句有没有被遮掉。
- hostSrc 在 TSX 未使用；八秒 Ken Burns 是上游条件，不是 V5 通用要求。

V5 适配提示：借鉴报道上台、语音划线和补充材料的证据链；真实来源就近标识，阅读时可保持静止，若采用镜头动作只作用证据截图并另行验证。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/news-card-desk.tsx#L87)：下划线有独立启动时刻，可与朗读关键词对齐。
  对照字串：`const redline = tw(t, CONFIG.redlineAt, CONFIG.redline, power2Out);`
- [html 第 98 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/news-card-desk/index.html#L98)：截图内部持续匀速放大，与卡片入场动作分开控制。
  对照字串：`duration: CONFIG.kbDur, ease: "none"`

## 演示与来源

![上游演示三个取样状态](../previews/news-card-desk.jpg)

[本地静音 HTML 演示](../upstream/demos/news-card-desk/index.html?embed=1) · [完整配方](../upstream/references/cards/news-card-desk.md) · [TSX](../upstream/template/cards/news-card-desk.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
