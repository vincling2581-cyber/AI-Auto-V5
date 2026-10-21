# 左右摇移 · sway-parallax

类别：运镜；研究用途：证据或卡片运镜；输入：图, 截图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

原始证据是超宽流程、时间线或对比长图，必须沿阅读方向依次显露并保持字号可读。

语义关系：横向序列连续浏览、超宽证据保尺寸

## 避免误用

完整静态插画、普通宽度页面，或关键条款需要停读但页面仍不断横移。

## 可见过程

1. 宽页从阅读起点展示
2. 相机轻缓起步横移
3. 沿横向结构浏览并轻倾跟随
4. 到终点降低速度
5. 保留末速继续漂一段后停止有限演示

配音落点：横移行程对齐横向项目次序，速度由扫读与讲述共同决定；真正需精读的点应另规划停止。

## 关键限制与适配

- 源码注释称sine.in加速末速与主摇无阶跃，但按vT/2距离及正弦导数末速约πv/4，切到主段v时并不连续。
- camEase(r)主段实际变速而非严格匀速，勿直接继承文档速度保证。
- hold继续漂会越过证据边界，页宽、xTo、hold余量必须同核；V5插画禁止这种相机平移。

V5 适配提示：仅作证据或卡片超宽内容的条件浏览候选，先校正速度曲线及停点，再考虑使用，不引入相机永不静止要求。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 33 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/sway-parallax.tsx#L33)：该函数末端导数为π/2，配vT/2的加速距离不能获得文档声称的末速v。
  对照字串：`const sineIn = (x: number) => 1 - Math.cos((x * Math.PI) / 2);`
- [html 第 169 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/sway-parallax/index.html#L169)：HTML主摇用非线性多项式，其速度随p变化，末速为平均速度的r倍。
  对照字串：`const camEase = (r) => (p) => p + (1 - r) * p * p * (1 - p);`

## 演示与来源

![上游演示三个取样状态](../previews/sway-parallax.jpg)

[本地静音 HTML 演示](../upstream/demos/sway-parallax/index.html?embed=1) · [完整配方](../upstream/references/cards/sway-parallax.md) · [TSX](../upstream/template/cards/sway-parallax.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
