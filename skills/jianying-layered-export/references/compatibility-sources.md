# 已核对的能力来源与适用边界

核对日期：2026-10-18。这是维护 Skill 时的资料基线，不要求每次导出重新联网。依赖版本改变或发生相关问题时，再按具体能力更新。源码说明“怎样写入数据”，维护者文档说明其支持范围；两者都不能代替本机剪映实际渲染。

## 官方资料

- [剪映官网](https://www.capcut.cn/)与[剪映开放平台](https://open.capcut.cn/)确实存在。本次公开检索未取得可核验的本地草稿 JSON schema 或官方本地草稿写入 SDK；不能因此说官方不存在开放接口，也不能把本 Skill 的 `manifest.json` 称为官方规范。
- [CapCut：把一个项目导入另一个项目](https://www.capcut.com/help/import-a-previous-project-into-the-current-project)说明渲染视频再导入不会保留原项目图层。[第三方编辑工程互通说明](https://www.capcut.com/help/how-to-export-pro-project)也不能支持“任意 AE/其他工程自动无损转剪映”的承诺。CapCut 帮助只代表页面所述产品和功能，不能证明中国版剪映有完全相同的草稿格式。
- [本地媒体导入格式](https://www.capcut.com/help/can-not-local-assets-be-recognized-during-import)列举的是指定平台的容器支持。MOV 容器支持不等于 Windows 剪映各版本都支持 ProRes 4444 的 alpha；现有编码参数只能称为已用配置，原生透明边缘仍以对应版本证据为准。

## GitHub 一手资料

| 实现 | 固定资料 | 对适配的影响 |
| --- | --- | --- |
| GuanYixuan/pyJianYingDraft | [README，1e228479](https://github.com/GuanYixuan/pyJianYingDraft/blob/1e228479dda361e312e85f6037002346cf6dca9a/README.md) | 当前上游使用 append/insert 轨道接口；支持矩阵按具体功能和版本阅读，不把生成、原生读取、注册、自动导出混为一项。 |
| 关键帧属性与写入 | [keyframe.py](https://github.com/GuanYixuan/pyJianYingDraft/blob/1e228479dda361e312e85f6037002346cf6dca9a/pyJianYingDraft/keyframe.py)、[segment.py](https://github.com/GuanYixuan/pyJianYingDraft/blob/1e228479dda361e312e85f6037002346cf6dca9a/pyJianYingDraft/segment.py) | Alpha 注明用于 VideoSegment；通用写入方法不作完整的媒体类型检查。等比缩放落到 ScaleX 与开关配合，是库侧抽象；关键帧默认线性插值。 |
| 原生文字与动画 | [text_segment.py](https://github.com/GuanYixuan/pyJianYingDraft/blob/1e228479dda361e312e85f6037002346cf6dca9a/pyJianYingDraft/text_segment.py) | 入场贴片段头、出场贴片段尾；类型和 duration 不代表任意起点或任意透明度曲线。样式 size 直接序列化，没有 CSS px 的官方通用换算常数。 |
| 上游模板读取 | [draft_folder.py](https://github.com/GuanYixuan/pyJianYingDraft/blob/1e228479dda361e312e85f6037002346cf6dca9a/pyJianYingDraft/draft_folder.py) | 本次公开构造参数为 folder_path/fallback_loader；不能假定具有分支扩展的 codec/user_data_path。 |
| GuanYixuan/pyCapCut | [README，ec61408d](https://github.com/GuanYixuan/pyCapCut/blob/ec61408d9f039c4045f946370bb35746b89b2479/README.md) | 面向 CapCut，接口演进和验证版本不同。不能换包名后直接沿用剪映资源 ID、格式或原生支持结论。 |
| aoguai/pyJianYingDraft | [README，69cee12a](https://github.com/aoguai/pyJianYingDraft/blob/69cee12ae3f7442416df16acdf368ae574764811/README.md) | 公开可见的 fork；维护者将 font_path、本机 codec 与注册称为额外扩展。codec 依赖本机组件、Windows 和匹配运行时；“私有扩展”不等于仓库不可见，也不保证同名上游包支持。 |

## 应保留的运行时记录

在当前修订记录实际编辑器产品/版本、操作系统、Python/库模块路径、版本与可查的来源/commit、关键适配器哈希、使用的字体和媒体编码。只填实际取得的信息，不因版本字符串相同就推断等于上述 commit。

为本次用到的能力注明 `documented`（资料声明）、`source_confirmed`（源码可写）、`native_verified`（绑定具体运行时的原生证据）或 `unknown/unsupported`。这些级别不能互相替代；不需要制作与当前任务无关的全功能支持表。

未找到通用字号倍率、跨版本稳定的零缩放显隐机制或完整的剪映透明视频兼容矩阵。遇到这些缺口，保留范围限定，不用营销文章或 issue 评论补成确定结论。无需下载未知可执行文件、替换编辑器组件或修改第三方软件来完成普通导出。
