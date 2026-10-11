# ECHO · 五款 AI 工具

本集使用提供的 `10月8日.mp3` 和 SRT，输出 1920×1080、30 fps、2777 帧，约 92.57 秒。保持原声时序、语速和音量，不加 BGM、音效或旁白字幕。画面保留必要名称、概念、条件及来源提示。

## 观看与文件

- `07_exports/ECHO_五款AI工具_增强信息卡_1080p.mp4`：完整视频。
- `07_exports/ECHO_原声对应_名称更正.srt`：对应原声时间的旁挂字幕，仅更正工具名等转录拼写；其中数值不应作为已核实事实引用。
- `00_brief/事实核查与画面更正.md`：逐项事实处理、官方链接、许可和数字说明。
- `03_storyboard/cards.json`：16 个镜头和精确帧边界。
- `03_storyboard/events_override.json`：信息卡语义事件起止。
- `04_assets/illustrations`：9 张本集人物场景原图。
- `04_assets/prompts` 以及插画目录内 `Axx.prompt.json`：完整图像提示词、引用、修订及生成记录。模式为内置 image_gen。原图 1672×941，视频按比例适配，无拉伸。
- `04_assets/official`：带出处清单的官方素材。部分调研下载文件未进入成片；实际使用清单见 `08_qc/asset_usage.json`。
- `06_project/cards`：可编辑 SVG/JavaScript 场景与本地渲染器。
- `08_qc`：采样、编码帧、声音对齐和保护范围检查；以最后的 `delivery_report.json` 为交付状态入口。

## 编辑和重渲染

这是 HTML/SVG 源项目，不是 AE 工程或剪映原生草稿。制作方式延续现有 Chrome → FFmpeg 流程。本集无需安装 AE。

运行环境：Windows、Microsoft YaHei 字体、Python 3.12、Google Chrome、FFmpeg。Python 依赖：`playwright Pillow numpy`。渲染器使用已安装的 Chrome；不依赖外网字体、CDN 或远端脚本。

在本集目录执行：

```powershell
python -B -X utf8 .\06_project\preview.py
```

控制台会给出本地预览网址。预览以配音播放时间定位画面，可暂停、拖动和逐镜查看。浏览器预览会受设备性能影响，最终文件以 MP4 为准。

常用修改位置：标题/页脚在 `03_storyboard/cards.json`；卡片内容与动效在 `06_project/cards/scenes_a.js`、`scenes_bc.js`、`scenes_de.js`；品牌和共有绘图在 `common.js`。逐帧画面由本地时间参数决定。调整镜头长度时同步维护 `build_timeline.py`、事件与音频语义对应，不能仅把配音拉伸。

重渲染一个镜头和重新合成：

```powershell
python -B -X utf8 .\06_project\cards\render_cards.py --cards C05 --workers 1
python -B -X utf8 .\06_project\assemble_and_qc.py
```

全部重渲染：

```powershell
python -B -X utf8 .\06_project\cards\render_cards.py --workers 2
python -B -X utf8 .\06_project\assemble_and_qc.py
```

`00_brief/effective_defaults.json` 的 `tools_local.ffmpeg` 是本机 `D:\ffmpeg\bin\ffmpeg.exe`；换电脑时改为实际路径即可。字体路径同样在该文件。成片重渲染不需要 V4，不需要重新下载素材，也不需要运行记录首次准备工作的 `prepare_episode.py`。

## 规则与判断边界

本集锁定已核实的 V4 v4.5 标准副本，按用户授权使用增强信息卡动效，并在本集记录视觉与音频选择。全局规则、V4 目录、两个已有 V5 动效试样以及输入文件不属于修改范围。交付时核对保护清单；该清单是全树元数据和选定关键文件 SHA256 检查，不等同于全树所有字节哈希。

人物动画采用动作关键姿势与短镜头组合。开头和结尾是同场景动作前后两姿势；各人物镜头均不足 2.8 秒。不是骨骼连续动画。信息卡通过对象传递、筛选、布局重排、断网状态与结果变化表达语义；进度细线和淡入本身不作为语义变化证明。

用户已选择保留原配音，在画面更正工具名称、数字和使用条件。因此原声与画面个别数字/条件存在有意保留的差异，例如 Impeccable 星标；发布者应同时阅读核查说明。

官方界面截图用于介绍界面，不表示本机实测运行。自制界面与任务数字均为流程示意。Open WebUI 官方截图含外部 API 示例，离线能力由单独的本地流程示意说明，必须预先准备本地模型和相应配置。

帧级截图、编码、解码、对象状态和音频相关性检查可以确认结构与时序，不能代替用户正常速度看完整条视频、听辨声音或确认主观审美。最终报告会分别记录这些状态，不把抽帧检查写成全速视听验收。
