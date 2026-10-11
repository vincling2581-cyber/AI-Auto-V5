# reference_cards_v1 使用说明

这是最新认可成片 `card_style_v4_reference` 的通用信息卡方法资产，供新集重新编排内容和动作。默认视频链是 HTML/SVG → 浏览器逐帧绘制 → FFmpeg 片段 → 主工程合成；剪映导入不在默认方法内。

## 内容

- `card_kit.js`：可复用路径、描画、遮罩、图标、轮廓形变、容器开合等 primitive；无本集镜号、文案、场景调度或数据 fetch。
- `palette_profile.json`：配色职责、卡片字号和几何可调默认起点。
- `vendor/`：本地 Flubber 0.4.2 及许可；无 Tween.js 运行依赖。
- `archive/`：认可母版及原始活动源的只读证据，禁止作为新集默认执行入口。
- `method_sources.json`：输入和衍生文件路径、SHA-256、出处及归档关系。

## 新集如何使用

1. 从根 `production_standard.json` 选择标准，读取本集标准锁，把本集明确覆盖合入得到 effective defaults；不要直接将本包 profile 覆盖到已确认的本集参数之上。
2. 新写语义结构、场景布局和按口播确定的事件；可参考归档方法，但不能复制本集固定文案、C02 等编号、坐标、数量和时间。
3. 加载 `vendor/flubber.min.js`（有轮廓形变时）及 `card_kit.js`，调用 `const K = createReferenceCardKit(effectiveDefaults)`。函数要求有效的 video、type.family、cards.palette/typography/geometry/frame_time_easing。使用 `K.profile()` 保存本集传入配置；它不是各组件消费了全部配置的证明，实际生效仍须检查 SVG 和画面。
4. 自行实现 `renderFrame(frame)`：先 `K.beginFrame()`，计算 `t=frame/effectiveDefaults.video.fps`，将本集语义事件以明确时间变成 SVG。`K`不包含页面或整卡内容，不会自动完成新片。
5. 所有组件内置短入场、局部图标比例和形变曲线都是起点；新片按本集 effective defaults 及事件参数显式覆盖，核对配置是否实际影响输出。主题色板、字号、线宽和圆角由初始化配置注入。形变路径只提供通用几何，不构成固定的题材对象要求。
6. 检查对象身份、路径和到达交接、前后遮挡、并列/顺序语义。检查过程内部20%/50%/80%、编码中点邻帧及正常速度阅读；再纳入主工程。

## 接口边界

`box/panel/text/group/clip/settle/path/icon/packet/morph/folder` 与原始源工程的绘图含义一致。`packet` 依据同一 SVG path 的弧长移动，`morph` 通过本地 Flubber 在过程区间内连续插值；场景作者仍负责起终态对象、前后叠放和交接后保留，不能仅调用函数就声称语义正确。

`cards.frame_time_easing.object_default` 实际控制 `m()` 的默认进度及依赖它的对象变化；`morph_default` 实际控制形变轮廓、位置、大小和混色的进度。支持 `linear`、`quadratic_out`、`cubic_out`；当前认可方法起点分别为 `cubic_out` 和 `quadratic_out`。单次调用 `m()` 可显式传入同一组值，兼容旧函数参数别名 `quadratic`、`cubic`。未知或缺失的默认缓动在初始化时报错，不静默回退。路径点由调用者给出明确进度，仍依据真实路径弧长取点。

`cards.geometry.icon_viewbox_units` 是方法固定坐标单位，必须为 **100**，不是可调整的图标尺寸参数；初始化会拒绝其他值。用 `icon()` 的 `size` 调整画面上的图标尺寸，用 `icon_stroke_local_px` 调整局部线宽；路径局部坐标保持100单位以免图形比例漂移。

主体色板、文字默认字号、框线/圆角、连接线和图标局部线宽读取 effective defaults。`panel()` 的 soft/outline 装饰边色、`morph()` 的内部纸面细线、`folder()` 的局部笔触与造型、短入场姿态以及弧线高度等仍有方法内置起点；它们不是全部暴露在配置中的旋钮。新集需要改变时，在本集组件代码或调用参数中显式调整并记录、渲染检查，不把 `K.profile()` 返回的输入配置当作所有装饰和造型均已消费该配置的证据。

`text`是SVG文字。它在源代码中可改，在默认片段中随画面编码；不声称为剪映原生可编辑文字。原生字体换算、alpha片段拆分、ProRes抽层和草稿打包只属于用户另行要求的剪映交付，不在此包内。

## 归档使用限制

archive 原程序保留硬编码的本集台词、卡片边界、布局和时点，且可能读取旧标准快照。归档用于证据/历史复现。它们不会被本包自动加载；历史程序不得覆盖新标准。归档母版仅作认可效果参考，不是新片的可重复素材。

72/46/34px卡片字号和2/3/28等几何值继承已认可成片。用户于2026-10-06授权由助手检查，检查无问题后作为可调默认起点启用；不表示用户亲自逐项审阅，也不把这些数值固定为所有未来内容的唯一选择。本集明确需求和有记录的合理调整继续优先。
