---
name: xiangsu-lvbaoshi
description: 像素 Xiangsu 系列的绿宝石口播包装：编排并编译已粗剪横屏中文口播，保留荧光绿、玻璃、气泡、空间文字与点阵模板，协调证据、录屏、动作声音，并按内容选择 xiangsu-mg 或 Lemo-Opuscar 动画。
---

首次安装或运行时报环境缺失时，先阅读 [首次安装引导](references/first-install.md)。

# 像素·绿宝石 · Xiangsu Lvbaoshi

像素 Xiangsu 系列：`xiangsu-mg` 负责知识解释动画，`xiangsu-baijin`（白金）与 `xiangsu-lvbaoshi`（绿宝石）负责两套整片口播包装。

工程 profile、历史 producer/provider 与来源前缀保持兼容；新增 Lemo-Opuscar 制作方用于新规划或显式重做的段落，旧冻结工程不自动迁移。

独立的整片口播制作 Skill，保留28项 像素·绿宝石 模板、四组入退场及电子／快门声组。生产流程沿用白金版的冻结输入、全文编排、全量选型、物件分工、MG交接、严格校验和预览交付方法；使用独立资源包编译，不依赖白金版安装。完整命令与制作步骤见 [正片工作流](references/workflow.md)，执行字段见 [计划接口](references/plan-format.md)。技术接入与本期艺术验收分别记录，不把六秒样本或合成测试称为真人正片已经验收。

独立动画先按 [动画选型与交接](references/animation-routing.md) 比较两条制作路线：像素 MG 以知识关系、状态和教学落点组织画面；Lemo-Opuscar 以所选 STYLE 的媒介、对象行动与镜头语法组织画面，适合情境、隐喻、表演、产品空间，也可讲适配的机制。真人上的轻伴随效果仍直接用本 Skill。编排、候选、源工程冻结与 compiler 均支持逐段 provider 选择；Lemo 保留自身风格，不强制继承本包装 frame 或 Pixel2All 物件。两种动画制作能力是按需调用的外部 Skill，包装和适配代码保存在本目录。

## 编排与制作

以已粗剪、通常四分钟内的16:9中文真人口播为输入，保留真人拍摄背景和原声。按 host、data、dialogue、evidence、illustration、mechanism、operation 划连续观看任务，再从 [效果目录](references/effect-catalog.json) 选能解决本段阅读问题且输入完备的模板；干净真人段也是有效选择。编号L01、L25、L29保留删除状态，不恢复旧身份牌或旧版视觉。2026-10-15最新审看仅保留Pixel2all白色物件与圈点引出原有L02玻璃卡；本轮新增的其它五种标注和人后大字已撤下。2026-10-18 用户另选 A 银灰磨砂分章底栏，作为 `navigation.progress`：新视频严格大于180秒时默认联动章节角标、A进度条和换章滑入／青柠扫线转场；180秒及以下不自动启用，可显式关闭覆盖。章节按全文编排写入同一份 chapters.json，见 [导航进度条](references/navigation-progress.md)。新参考对应R01荧光三行重点字、R02轻透视圆角媒体窗、R03底部三阶段标题、R04灵活讲解舞台、R05顺应原拍摄构图的素材伴随，执行见 [参考配方与保留生产层](references/production-layers.md)，一并纳入全量候选评估。R01采用用户2026-10-18确认的中文A方案：保留全绿，明确中文字体，保留自然字形比例与行宽；布局和缩放接口以该参考页为准。原28项已选L模板不因本轮新增项取舍被清空。2026-10-18 用户另将白金22号[电影画框](references/material-display.md)加入可选素材／动画展映：media、broll、screen和animation均可显式选display.style=cinema，纳入全量候选，不占用原L22。

开场前10秒以快速抓住注意力为优先观看目的，允许比正文更密集地设计、编排动效：结合本期口播的疑问、反差、结果或大论点，较快交替重点字、物件动作、真实画面与视觉揭示。密集安排以信息推进和清晰焦点为依据，保留关键词的可读停留，不机械堆叠无关效果。先把0–10秒的变化与抓人目的写进edit-plan编排，10秒后按正文阅读需要调整节奏。

模板的生成源是 assets 下的 focus.js、flow.js、extra.js、material.js 与对应CSS。每期替换实际台词、数字、单位、媒体和位置；现有默认文案、来源、UI与人物图片是演示内容。目录中的“必要输入”是选型条件；正式实例通过 [生产槽位](references/content-slots.json) 的文字／图片数组和源码已消费的布局输入绑定本期内容。扩展接口时同步模板、调用方和实际预览，不填 renderer 不消费的字段。

真实证据保留原始素材；L18重新组织文档阅读，L31沿原图像素标记词组，二者分开使用。原生screenEffects只保留圈点引出玻璃解释卡，一般用于对着图片、录屏等素材讲解，按真实源像素圈定对象并直接复用L02材质，不另加深色卡皮肤。R02/R04/R05中的图或视频保留原始素材、颜色与可信时窗；实际构图与锚点需按素材核对，不声称自动跟踪。人物位置遵循原拍摄构图：原片居中就保持居中，不为模仿参考强行平移、裁切或放大人物。媒体窗可适度放大，按原片留白调整位置与尺寸；空间不足时改用独立素材画面。左右物件只用Pixel2all白色陶瓷原素材，沿透明轮廓加一点淡荧光绿边光，主体仍保持白色，不用自编有色物件代替；物件和真实Logo不能代替证据。

完整机制、持续流程、空间叙事或风格化情境按 [动画路由](references/animation-routing.md) 选择 xiangsu-mg 或 Lemo-Opuscar。选像素 MG 时默认由其继承本期完整 frame.md 及冻结资源；本Skill保留「一句指令AI剪辑-GlassLime」原始frame全文和对应黑底点阵、字体、颜色与玻璃材质实现，prepare逐字节冻结到新项目。逐字保留已指定的上游frame；主题和分镜另写，不概括重写视觉规范。用户明确选择独立的内置风格时沿用该选择。交接完整 fixed 时间窗、源工程和冻结片段，主合成保留已完成MG的内部画面；本期显式选中display.style=cinema时可用22号电影舞台完整展映，其余MG按原全画面接入。真实录屏、Scene Kit界面由对应制作方先完成，再作为实际动态画面接入。

HyperFrames 是主合成与输出框架，加载 hyperframes 并读取其 references/format.md 与 references/runtimes.md；镜头按本风格的空间构图与 MG 交接安排。字幕保留这里已保存的 白金版 OPPO Sans 字体、灰白字与柔和半透明底；浅色素材主画面上适当加深同款底以保持可读。实际字幕时间来自可信校订稿／对齐结果，样本字幕不代表逐字对齐。

## 材质、动作与声音

真人主画面与完整 MG／素材／录屏之间默认双向使用已批准的 [A-roll／B-roll 转场](references/roll-transitions.md)：01玻璃换片、02青柠漏光均为默认候选，按画面自行任选，无须再询问，不固定到某类素材。同一段进入与返回同款。新prepare自动冻结并接入，具体选择写rollTransitions与effective-plan；这组切换独立于章节导航和A–D局部特效进出场，真人上的叠字、物件或媒体小窗不触发。历史锁不自动改变。

真人背景可选用与白金版同类的“柔和边缘暗角”：保留中心亮度、宽幅渐变压暗四周，文字、字幕及玻璃前景保持清晰。每期沿用已确认的启用决定；新项目未指定时保持原画面。参考图判断、资源及已接入的预览参数见 [柔和边缘暗角](references/host-edge-shadow.md)。这属于背景修饰，不增加 L 编号。

玻璃的透明层、倒角厚度、轮廓法线折射、局部彩边和气泡连续轮廓集中在 glass.js、common.css 与 focus.css。轻量／厚度对照都保留；玻璃直接采样浏览器背后的画面，已验证背景替换；动态视频导出仍需实片验证。细节和接口见 [模板与动作](references/authoring.md)。

四组入退场及两套声组的唯一参数源为 [motion.json](references/motion.json)。保留按原设计，也可以显式选A–D；不随机给全片套用同一动作。B快门夹缝与D青柠细线为高频候选，A右上磁吸与C玻璃翻页按场景少量使用；E轻回弹与F分层错峰已撤下。L30自身就是画面交接，保留其原动作。全量候选评估不等于均匀使用；编排时核对各模板、路线与A–D的使用次数和累计时长，在语义同样合适时优先B/D，并兼顾模板种类；素材条件不满足时记录原因。当前项目应核对随项目工具包的候选清单与本Skill是否一致，旧冻结项目不会自动获得新增R配方。L14清单文字直接叠在原片上，保留文字轻阴影，不附加深色面板或模糊黑底。外层入退场不冻结纠错、定义展开、关键词高亮等内部语义推进。Domain Warp Dissolve只作为选定B/D实例末尾的局部退出材质：保留原入场和阅读，最后0.52秒溶解真实前景至透明，配轻微青柠边缘；真人、字幕、原声与章节角标连续保留。目录自带的SCENE A/B、说明页和四秒演示不得插入正片。

音效素材、原始来源告知、裁切元数据随 assets/sfx 保存。动作与声音来自同一六秒时间轴；改变实例时间窗时同时重算动作和声音节点。主合成中的声音以 HyperFrames 原生 audio 声明，实际口播原声独立保留。网页试听先点击播放启用声音，暂停、拖动和切换时停止声源。

## 正片计划与编译

prepare创建带输入缺口的草案；全文按连续观看任务覆盖0至片尾，在同一edit-plan中写观看目的、主画面制作方、执行引用、素材分工和进入／退出。先运行`effect_planning.py --catalog`读取当前完整候选（L模板、保留生产层、R配方、制作路线、背景修饰、导航进度条、电影画框、A/B转场与退出材质），逐段比较语义适配且输入完备的选项；不要只从旧项目或熟悉模板里挑。candidateReview记录未采用理由及对应段落；objectReview记录实际物件绑定或具体例外。B/D高频只约束入退场动作，不给某种模板或新旧配方额外权重。编排表同时展示零使用候选、次数、窗口时长和可替代段；同类观看任务重复用一种模板时，复核这些替代项，不为凑齐种类硬塞效果。先生成draft编排表并处理必要决定，再制作素材和完成正式计划。

```powershell
python scripts/prepare.py --source <粗剪.mp4> --project <新工程> --end <秒数> --timing <可信时间JSON>
python scripts/orchestration.py --project <工程> --plan <edit-plan.json> --draft
python scripts/compile.py --project <工程> --plan <edit-plan.json> --validate-only
python scripts/compile.py --project <工程> --plan <edit-plan.json>
```

选中局部Domain Warp退出时，按[计划接口的纹理准备步骤](references/plan-format.md#局部退出材质)先生成本期真实前景纹理，再正式编译；不依赖本期实验工程中的临时脚本。

ORCHESTRATION.md是计划生成的审阅视图；修改edit-plan后重生成。正式校验拒绝未覆盖、缺输入、孤立引用、未评估候选、未解决物件、未填写实际文字／图片槽位、资源漂移和媒体时窗不足。章节表达使用像素·绿宝石自己的L27／L28，L30保留其自身交接；主画面↔完整B-roll沿用已批准的01／02默认转场；大于180秒的新视频默认通过`navigation.progress`联动A进度条、导航角标与换章转场，不重复叠同章L28；L27/L28仍按独立表达需要选用；不恢复已删除编号或旧版视觉默认。

运行环境、源码自包含与维护冻结清单见 [运行依赖](references/runtime-dependencies.md)。

## 预览与验证

快速生成一个独立样本：

```powershell
node scripts/build_preview.mjs --effect L07 --motion A --sound camera --out <新样本目录>
node scripts/build_preview.mjs --effect L02 --content <内容JSON> --motion D --out <新样本目录>
node scripts/build_preview.mjs --effect L07 --host-finish soft-edge-v1 --out <暗角样本目录>
```

只使用本Skill内资源，不导入作者机器里的旧工程或旧Skill。生成目录含相对资源、可编辑 index.html 与固定版框架命令；复制整个目录即可继续制作。这个脚本创建视觉样本，不编译完整口播计划。

先做包含核心难点的20–30秒真实口播，再扩展整片；检查各镜、切点、字幕和原声，运行 HyperFrames check，核对正常播放及正反向 seek。更换选题、人物构图与媒体后再说明对应组合可复用。当前已验证的样本、动作和声音范围见 [保存记录](references/validation.json)。
