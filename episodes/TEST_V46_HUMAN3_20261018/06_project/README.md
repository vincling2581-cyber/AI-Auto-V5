# HUMAN 3.0 · v4.6 视觉测试源工程

当前是可重渲的 HTML / SVG / JavaScript 源工程，不是 AE 工程。渲染器使用已安装的 Python Playwright、本机 Chrome 和 `D:/ffmpeg/bin/ffmpeg.exe`；不安装依赖。HTTP 服务只绑定 `127.0.0.1` 的临时端口，在 Python 后台线程中运行；Chrome 与 FFmpeg 均不弹出窗口。

以下命令从本集目录 `episodes/TEST_V46_HUMAN3_20261018` 执行。

```powershell
# 只导出指定绝对帧号的 PNG，不编码视频
python 06_project/render.py --still-frames 0,119,420,947,1677

# 全片：07_exports/HUMAN3_v46_视觉测试_1080p.mp4
python 06_project/render.py

# 新版本完整输出；所有输出路径必须在本测试目录内
python 06_project/render.py --output '07_exports/HUMAN3_v46_视觉测试_1080p_v2.mp4'

# 从第 300 帧开始输出 180 帧，配音同步从 10 秒开始
python 06_project/render.py --start-frame 300 --frame-count 180 --output '07_exports/HUMAN3_frames_0300_0479.mp4'
```

`--still-frames` 的帧号从 0 开始，本集范围为 0–1677；截图写入 `08_qc/frame_XXXX.png`，再次导出同帧时更新该 PNG。它不能与局部渲染或 `--output` 参数组合。局部视频必须显式指定另一个输出名，`--frame-count` 省略时输出起点至片尾。

渲染参数读取 `00_brief/episode.json` 与 `00_brief/effective_defaults.json`。当前为 1920×1080、30 fps、1678 帧，H.264 / CRF 17 / fast / yuv420p，AAC 256k。原配音来自 `00_brief/input/10月18日.mp3`，约 55.902042 秒；视频为 55.933333 秒。配音转为 AAC，不改变速度或增益。局部输出按起点截取相应音频时间段。编码使用显式视频帧数，不使用 `-shortest`。

浏览器必须提供 `window.ready` Promise 和确定性的 `window.renderFrame(frame)`。脚本等待配置、字体及图片加载完成，逐帧以 JPEG 94 截图，直接通过 MJPEG 管道输入 FFmpeg，不保存海量中间帧。每 300 帧输出一次进度。JS 异常、图片加载失败及编码错误会终止任务，详细日志保存在 `08_qc/render_*.log`。

视频先写到同目录的 `*.partial.mp4`，编码结束后核对帧数、尺寸、帧率及音轨，才原子更名为目标 MP4。已有正式视频或同名 partial 文件均拒绝覆盖；请给新版本指定 `--output`。失败文件保留用于排错，不能作为成片交付。

## 可编辑内容与资产映射

| 文件 | 可编辑内容 |
| --- | --- |
| `00_brief/episode.json` | 本集总帧数、帧率、原配音路径及输入 SHA-256；更换输入需同步更新记录 |
| `00_brief/effective_defaults.json` | 本集画幅、编码、品牌色、字号与本集覆盖项 |
| `02_timing/subtitles.json` | 字幕 `start` / `end` / `text`；单位为秒 |
| `03_storyboard/scenes.json` | 分镜帧区间、`type`、`asset`、语义任务与保持理由 |
| `06_project/index.html` | 画面容器、页面样式与模块加载 |
| `06_project/app.js` | 时间驱动、场景选择、插画显示、字幕和帧入口 |
| `06_project/cards.js` | 信息卡布局、语义过程和连续中间状态 |

插画逻辑名与本集文件对应：

| `scenes.json` 中的 `asset` | 图片路径 |
| --- | --- |
| `crossroads` | `04_assets/illustrations/crossroads.png` |
| `ascent` | `04_assets/illustrations/ascent.png` |
| `conversation_listen` | `04_assets/illustrations/conversation_listen.png` |
| `conversation_answer` | `04_assets/illustrations/conversation_answer.png` |
| `clarity` | `04_assets/illustrations/clarity.png` |

信息卡的逻辑名由 `cards.js` 实现，具体时间范围以 `scenes.json` 为准。替换插画后保留角色身份和眼部、明确的动作、自然延伸到下沿的完整场景；调整保持与过渡时间时按语义和配音安排，不设固定切图间隔。

脚本成功及容器检查仅证明渲染和基本媒体参数，不代表正常速度主观视听、剪映原生打开或原生导出已经完成。
