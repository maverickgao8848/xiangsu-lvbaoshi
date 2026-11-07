# Glass Lime 本期有效视觉规范

来源：glass-lime-editorial-lab/samples/frame.md 与用户指定 Skill 的当前 assets。用户确认从此视觉稿接入 MAVMG 高级模式；本期不套用其七种内置美术。

## 材质与颜色

背景 #08090b，文字 #f5f6f2，次级文字 #a8afb4，青柠重点 #d7ff48，细点阵 #29414d。真人保留原背景；仅真人窗口启用 soft-edge-v1 中心透明、宽幅渐变暗角。

玻璃有低浓度透明面、连续倒角、轮廓法线折射、局部蓝紫与琥珀彩边、前沿高光及内侧暗边。玻璃采样真实动态背景，字层独立清晰。白气泡使用连续轮廓与短尾巴；深色实体对象与玻璃区分阅读任务。

## 字体与画面

1920×1080，30fps。中文标题 Noto Sans SC 800/900，正文400/500；数字与英文 Montserrat800；字幕 OPPO Sans400，#d9d9d9、rgba(48,49,52,.56)半透明柔和底，底部80px。三套字体使用 Skill 冻结的本地文件。

本片真人脸部保护区保守取 x=650..1250、y=120..735；麦克风保护区 x=900..1250、y=660..900。真人侧边面板以 x=105..650 或 x=1270..1805 为优先阅读区域，前景及字幕不覆盖口鼻和麦克风。阅读期间一次一个主要焦点。

## 完整 MG

同一条原片作为可识别的 workpiece，穿过模板、素材、动画与输出的工作站；以有厚度的玻璃片、真实陶瓷物件和青柠路径建立关系。连续相机场景有离站、移动、到站与清晰阅读状态；对象的本地运动和相机分别拥有 transform。

点阵与偏心低亮椭圆建立深度，焦点从前站传到后站；玻璃厚度、轻微2.5D倾斜、遮挡和尺度变化共同表达纵深。机理图保留必要标签，字的出现伴随对应对象或状态变化。主合成不再给完整MG叠字、人物小窗或染色。

## 动作与声音

Glass Lime A–F 参数只来自 references/motion.json。F仅用于L02/L08/L27；L30保留原动作。外层动作保持内部语义推进。样段的高亮用B／快门，输入面板用D／电子，模型事实表用C／快门。

背景音乐为轻电子氛围、无旁白；保持人声主导，音乐约低于口播22dB，交叉淡化循环并淡入淡出。音效与动作节点按实际时窗一起重算。

本期真人侧边输入面板的实际布局由下方代码块消费；坐标保持在脸部和麦克风左侧。模板内部动作保持原设计，媒体窗口完整contain。

```host-layout-css
.x-input{left:105px;top:500px;width:520px;padding:25px 28px}
.x-input-line{white-space:normal;font-size:30px;line-height:1.4;padding-top:20px;padding-bottom:16px}
.x-input-tools small{font-size:17px}
.x-roll-window img{object-fit:contain;background:#08090b}
.f-facts{width:540px!important}
.f-facts-heading{width:470px}
.f-facts-table{width:474px}
.f-facts-row{grid-template-columns:125px 1fr}
.f-facts-value{font-size:33px}
.f-facts-demo{font-size:21px}
.f-facts.glass{background:linear-gradient(120deg,#10161d99,#16212c77);backdrop-filter:blur(4.5px) var(--glass-optics,blur(0px)) saturate(1.03) brightness(.86)}
.x-corner{left:48px;top:26px;grid-template-columns:32px 1px minmax(0,450px);column-gap:18px;max-width:540px}
.x-corner-index{font-size:21px;line-height:40px}
.x-corner-divider{height:22px;margin-top:8px}
.x-corner h2{font-size:28px;font-weight:500;letter-spacing:1px;line-height:1.42}
#research-duration-content .v-ratio-value{font-size:150px;letter-spacing:-6px}
#research-duration-content .v-ratio-value span{font-size:52px;letter-spacing:0}
#research-duration-content .v-ratio-label{font-size:46px}
#research-duration-content .gl-companion-object{right:225px;top:195px;width:265px;height:265px}
#diagnosis-response-content .gl-companion-object{right:175px;top:120px;width:225px;height:225px}
.x-media img{object-fit:contain;background:#08090b}
```

原片测量：口播平均−33.2dB、峰值−10.8dB；音乐源平均−13.7dB。下面数值由主编译器与音乐预处理共同消费，口播只做线性增益，时序与原声内容保持。

```native-audio-mix
{"voiceGainDb":9,"sfxGainDb":-16,"musicGainDb":-32.5}
```

用户样段反馈：认可现有方向，并明确要求持续左上角章节角标、由内容自动分章。2026-10-18 用户另选 A 银灰磨砂分章底栏（`navigation.progress`，默认关闭，可选装配），替换此前“不需要进度条”的临时决定；章节唯一数据源仍为项目根chapters.json，开场导入00，正文分01–04。角标沿用L28的透明编号、细分隔线与开放留白，位于真人、素材和完整MG之上的独立导航层。原MG工程保留其frame，导航由主工程装配。
