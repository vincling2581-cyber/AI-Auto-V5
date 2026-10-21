# 逆向工程 Skill 单集：片段来源校验修复

此前，修改公共卡片代码后仅重渲一个镜头，合成器仍会拼入其余旧片段；机器检查又根据当前源码重建依赖清单，可能把混用旧片段的成片记为通过。

本次修复为每个实际渲染并完成原有检查的镜头保存 `.render.json`，记录渲染前后的源码、配置、素材、字体和工具指纹，以及片段输出哈希。合成器在写入拼接清单或调用 FFmpeg 前校验全部片段，成功后保存成片来源记录。机器检查在写依赖清单前及签发通过报告前再次校验成片、片段和来源记录。

现有制作规则、视觉实现和命令接口保持不变。源实现按本集原来锁定的配置执行，不将旧集迁移到当前新集标准。

## 代码范围

- `episodes/ECHO_逆向工程Skill_20261011/06_project/clip_provenance.py`
- `episodes/ECHO_逆向工程Skill_20261011/06_project/cards/render_cards.py`
- `episodes/ECHO_逆向工程Skill_20261011/06_project/finish.py`
- `tests/test_reverse_skill_clip_provenance.py`

该单集此前没有纳入版本控制，因此同时纳入原有渲染入口 HTML、其加载的四个 JavaScript 文件，以及运行和检查所需的单集配置与标准锁；这些文件保留现有内容。

## 使用方式

在具备本集本地素材的单集根目录，继续使用原命令：

```powershell
python 06_project/cards/render_cards.py --cards C03 --workers 2
python 06_project/finish.py --assemble --qc
```

若存在过期片段或缺少生成记录，合成器列出需要重渲的镜头并停止。补齐这些镜头后，再使用原合成命令。共享脚本及信息卡素材依赖按保守范围判断；只修改单卡分镜数据时，其余依赖未变的片段仍可复用。

`--samples` 不签发可供合成的片段生成记录；`--verify-existing` 必须先有匹配的生成记录，不能用当前源码为未知来源旧片段补发身份。运行期间改变已加载的 Python 源码、配置或分镜，也会拒绝签发新记录。

原音频、字幕、插画、仓库截图、渲染片段、成片和本地检查产物继续留在本地。真实整集运行仍需要恢复这些本地文件，以及本集原有标准快照；本提交不包含媒体交付包或预览服务。

## 针对性验证

从仓库根目录运行：

```powershell
python -B -m unittest discover -s tests -p test_reverse_skill_clip_provenance.py -v
```

13 项测试通过。覆盖配置、源码、素材、字体及输出变化，记录缺失或损坏，单卡修改复用，成片被替换，运行期间输入变化，以及来源不明片段的复检限制。集成用例在临时目录真实运行 Chrome 和 FFmpeg，确认局部重渲混入旧片段会被拒绝，补齐重渲后能合成。

测试环境为 Windows、Python 3.12、Chrome、FFmpeg、微软雅黑及 Playwright、Pillow、NumPy、OpenCV；本机工具与字体路径来自本集配置。测试生成的媒体均位于临时目录，不会重渲或覆盖已有成片。此验证仅覆盖来源校验修复，不代表重新完成整集主观视听验收。
