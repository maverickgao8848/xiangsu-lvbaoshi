# 白金黑纹理 · Xiangsu Baijin

内置预设，ID `baijin-black-texture`。从白金的完整 frame 接口、Reference A 字体/配色和实际黑底 renderer 独立接入。与 Lime 同为入口的默认二选一；选择顺序和已有项目保护由 Skill 的输入与风格合同定义。运行所需资源随本预设冻结，不读取其他口播包装 Skill。

## 视觉意图

在有实体质感的黑色缎面舞台上解释知识：暖白衬线标题形成观点，浅金编号与细线引导关系，真实白瓷物件成为观众能追踪的主体。物件、必要标签和机制变化承担解释；背景保持克制的颗粒、脊纹与流动微光。构图随知识关系展开，可以从单物件、短命题、对照、局部机制发展到整体关系。

## 黑色程序纹理

默认调用随包 `runtime/black-texture.js` 中的 `BaijinTexture.blackBackground(stage, timeline, duration)`，并加载 `runtime/black-texture.css`。它保留源 renderer 的完整函数体与纹理 CSS；独立导出适配器在同一时间线上显式设置原有第0秒微光状态，修复首次显示与反向seek回0时的差异，不以静态图近似。

- 底色 `#08090a`；118度细重复斜纹与128度深浅缎面带构成脊纹，精确颜色和间距由冻结 CSS 消费。
- 512×288颗粒画布使用固定种子7419，opacity `.095`、`soft-light`。
- 微光沿当前场景的同一 GSAP 时间线从 `xPercent:-12 / opacity:.34` 到 `xPercent:12 / opacity:.5`，`sine.inOut`，覆盖解释窗口。它没有自己的播放时钟。
- 背景保持屏幕坐标层；当前相机 world 与对象放在独立前景层，避免纹理随推镜被放大。前景的遮挡、视差、尺度和焦点变化继续由本题设计。

静态 `textures/black-satin-metal-v1.png` 只用于本期明确选择的 `image-backup`。每个场景使用已选定的程序背景或 image-backup。`textures/grain.png` 按需用于阅读面板的微弱表面纹理。

## 字体、颜色与材质

1920×1080、30fps。完整本地字体文件随预设提供：

| 角色 | 字体与颜色 |
|---|---|
| 标题、关键短命题 | Chiron Sung HK Bold / 700，`#f3f1df` |
| 正文、标签、字幕 | OPPO Sans 4.0 / 400，`#dddeda` |
| 阅读正文 | OPPO Sans 4.0 / 400，`#cdcfcc` |
| 次级说明 | OPPO Sans 4.0 / 400，`#adafac` |
| 编号、强调与细线 | OPPO Sans 4.0 / 400，`#e0d990` |
| 焦点描边 | `#e0d88f` |

**本风格使用 OPPO Sans，Copyright 2024 Guangdong OPPO Mobile Telecommunications Corp., Ltd.** 原字体和许可随包保存。Chiron Sung HK 的 OFL 原文也随包保存。CSS 以 `BaijinSung`、`BaijinSans` 作为独立字体别名，从工程内 `assets/references/styles/baijin-black-texture/fonts/` 加载。

`runtime/theme.css` 从冻结的 Reference A 完整源 CSS 提取实际角色：深石墨 window 边 `#333537`、24px圆角、外影 `0 24px 68px #0008` 与内沿 `inset 0 1px 0 #ffffff06`；reading 边 `#3d3f41`；功能标签底 `#f0e99d`、字 `#1c1d1c`、边 `#e8e195`。原样式留在 `provenance/`，仅作来源；当前构图加载作用域限定的 theme，不整页加载原版 `.fill/.wash` 或 `body *` 规则。

Reference A 的104px标题、1.28行高、字组 `scaleX(.74)` 与41px阅读标题是对应阅读布局的参考尺度，不固定每个 MG 的字形压缩或标题位置。当前主题默认用真实字形；按文字长度、景别和画面层级安排大小与换行。需要采用参考压缩时只改变对应标题组，并在本期分镜记录。分字层继承同一字族和字重。

## Pixel2All 物件与解释动作

物件接口完整沿用 Skill 的 `references/object-library.md`：`BRIEF.md` 记录 `object_source: pixel2all`，逐对象检索、按需下载和导入透明 PNG，保存来源、实际使用及例外证据。Skill 不随包复制物件原图库。白瓷等素材保留原色、原透明度与实体质感；真实品牌使用有来源的 Logo。主题 CSS 只管文字、面板和关系线，不给图片整体染金。

以物件关系与状态变化讲清本题机制：对象靠近/离开显示联系，聚合/拆分显示结构，内部变化显示处理，保留身份的交接显示步骤。具体主体可以占据主画面，也可以让位给公式、比较或结论；浅金线和标签连接到它们真实表达的部位。按当前信息结构选择面板与构图。

共享动作、连续空间、相机、焦点、读字和 seek 规则见 Skill 的 `references/motion-direction.md`；本题对象、状态、时间窗和相机路线写入原有 STORYBOARD，由像素 MG 编排。单张 PNG 的素材能力仍按共享合同判断。旁白和声音继续沿用当前项目合同，

## 独立应用与 frame 接口

从当前 `xiangsu-mg` 安装目录执行：

```sh
node scripts/apply-style.mjs --style baijin-black-texture --project <project-directory>
```

加载器将有效 `frame.md` 与 `frame-resources.json` 写入工程，将全部资源复制到 `assets/references/styles/baijin-black-texture/`。这些工程相对路径可由 `inherit-frame.mjs` 继续继承到子工程；播放和渲染不需要源口播包装 Skill 或作者电脑路径。已有 `mav-editorial-black-texture` 完整继承工程继续保留原身份与 frame，不因新预设更名。

在已有 HyperFrames composition 内加载：

```html
<link rel="stylesheet" href="assets/references/styles/baijin-black-texture/runtime/black-texture.css">
<link rel="stylesheet" href="assets/references/styles/baijin-black-texture/runtime/theme.css">
<script src="assets/references/styles/baijin-black-texture/runtime/black-texture.js"></script>
<div id="explanation" class="baijin-scene">
  <div class="bj-world"><h1 class="bj-title">当前解释对象</h1></div>
</div>
```

布局完成时，对当前场景只初始化一次：

```js
const stage = document.querySelector('#explanation');
// tl 是本期已注册的场景时间线。
BaijinTexture.blackBackground(stage, tl, sceneDuration);
// 之后继续把本题前景、对象和相机动作编排进同一时间轴。
```

初始化在 scene-local 时间0处注册微光；完整场景只通过同一时间轴的播放/seek 更新时间。`bj-world` 保留独立相机 transform，背景固定在它下方。主题 CSS 使用 `.baijin-scene` 作用域，seek 更新已有背景状态。

## 来源与验证范围

`provenance/FRAME.source.md` 保存完整源 frame，`reference-a.source.css`、`reference-a.preset.json`、源背景函数与纹理规则保存来源证据；它们不替代本期有效 frame。源身份、哈希和迁移说明见 `provenance/sources.json`。`samples/` 的背景与排版探针用于观察当前冻结实现，具体范围见 metadata；它们不构成新主题成片或跨选题通用效果的艺术批准。每期仍按现有 quality 合同审看关键帧、实际动作与正常播放。
