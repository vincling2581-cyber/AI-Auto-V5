# HUMAN 3.0 角色与语义插画修订完整版

本目录是独立修订工程。`source/timeline.json` 使用 16 个连续半开区间，包含 12 张语义动作插画，以及原来的 quadrants、prompt、plan、choice 四段信息卡。总计 1678 帧、30 fps、1920×1080，画面时长 55.933333 秒。

当前完整成片为 `exports/full_01/HUMAN3_角色与语义插画修订完整版_1080p.mp4`，12,475,417 字节，SHA-256 为 `d559ca86a43e0cb5f175fd236e46f4649b0cb4fc5d54107872c1485ff94d338d`。机器检查与编码抽帧审阅分别记录在 `qa/full_01/machine_checks.json`、`qa/full_01/visual_review.json`，完整交付索引为 `qa/full_01/delivery_receipt.json`。

机器检查已通过，原音 2409 个包的内容和时间戳完全一致。已查看 12 个插画代表编码帧、所有切换接点与四段卡片过程。保留两项构图观察：继续攀登镜头的前脚接近字幕但未被遮住；首个对谈镜头的坐姿脚趾有部分字幕遮挡，提问动作、笔尖、双手和笔记完整可见。正常速度整片主观视听未执行。

## 重渲

在此目录执行 `python -X utf8 source/render_full.py --mode preflight` 检查依赖。全部素材位于 `assets/` 后，可执行以下命令。

```powershell
python -X utf8 source/render_full.py --mode preview --run preview_01
python -X utf8 source/render_full.py --mode render --run full_01
```

每次运行写入新的 `exports/<run>/` 与 `qa/<run>/`。已有运行目录及文件拒绝覆盖；重试请使用新 run 名。完整成片为 `exports/<run>/HUMAN3_角色与语义插画修订完整版_1080p.mp4`。

工具依赖为本机 Chrome、Python Playwright/Pillow、FFmpeg。`source/config.json` 记录本机 FFmpeg 路径。迁移时将本修订目录与本集原完整版一同复制，保持 `episodes/<本集>/09_revisions/<本修订>/` 关系；也可在新副本中修改 config 的原片路径及工具路径。

## 可修改范围

- `source/timeline.json` 管理各镜起止帧与插画文件。所有插画固定满幅，硬切根据语义时点，没有缩放、横移、移动路线和额外说明框。
- `source/config.json` 管理开头文字位置、固定字幕参数及编码参数。前 119 帧显示“第一步 / 往哪走？”双行标题，字号 106 / 118 px；119–235 帧显示轻量 HUMAN 3.0 / Dan Koe 标识。生成素材 1672×941 或 1671×941 的微小比例差按授权允许 cover 缩放，比例容差 0.2%。
- `source/app.js` 管理合成层；字幕始终居中，文字与底板都没有横移。
- `source/cards.js` 是本集现有代码的逐字节副本；其四段起止帧、局部时间和 `effective_defaults.json` 保持一致，连续运动、中间状态与阅读保持全部保留。
- `source/original.srt` 和 `source/subtitles.json` 是原文件副本；预检比较全部字幕原文及时间，不改写或重新计时。

## 音轨与检查

完整片先生成无声 H.264 画面，再从本集 `07_exports/HUMAN3_v46_新版开头完整版_1080p.mp4` 复制完整第一条音轨，最终使用 `-c:v copy -c:a copy`。不裁音、不变速、不增益、不混音、不再次编码音轨。

一次最终验证包括媒体规格、全部音视频解码、每个音频包的内容与 PTS/DTS/时长一致性。编码抽帧覆盖 12 个插画代表帧、全部镜头切换的前后帧、四段信息卡的过程与结果帧。报告记录实际输入、源码、配置、素材、字体、浏览器与 FFmpeg 依赖。

信息卡实现相同并不自动继承旧成片验收结论。新运行只记录本次实际执行的检查。正常速度整片主观视听、剪映原生打开/播放/导出保持 `not_performed`，除非另有独立证据。未调用剪映或 AE。

12 张最终素材已由图像制作分工写入并用于上述成片。`*_initial.png` 等生成参考不参与时轴。`preview_01` 是 favicon 请求触发严格浏览器错误检查后的中止记录，已修复；有效合成预览为 `qa/preview_02/`。各运行目录及其证据保留，不覆盖旧文件。
