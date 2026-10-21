# 人名条展示牌 · lower-third-nameplate

类别：人物互动；研究用途：证据与素材呈现；输入：人(可选), 文

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

真人或被引用人物首次出现，需要用可核对姓名、职位说明来源身份时。

语义关系：人物到姓名与身份、主要身份先于补充头衔

## 避免误用

匿名叙事角色、身份未经核对，或只是想增加常驻栏目包装时。

## 可见过程

1. 底部一侧色条先展开
2. 姓名沿水平方向揭示
3. 头衔稍后接上并保持
4. 头衔、姓名、色条依次反向收回

配音落点：人物首次发言时给姓名，身份与内容相关的部分再补出。

## 关键限制与适配

- 文档称三段接力，代码姓名在色条进度约七成时启动，实际有交叠。
- 左下并不天然安全，仍可能压住固定底部字幕。
- 姓名与头衔在 JSX 中，不能只传 hostSrc 就获得可配置身份。

V5 适配提示：仅对真实人物或引用来源使用，保留姓名与身份层级；不转成固定品牌角标，按字幕安全区重新定位，停留由阅读决定而非固定模板秒数。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/lower-third-nameplate.tsx#L87)：姓名与色条尾段交叠，严格串行只是文档概括。
  对照字串：`const nameAt = t0 + CONFIG.barDur * 0.7;`
- [html 第 87 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/lower-third-nameplate/index.html#L87)：退出最后才收色条，保持身份文字先消失的层次。
  对照字串：`.to(bar, { scaleX: 0, duration: CONFIG.outDur`

## 演示与来源

![上游演示三个取样状态](../previews/lower-third-nameplate.jpg)

[本地静音 HTML 演示](../upstream/demos/lower-third-nameplate/index.html?embed=1) · [完整配方](../upstream/references/cards/lower-third-nameplate.md) · [TSX](../upstream/template/cards/lower-third-nameplate.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
