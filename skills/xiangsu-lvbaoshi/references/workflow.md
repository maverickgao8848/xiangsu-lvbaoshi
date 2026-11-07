# 正片制作

先读取本期已确认决定、原片、可信校订稿及其时间。保留 `^正文^（要求）` 的内容锚点；不把粗剪再改成新文案。无可信时间先按 media-use 转录／对齐并校订，精度不足时声明段级时间。

## 冻结与起草

```powershell
python scripts/prepare.py --source <粗剪.mp4> --project <新工程> --end <秒数> --timing <可信时间JSON>
```

也支持 MAV 的 `--alignment` 加 `--source-map`、`--handoff`、`--start`、`--preserve-full-input`。默认最多240秒；明确批准保留更长原片才用 `--max-duration 300`。prepare 保存源片、来源SHA、时间精度、模板／字体／声音的冻结指纹，并创建整片草案。`--timing` 为 `{basis,precision,tokens}`；precision 是 word 或 segment，tokens 为 `{start,end,text}`，时间相对所提供的完整粗剪。源片原声保留。没有时间稿时可冻结、起草，正式 compiler 拒绝空时间。

## 全文规划

prepare先用`--upstream-frame <完整frame.md>`或自动发现的上级frame冻结本期风格；无上游时逐字节采用assets/frame/FRAME.md（用户指定GlassLime旧项目原文）。frame-resources.json保存背景/点阵、字体、颜色和材质的实际文件及SHA。新增MG按动画路由完整继承，不为选题重新概括视觉规范。

先读全文，将其按连续观看任务组织成 host、data、dialogue、evidence、illustration、mechanism、operation。每段写真实台词锚点、观众应获得的信息、主画面制作方、辅助表达、素材分工及进入／退出。干净真人段也写入计划；一段连续解释整体交给所选动画制作方，不把每句话拆成一个短 MG 工程。

逐段遍历`effect_planning.py --catalog`导出的完整候选；它合并[效果目录](effect-catalog.json)、[保留生产层与R配方](production-layers.json)、正式路线、背景修饰、导航进度条、A/B转场和局部退出材质。新旧候选基础权重相同，先比较语义和必要输入，不沿用旧片的效果子集。未采用候选填写具体考虑或排除理由；considered项绑定实际段落，供编排表显示可替代项。检查使用次数、窗口时长和零使用项，同类观看任务重复时再比较备选；不随机或为了凑种类塞效果。B/D高频仅适用于动作层。多数适用表达窗主动检索 Pixel2All 物件，平台用真实 Logo；绑定实际图片槽，或记录本段具体例外。数字／原文用真实证据，物件不能代替证据。必要输入、媒体类型、透明背景、源像素及一致性只按当前方案约定。

```powershell
python scripts/effect_planning.py --catalog
python scripts/orchestration.py --project <工程> --plan <edit-plan.json> --draft
```

展示生成的 ORCHESTRATION.md，先处理缺事实、缺素材和影响艺术表达的决定；已有本期授权与选择直接沿用，不反复访谈。表由计划生成，不能反向手改它。prepare 草案里的 missing 和未评估候选不自动获得批准。

## 制作和装配

主画面↔完整MG／素材的交接默认使用[01玻璃换片或02青柠漏光](roll-transitions.md)，两款均已批准，制作时按画面自行选用并写入rollTransitions；不要求再让用户逐段挑选。编译器在真实A/B切点双向执行，同段进出同款，与章节导航、A–D局部特效进出场分开处理。检查effective-plan、build-report和编排表里的实际选择。

先制作必要素材／Scene Kit／真实录屏／所选动画，再把实际资产和时间写回同一计划。来源、许可或使用依据与 SHA 登记在 asset-credits.json。Pixel2All 搜索／导入使用 scripts/stage_object.py（PNG 转换需 Pillow）；Logo 可用 stage_logo.py 从本期仓库图库选取。外部媒体先用本期已有素材，需补素材时查 editorial-asset-library。

像素·绿宝石 模板以 [生产槽位](content-slots.json) 填充实际文字／图片，沿用已保存材质；实际源码生成布局，槽位不创建第二套模板。数据、证据和截图高亮先核对正文、出处及源像素。视频素材正常用动态 `media`／`screen`，抽帧不自动替代展示视频；确需静帧阅读时写 stillReason。MG 交接见 [动画路由](animation-routing.md)。

使用`exitMotion:"domain-warp"`时，先按[局部退出材质](plan-format.md#局部退出材质)准备并截取本期真实透明前景；声音节点与退出时间一起由编译器生成。它是原效果退出的一部分，不单独占用段落。

大于180秒的新视频默认开启A银灰导航三件套：章节角标、分章进度条和换章滑入／青柠扫线转场。按全文编排真实章界、编号和标题，写进项目根 chapters.json；编译器自动装配，不占段落或物件槽，不重复叠同章L28。180秒及以下可显式navigation.progress=true启用，false可覆盖关闭；接口和约束见 [导航进度条](navigation-progress.md)。

```powershell
python scripts/compile.py --project <工程> --plan <edit-plan.json> --validate-only
python scripts/compile.py --project <工程> --plan <edit-plan.json>
```

compiler 校验完整覆盖、执行引用、全量候选、物件实际绑定、资源／源片／时间指纹、文字图片槽位、原图矩形、动态媒体时窗与 MG 源工程；输出原声、字幕、背景修饰、模板动画、静音B-roll及原生audio的 HyperFrames 工程。生成 HTML 不手改；修改计划或素材，再重新编译。

字幕由编译器分组为原生子合成，避免 Studio 将整片字幕识别成大量嵌套结构；字幕文本、绝对时刻、字号和背景样式保持同一份 cues 数据。

## 验证与交付

先用含核心难点的20–30秒真实口播段检查：人物→证据→完整MG→人物、动态玻璃采样、切点、字体、字幕、原声和声音节点；运行 npm run check，检查正常播放、正反向 seek。选用 A 进度条时，另核对每个章节切换点的分段填充、游标和亮暗状态，并确认不压字幕。技术 fixture 只能证明接口，不能替代用户艺术审看。预览确认后按本期导出授权渲染。更换选题／人物／媒体复测后才说明相应组合可复用。

交付 edit-plan、ORCHESTRATION.md、input-lock、words／captions、build-report、可编辑主工程、像素 MG／界面源工程与冻结视频、媒体来源及检查证据。保存的六秒样本仍用于选型，不作为正片验收。框架、MG 与素材获取能力作为明确外部依赖；编译不导入旧 MAV Skill。

素材或动画需要电影式展映时，在对应media/broll/screen/animation beat显式选display.style=cinema；先评估display:cinema并阅读[22号电影画框](material-display.md)，再制作与编译。
