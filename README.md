# AI-Auto-V5

V5 视频制作项目的代码、规则与必要配置仓库，保留本地目录结构。采用增强信息卡的 HTML/SVG/JavaScript → Chrome → FFmpeg 制作方式，无需安装 AE。

本仓库不包含配音、字幕原文件、插画、品牌参考图片、官方媒体、成片、渲染缓存和剪映交付包。这些文件继续保留在本地，需另外备份；仅克隆本仓库不能直接预览或重渲染已有视频。

## 当前入口

先读 [AGENTS.md](AGENTS.md)、[CURRENT_PROJECT.json](CURRENT_PROJECT.json) 与[单集工作约定](docs/SINGLE_EPISODE_WORKFLOW.md)。按准确指针加载当前标准和本集状态，不按旧集日期或历史对话推测规则。

当前采用 v4.5 标准的 V5 本地快照和增强信息卡方法。标准锁及其文件哈希保留原样；`.gitattributes` 禁止 Git 自动转换换行，避免改变锁定文件的字节。

## 目录与上传范围

| 路径 | 用途 |
|---|---|
| `AGENTS.md`、`CURRENT_PROJECT.json` | 当前制作入口、有效版本与交接指针 |
| `docs/`、`templates/` | 工作约定与单集状态模板 |
| `episodes/.../00_brief/` | 本集配置与标准快照，输入媒体不入库 |
| `episodes/.../02_timing/`、`03_storyboard/` | 时间轴、分镜和语义设计数据 |
| `episodes/.../06_project/` | 制作、预览、渲染、合成及检查源码 |
| `episodes/.../09_revisions/jianying_layered_20261009_v1/` | 剪映分层导出的构建脚本、`adapter`、`delivery_tools`、图层/文字配置及 `source/episode` 源码；媒体与生成草稿除外 |
| `card_motion_trial_v1/`、`card_motion_trial_v2_complex/` | 保留的动效试验源码与配置，日常制作不默认读取 |

`.gitignore` 采用代码/配置扩展名允许清单，排除素材、输入、成片、运行依赖、生成报告及缓存。新增类型确需入库时单独检查，不用 `git add -f` 绕过素材或凭据排除规则。

## 运行环境与恢复

基础环境：Windows、Python 3.12、Google Chrome、FFmpeg/FFprobe、Microsoft YaHei 字体。Python 核心包记录在 `requirements.txt`，版本取自首次入库时的现有环境；未据此宣称已完成全新机器安装验收。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

渲染器使用本机 Chrome。FFmpeg、字体及部分可选工具路径记录在本集 `00_brief/effective_defaults.json` 或脚本中，换机时按实际位置调整并记录；保留结构不代表这些路径已全部参数化。

恢复旧集时，从本地备份放回配音/SRT、`04_assets`、标准快照中的品牌与参考媒体；恢复剪映导出还需对应人物镜头、分层媒体或重新生成它们。具体缺项按本集配置和标准锁核对。标准锁中有意保留本地素材条目，缺文件时应恢复，不能删除条目或改哈希伪装通过。

剪映构建另依赖与现有脚本兼容的 `pyJianYingDraft` 及其草稿加密 API。它未列入基础依赖；当前项目不能保证任意同名 PyPI 版本可用，使用导出前需核对 `delivery_tools` 和实际依赖环境。日常视频制作不自动执行剪映导出或注册。

`CURRENT_PROJECT.json` 和旧集 README 可能指向仅本机存在的成片、安装回执、报告；这些链接作为本地索引保留。历史报告不能证明克隆后已验证，恢复后应执行受影响的检查。

## 功能迭代

1. `main` 保存可追溯基线；首次提交是现状入库，不表示完成新的全流程运行验收。
2. 每个功能使用独立分支，例如 `feature/card-layout`，保持改动范围清晰。
3. 用代表镜头验证相关功能，涉及全片输出时补充必要检查，再合并。
4. 单集制作记录实际使用的代码提交和规则锁；升级通用功能不改写旧集验收记录。

不要直接运行旧集或试验的 `prepare*.py` 来创建新集：它们可能含固定文案、时点、旧路径或历史初始化行为。新集按当前工作约定建立独立目录。

所有操作限定在 V5；`D:\AI-Auto-V4（Codex）` 不属于本仓库且禁止作为本次迁移或迭代的写入目标。第三方代码附带的原有许可文件保留；本次入库不额外声明整个项目采用某种开源许可。
