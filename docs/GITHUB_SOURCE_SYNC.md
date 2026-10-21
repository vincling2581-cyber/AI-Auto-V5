# V5 GitHub 源码同步范围

本仓库同步代码、当前有效制作约定、标准锁、提示词和必要配置。音频、原始字幕文件、插画、参考图、演示媒体、渲染片段、成片、剪映草稿包及本地验收产物留在本地，不通过 Git 分发。

## 当前入口与制作约定

从根目录 `CURRENT_PROJECT.json` 定位当前标准、单集入口、导出工具和信息卡动效库。`AGENTS.md` 与 `docs/SINGLE_EPISODE_WORKFLOW.md` 包含已确认的动效检索、逐卡选型记录和实际画面检查步骤。v4.7 正式 SOP、规则、提示词与默认参数位于 `standards/v4.7/`；旧集继续使用自己的标准锁。

仓库内剪映分层导出 Skill 位于 `skills/jianying-layered-export/`。Git 同步不安装或更新全局 Skill，也不触发草稿导出、注册或原生复检。

## 108 套候选动效

`research/video-talkcraft/` 包含 108 份中文研究笔记、可搜索 HTML 索引、结构化目录、语义索引、查询工具，以及固定上游版本的 332 份文本源码和授权说明。原始来源清单继续保留全部 366 项哈希，其中 34 项媒体不随 Git 分发。图片与视频缺失不影响候选检索和源码阅读，部分上游演示须恢复媒体才能完整播放。

从仓库根目录进行源码完整性检查：

```powershell
python -B research/video-talkcraft/scripts/validate_library.py --source-only --no-write
python -B research/video-talkcraft/scripts/query.py 汇聚 --limit 3
```

源码检查通过只证明本次分发的覆盖、哈希、证据字串和索引一致，不证明演示媒体齐全、108 套均已生产适配或正常速度视听通过。按整段文案选候选、按需适配与验证，继续执行单集工作流 §3.1。

## 当前重制集源码

根入口指向 `episodes/REMAKE_HUMAN3_V47_TALKCRAFT_20261020/`。仓库保留该集配置、标准文本快照、事实来源、字幕时序 JSON、分镜、语义选型、制作合同、HTML/SVG/JS/Python 源工程与第三方许可。

本地已有媒体与成片无需移动或重新渲染。新机器仅克隆仓库后，需要另行恢复：

- 该集 `00_brief/input/` 的原配音和 SRT。
- `04_assets/illustrations/` 的 I01 至 I05 插画。
- 本集 `standard_snapshot/production_standard/assets/` 的两张角色参考 PNG；新集制作也须恢复根标准 `brand_assets.json` 指向的本地参考图。
- 配置要求的 FFmpeg、Chrome、微软雅黑及 Playwright、Pillow、NumPy、OpenCV 等本机依赖。

缺少媒体时，锁定的 `run_stage.py` 预检失败是预期行为；应恢复原文件并核对哈希，不能删除校验、修改旧锁或把已有通过记录当作新机器已经验收。恢复后按本集 `06_project/README.md` 使用锁定入口重渲。

`episode_state.json` 记录的是原本地制作状态。Git 克隆不包含其中引用的成片和本地检查证据，不能仅凭状态里的 `passed` 宣称当前环境或新输出已通过。机器检查、编码画面抽样、正常速度主观视听及剪映原生状态继续分别记录。

本次同步保留现有规则和媒体，不迁移或修改 V4，也不把其他未完成试验或旧集修订混入当前执行入口。
