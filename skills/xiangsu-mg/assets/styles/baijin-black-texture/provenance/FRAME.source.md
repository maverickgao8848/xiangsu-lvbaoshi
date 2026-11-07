# MAV Editorial · 黑色纹理动画视觉规范

本规范是 MAV Editorial Kit 新 MG 的默认美术输入。无论是否安装 MAV-MG，都保持本 Skill 原有黑色 metal 物件舞台的材质，以及参考 A 的字体与配色。MAV-MG负责机制表达、动作、构图、空间运镜和检查；用户明确换风格时再使用另一套视觉规范。

## 黑色纹理舞台

背景直接使用随项目冻结的 assets/editorial-mav/effects.css 中 .mav-black-texture、.mbt-ridges、.mbt-sheen、.mbt-grain，以及 assets/editorial-mav/runtime.js 导出的 MAVEditorial.blackBackground(root, timeline, duration)。这是原 relationships.py 黑底物件路线实际使用的同一实现，不另画近似纹理。

底色 #08090a。脊纹由118度的细重复斜纹与128度的深浅缎面带共同形成，完整颜色和间距以冻结CSS为准。512×288的颗粒画布使用固定种子7419，CSS opacity .095、soft-light；微光由同一GSAP场景时间线驱动，xPercent从-12到12、opacity从.34到.5、ease sine.inOut，duration覆盖当前解释窗口。保留真实颗粒、脊纹和移动微光。

把背景放在全屏舞台的固定层，对象与相机置于独立前景层。微光和颗粒不因相机world缩放而放大，前景通过遮挡、视差、尺度和焦点交接产生纵深。原静态 black-satin-metal-v1.png 仅用于明确选择的 image-backup；新MG默认使用程序纹理。

## 字体与颜色

字体与文字色的唯一来源仍为 assets/reference-layout/style.css；assets/frame/mav-theme.css由mav_typography.py生成，并将字体URL解析到本期本地assets/fonts。中文标题Chiron Sung HK Bold（Sung，700）、#f3f1df；正文OPPO Sans 4.0（OPPO，400）、#dddeda；阅读正文#cdcfcc；次级#adafac；编号/强调#e0d990；焦点描边#e0d88f。字体文件和许可随frame-resources.json完整冻结。

主题CSS中的字体角色、权重、颜色与细线按真实实现消费。参考A标题104px、行高1.28、标题字组scaleX(.74)、阅读标题41px等属于对应阅读角色的参考尺度；MG根据本期语义和镜头布局安排。逐字拆分文字继续继承字族，验证本地字体实际加载。

## 物件、面板与边缘

具体物件按MAV-MG的当前Pixel2All素材合同检索与导入，使用本期有来源的透明物件，保留素材原色和实体质感；真实品牌使用真实Logo。黑纹理舞台上以物件关系和必要短标签解释机制。

需要面板时沿用参考A深石墨材质：window边#333537、圆角24px、外影0 24px 68px #0008、内沿inset 0 1px 0 #ffffff06；reading边#3d3f41与低亮内沿；功能标签底#f0e99d、字#1c1d1c、边#e8e195。精确角色按完整冻结源CSS取值。面板按本期信息结构使用，黑色纹理始终是MG舞台；Glass Lime点阵、青柠配色和透明彩边玻璃不属于本规范。

## 动画与运镜

以选定MAV-MG的motion-direction为动作与相机权威，普通/高级模式均保持其完整分镜、素材、组件、连续空间、关键帧和艺术验收合同。按本期知识关系安排对象进入、状态变化、目标间移动、推拉/横移/穿行、视差与焦点交接，抵达后提供清晰阅读停留；对象本地运动和相机分别拥有transform。

本规范固定美术，不固定relationships.py的gap/journey等构图和动作配方。安装MAV-MG时由它规划完整机制动画，保留其动作与运镜能力。主题、口播、物件、时窗和相机路线写在本期BRIEF/SCRIPT/STORYBOARD，frame原文字节保持完整。

## 制作与交接

新MG先从父工程frame.md执行MAV-MG的inherit-frame.mjs，保留frame-provenance.json和全部资源。实现时加载assets/editorial-mav/effects.css、assets/frame/mav-theme.css与assets/editorial-mav/runtime.js，在已注册的场景时间线中调用MAVEditorial.blackBackground(stage, tl, duration)，再把本期相机world放在背景之上。上述路径相对MG项目根，子目录HTML需按框架装配基准解析。Reference A完整源CSS保留作字体、配色和按需面板的权威，不整页加载其.a .fill/.wash来覆盖黑纹理，也不重复叠加grain.png。

真人原拍摄背景和真实证据保留原色；真人暗角沿用本期决定。主工程直接装配完整MG画面，不补染背景、另加人物窗或覆盖字体。检查画面时同时核对脊纹、颗粒、移动微光、字体字重、物件质感与实际运镜；字节继承不能代替视觉验收。历史冻结工程沿用其原frame；用户明确要求换风格或迁移后再做新预览。
