# 通用信息卡绘图组件

本目录只保留既有 `card_kit.js`、可选 Flubber 0.4.2 及原许可证；v4.7 沿用绘图算法，并修正有效参数传递与 SVG 文字转义。不附带旧集场景、成片或历史通过报告。

1. 从项目 `CURRENT_PROJECT.json` 或本集锁选择标准，得到本集 `effective_defaults.json`。
2. 先根据语义选择卡片关系与形式。允许文章证据、自由关系图、映射、循环、极简结论等无大框画面，不因为 helper 有 `panel()` 就强制套双栏/三栏。
3. 每个场景按内容选择 `cards.palette_presets.paper`、`dark` 或登记的自定义色板，写入该场景传给 helper 的 `cards.palette`。全局 fallback 为浅纸色；局部深绿面板显式使用浅色字，浅表面使用深字，同时检查线条及辅助文字对比。绿白双框只约束已选中的双框布局。
4. 加载 `card_kit.js`，调用 `createReferenceCardKit(effectiveDefaults)`；需要轮廓形变时再加载 `vendor/flubber.min.js`。本集自己实现 `renderFrame(frame)`，语义事件与配音锚点决定起止帧。
5. helper 提供绘图、遮罩、路径、几何形变等基础函数，不负责镜头切换，也不消费动画同状态时长参数。内部短动效参数是可调起点，不能当作叙事节奏限制。
6. 对象沿同一路径移动、到达后目标更新、来源保留和遮挡需要场景作者实际实现；有像素变化不等于语义正确。完成后按 SOP 做适用的过程与正常速度阅读检查。

`K.profile()` 只返回传入配置，不能证明全部字段已被组件消费。实际消费边界如下。

| 配置或参数 | 实际入口 |
|---|---|
| `cards.palette` | 绘图函数的颜色角色；`panel('soft')` 使用 `soft/edge`，`panel('outline')` 使用 `soft/line`，后者仍有填充 |
| `type.family` | `text()` 的字体；字体列表中的引号与正文特殊字符会转义为合法 SVG |
| `cards.typography.node_px` | `text()` 未指定字号时的默认值 |
| `cards.typography.title_px`、`support_px` | 场景按文字职责显式传入，例如 `K.text(title,x,y,effective.cards.typography.title_px)`；helper 不猜测文字层级 |
| `panel_border_px`、`panel_radius_px` | `box()`、`panel()` 的边框与默认圆角；显式圆角参数可覆盖默认值，包括 `0` |
| `connection_stroke_px` | `path()` 的默认线宽；显式 `width` 可覆盖 |
| `icon_stroke_local_px` | `icon()`、`folder()` 在 100 单位图标坐标内的描边宽度 |
| `process_initial_seconds`、`frame_time_easing` | `m()` 的默认局部时长及对象／形变缓动；事件显式时长与曲线优先 |
| `video.width/height` | `path()` 的遮罩画布；帧率、背景绘制、字幕及镜头切换由场景实现 |

`morph()` 的内文细线默认使用 `ink` 角色；深色填充可通过末尾可选参数 `lineInk` 指定 `paper` 等可读角色。形变轮廓与内文的 `1/1.8` 单位细线、路径形状、控制点和短动效内部细节是局部造型，不是面板边框参数。`icon_viewbox_units=100` 是固定图标坐标单位；显示尺寸通过 `icon()`、`folder()` 的 `size` 或 `morph()` 的目标矩形调整。主题与尺寸改变后仍按实际输出检查对比和阅读。

文字在源码中可改，编码后是视频像素；剪映原生文字与分层导出按用户另行要求处理。
