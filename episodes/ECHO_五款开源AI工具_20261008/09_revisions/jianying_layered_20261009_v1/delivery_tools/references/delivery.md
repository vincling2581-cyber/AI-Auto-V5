# 草稿包与本机注册

本 skill 的助手脚本不负责把任意 MP4 自动还原成图层。先完成本项目渲染/抽层适配，再用脚本验证通用草稿包；支持的本机运行时可继续注册草稿。

## 包与记录

按 [package-schema.md](package-schema.md) 生成包内相对路径清单，文本嵌套 JSON 中的字体路径也应指向包内文件。建议结构：

```text
export-revision/
  package/
    draft_content.json
    manifest.json
    media/                 必要图片、透明动效、镜头、声音、字体
    draft_cover.jpg        可选
  source/                  本次源工程与适配器，或记录已经交付的实际位置
  按大框编辑索引.txt
  检查报告.json
  编辑说明.txt
```

编辑索引列出镜号、框名、片段名、轨道、起止时间，以及框体/文字/图形/公共层。轨道名可复用，片段名保留具体内容。图形动画通常是透明 MOV，框体通常是 PNG 或透明 MOV；它们可整层调整与替换，不能声称内部已成为剪映原生矢量。

需要 ZIP 时，先写完全部说明及报告再打包，对每项记录字节数和 SHA-256，完成 ZIP CRC 和逐项哈希校验。不要在校验后再悄悄追加“最终报告”使校验失效。可重渲源代码不得依赖未交付的旧集修订目录。

## 找到运行时

- 检查目标项目已有导出工具、当前 Python 环境、`Get-Command python,ffmpeg,ffprobe`，必要时查看用户已配置的虚拟环境。不要把任何历史机器的盘符、用户名、Python 环境和版本号写成要求。
- 构建草稿可以用目标环境实际支持的剪映库。附带安装助手支持带 `DraftFolder(..., content_codec=..., user_data_path=...)`、`JianyingDraftCryptoCodec` 与 `DraftCryptoConfig` 的 pyJianYingDraft 实现；先验证本地 API。其他库/版本使用当前可用适配器，不盲目覆盖安装或悄悄降级。
- Windows 常见 User Data 在 `LOCALAPPDATA/JianyingPro/User Data`，根索引在其 `Projects/com.lveditor.draft/root_meta_info.json`，但媒体草稿目录可能已自定义。读取当前配置/索引确认实际路径。软件安装目录亦需现场发现。
- 用户只要求导出草稿包时，不需要访问或修改本机根索引。依赖不可用不应阻止已能完成的素材/源工程打包；对无法完成的原生构建或注册明确标注。

## 本机注册助手

所有命令中的路径都是当前任务提供的参数，使用正确的 shell 引号。默认仅预检，不写剪映目录：

```text
python scripts/install_draft.py --package PACKAGE --user-data USER_DATA --draft-root DRAFT_ROOT --jy-install JY_INSTALL --name NEW_NAME
```

用户已明确要求直接导入时，用具备兼容库的 Python 加 `--install` 执行。同名拒绝覆盖；选择新的名称即可，无需因此让用户重复批准已经授权的新草稿创建。不要向脚本提供用户正在编辑的现有草稿名。

```text
python scripts/install_draft.py --package PACKAGE --user-data USER_DATA --draft-root DRAFT_ROOT --jy-install JY_INSTALL --name NEW_NAME --install --audit-dir AUDIT_DIR
```

助手会在写入前校验包、记录根索引和既有草稿，复制素材到新目录，重定向素材及嵌套字体路径，然后通过本地库保存与注册。不能仅复制目录就声称已注册；应确认唯一索引记录和媒体链接。

剪映运行中不自动关闭、重启或控制 UI。注册前发现根索引或既有草稿变化时，保留已完成的新目录和审计记录，停止注册并重新读取现状；不得用旧备份覆盖用户新状态。重试采用新名称/明确清理自己创建的暂存副本，不能无限重试。

助手仍可能受软件保存与注册之间的并发窗口影响；本机导入检查不等于编辑器已经成功显示。注册失败报告实际阶段，不把“目录存在”当成功。不得自动回滚用户根索引或删除旧草稿。

## 最终报告

只报告已验证内容：新草稿名称/路径、分层粒度与轨道数、媒体完备、是否完成注册、独立性与编码检查结果。若未在剪映原生打开播放和导出，标注未验证；如未迁入旧草稿手动修改，直接说明。把复杂文字映射差异与图形内部编辑边界留在随包说明中，重大可见差异同时在交付消息中提示。
