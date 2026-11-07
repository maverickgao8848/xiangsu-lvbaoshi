# 首次安装与环境检查

本 Skill 是 Xiangsu 开源仓库的一部分。首次使用时，让 AI 阅读仓库根目录的 [INSTALL.md](https://github.com/maverickgao8848/xiangsu-lvbaoshi/blob/main/INSTALL.md)，检查 Node.js、Python、FFmpeg、Chrome、官方 HyperFrames Skills 与 Pillow，并按说明部署和验证。安装完成后重启 AI 会话。

如已安装，只在工具缺失时检查，不覆盖已有 Skill 或虚拟环境。使用绿宝石 prepare 时，通过本 Skill 同级的 `xiangsu-lvbaoshi/scripts/with-runtime.mjs` 运行 Python，以临时加入锁定的 FFmpeg/FFprobe。
