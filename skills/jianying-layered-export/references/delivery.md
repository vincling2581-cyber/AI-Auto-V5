# 草稿包与本机注册

本 skill 的助手脚本不负责把任意 MP4 自动还原成图层。通过本项目渲染/抽层适配生成草稿包；用户另行要求复检或注册时，才使用对应助手。

默认只生成并交付草稿包，随后结束；上述验证脚本仅在用户明确提出复检后使用。默认不运行校验、原生校准或注册。缺少原生证据不阻止“导出完成”，复检状态另记 `not_performed`。

## 包与记录

按 [package-schema.md](package-schema.md) 生成包内相对路径清单，文本嵌套 JSON 中非空的字体路径也应指向包内文件。系统字体可使用明确的依赖声明并留空文件路径，不能承诺换机字形一致。建议结构：

```text
export-revision/
  package/
    draft_content.json
    manifest.json
    native-evidence.json   可选；用户要求原生验收并实际执行后保存
    evidence/              可选；仅存实际执行复检取得的证据
    media/                 必要图片、透明动效、镜头、声音、字体
    draft_cover.jpg        可选
  source/                  本次源工程与适配器，或记录已经交付的实际位置
  按大框编辑索引.txt
  检查报告.json
  编辑说明.txt
```

编辑索引列出镜号、框名、片段名、轨道、起止时间，以及框体/文字/图形/公共层。轨道名可复用，片段名保留具体内容。图形动画通常是透明 MOV，框体通常是 PNG 或透明 MOV；它们可整层调整与替换，不能声称内部已成为剪映原生矢量。

需要 ZIP 时，先写完全部说明再打包，可在归档清单中记录字节数和 SHA-256。默认不追加 ZIP CRC 或逐项哈希复验；用户要求包完整性复检时才执行，并绑定最终归档。可重渲源代码不得依赖未交付的旧集修订目录。

## 找到运行时

- 检查目标项目已有导出工具、当前 Python 环境、`Get-Command python,ffmpeg,ffprobe`，必要时查看用户已配置的虚拟环境。不要把任何历史机器的盘符、用户名、Python 环境和版本号写成要求。
- 构建草稿可以用目标环境实际支持的剪映库。附带安装助手需要分支扩展的 `DraftFolder(..., content_codec=..., user_data_path=...)`、`JianyingDraftCryptoCodec` 与 `DraftCryptoConfig`；它们不等于公开上游或任意同名 PyPI 包均支持。先核对模块路径、签名与平台依赖，来源见 [compatibility-sources.md](compatibility-sources.md)。其他库/版本使用适配的工具；缺依赖时给出明确错误，不自动覆盖安装、替换编辑器组件或悄悄降级。
- Windows 常见 User Data 在 `LOCALAPPDATA/JianyingPro/User Data`，根索引在其 `Projects/com.lveditor.draft/root_meta_info.json`，但媒体草稿目录可能已自定义。读取当前配置/索引确认实际路径。软件安装目录亦需现场发现。
- 用户只要求导出草稿包时，不需要访问或修改本机根索引。依赖不可用不应阻止已能完成的素材/源工程打包；对无法完成的原生构建或注册明确标注。

## 本机注册助手

本节仅在用户明确要求注册时使用，不是默认导出的步骤。三种模式不能混淆：已有完整原生证据用默认门禁；用户只要求直接导入用 `--allow-unreviewed`；真正的校准/测试稿才用 `--allow-unvalidated-test-draft`。不要为了正常导入强制把草稿伪装成测试稿，也不能因缺证据自动启动校准。

已完成原生验收后使用默认安装模式：读取包内 `native-evidence.json`，或以 `--native-evidence` 指定包内其他 JSON。证据绑定最终草稿、媒体、字体、画布、时长/帧率与实际剪映版本及 exe SHA-256。版本文件改变后证据失效，重新校准及审核仍需用户明确提出。

所有命令中的路径都是当前任务提供的参数，使用正确的 shell 引号。默认仅预检，不写剪映目录：

```text
python scripts/install_draft.py --package PACKAGE --user-data USER_DATA --draft-root DRAFT_ROOT --jy-install JY_INSTALL --name NEW_NAME
```

用户已明确要求直接导入、未要求原生验收时，用具备兼容库的 Python 加 `--install --allow-unreviewed` 执行。它仍执行安装前必要的结构与素材检查，保留动效/系统字体等未确认提示，不追加原生复检。同名拒绝覆盖；选择新的名称即可，无需因此让用户重复批准已经授权的新草稿创建。不要向脚本提供用户正在编辑的现有草稿名。

```text
python scripts/install_draft.py --package PACKAGE --user-data USER_DATA --draft-root DRAFT_ROOT --jy-install JY_INSTALL --name NEW_NAME --install --allow-unreviewed --audit-dir AUDIT_DIR
```

助手会在写入前校验包、记录根索引和既有草稿，复制素材到新目录，重定向素材及嵌套字体路径，然后通过本地库保存与注册。不能仅复制目录就声称已注册；应确认唯一索引记录和媒体链接。

普通未复检注册成功返回 `registered_native_review_not_performed`，不强加 `[TEST]`；`exportStatus`、`registered/registrationStatus`、`nativeReviewStatus` 分开记录。`deliveryReady:false` 仍描述原生证据门禁，不能解释为没有导出或没有注册。正式证据模式存在未解决的动效风险时，在写入前停止；切换普通未复检模式必须符合用户的实际交付范围，不能偷偷改模式来宣称原生验收通过。

保存后、报告安装完成之前，助手重新核对新目标目录内清单所列全部媒体（含字体）的字节数与 SHA-256，并保存 `installed_media_verification.json`。缺失、越出目标目录或内容变化时，安装结果为未完成且 `deliveryReady:false`，保留新目录与审计，不回滚索引或覆盖用户文件。

校准必须先注册才能原生采样时，可以明确使用测试模式：

```text
python scripts/install_draft.py --package PACKAGE --user-data USER_DATA --draft-root DRAFT_ROOT --jy-install JY_INSTALL --name CALIBRATION_NAME --install --allow-unvalidated-test-draft
```

此参数只跳过安装助手的原生证据门，不跳过结构、路径、媒体或已有草稿保护检查。名称若无 `[TEST]` / `[CALIBRATION]` 前缀，助手强制加 `[TEST]`；结果及审计始终 `deliveryReady:false`，成功状态为 `test_only_installed_not_for_delivery`。如实说明该注册模式，不将其宣称为原生验收通过；工具的测试标签不撤销导出完成状态。仅在用户明确要求后采样审核、更新证据或另建正式草稿。

剪映运行中不自动关闭、重启或控制 UI。注册前发现根索引或既有草稿变化时，保留已完成的新目录和审计记录，停止注册并重新读取现状；不得用旧备份覆盖用户新状态。唯一可继续的自动扫描情形是：旧草稿、全部原条目及根字段完全未变，仅新增唯一指向本次目标目录的索引项，且 ID 匹配本次 `create_draft` 创建的 stub 或最终 payload、名称匹配目标。如果库创建时只复制了空 ID 模板，助手保存该初始快照；随后仅在当前自建目标的 sidecar 与唯一新增索引项拥有相同新 ID、名称/路径匹配、仍为零时长且无时间轴素材的空 stub、该 ID 未被旧草稿使用、已写入的目标 payload 未被更改时，接纳编辑器补写的身份。不得只凭索引里的陌生 ID 扩大允许列表。助手记录扫描审计后由库正常 `save()` 完成一致注册。其他并发变化仍停止。重试采用新名称/明确清理自己创建的暂存副本，不能无限重试。

源包在验证后变化时停止；目标目录、媒体及封面复制前检查路径包含关系和链接，拒绝 Windows 保留名称/越界路径，不覆盖目标已有文件。审计目录新建在包和真实草稿根之外。`load_template` 后、`save` 前再次核对索引及既有内容，不能只在最后检查已被旧快照覆盖的结果。

第三方库 `save()` 内部仍存在读改写并发窗口；前后哈希与临时文件替换不能提供真正的 compare-and-swap 事务。当前助手不能保证完全消除编辑器同时保存造成的丢更新，也不会因此关闭或重启软件。本机导入检查不等于编辑器已经成功显示。注册失败报告实际阶段及可确认的注册状态，保留新目标和审计，不自动回滚索引、删旧稿或无限重试。

提供双击入口时，用正确引用自身目录的 `.cmd` 调用 PowerShell，包含中文的 Windows PowerShell 5 脚本使用合适的 UTF-8 BOM。不要把通常会在编辑器里打开的 `.ps1` 本身当作可靠的双击执行入口。打包只包含助手及声明依赖，不把某台机器的运行时绝对路径当通用要求。

## 最终报告

默认简短交付文件位置、导入/编辑说明及“导出完成；复检未执行”，随后结束，不追问复检。另有明确要求并实际完成检查或注册时，再报告对应范围及证据；证据契约通过仍不代表整集正常速度播放或完整导出通过。已知复杂文字映射差异与图形内部编辑边界写入随包说明，重大可见差异同时在交付消息中提示。
