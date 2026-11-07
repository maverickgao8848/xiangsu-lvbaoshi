# A · 银灰磨砂分章进度条

2026-10-18 用户在三案中选定 A，替换此前样段里“不需要进度条”的决定。它是独立导航层，不并入 L/R 编号。用户随后确认：新视频严格大于180秒时默认启用本层的章节角标、分章进度条和换章滑入／青柠扫线转场；180秒及以下默认关闭。

![A · 银灰磨砂分章底栏](images/progress-bar-a.png)

## 视觉

- 40px 底栏贴画面底；分段宽度按真实章节时长分配。
- 烟灰雾面玻璃：`backdrop-filter` 30px、低饱和、暗色渐变、1px 磨砂噪点；银色上沿与拉丝银填充。
- 2px 银边游标跟随当前章节；章节号用 Montserrat 12px，标题用 OPPO 18px。
- 字幕 `bottom:80px`，进度条高 40px，两者留 40px 间隔；不覆盖人物、口鼻与麦克风。
- `z-index:46`，位于 effects 30 / production 32 之上、字幕 50 之下。
- **左上角章节角标（2026-10-18 加入）**：192×44 的深色渐变玻璃标签，左侧 2px 青柠边，章节号 Montserrat 12px 青柠、标题 OPPO 18px 白字。位置 `left:48px / top:44px`，在 R01 首行（y=142）上方、电影画框左外侧（画框从 x=240 起）。
- 每章进入时角标从左侧 14px 滑入（0.5 秒），下方青柠细线从左扫到右（0.55 秒）再收掉（0.35 秒），作为章节转场；其余时间常驻显示当前章。
- 全画面录屏窗口（没有 cinema 画框的 `screen` beat）会临时淡出角标，避免压住源画面自己的标题/工具条；cinema 与 MG 窗口保留角标。

## 计划接口

```json
"navigation": {"progress": true}
```

只接受 progress 这一个布尔字段；false显式关闭这组导航。章节数据只从项目根 `chapters.json` 读取，避免第二份事实源。

`chapters.json` 可以是数组，也可以是 `{"chapters":[...]}`：

```json
[
  {"number":"01","title":"开场","start":0},
  {"number":"02","title":"关系","start":22},
  {"number":"03","title":"机制","start":58},
  {"number":"04","title":"结论","start":94}
]
```

约束：

- 1–6 章；首章 `start=0`；`start` 严格递增且在片内；每章至少 1 秒。
- `number` 为唯一 1–3 位数字字符串；`title` 为 1–14 字单行文本。
- 新prepare在输入锁冻结navigationDefaultsVersion；大于180秒省略navigation也会开启，180秒及以下省略时关闭。`{"progress":false}`可覆盖关闭。没有该标记的历史锁保持原计划。
- 本层角标、进度与换章转场消费同一章节表；L27可另作章节开启，同章不重复叠L28角标。

## 编译

- `scripts/navigation.py` 校验章节并生成 `compositions/navigation-progress.html`。
- 主合成增加全片 layer：`data-track-index=46`、`z-index=46`、`data-start=0`。
- 逐章线性填充；游标随章节移动；章节标题在进入时点亮，离开后保留略暗的已读状态。无入场动画、无音效、无图片槽。
- 角标与底栏同一导航层；`hide` 窗口由 compiler 从全画面 `screen` beat 计算，随 `data` 传入 runtime。
- 新项目由 prepare 冻结 `assets/navigation-progress`；旧项目需要重新 prepare，不能混用渲染器。
- `build-report.json` 记录 `navigation.version`、章节表与资源 SHA。

## 选型

- `effect_planning.py --catalog` 现包含 `navigation:progress`；未启用时必须在 candidateReview 写 considered/inapplicable/unavailable 与具体原因。
- 它是导航候选，不占段落 `layerIds`，不参与物件绑定。
- 新视频大于180秒默认装配；180秒及以下可显式 `navigation.progress=true` 启用。默认启用同样计入全量选型，不能记录成未采用。

## 验证

- `python scripts/test_navigation_progress.py`：19 项接口、180秒阈值、覆盖关闭、新旧输入锁、草案和选型测试。
- 2026-11-05：进度头改以章节局部宽度驱动水平位移，已完成章节编号略提亮；在 1920px、1300px 两种宽度和多个章节位置比较正反向定位，进度位置与预期一致。开启导航的模拟整片通过 HyperFrames 0.8.231 检查，导航编号仍有小字号提示；旧工程冻结资源不会自动更新。
- 上图是 1920×1080 静态设计帧；本轮完成模板与 compiler 技术验证，真人正片与正反向 seek 仍按 [正片工作流](workflow.md) 验收。
