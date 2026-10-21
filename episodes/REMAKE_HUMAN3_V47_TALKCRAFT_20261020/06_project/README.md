# HUMAN 3.0 本集重渲源工程

本集为 1920×1080、30 fps、1678 帧，时长约 55.933 秒。以下 PowerShell 命令均从本集根目录 `REMAKE_HUMAN3_V47_TALKCRAFT_20261020` 执行。

本次完整视频位于 `07_exports/HUMAN3_v47_TalkCraft_完整重制_1080p.mp4`。`cards.js` 编辑卡片过程与布局，`app.js` 负责静态插画和独立字幕合成；时间轴为 `03_storyboard/scenes.json`，插画在 `04_assets/illustrations/`。编辑时间轴或资产后，重渲前应再次运行锁定阶段入口，更新本集相应证据；既有成片保持不覆盖。

原配音不变速、不增益。字幕及底板独立固定在底部中央；插画为完整静态画面硬切，信息卡保留对象关系、中间状态、连续语义过程与阅读保持。本集未制作剪映草稿或 AE 导出。

## 浏览器预览

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

打开 [06_project/index.html](http://127.0.0.1:8765/06_project/index.html)。页面初始显示第 0 帧，不自动播放配音；在浏览器开发者工具控制台执行以下代码可检查指定帧，合法帧号为 `0..1677`。页面没有 URL 帧参数。

```javascript
await window.ready;
window.renderFrame(525);
window.getFrameState();
```

## 通过锁定入口重渲

全片、局部、截图和配置验证均须通过本集锁定的 `run_stage.py`；阶段检查失败时不启动渲染。先设置本集路径。

```powershell
$ep = (Get-Location).Path
$stage = Join-Path $ep '00_brief/standard_snapshot/production_standard/run_stage.py'
```

全片重渲另存新文件，不覆盖已有成片。

```powershell
python "$stage" --episode-root "$ep" --stage render --entry 06_project/render.py -- --output "07_exports/HUMAN3_v47_TalkCraft_重渲_v1.mp4"
```

局部视频必须同时明确 `--start-frame`、`--frame-count` 和新 `--output`。帧号按全片绝对帧计，音频从相应时间截取，保留原速与原增益。

```powershell
python "$stage" --episode-root "$ep" --stage render --entry 06_project/render.py -- --start-frame 525 --frame-count 90 --output "07_exports/HUMAN3_v47_TalkCraft_局部_0525_0090_v1.mp4"
```

截图输出至 `08_qc/frame_XXXX.png`，不编码视频。

```powershell
python "$stage" --episode-root "$ep" --stage render --entry 06_project/render.py -- --still-frames "0,119,525,1677"
```

只验证阶段环境和配置，不启动网页、浏览器或编码。

```powershell
python "$stage" --episode-root "$ep" --stage render --entry 06_project/render.py -- --validate-config
```

视频输出路径必须位于本集内；已有目标视频或同名 `.partial.mp4` 会被拒绝覆盖，重渲时请更换版本名。

## 输出检查与制作依据

对本次全片成片执行机器检查，也须经过本集锁定阶段入口。核验脚本先校验配置，并拒绝缺失 V5 stage 环境的直接调用。`--video` 接受本集内的相对或绝对路径，报告固定写入 `08_qc/output_machine_checks.json`。

```powershell
python "$ep\00_brief\standard_snapshot\production_standard\run_stage.py" --episode-root "$ep" --stage render --entry 06_project/verify_output.py -- --video "07_exports/HUMAN3_v47_TalkCraft_重渲_v1.mp4"
```

机器检查不能替代正常速度主观视听，也不能据此宣称整片观感验收通过；剪映原生打开和导出状态需另行记录。

- [配方选择、采用理由与配音落点](../03_storyboard/semantic_design.json)
- [事实说明与来源](../01_research/facts.json)
- [分镜表](../03_storyboard/分镜表.md)
- [分层制作合同](../03_storyboard/production_contract.json)
- [本集有效配置](../00_brief/effective_defaults.json)
- [本地依赖与第三方说明](THIRD_PARTY.md)
