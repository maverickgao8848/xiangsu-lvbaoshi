# 参考配方与保留生产层

本页按2026-10-15审看维护，2026-10-18补记：原28项L模板保留；本轮新增项只保留两项并新建R01–R05。区域聚光、实/虚框选、半透明区域高亮、局部摘取和人后大字已撤下，不作为候选，不留下新生产入口；分章进度已由用户于2026-10-18另选 A 银灰磨砂分章底栏，走 `navigation.progress`，不并入本页R配方。历史已冻结预览是审看记录，不自动迁移。目录权威为production-layers.json。

## 两项保留

`companions:[{id,start,end,left:{asset,label,motion,x,y,size},right:{asset,label,motion,x,y,size}}]`，单侧或双侧。asset必须是实际Pixel2all白色陶瓷PNG，按原素材展示，沿透明轮廓加一点淡荧光绿边缘发光，保持白色主体，不染成荧光色，不用自编玻璃几何物件替代。motion为hold/float/nod/pulse，x/y/size为1920×1080舞台像素。检索和导入沿用scripts/stage_object.py，asset-credits保留对象页、SHA、来源及使用依据；objectReview以companions:<id>绑定实际图片。真实品牌沿用原Logo合同，不冒充白色陶瓷物件。

`screenEffects:[{id,start,end,targetBeat,mode:"callout",region:{x,y,width,height},card:{x,y},label,definition,note?}]`。一般在对着素材讲解时使用，优先圈出截图、录屏或图片中的具体对象。targetBeat引用正在展示的screen/media/broll原图/视频；region是源像素椭圆外接矩形。画圈后引线直接接已有L02：使用同一render、motion、common/focus CSS与GLGlass光学材质。card放实际545px玻璃卡，label作词条，definition作正文，note可选。不要另加深色底/金属卡皮肤；不要把其它已撤下标注模式重新放回本接口。

## R01–R03：质感按参考逐项对照

R01以2026-10-18用户确认的中文A方案为准；R02/R03继续以参考14/15的字面、颜色、细边、阴影、圆角、透视和排版为校准基准；台词与媒体每期替换。人物背景是独立本期素材。截图无法确定原动效时间，样板入场为本次编排，不宣称已复刻原始视频时序。

使用`editorialScenes:[{id,start,end,templateId,content}]`作为真人辅助层。

- R01 content为`{lines:[{text,x,y,width,height,at}]}`。使用用户确认的A方案：三行全部荧光绿，字型与样式的唯一来源为`assets/production.css`中的`.glp-stack-copy`：明确使用本地GLSans（Noto中文字体），72px / 600 / 1.2，颜色#d8fb54，无描边、轻阴影。`x/y`定义行框左上角，`width/height`是最大可用行框，不是要强制铺满的字面。文字保留自然宽度、不扩字距；空间不足时全部行采用同一最小比例等比缩小，保持统一字号和字形原比例。1920×1080画布建议x=100、首行y=142、行起点间距132、每行width=500/height=90，再按人物留白调整位置和最大宽度。入退场和逐行at继续沿用现有R01动作。
- R02 content为`{title,width,height,corners:[{x,y},…共4点],media}`。corners依次左上、右上、右下、左下，以平面投影直接定位，避免嵌套透视跑位。薄圆角媒体面、细边与柔软投影；视频槽可比图片样板放大约两成，按原片留白安排位置，不通过挪动人物腾空间；media可以是真实图片或视频，窗口的正文必须由实际素材提供。
- R03 content为`{items:[{label,caption?,captionWidth?,x,y,width,height,at}]}`。白色短上标题，荧光阶段词、浅色细描边和轻暗影；默认按参考横排三个阶段。caption仅放其实际所属阶段，不当成全片进度条。主口播字幕在R03窗内保持原字型/字色，并自动移到阶段文字上方，避免遮住底部词组。

R01使用原生HTML文字与明确加载的本地OFL Noto中文GLSans，运行时只做统一等比缩小；R03沿用原生SVG及本地OFL Roboto/GLSans的字面拟合。两者均可替换、seek和导出。参考字形源字体未获证实；本地对照以观察到的字面外形为准，不把视觉接近说成精确识别字体。

## R04/R05：构图灵活

R04/R05是完整主画面beat：`{id,kind:"editorial",start,end,templateId,content}`，所属编排段在beatIds引用。data/evidence/illustration/operation可用，机制持续解释仍交像素 MG。

- R04 content为`{kicker,title,side:"left"|"right",media,steps:[短说明]}`。黑底/本项目荧光重点、大幅原媒体与另一侧短说明、编号、细线轻动画。side决定说明区的位置，不要求每期复制参考16整页；按本期素材/说明长度重新编排，不能让说明与主媒体竞争焦点。
- R05 content为`{hostSide,hostSource,hostMediaStart,title,media,note}`。hostSide为left/center/right，记录原拍摄的人物位置，不是移动人物的命令。人物源画面全幅contain，不平移、不裁切、不做人物入场运镜；原片人物在右侧就利用左侧留白，原片在左侧则反向，居中时保持居中并用较窄侧窗避开人脸。阴影只衬托素材区域，不对整个人物压暗。媒体需更大而空间不足时改用R04等独立素材画面，不能强行挪人。保留原媒体颜色，不继承参考17配色。hostSource与主口播按实际时间对齐；辅助视频静音，口播原声独立保留。按本期全段核对脸、手和肩与素材的遮挡。

media是`{source,mediaStart?,crop?}`；crop为原始素材像素`{x,y,width,height}`。编译器读取实际尺寸，按contain保留比例/原像素，视频按冻结时窗同步。裁切不是重绘、自动OCR或文字跟踪；不把截图中的播放器工具栏、弹幕、水印当模板组件。

## 编排、验证与预览

辅助层在所属段的layerIds引用；完整R04/R05在beatIds引用。所有7个新增候选均进入candidateReview；真实物件依照objectReview来源核验。编译拒绝孤立引用、越界时间/像素、被占用人物窗、未消费字段和已撤下接口。

`node scripts/build_reference_preview.mjs --out <新目录> --plate <干净参考底图> --objects <已导入Pixel2all素材工程> --host-video <真实人物片段> --insert-video <实际媒体片段>`生成新预览：前3项可以在制作效果/原图间切换，文字替换验证、图片/视频槽、左右构图和L02材质分别审看。生成器不使用旧新增特效；素材与许可记录随工程保存。开场前10秒允许更密集动效的已确认规则继续沿用。
