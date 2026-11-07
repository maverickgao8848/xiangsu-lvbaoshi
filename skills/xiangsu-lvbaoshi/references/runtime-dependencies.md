# 运行依赖与自包含边界

包装的 prepare、编排／选型、模板、素材展映、Scene Kit 适配、声音与 compiler 均从本 Skill 目录解析；不需要安装白金版，也不读取作者旧实验工程。字体、GSAP、模板／声音资源和来源随 assets 保存。项目媒体、源码、冻结清单与生成 HTML 使用项目相对路径。

运行需要 Python 3、Node.js 22.14+、FFmpeg/FFprobe 与已安装的 HyperFrames；PNG 导入按 stage_object.py 需要 Pillow。像素 MG 或 Lemo-Opuscar 是按需调用的独立动画制作能力，按 [动画路由](animation-routing.md) 查找，只有选中某制作方才需要其安装／库。Pixel2All 与实际录屏／品牌是本期输入；必要时用素材库与 media-use 检索、对齐。这里的“自包含”指包装代码和资源不借用其它目录，不将两个完整制作引擎复制为私有分叉。

维护本目录的代码或资源后，运行 `python scripts/refresh_bundle.py` 查看分发清单差异，核对预期改动后才用 `--write` 更新本地清单，再运行测试和 prepare。项目已冻结资源仍受原哈希保护；更新清单不迁移或批准旧项目。
