# 主画面 ↔ B-roll 默认转场

2026-10-18 用户审看后同时选用 01「玻璃换片」和 02「青柠漏光」，授权制作时按画面自行决定，无须逐段询问。两款均用于真人主画面与完整 MG／素材（含录屏、完整界面）的进入和返回；不按 MG／素材固定分配，也不要求轮流或平均使用。同一 B-roll beat 的进入、返回使用同款。

这是完整主画面间的切换，与章节导航、L27/L28、L30自身表达和 A–D 局部特效进出场分别工作；真人上的叠字、物件或媒体小窗不触发它。

| 配方 | 时长 | 已批准的外观 |
|---|---:|---|
| glass-slide / 01 玻璃换片 | 0.64s | 画面轻收为91%，银灰薄玻璃边框，横向换片归位，淡青柠扫光 |
| lime-leak / 02 青柠漏光 | 0.56s | 保持全屏，青柠漏光与短促曝光；减少白金09的胶片碎屑和划痕 |

参数权威为 [preset.json](../assets/roll-transitions/preset.json)，实际动作与素材在同目录。资源随本 Skill 独立提供，不需要白金安装。来源与审看依据见 [source.json](../assets/roll-transitions/source.json)。

## 调用与选择

新 prepare 冻结 `rollTransitionsVersion`、资源 SHA，并在草案加入：

```json
"rollTransitions": {"default":"auto", "beats":{}}
```

编排可自由选用两款，将具体选择写进 `beats` 映射；未挑选的段由编译器按 beat ID 稳定分配，写入 `effective-plan.json` 和 `build-report.rollTransitions`，不会在播放、seek或再次编译时重新随机。`default` 也可写任一款 ID，作为全片基础选择；`beats` 按实际 beat ID 覆盖。全片关闭用 `false`，个别短段可显式填 `false`，并在编排说明具体例外。

```json
"rollTransitions": {
  "default":"auto",
  "beats":{"mechanism-one":"glass-slide","material-one":"lime-leak"}
}
```

只在 `beats` 与真人空隙之间生成 A→B／B→A；连续 B/B 切点、整片起止不添加一次真人交接。没有章节也照常工作；有章节时不依赖章界，也不借章节转场代替。叠字、物件、原生R01–R03媒体小窗仍沿用局部动作，不因出现媒体就触发全屏转场。

每个动作以现有语义切点为中心，前后各半窗，不改媒体的 start、duration、mediaStart，不要求额外素材尾帧。玻璃换片在切点前退出旧画面，切点后进入新画面；包裹的是无时间字段的视觉层，播放与可见时窗仍由 HyperFrames 管理。来源标注随所属素材一起移动，字幕、章节角标、进度条和口播原声独立连续。cinema素材的舞台淡入／缩放在已有 A/B 入场处交给转场，稳定画框、光线、说明继续保留。无新增默认音效。

超出片长、转场窗互相重叠、B-roll未留下0.5秒稳定阅读窗或冻结资源漂移时拒绝编译；调整语义窗口或明确关闭该短段，不能静默加尾帧。没有 `rollTransitionsVersion` 的历史锁不自动新增效果与必填候选；历史工程需要这组新增资源时重新 prepare。

`roll:glass-slide` 与 `roll:lime-leak` 均纳入新项目全量选型；编排表按实际切点、方向、时窗和使用次数呈现，不把局部 A–D 的次数算成 B-roll 转场。两款外观已经批准；真人正片仍检查切点、动态视频、完整MG、字幕／原声及正反向seek，合成接口测试不等于所有题材复用已验收。

技术验证范围与结果记录在 [validation.json](validation.json) 的 rollTransitions。边界／选择／历史锁测试为 `python scripts/test_roll_transitions.py`；完整 prepare→compile 回归为 `python scripts/test_production.py`。测试使用合成素材，不替代真人正片审看。
