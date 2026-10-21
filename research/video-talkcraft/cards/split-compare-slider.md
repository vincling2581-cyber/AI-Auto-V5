# 对比双分屏（滑动揭示） · split-compare-slider

类别：素材呈现；研究用途：证据与素材呈现；输入：图

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

前后两图来自同一机位和相同尺度，分割线扫过时每个位置都能直接对应内容差异时。

语义关系：同位前后差异、变化范围揭示

## 避免误用

构图不同的两图、伪造调色前后或需要横向移图才能凑齐的位置不能作此对比，也不能用于 V5 插画推拉。

## 可见过程

1. 完整前图先供观察
2. 分割线与裁切边一起到中线揭示后图
3. 停留后轻推提示另一侧，再近乎全露后图
4. 回到中线确认差异，标签与两图同收

配音落点：首次揭示锚定“改完以后”，停在中线对应具体差异说明，近端全露对应结果整体，回中作为比较结论。

## 关键限制与适配

- 两张素材本体应保持同位，裁切不能被横移替代。
- TSX 在缺图或同一路径时自动套滤镜模拟前后，不能把此默认效果交付为真实证据。
- 示例两图共用极慢推，精确证据可取消该推镜；保留时务必共用倍率避免边界错位。

V5 适配提示：V5 可用于来源明确的同构图界面或处理前后，标清两侧身份；若是不同构图采用独立卡片，不伪造对应关系。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 108 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/split-compare-slider.tsx#L108)：TSX 把缺素材和同路径判为滤镜示意状态，真实对比需两份经确认素材。
  对照字串：`const grade = !srcBefore || !srcAfter || srcBefore === srcAfter`
- [html 第 90 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/split-compare-slider/index.html#L90)：同一进度同时写入裁切边和分割线，并依各侧露出比例决定标签可见性。
  对照字串：`divider.style.left = o.p + "%"`

## 演示与来源

![上游演示三个取样状态](../previews/split-compare-slider.jpg)

[本地静音 HTML 演示](../upstream/demos/split-compare-slider/index.html?embed=1) · [完整配方](../upstream/references/cards/split-compare-slider.md) · [TSX](../upstream/template/cards/split-compare-slider.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
