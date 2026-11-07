# 青柠玻璃 · Glass Lime

内置风格，ID `glass-lime`。来源是用户指定的 `glass lime.mp4` 与「口播编辑台」中段 MG，以及已经冻结的 Glass Lime 字体、背景与玻璃光学实现。本文件是新项目的有效视觉规范；`provenance/FRAME.source.md` 完整保存历史项目规范，仅供溯源，不作为本期制作指令。历史 `glass-lime-extracted` 工程继续保留原身份与 frame。

## 视觉意图

把知识对象放进可探索的深色工作空间：有厚度的透明玻璃承载内容，白色陶瓷物件指认实体，青柠路径与状态变化说明关系。观众能追踪同一个对象怎样经过步骤、进入结构、形成结果；标题、对象、路径和镜头一起交接注意力。构图随关系发展，保留空场和清晰阅读窗口。

## 颜色与背景

| 角色 | 色值与表现 |
|---|---|
| 空间底色 | `#08090b` |
| 主文字 | `#f5f6f2` |
| 次级文字 | `#a8afb4` |
| 当前重点、路径、选中态 | `#d7ff48` |
| 低亮点阵 | `#29414d`，24px 间隔，点半径约 1.5px |
| 空间亮区 | 偏心、低亮、宽幅椭圆，青柠光在主体后方渐隐 |

保留点阵、低亮空间光与大面积暗场的层次。以 `samples/lime-73.jpg` 为材质和背景对照：点阵在非主体遮挡的暗场中连贯可辨，绿色空间光柔和，亮度不压过文字或主体。路径和选中态使用青柠色，普通标签保持暖白或灰色；同时必读的次级标签仍清晰。背景与对象的相对变化配合本期机制推进。

## 字体与画幅

1920×1080、30fps，中文标题使用本地 Noto Sans SC 800/900，正文与标签400/500；数字与英文强调使用本地 Montserrat800；字幕使用本地 OPPO Sans400。**本风格使用 OPPO Sans，Copyright 2024 Guangdong OPPO Mobile Telecommunications Corp., Ltd.，许可原文随字体保存。** 三套字体均为完整冻结文件，路径从本期工程读取：

- `assets/references/styles/glass-lime/fonts/noto.ttf`
- `assets/references/styles/glass-lime/fonts/montserrat.ttf`
- `assets/references/styles/glass-lime/fonts/oppo.ttf`

标题可从64–96px、关键短命题从88–144px、对象标签从30–44px起排；按真实字数、景别和播放尺寸调整。字幕用 `#d9d9d9` 与 `rgba(48,49,52,.56)` 柔和底，1080p可从底部80px处排布。嵌入父片时由父片统一字幕，本 MG 不重复叠加。以上尺寸是起点，具体阅读区仍写入本期 STORYBOARD。

## 玻璃、实体与路径

玻璃包含低浓度透明面、连续圆角倒面、沿轮廓变化的折射、局部蓝紫与琥珀彩边、白色前沿高光及内侧暗边。复用随包 `runtime/glass.js`：它根据当前轮廓建立法线与边缘贴图，并折射**实际背景**。文字与图示作为清晰前景放在面内。卡片发生倾斜、缩放或遮挡时仍保留可辨厚度。

白气泡以连续轮廓和短尾巴表达提问或判断；深色实体板承载命令、规则和输入；玻璃面承载流转、窗口与空间层级。按阅读任务选择材质，但本风格的代表性机制画面应让玻璃作为清楚可见的主要载体：在最终播放尺寸能辨认透明面、连续厚度与局部蓝紫或琥珀彩边，不能只剩平面描边或深色实板。允许短暂全屏媒体、特写或纯文字画面依任务减少玻璃与点阵，不要求每帧都出现。`runtime/mg-style.css` 提供这些材料起点与本地字体声明。

具体实体沿用 Skill 的 Pixel2All 物件合同：保留白色陶瓷原色、柔和投影及淡青柠边光；物件身份与状态按本拍解释职责发现并比较，风格只约定材质与呈现。单张透明 PNG 支持平面与有限2.5D表现；需要背面或真实结构变化时依素材能力选其他路线。抽象的容器、连接、内部结构与路径用可控 DOM/SVG 实现。

## 构图与动作性格

让同一输入、样本或核心对象跨拍点保留身份。流程中可随对象经过工作站，机制中可推近局部，解释结束可拉远看到此前各部分如何组成整体。玻璃面、主体与路径之间有清楚的前后层；倾斜、遮挡和尺度变化服务当前关系，到站恢复读字。

标题既可以先占主画面，再让出机制空间，也可以在关系图建立后归纳结论。对比时保留同一组对象并改变状态，让差异可见；汇总时把已有对象归拢。优先复用工程内 `assets/references/styles/glass-lime/recipes.md` 的发展结构，并重算本题布局、时窗与交接。它们作为编排参考使用，组件可用状态见 collection 与 metadata。

共享运镜、焦点、文字编舞、时间和 seek 要求由 Skill 的 `references/motion-direction.md` 定义。声音沿用当前项目的真实旁白和混音合同；可以用轻电子氛围与少量动作音效支持交接，实际音量与同步按本期声音检查。Lime 不附带音乐、配音或上一条片子的音量参数。

## 参考校准与呈现

在完整时间轴制作前，用本期内容制作一张代表性机制校准帧，对照 `samples/lime-73.jpg`，在输出尺寸和预期播放尺寸观察：暗场中点阵是否清楚连续；主体玻璃是否同时看得出透明面、厚边、高光与局部冷暖彩边；主体、文字与背景是否仍有清晰层次。参照材质和背景，不复制示例的人物、文案、对象或布局。已有同一工程、同一生效 frame 和呈现条件的有效校准可复用；内容、缩放、遮挡或父片合成改变可见性时重新检查。

校准帧及参考路径、观察和修正写入 `ART-REVIEW.md`，并纳入现有分镜关键帧审看。玻璃或点阵不可辨时先检查 `.gl-scene` 作用域、背景层遮挡、CSS 覆盖、玻璃尺寸和布局完成后的 `GLGlass.install`；再根据实际画面调整背景对比、玻璃边光或面透明度，保持参考的深色层次和文字可读性。进入父片后还要复查缩放、裁切、叠层和调色是否保留材质。具体记录与通过条件见 Skill `references/quality.md`。

## 独立使用接口

从已安装 `xiangsu-mg` 运行：

```sh
node scripts/apply-style.mjs --style glass-lime --project <project-directory>
```

加载器核对完整资源哈希，写入 `frame.md`、`frame-resources.json`，将本风格全部文件复制到 `assets/references/styles/glass-lime/`。运行时读取已复制到工程内的相对路径。

```html
<link rel="stylesheet" href="assets/references/styles/glass-lime/runtime/mg-style.css">
<script src="assets/references/styles/glass-lime/runtime/glass.js"></script>
<!-- 放入已有 HyperFrames composition；当前场景作为作用域 -->
<div id="explanation" class="gl-scene">
  <div class="mg-background"></div>
  <div class="world"><div class="glass"><div class="gl-content">当前解释对象</div></div></div>
</div>
```

布局与字体准备好后执行 `GLGlass.install(document.querySelector('#explanation'), 'scene-unique-id')`。给每个场景独立 ID，并在不同尺寸或轮廓定稿后重新初始化；位置/旋转/缩放变化由现有材质实例随对象变换。相机、局部动作与文字由本期确定性时间轴驱动，玻璃运行时只负责材料；尺寸为零或尚未布局时先完成布局。CSS 使用 `.gl-scene` 作用域，玻璃初始化只扫描传入场景，保持多场景隔离。

## 随包参考

下列 `samples/` 路径在应用后位于 `assets/references/styles/glass-lime/`。图像时间与源视频 SHA 见 `provenance/sources.json`。参考中的文案、人物、对象数量和产品界面属于历史内容，不成为新题事实。

| 文件 | 来源时间 | 观察重点 |
|---|---|---|
| `samples/lime-36.jpg` | 第一条36秒 | 第一站到第二站：同一视频与相邻工作站保持关系 |
| `samples/lime-42.jpg` | 第一条42秒 | 随核心对象流转、玻璃厚度、路径与下一站露出 |
| `samples/lime-45.jpg` | 第一条45秒 | 回到总览，已访问的四站构成完整流程 |
| `samples/lime-66.jpg` | 第一条66秒 | 同组对象的平面比较起点 |
| `samples/lime-73.jpg` | 第一条73秒 | 同对象展开空间、倾斜、遮挡、层次与路径 |
| `samples/lime-79.jpg` | 第一条79秒 | 固定模板与多份替换内容的一对多关系 |
| `samples/workbench-64.jpg` | 第二条64秒 | 来源提炼进同一库；物件与模板结构共同解释 |
| `samples/workbench-78.jpg` | 第二条78秒 | 候选退居次要、唯一选中、选型结果收束 |

视频逐帧变化依据原视频取样；静帧本身不证明运动、音效或通用配方已验收。参考偏好支持本风格方向，本次接入不代替每期关键帧、正常播放和内容替换检查。
