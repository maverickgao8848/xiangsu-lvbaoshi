# 正片计划接口


名称兼容：Skill 调用名为 `xiangsu-lvbaoshi`；下述历史 profile 与 `generated:mav-mg:` 来源前缀保持原值。机制段 producer 可写 `xiangsu-mg`，旧 `mav-mg` 继续有效。
profile 是 `glass-lime-editorial-kit/v1`。可执行字段的权威是 scripts/compile.py 的 validate、scripts/orchestration.py 和 scripts/effect_planning.py；槽位清单由实际 render HTML 生成，不把用途文字当成 JSON 字段。

| 顶层字段 | 合同 |
|---|---|
| id / duration / profile | 小写连字符唯一ID；时长与 input-lock 完全一致；像素·绿宝石 profile |
| orchestration | version=`glass-lime-editorial-orchestration/v1`；segments、candidateReview、objectReview；多数物件例外时有 objectMajorityException |
| effects | 真人辅助层；host 背景模板，禁止并发重叠前景；通过同模板图片槽配物件 |
| beats | 顺序、无重叠的完整主画面窗口；非host段由所属beats连续覆盖 |
| captions | 可选 `{match,text}` 数组；match顺序覆盖全部可信词，不拆词伪造时间。省略／空数组按MAV整词方法分句 |
| hostFinish | `{enabled:boolean,preset:"soft-edge-v1"}`；只对host窗口收暗 |
| navigation | 可选 `{progress:true|false}`；大于180秒的新项目默认开启章节角标、A银灰磨砂分章底栏和换章转场，180秒及以下默认关闭；开启时只读项目根 `chapters.json`，见 [导航进度条](navigation-progress.md) |
| rollTransitions | 新prepare默认 `{"default":"auto","beats":{}}`；主画面↔完整MG／素材双向转场，两款按画面任选；可按beat ID指定glass-slide或lime-leak。`false`关闭，详见 [A/B转场](roll-transitions.md) |
| mg | 有 provider=xiangsu-mg（含缺省）的 animation 时必填 `{styleId}`；当前可选风格ID或与frame-provenance.json一致的上游自定义ID；新项目默认glass-lime-extracted。历史productionMode字段不再参与校验或策略选择 |
| soundCues | 可选 `{id,file,at,duration,volume}`；项目相对音频及来源SHA，时窗不越界 |
| screenEffects / companions / editorialScenes / beats.kind=editorial | 新增原生生产层；实际字段、媒体与段落layerIds合同见 [production-layers.md](production-layers.md) |

## 编排与评估

segments 为 `{id,start,end,scenario,producer,narration,purpose,beatIds,effectIds,inputs,entry,exit}`，从0连续覆盖全文；inputs 是 `{need,status:"ready"|"missing"}`。正式编译拒绝 missing、孤立引用、重复所属、遗漏段和主画面空窗。host / editorial 不用主画面beat；mechanism / xiangsu-mg 用 animation；dialogue / scene-kit 用 interface；operation / editorial 用 screen；data、evidence用 evidence/material/explanation；illustration 用 media/material/broll。

candidateReview 每行 `{candidateIds,decision,segmentIds,reason}`。decision 为 considered/inapplicable/unavailable，考虑过的候选须给对应段。已实际使用的候选自动计入覆盖；剩余全部记录，不能把未用当成不适用。候选ID由 effect_planning.py --catalog 输出。

objectReview 沿用 MAV 的 `{entryIds,decision,searchTerms,bindings,reason}`，entryIds 形如 `effects:question-one` 或 `beats:mechanism-one`；decision 为 used/exception/pending，binding 为 `{entryId,path}`。used 必须绑定实际执行图片槽或MG源工程里真实使用的对象，并核对 Pixel2All 来源／使用依据／SHA；pending 只能留在 draft。多数适用窗口采用例外时写具体 objectMajorityException。来源接口复用 object_assets.py，不携带旧整库。

## 像素·绿宝石 实例

模板实例有 `id,start,end,templateId,content,motion,sound`；主画面beat再加 kind=evidence/material/explanation。`motion` 省略为 none，或 A–D；B/D为高频候选，E/F已撤下，L30保留自身动作。`sound` 为 auto/mute/electronic/camera，auto随动作配套。以保存的六秒设计为母时间轴，按实例时长一起重算动作和SFX节点，不单独延长声音或循环画面。

content 至少有 `text` 和 `images` 数组，分别按 DOM 中非SVG、非装饰字符的文字节点和 img 顺序填满。[content-slots.json](content-slots.json) 展示默认布局的槽位顺序；其中原文只是样例，正片每项明确填写本期文字。可附 title/definition/note/old/question 等源码已消费的布局输入，再用实际 render 检查槽位数。动态结构变化时重新运行 content_slots.py 或读取 render结果，不假定旧槽位数。images 必须全部指向项目内冻结且有来源的媒体；不接受默认 host.jpg 作为本期素材。

host模板可给content.object绑定实际透明物件／Logo，在同一实例的右侧伴随显示；images同时填入这个新增图片槽。L24本身的object替换示意SVG，正式生产必须指定。素材同属这一语义窗，objectReview绑定该实例的实际图片路径；无需叠另一块整屏前景。偏右人物或右侧模板须先审看占位，必要时保留干净真人或记录素材例外。

例如L07的实例：

```json
{"id":"question-one","start":1,"end":7,"templateId":"L07","motion":"C","sound":"auto","content":{"title":"它为什么会这样？","text":["它为什么会这样？"],"images":[]}}
```

L31额外需要 source 和 regions。当前布局支持1920×640 PNG；每个 region 为源像素 `{x,y,width,height,group}`，group为非负整数；images的原图及每层高亮副本都必须绑定同一source。其它比例须显式准备阅读裁切并重新标坐标，不声称自动OCR。证据、L17/L18/L19/L31写真实 sourceLabel/sourceUrl；静帧展示原视频时写 stillReason。原文及来源说明也通过生产文字槽明确填写。

## 完整外部画面

media/broll/screen可选display.style=cinema电影舞台，见[电影画框](material-display.md)；原生interface不使用该字段。

media/broll/screen/interface 的beat使用 `{id,kind,start,end,video,mediaStart,sourceLabel,sourceUrl}`，video为实际动态画面，保留原色；静音播放，主口播原声独立持续。screen/media/broll也可明确使用image静态源图，与video/mediaStart互斥。界面写 sceneId=S01/S03/S12、editableSource=interfaces/…，保留可编辑 index.html。真实操作走screen，不把模拟Scene Kit当证据。原生screenEffects可直接标注原画面；复杂裁切/动态跟踪仍由制作方按实际源帧完成，不接受未实现的摄像机字段。

Scene Kit另有原生生产接口：interface beat写 `{id,kind,start,end,sceneId,config,sourceLabel}`，config必须包含实际content。冻结的Scene Kit生成器校验S01/S03/S12、读取真实内容并生成自己的序列；compiler以像素·绿宝石点阵舞台装配，保留界面内部原色，生成可编辑interfaces/<id>/工程。不能在同一实例混用config与video；未填正文不启用样例对话。输入字段由已保存的assets/component-kit/prepare.mjs负责，不另造Scene Kit schema。

像素 MG 的 animation 沿用 MAV 的video、mediaStart、editableSource合同，源工程在 animations/…，至少保留 index.html、STORYBOARD.md、frame.md 和BRIEF.md。16:9视频覆盖固定时窗；来源记录为 `generated:mav-mg:<beat-id>`。保持原MG内部画面；可显式选display.style=cinema完整展映，接口见[22号电影画框](material-display.md)。省略display仍为原全画面，不另加人物窗、模板叠字、染色或主工程相机。动画编译交接不会替代 像素 MG 的 model/素材/关键帧/ART-REVIEW 合同。

工程资源和媒体采用相对路径；正式校验拒绝未消费的顶层字段。L27/L28分别承担像素·绿宝石章节开启与角标；2026-10-18 用户选定 A 银灰磨砂分章底栏，`navigation.progress` 对大于180秒的新输入默认开启，角标／分章进度／换章转场一并装配；可显式false覆盖；章节只读项目根 `chapters.json`，见 [导航进度条](navigation-progress.md)。旧MAV头像和黑底备用renderer不自动加入本模板；2026-10-18已批准的绿宝石01／02主画面↔B-roll转场按roll-transitions.md接入新项目。圈点玻璃卡、Pixel2all白色物件及R01–R05使用production-layers.md实际接口。

## 导航进度条（A）

计划写 `navigation:{"progress":true}`，并在项目根提供 `chapters.json`；编译器生成全片 `navigation-progress` 层，不占段落、不占物件槽。章节首项从0开始、严格递增、每章至少1秒、最多6章；`number`唯一1–3位数字，`title` 1–14字单行。`{"progress":false}`显式关闭这组导航。新prepare冻结navigationDefaultsVersion；大于180秒省略字段仍会开启，180秒及以下省略时关闭；没有该版本标记的历史锁不自动改变。`effect_planning.py --catalog`中的`navigation:progress`仍须在 candidateReview 记录未采用理由。同一导航层自带角标和换章滑入／青柠扫线，不重复叠同章L28；视觉、资源冻结和验证见 [导航进度条](navigation-progress.md)。

```json
{"navigation":{"progress":true}}
```

## 局部退出材质

模板实例可指定`exitMotion:"domain-warp"`（当前搭配B/D入场）。只作用于实际特效前景，最后0.52秒局部溶解至透明，不新增时长、不插入目录演示、不处理真人背景。参数唯一来源为motion.json的exitTreatments；透明前景纹理与局部边界由本期实际模板生成，记录内容/素材指纹。改文案或素材后重新生成纹理。

```powershell
python scripts/prepare_exit_textures.py --project <工程> --plan <edit-plan.json>
node scripts/capture_exit_textures.mjs --project <工程>
```

截图脚本使用已有Playwright/Chromium，并自行启动仅本机可访问的临时资源服务、完成后关闭。模块不在默认搜索路径时，通过工作区依赖工具找到已捆绑的Node模块根目录与Chromium，再传`--playwright-module <模块根目录> --browser <Chromium路径>`；不把作者机器路径写进Skill。输出为`assets/glass-lime-exits/<实例id>.png`、`manifest.json`与对应来源SHA。保持透明底、原字色、字型和本期布局；主内容与伴随物件按各自边界定位。L02/L08/L14已有实际审看，其它模板通过通用前景边界接入后，先核对一处实际退出再扩展。

`exit:domain-warp`同时进入完整候选评估；没有选用时可按本期阅读、时窗或素材条件记录原因，不固定到某三个实例，也不要求每片都用。

## 动画制作方

动画 beat 可写 provider（缺省 xiangsu-mg）和 Lemo 专用 styleId；选择 lemo-opuscar 时 producer 同名，使用 generated:lemo-opuscar: 来源及 animation-source.json 完整源码交接，不执行 MG frame 校验或全片 mg.styleId。像素 MG 的原 frame、历史字段和来源规则保留。字段示例、冻结命令、路由与声音归属见 [动画选型与交接](animation-routing.md)。
