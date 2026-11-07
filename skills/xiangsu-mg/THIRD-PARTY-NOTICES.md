# 配套工作流来源

本地交付包中的 `hyperframes`、`hyperframes-cli`、`hyperframes-registry`、`media-use`、`figma`、`remotion-to-hyperframes` 与 `slideshow` 来自官方仓库 https://github.com/heygen-com/hyperframes 的提交 `291144e87ddfee93a3cd01764810311f0b5c5016`，完整保留对应目录；各文件与官方 Git blob 校验一致。

保留上游 [Apache License 2.0 原文](assets/licenses/HyperFrames-LICENSE.txt)。随包文件以 `MANIFEST.sha256` 为准；接收端 CLI 固定为 0.8.192，版本与传递依赖见 runtime/package.json 及其锁文件。

像素 MG 自身代码按本仓库 MIT 许可发布；第三方风格资源继续使用各自 metadata 与字体许可；上游工作流的许可不替代这些资源的许可。

# 青柠玻璃（Lime）字体与参考

本风格使用 **OPPO Sans，Copyright 2024 Guangdong OPPO Mobile Telecommunications Corp., Ltd.**，按随包 `assets/styles/glass-lime/fonts/OPPO-License.txt` 保留原文件和许可；Noto Sans SC 与 Montserrat 各自的 OFL 原文同在该字体目录。三套字体随软件与风格资源组合提供。玻璃实现与历史规范保持来源记录；视频参考帧来自用户指定的本地素材，来源、时间和 SHA 见 `assets/styles/glass-lime/provenance/sources.json`，2026-11-07 仓库所有者确认允许本次公开再分发。


# 白金黑纹理字体与来源

白金黑纹理的完整 Chiron Sung HK Bold 保留 Tamcy 的 SIL OFL 1.1，原文见 `assets/styles/baijin-black-texture/fonts/Sung-OFL.txt`。本预设同时使用 **OPPO Sans，Copyright 2024 Guangdong OPPO Mobile Telecommunications Corp., Ltd.**，保留原字体与 `fonts/OPPO-License.txt`。源 frame、Reference A 和背景实现的冻结来源见该风格的 `provenance/sources.json`；这些来源记录不要求接收方安装口播包装 Skill。

# 语义分镜与过程预演参考

[Table-VideoSOP](https://github.com/duoduoler-ops/Table-VideoSOP/tree/0cad435d10f937cc52fe6b87036fd09eb6df6756)，作者一只桌子，正文以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 发布。preview.32 的语义分镜、过程预演与阅读时间组织参考其视觉叙事经验、镜头剧本模板和验收正文，并改写到本 Skill 既有的 visual-grammar、motion-direction、quality 与分镜示例中；有改动。未移植其 Remotion 实现、工具脚本、角色或展示图片。

# 接收端运行时

固定运行时依赖见 `runtime/package.json` 与 `runtime/package-lock.json`。HyperFrames 为 Apache-2.0，Sharp 为 Apache-2.0，ffmpeg-static/ffprobe-static 的包与下载二进制保留各自许可。它们在接收端安装，原包 LICENSE 与 notices 随 npm 依赖落盘；本仓库不复制本机安装的运行时二进制。像素造物图片按需下载，其本交付使用依据见 `references/pixel2all-rights.md`。
