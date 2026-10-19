# 本地依赖

Flubber 0.4.2，MIT 许可，原构建文件 `flubber.min.js` 与原许可 `flubber-LICENSE` 一并保留。项目：https://github.com/veltman/flubber 。本版源文件哈希见标准根目录 `production_standard.json` 的文件清单。

本包只在需要轮廓形变时调用 Flubber。位置、尺寸、透明度、遮罩与路径由明确帧时间的纯函数驱动，不加载 Tween.js、Remotion 或旧 `motion.tsx`。旧本集的 THIRD_PARTY.md 曾保留历史 Tween.js 说明，不作为本包运行依赖依据。
