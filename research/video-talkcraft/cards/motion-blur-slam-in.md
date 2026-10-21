# 模糊甩入急停 · motion-blur-slam-in

类别：素材呈现；研究用途：证据与素材呈现；输入：图, 截图, 人(可选)

状态：配方文档、TSX 关键实现与 HTML 动画代码已研究；V5 适配、真实配音同步、生产渲染与剪映原生验证尚未执行。

## 选择条件

口播正在明确抛出一份或连续两份素材，快速入场本身能对应“直接给你看”的动作语气时。

语义关系：证据压入、同向连续举例

## 避免误用

平静精读、长数据说明或插画镜头不适合从屏外甩入；高速展示不能替代证据停留和内容解释。

## 可见过程

1. 人物旁预留的空区保持干净
2. 素材从画外同方向快速冲入
3. 横向拖影随减速收敛，落位时清零
4. 微量过冲回正，第二张以同方向接续

配音落点：首卡起点对齐举证词，第二卡对齐第二个证据对象；素材落定后应有可读保持，而非仅按示例短时长闪过。

## 关键限制与适配

- CSS 各向同性 blur 会读成失焦，示例使用 SVG 横向高斯模糊，需保留滤镜方向。
- sigma 被描述为跟速度，但代码实际用已缓动进度的幂次近似，并非真实速度采样。
- 滤镜边界太窄会截断拖影，停止后不摘 filter 还可能留下脏边。

V5 适配提示：V5 可研究为少量截图证据的克制入场，默认去人物占位并扩展落定阅读段；不得用于让叙事插画飞入或运动。

上游演示时长仅为原样例参数，不是 V5 默认时长或配额。上游工作流、品牌、字幕、持续运镜及验收指令不自动生效。

## 源码对照

- [tsx 第 90 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/template/cards/motion-blur-slam-in.tsx#L90)：TSX 用位移同一缓动进度计算横向模糊近似，飞入完成直接返回 sigma 为零。
  对照字串：`sigma: CONFIG.blurMax * Math.pow(1 - p`
- [html 第 107 行](https://github.com/Vincentwei1021/video-talkcraft/blob/a7c29edfb2404612dde6a5a1c8aa94232e85625b/demos/motion-blur-slam-in/index.html#L107)：HTML 仅设置横向标准差，并在小于阈值时移除卡片滤镜。
  对照字串：`fe.setAttribute("stdDeviation", sigma.toFixed(2) + " 0")`

## 演示与来源

![上游演示三个取样状态](../previews/motion-blur-slam-in.jpg)

[本地静音 HTML 演示](../upstream/demos/motion-blur-slam-in/index.html?embed=1) · [完整配方](../upstream/references/cards/motion-blur-slam-in.md) · [TSX](../upstream/template/cards/motion-blur-slam-in.tsx)

关键帧取样用于研究，不等于正常速度主观审片或当前工程验证。

来源版本：`a7c29edfb2404612dde6a5a1c8aa94232e85625b`。授权和来源见 [README](../README.md)。
