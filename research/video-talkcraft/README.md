# video-talkcraft 信息卡动效研究库

这是 V5 内独立保存的候选方法库。覆盖固定版本的全部 108 套配方，用于以后按文案含义选择效果，再按实际需要完成 V5 适配与验证。

直接打开 [可搜索索引](index.html)，或用 [命令行查询工具](scripts/query.py) 返回少量候选。初次研究不等于 108 套均已接入当前渲染器；也不等于每套效果都适合 V5 的插画或信息卡。

## 已研究的内容与边界

- 108/108：逐项核对配方重点章节、TSX 关键实现和 HTML 动画代码，记录语义关系、选择条件、误用边界、可见过程、配音落点、特有问题及实现证据。
- 108/108：上游 HTML 演示离线运行，每套提取三个时间状态，保存为轻量预览。取样状态用于理解构图与过程，不能代替正常速度主观视听。
- 本库新记录的 V5 适配、真实文案与配音同步、生产渲染验收、剪映原生验证均为 `not_performed`。此前独立研究样片不自动转为本库全部效果的生产验证。
- 研究方法为“重点文档与关键实现对照”，不是逐行代码审计；对已发现的文档/实现差异逐卡记录。原始上游文件保留，未代为修复。

跳转取样也有边界。`tracking-in`、`long-take-world`、`host-shrink-to-chip` 的本地取样出现了模糊、到站内容未显现或裁剪内人物未显现，已在索引与逐卡笔记标记，不能据此宣称正常播放或适配通过。详细观察见 [visual_observations.json](verification/visual_observations.json)。

## 后续制作怎样读取

先按整段文案判断观众需要理解的对象关系和变化，再检索候选；素材是否具备、关系是否准确、当前集规则是否允许，仍需结合内容判断。关键词搜索只提供候选，不能自动决定语义。

```powershell
python -B "research/video-talkcraft/scripts/query.py" "汇聚"
python -B "research/video-talkcraft/scripts/query.py" "比较" --limit 3
python -B "research/video-talkcraft/scripts/query.py" --id source-converge
```

常规任务先读本页或查询结果，再打开选中卡片的 `cards/<id>.md`；只有需要适配时才读对应 TSX、HTML 或完整配方。不把整个 `catalog.json`、108 份说明或全部源码一起送入上下文，不追溯本次研究聊天。

用户已确认的执行步骤见 [单集工作流 §3.1](../../docs/SINGLE_EPISODE_WORKFLOW.md#31-信息卡动效选型与实现检查)：设计前按整段关系检索；每卡记录配方 ID、理由与配音落点，无适用项说明原因并另行设计；实现后核对实际编码画面并留证。记录并入本集 `authoritative_files.semantic_design` 指向文件，由制作代理完成检索、适配与检查，不新增人工选卡审批，用户继续沿用既有样片反馈流程。此约定不强制每张卡使用库效果，不改变当前视觉规则。

每套笔记均有：

| 字段 | 用途 |
|---|---|
| `relations`、`select_when` | 按语义关系和具体条件选择候选 |
| `avoid_when`、`pitfalls` | 防止误读、顺序错误或套用实现缺陷 |
| `sequence`、`narration_anchor` | 记录实际过程以及应对齐的口播含义 |
| `v5_role`、`v5_adaptation` | 区分卡片主体、标注、证据呈现、运镜、转场及人物互动 |
| `evidence`、`sources` | 对应源码字串、行号、原文件哈希与固定版本链接 |
| `status` | 分别标记研究、关键帧取样、适配与验证状态 |

## 与 V5 当前规则的关系

本库的用途是提供候选表达方法。当前 `CURRENT_PROJECT.json`、标准锁、单集规则和明确用户要求继续决定制作方式，原有规则没有被本库替换。

- 连环画插画仍按当前标准保持完整静态与硬切；上游推拉、视差、漂移等不得因收录进本库就用于插画。证据截图或信息卡使用运镜，也需按实际语义与本集规则判断。
- 信息卡保留对象关系、中间状态和结果阅读。上游样例秒数、强调幅度、条目容量只是原效果参数，不是本项目新增配额或固定节拍。
- 上游固定品牌、角标、字幕运动、人物占位、音效、工作台、默认配色及整片制作/验收流程不自动采用。案例中的日期、数字、产品界面均不是本集事实或素材来源。
- 源码内的文字对象可分离，不等于剪映原生文字、轨道或曲线属性已经可编辑。明确要求剪映导出时，继续按仓库内有效的剪映分层导出 Skill 执行。
- 实际适配效果时保留动态机制，可按文案调整布局、配色、中文字体、素材、时长和结果保持；不能把库里的中性色块重复套成整集统一模板。

## Git 源码分发

GitHub 同步 108 份中文笔记、语义索引、查询工具、固定版本的配方文档、TSX、HTML 及必要运行时代码、来源清单和授权。预览图、上游图片与视频保留本地，不随 Git 提交；索引中没有预览图时会显示说明，部分上游演示需恢复媒体后才能完整播放。

仅下载源码时使用以下校验，核对 332 份上游文本源码、108 套覆盖、证据与索引，不要求媒体存在，也不覆盖原完整校验报告：

```powershell
python -B "research/video-talkcraft/scripts/validate_library.py" --source-only --no-write
```

源清单仍保留原始全部 366 项及其哈希，其中 34 项为上游媒体。源码校验通过不代表这些媒体齐全，也不代表演示、V5 适配或正常速度主观视听通过。`catalog.json` 与 `previews/capture_report.json` 的历史取样记录只说明研究时曾执行，不能作为新克隆环境的播放验证。

`scripts/sync_snapshot.py` 会按固定版本补齐原始上游文件，包括媒体，不是日常制作或纯源码验收入口。完整本地媒体均已恢复时，才使用下面原有的严格完整校验。

## 文件组织

| 路径 | 内容 |
|---|---|
| `index.html` | 本地可搜索、可筛选的 108 套索引与预览 |
| `cards/` | 108 份逐卡中文研究笔记 |
| `catalog.json` | 完整结构化研究记录，供程序按需读取 |
| `semantic_index.json` | 语义关系、分类和用途索引 |
| `source_manifest.json` | 上游版本、来源、授权及文件 SHA256 |
| `upstream/` | 惰性保存的上游原文件；不是全局安装的 Skill |
| `previews/` | 静音演示取样、拼图与取样报告 |
| `research_batches/` | 分批独立研究记录及 ID 分工 |
| `research_summary.json` | 全量覆盖统计 |
| `verification/` | 完整性与索引浏览检查证据 |

需要复核完整性时运行：

```powershell
python -B "research/video-talkcraft/scripts/validate_library.py"
```

已经通过的检查不用在每集制作时重复运行。只有相关文件变化、检查失败或明确要求复核时才重新检查。

## 来源、授权与更新

原项目：[Vincentwei1021/video-talkcraft](https://github.com/Vincentwei1021/video-talkcraft)。本次锁定提交 `a7c29edfb2404612dde6a5a1c8aa94232e85625b`，不以在线目录变化悄悄替换本次研究结果。

Required Notice: Copyright (c) 2026 Vincent Wei (https://github.com/Vincentwei1021/video-talkcraft)

原文件按 [PolyForm Noncommercial 1.0.0](upstream/LICENSE) 保存，其他来源说明保留于 [THIRD_PARTY_NOTICES.md](upstream/THIRD_PARTY_NOTICES.md)。媒体仅作为上游研究演示依赖；正式视频需要按具体素材来源和实际用途处理。本次没有安装上游全局 Skill，没有导入它的制作规则，没有自动提交或推送 GitHub。

`scripts/sync_snapshot.py` 只补齐该固定版本的研究文件；文件已齐时使用本地缓存。若以后升级上游版本，应另建研究快照并重新核对受影响卡片，不复用不匹配版本的通过结论。
