# 动画选型与制作方交接

## 先选观看任务，再选制作方

像素 MG 与 Lemo-Opuscar 都能做解释动画；区别在组织画面的出发点，并非“一个只能信息图、一个只能艺术短片”。

| 选择 | 核心组织方式 | 优先场景 | 素材与风格 |
|---|---|---|---|
| Editorial 局部效果 | 保留真人，用短文字、物件、媒体窗补充一句话 | 重点、术语、提问、简短对照、来源与轻伴随动作 | 使用本包装模板和已接入槽位；无需完整动画子工程 |
| xiangsu-mg | 围绕教学目标安排对象、关系、状态变化和可读落点 | Agent 分工、因果、分类、抽象比较、多步流程，需要看清“谁与谁、怎么变” | 默认完整继承本期白金／绿宝石 frame；具体物件执行 Pixel2All 来源合同 |
| lemo-opuscar | 围绕所选 STYLE 的媒介、对象动作、场景调度和镜头语法组织段落 | 情境／故事、视觉隐喻、角色表演、产品空间与拆解、具有媒介意味的过程；blueprint／swiss-motion 等也可讲机制 | 逐段选择真实风格；保留该风格的引擎、材料、动作和声音边界，不强加包装的黑纹理／玻璃或 Pixel2All 物件 |
| 真实素材／录屏 | 展示可核对的原始画面和操作时序 | 数字、引文、界面证据、实际操作结果 | 动画示意不能代替事实证据；情境模拟沿用显式标识 |

例如：“三个 Agent 怎样分工”通常选像素 MG；“信息像包裹一样经过分拣站”可选 Lemo 对象表演；“产品怎样分层装配”可比较像素 MG 的关系解释与 Lemo teardown／blueprint 的空间表现。比较本段观众要理解的变化、媒介适配、阅读窗、素材成本及前后连续性后再选，不按名称或新鲜程度优先。不要把像素 MG 的教学结构机械套成所有 Lemo 风格，也不要仅靠镜头移动掩盖对象没有行动。

编排阶段将两条路线纳入全量候选，未采用时在 candidateReview 写本段取舍或缺口。用户已委托制作且没有新的关键艺术分歧时按上述依据选择；指定了风格就沿用，未解决的关键风格取舍列入 inputs，不能把“接入 Lemo”当作本期任意风格都已获认可。Lemo 选中后缺安装、风格或必要输入时报告该缺口，不静默换成 MG／备用 renderer。

## 可执行路由

两条路线都用 `beats.kind=animation`，完整视频静音展映；源工程在本期 `animations/<beat-id>/`。每个 beat 的 `provider` 默认 `xiangsu-mg`，也可显式 `lemo-opuscar`；历史 `mav-mg` 作为像素 MG 的别名继续有效。orchestration 的 producer 必须与 beat.provider 一致。

- `mechanism / xiangsu-mg`：关系与流程；兼容原 `mechanism / mav-mg`。
- `mechanism / lemo-opuscar`：适合该风格的机制／空间过程。
- `illustration / lemo-opuscar`：情境、表演、隐喻、产品叙事。

新 prepare 冻结 animationRoutingVersion；新制作全量评估 Lemo，旧锁不因此新增必填候选。旧工程显式采用 Lemo 或在 candidateReview 显式评估它时才纳入新增候选。编排、选型、交接、compiler 都消费同一制作方身份。艺术检查仍依制作方和本包装的实际预览，编译通过只证明技术接口。

每次规划按仓库 `.agents/skills/<provider>/SKILL.md`、`.codex/skills/<provider>/SKILL.md`，再按个人 `.agents`、CODEX_HOME、个人 `.codex` 查找；仓库优先。选 Lemo 只发现 Lemo，不要求像素 MG 同时安装。制作前完整读取选中 Skill 及它引用的当前库／STYLE 合同；桥接代码不复制或重写动画引擎。继续既有源工程时先检查所采用的库和依赖，不能先更新库再核对。

## Lemo 制作与冻结

给 Lemo 完整连续段原口播、可信时间、fixed start/end、本段观看目的和采用的风格。将已有原声作为唯一时间依据，局部时间为整片时刻减 beat.start；不重新配音、改词、变速或循环来填窗。按其 SKILL、Production continuity 与 Motion realization 制作 treatment、实际引擎风格帧及核心难点的动作验证。所需素材和源码以所选风格为准；不把 MG 的 FRAME/STORYBOARD 目录结构强加给 Lemo。

保留 index.html、TREATMENT.md、实际构建入口、所选 STYLE 及完整源码／素材。构建依赖采用锁文件或可重取的固定库版本；不能仅留下作者机器某个目录或一条提交号就宣称可复现。制作源工程放在当前项目内，冻结交接可用各 Skill 自带的同名脚本：

```powershell
python scripts/stage_animation.py --project <父工程> --beat <新beat-id> --source <Lemo源工程> --video <完整渲染片段.mp4> --style blueprint --style-file <所选STYLE.md> --build-entry build.sh
```

source 是完整已制作的源目录，冻结目标 `animations/<id>` 须不存在且不位于 source 内；可用 build.ps1／build.mjs 等实际入口。脚本保存相对源码、风格快照、文件 SHA 和视频来源，输出 beat 字段片段（白金同时给出空 title，绿宝石不增加标题字段）；作者补真实 start/end，不改写现有计划。它不是 Lemo 制作器，也不会自动运行任意构建代码。

```json
{
  "id":"metaphor-sorter", "kind":"animation", "provider":"lemo-opuscar", "styleId":"blueprint",
  "start":20, "end":32, "video":"assets/animations/metaphor-sorter.mp4", "mediaStart":0,
  "editableSource":"animations/metaphor-sorter", "sourceLabel":"Lemo-Opuscar · blueprint"
}
```

对应 segment 写 `scenario: illustration`（或 mechanism）、`producer: lemo-opuscar`、`beatIds: [metaphor-sorter]`。Lemo 来源前缀为 `generated:lemo-opuscar:<id>`；像素 MG 沿用 `generated:mav-mg:<id>`。Lemo 源清单 animation-source.json 核对 provider/styleId、构建入口、风格和文件 SHA；像素 MG 仍执行下面的 frame 继承校验。Lemo 不填全片 mg.styleId，不需要伪造 frame-provenance 或 MG 文档。

主工程保留完整源构图及父工程原声／字幕；Lemo 原有旁白不重复混入，确需其动作声时在本期明确声音归属后按已有 soundCues／声音接口接入，不因动画视频静音而声称保留了其中声音。视频必须为完整16:9且覆盖实际播放窗及叠接尾部；外框与A/B转场沿用本包装现有默认，不额外加人物窗、重染画面或驱动内部相机。检查原生片段和最终合成的动作、读字、边界、声音与正反向 seek。

编译后 ANIMATION-ROUTING.md 与 build-report 标明各 beat 的制作方、源工程和冻结片段；主工程消费视频，可编辑图形在子工程中。

## 像素 MG 的既有制作合同

下面只适用于选择了像素 MG 的段落；“找到就采用”和缺失时的备用条件不再覆盖显式选择的 Lemo 段。

# 像素 MG 制作与交接

整片规划先决定哪些连续段需要完整机制、关系、比较、多步流程或空间叙事。真人侧边物件／Logo与简单伴随动作仍用 像素·绿宝石 模板；不为每个名词启动完整MG。将完整解释段的原声、可信台词及固定 start/end 交给 xiangsu-mg，局部时间为整片时间减beat.start，不重配旁白、不改写口播或伪造逐字时间。

每次规划重新按 scripts/animation_routing.py 查找：实际仓库 `.agents/skills/xiangsu-mg`、`.codex/skills/xiangsu-mg`，然后个人 `.agents/skills/xiangsu-mg`、配置的 CODEX_HOME/skills/xiangsu-mg、个人 `.codex/skills/xiangsu-mg`。仓库优先；从选中目录完整读取 SKILL.md 与输入、风格、素材、动作和质量合同，不混用安装版本。

## 完整上游风格继承

默认继承本期frame，不再为了接入而先选一个近似的内置风格。prepare将assets/frame/FRAME.md逐字节冻结为项目frame.md；该文件完整保存「一句指令AI剪辑-GlassLime」的原始规范，来源和哈希保存在assets/frame/source.json。背景、24px细点阵、字体、颜色及玻璃材质的可执行资源由frame-resources.json声明。原项目的口播、旧动作选择和音频混音参数仅保留作上下文；本期时窗/动作/声音仍依当前合同和计划。

新MG子工程先执行选中像素 MG安装的 `node scripts/inherit-frame.mjs --project <film/animations/beat> --upstream <本期frame.md>`；没有显式路径时自动查找最近上游frame。完整保留原始字节、字体/许可、CSS/JS/纹理和来源哈希，不用“深色、青柠、玻璃”等概述替代。父工程不在film目录时传明路径。已有不同frame的工程保留，用户明确改风格后才用--replace。

默认styleId为glass-lime-extracted，采用像素 MG 的单一制作流程；不把它伪称gable-reed等未改动的官方风格。compiler对带frame-provenance.json的子工程验证完整继承及资源哈希，并允许该自定义身份。用户明确选择独立内置风格时才按安装版style-contract提供当前候选风格；其画面不被主工程强加点阵或覆盖字色。保留像素 MG 的素材、动作和质量合同，不再询问制作模式。

动画源工程放在本期 animations/<beat-id>/，保留 BRIEF、SCRIPT、STORYBOARD、frame、实际来源与检查证据；按 像素 MG 的预览／导出授权得到完整16:9冻结片段。plan 写 beats.kind=animation、video、mediaStart、editableSource、sourceLabel；mg记录styleId；历史productionMode字段仅作记录，不再消费。asset-credits登记实际片段SHA与sourcePage=`generated:mav-mg:<beat-id>`。compiler校验文件、时窗、源工程及已安装或已验证继承的风格，生成 ANIMATION-ROUTING.md。主工程保留原口播声轨，动画视频静音。

主工程消费冻结视频，原生可编辑图形在MG子工程；不能将其描述为主时间轴上的原生图形。技术编译成功不等于本期视觉验收，仍检查真实衔接、读字、字体、空间动作、字幕、声音和正反向 seek，按本期决定再导出。

本期animation beat可显式选 `display:{"style":"cinema"}`，由父工程用白金22号电影舞台等比contain展映完整冻结片段；不改MG子工程，不在两处重复套框。省略display保持全画面。选型、参数与检查见[电影画框](material-display.md)。
