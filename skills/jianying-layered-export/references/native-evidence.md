# 原生校准及最终排版证据

仅在用户明确要求原生校准、排版复检或原生验收时读取并执行。本契约定义“原生复检通过”的证据，不是默认草稿导出的前置条件。默认导出完成即交付，复检未执行不阻塞导出；注册或旧证据失效也不会自动授权复检。只在真实采集、对照并确认对应项目后填写 `passed` 或 `true`。

## 工作次序

1. 用当前画布、帧率、字体及剪映版本创建少量代表性样例，实际在剪映预览或原生导出中采样。覆盖每种字体/字重、大小范围、锚点和换行情形，测量字号及位置映射。实测可以形成公式或查表，但没有默认的固定转换倍率或 Y 偏移。保存校准草稿 JSON、原生画面、源参考及实测参数。
2. 把参数应用到最终可编辑草稿。需要预先注册以便查看时使用 `--allow-unvalidated-test-draft`，只产生有显著标记的测试稿。
3. 从最终实际草稿采集原生截图或原生导出帧，与同一时刻源参考对照。最终采样联合覆盖全部 `text` / `brand` 片段，逐项核对字体、视觉字号、位置、换行、裁切。时间在片段范围内仍不足以证明可见：对有零透明度/零缩放或遮挡的片段，应采集真正可见时刻。
4. 完整原生验收要求下保存下述证据并运行默认校验。缺校准、缺原生样本、仍有明显差异或证据失效时，不能标原生验收通过，但已完成的导出仍可交付。仅局部复检时记录实际覆盖范围，不扩展成全量验收；继续检查或迭代须处于用户明确要求的范围内。

原生图像来自剪映 UI 或剪映自身导出的采样帧。源参考可以从 SVG/HTML/其他源工程渲染；重画草稿中字号、把字号乘回原比例、浏览器合成、PIL/SVG 复合都不是原生证据。不得复制源图当作原生图，也不得只改来源字段绕过门禁。

源工程具有相应内容时，最终原生采样还须覆盖这些实际风险：

- SVG 空白折叠前后可能变化的中英文文本，确认空格、字距、换行与对齐继承源画面。
- 水平/竖直描边线，确认整段分隔线和连接线未因零维几何包围盒被筛掉或裁掉。
- 移动标签相互穿叠的过程帧，确认文字随所属对象保持原绘制遮挡顺序，没有双重字形或从前景对象上透出；到达后无重叠的静帧不能证明此项通过。
- 遮罩开始前、遮挡途中及完全隐藏后的代表帧，确认没有提前出现的空框、残留轮廓、黑边或透明接缝。用于遮字的前景遮罩还须检查其他对象早期进入、穿越中途及离开其区域的帧，确认没有误切无关对象的背景、文字或连线；灰边消失或到达帧正常不能证明此项通过。必须使用实际剪映输出检查透明边缘与遮挡关系。

上述检查可以复用同一组有针对性的采样，不固定帧数，也不要求无对应效果的工程额外造样例。在样本或随附审核记录中注明覆盖的过程与结论；`review.clipping` 只有在相应裁剪、遮挡及遮罩边缘均核对后才能填 `true`。当前脚本能确认文本片段覆盖，不能自动判断是否挑中了这些关键过程，也不能识别像素中的遮挡错误，审核者不得仅凭到达帧齐全填写最终 `passed`。

## 文件与绑定

证据默认在包根 `native-evidence.json`，也可用 `--native-evidence 包内相对路径`。所有 `artifact` 都是 `{ "path": "包内相对路径", "sha256": "文件 SHA-256" }`。不允许绝对路径、上级路径或移出包根的链接。证据与画面放独立 `evidence/`；它们无需列入只描述草稿引用素材的 `manifest.media`，避免证据包含自身哈希形成循环。若交付 ZIP，归档清单仍要包括证据文件。

`binding` 包含最终可移植 `draft_content.json` 与完整 `manifest.json` 的 SHA-256、画布、帧率、微秒时长、所有实际原生字体及媒体清单指纹。仅媒体指纹不能覆盖对象归属/片段清单变动，因此 `manifestSha256` 也必须匹配。旧证据缺少该绑定时视为失效，不能只补一个当前哈希就声称已经重新审核。媒体指纹用助手计算，不自行拼接：

```python
from native_evidence import media_manifest_sha256
binding["mediaManifestSha256"] = media_manifest_sha256(manifest)
```

该函数对媒体项 `{path, sha256, bytes}` 按 path 排序，将路径分隔符规范为 `/`、哈希转小写，再以 `json.dumps(..., sort_keys=True, separators=(',', ':'), ensure_ascii=False)` 的 UTF-8 字节计算 SHA-256。当前完整证据助手要求实际草稿引用的包内字体文件，不能只填显示名称；普通导出及未复检导入可以采用声明的系统字体依赖。系统字体的运行时文件绑定尚未由此证据格式覆盖，不得强制复制无权分发的字体或伪造路径来通过门禁。

`runtime` 指定版本字符串和在 `--jy-install` 下的实际 exe 相对路径及 SHA-256。所有样本都来自这一版本。升级、换 exe、字体或画布后标记相关证据失效，用户提出复检后才重做对应校准及检查；默认安装模式验证 exe 哈希。

测试注册只允许名字/ID 及素材路径重定位影响安装副本。截图记录的 `capture.draftSha256` 绑定用于该次注册的可移植草稿；核对安装审计中解码后的 tracks/materials 与该包重定位后相符。若在剪映中改过排版，先回收这些实际修改到最终包，再绑定新哈希并重新采样；不能对旧包哈希声明新画面合格。

## JSON 形状

以下是字段形状，示意值不是可交付证据。`calibration.parameters` 保存实际测得的公式系数、字号查表、位置/锚点处理等，不限定某种实现。两个阶段都要记录实际审核者和时间。

```json
{
  "schemaVersion": 1,
  "binding": {
    "draftSha256": "最终草稿的 SHA-256",
    "manifestSha256": "最终完整 manifest.json 的 SHA-256",
    "canvas": {"width": 1920, "height": 1080},
    "fps": 30,
    "durationUs": 10000000,
    "mediaManifestSha256": "由助手计算",
    "fonts": [{"path": "media/fonts/body.ttf", "sha256": "字体文件 SHA-256"}]
  },
  "runtime": {
    "product": "JianyingPro",
    "version": "实际运行版本",
    "executableRelativePath": "JianyingPro.exe",
    "executableSha256": "实际 exe 的 SHA-256"
  },
  "calibration": {
    "status": "passed",
    "reviewer": "实际审核者",
    "reviewedAt": "实际时间",
    "method": "原生样例与源参考对照并测量",
    "parameters": {"mapping": "本次实际测量得到的字号及位置映射"},
    "draft": {"path": "evidence/calibration-draft.json", "sha256": "校准稿 SHA-256"},
    "samples": []
  },
  "finalLayout": {
    "status": "passed",
    "reviewer": "实际审核者",
    "reviewedAt": "实际时间",
    "samples": []
  }
}
```

两个 `samples` 都必须非空。每项共有字段如下：

```json
{
  "timeUs": 1000000,
  "nativeFrame": {"path": "evidence/native-01.png", "sha256": "原生栅格 SHA-256"},
  "referenceFrame": {"path": "evidence/source-01.png", "sha256": "源参考 SHA-256"},
  "capture": {
    "method": "jianying_ui",
    "draftSha256": "此样本对应草稿的 SHA-256",
    "recordedAt": "实际捕获时间",
    "viewport": {"x": 0, "y": 0, "width": 1920, "height": 1080}
  },
  "review": {
    "status": "passed",
    "font": true,
    "textSize": true,
    "position": true,
    "lineBreaks": true,
    "clipping": true
  }
}
```

- 校准样本另加 `fontPaths:["media/fonts/body.ttf"]`、`sourceFontSizePx:实测源字号`、`nativeFontSize:对应原生字号`，以及 `nativeStyle:{"bold":false,"italic":false,"underline":false}`。`nativeStyle` 仅支持这三个布尔字段，未填写的字段默认为 `false`；兼容旧样本省略整个对象时，也只声明常规、不倾斜、无下划线样式。一个样本的全部 `fontPaths` 使用同一组声明样式和字号；不同样式或字号各写一条样本，可以引用同一张实际审核过的原生帧。
- 声明的每个字体、`nativeFontSize` 和 `nativeStyle` 必须同时匹配校准稿该 `timeUs` 的活动原生文字实际样式。字体路径以 `/` 规范化；样式从草稿 `content.styles` 的 `font.path`、`size`、`bold`、`italic`、`underline` 读取，缺省布尔字段按 `false` 处理。字号匹配允许绝对误差 `1e-6`。只有声明且匹配的样式/字号计入已测集合；同帧其他字重、倾斜、下划线或其他字号不会自动计入。
- 最终全部 `text` / `brand` 片段中的每种实际字体及样式组合都必须有上述校准记录；最终每个实际原生字号必须落在同字体、同 `bold/italic/underline` 组合已测实际字号的 `[min,max]` 内，端点允许绝对误差 `1e-6`。常规样式不能覆盖粗体；只测一个字号仅覆盖该字号，区间外不能外推。脚本返回 `calibratedStyleRanges` 供检查覆盖范围；字号范围通过不代替锚点、换行或具体画面的视觉审核。`capture.draftSha256` 必须等于 `calibration.draft.sha256`，校准稿画布与帧率必须匹配最终包。
- 最终样本另加 `segmentIds:["实际文本片段ID", "另一文本片段ID"]`。并集必须覆盖全部 `text` / `brand`；`timeUs` 必须位于所列各片段有效时段。`capture.draftSha256` 必须等于 `binding.draftSha256`。
- PNG/JPEG 必须为实际栅格文件；把 SVG 改扩展名不接受。助手检查 PNG 的像素数据结构及 JPEG 的基本帧/扫描结构，但这不能证明图像真实来自剪映，也不等于完整图像解码。源参考尺寸必须等于画布。原生帧可以是包含 UI 的截图，`viewport` 标明原图中的画布预览区域；矩形不能越界、宽度至少 `min(320, 画布宽度)`，宽高比相对误差不超过 1%。最好采集接近输出分辨率的画面。
- 原生导出采样用 `capture.method:"jianying_native_export"`，并增加 `capture.exportMedia:{path,sha256}` 指向包内实际导出媒体；`timeUs` 表示原始草稿时间，若为区间导出，额外记录区间起点及抽帧时间，确保可复现。原生样本与参考不能是同一哈希。
- `review` 是视觉审核结果。脚本无法判断截图是否实际上来自剪映、内容是否真的无误；伪造来源或自动填写通过违背本契约。机器只验证文件完整性、依赖、来源声明及覆盖。

## 检查与结果

用户明确要求完整原生证据检查时：`python scripts/validate_package.py --package PACKAGE --require-native-evidence --report REPORT`。旧的无模式参数调用仍保留此门禁，不是 skill 默认导出步骤。缺失、失效或不完整证据返回失败，`deliveryReady:false`；这些字段描述证据门禁，不否定导出文件已生成。静态证据匹配后 `nativeValidation:"evidence_verified"`，但未解决的动效警告仍使 `motionValidation:"requires_review"`、`deliveryReady:false`；不能仅看 `passed` 或退出码就宣布全片效果通过。

用户仅要求结构复检时使用 `--structure-only`，结果为 `status:"structure_passed"`、`nativeValidation:"not_performed"`、`deliveryReady:false`。真正的测试/校准注册仍可用旧 `--allow-unvalidated-test-draft`，普通未复检导入使用安装助手的 `--allow-unreviewed`，见 [delivery.md](delivery.md)。这些模式均不能用于宣称原生验收通过，正常导出不需要运行它们。

原生证据契约通过、机器结构检查、完整正常速度视听、原生完整导出分别记录。证据中的导出采样不能自动推广为整集播放或最终完整导出通过。独立行为测试使用 `python scripts/test_native_gate.py` 和 `python scripts/test_style_coverage.py`；测试生成的合成图片仅用于门禁逻辑，绝不是任何项目的原生验收证据。
