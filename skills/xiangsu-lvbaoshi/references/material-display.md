# 22号电影画框（可选）

2026-10-18 用户要求把白金版22号电影画框加入绿宝石，素材和动画都可使用。选型ID为 `display:cinema`，属于画框修饰，不占用L22或新增L模板编号。原L22保持原功能。

窄暖白框、灰黑舞台、侧光、框体比例和入场沿用白金已选cinema；默认外框约1737.5×989.41px、打光0.75。资源独立保存在本Skill `assets/material-display/`，来源哈希见其中source.json，制作时不依赖白金安装。来源说明使用绿宝石现有OPPO字体，在底部40px导航上方显示。

## 实际用法

在 `media`、`broll`、`screen` 或 `animation` beat上显式写 `display:{"style":"cinema"}`。图片和视频二选一，媒体路径、来源SHA、时窗和动画源工程继续遵循原接口。图片始终contain完整展示；视频和动画同样等比contain，保留原始颜色，视频静音，真人主声轨持续。省略display沿用原有全画面，不自动给每段加框。

```json
{"id":"material-one","kind":"media","start":10,"end":16,"image":"assets/example.png","sourceLabel":"本期已核对来源","display":{"style":"cinema"}}
```

```json
{"id":"mechanism-one","kind":"animation","start":16,"end":24,"video":"animations/mechanism-one/video.mp4","mediaStart":0,"editableSource":"animations/mechanism-one","sourceLabel":"机制示意 · 像素MG","display":{"style":"cinema"}}
```

可选 `scale` 范围0.8–1.2065972222222223，默认最大值；`light`为0–1，默认0.75；`fit`可省略或写contain。每段至少2秒。编译器拒绝其它画框、裁切、未知字段和资源漂移。该接口不接受原生Scene Kit config、L模板或真人叠字；已有素材模板可继续按原方式展示。

动画由所选 xiangsu-mg 或 Lemo-Opuscar 制作完整画面，父工程仅在本期选中display时装配电影舞台，不改动画子工程、字体、内部背景、动作和原色。没有display时保持原来的完整MG交接。不要在MG源工程和父工程重复套同一画框。

现有圈点引出玻璃卡使用未加框的源像素坐标，暂不与此画框同beat混用；需要圈点时独立使用未加框screen窗口。字幕、来源说明、章节角标和进度条须审看避让；对证据底部文字有遮挡时调整本期字幕编排或采用独立阅读窗。

新prepare冻结画框CSS、预设与来源到项目assets/glass-lime/material-display，compiler实际生成电影舞台子合成并记录build-report.materialDisplay。全量选型与编排表统计display:cinema的次数和时长；素材或机制任务适合展映时主动评估，未选用则记录本期理由。历史冻结项目不自动升级，使用新增资源需新prepare。

## 验证范围

复用已选画框视觉，技术验证使用合成输入检查图片、动态视频与MG的正式编译、时窗、来源、无display兼容和错误拒绝；不据此宣称真人正片艺术验收。每期仍按工作流审看正常播放、正反向seek、字幕和实际媒体可读性。
