# 初次安装：给 AI 助手的操作说明

本页面向能执行命令的 AI 编程助手。先检查实际环境，向用户说明需要联网下载的组件；安装和验证通过之后，再读取对应 Skill 并开始制作。未经用户指定，不改写已有 Skill 或已存在的视频工程。

## 1. 准备

- Node.js **22.14 或更新版**、npm 和 Python **3.10 或更新版**；分别检查 `node --version`、`npm --version`、`python --version`。macOS/Linux 可能使用 `python3`。
- 需要联网、可执行本地命令、足够磁盘空间。运行时会下载 HyperFrames 0.8.192、Chrome、FFmpeg、FFprobe 和 Sharp。已有视频不需要语音 API；生成旁白需要用户自己的服务和凭据，切勿索要或提交凭据。
- 缺少 Node 或 Python 时，根据用户的系统给出官方安装步骤，确认安装后重新检查；不改变已有环境或覆盖文件。

## 2. 安装两个本仓库 Skill

在仓库根目录运行：

```sh
node install.mjs
```

默认装入 `$CODEX_HOME/skills`，未设置时装入 `~/.codex/skills`。首次需要联网；若同名 Skill 与本仓库不一致，安装器停止并保留原目录，可指定新的空目录：

```sh
node install.mjs --destination /path/to/empty/skills
```

只复制 Skill、稍后部署运行时：`node install.mjs --skills-only`。失败后可重跑相同命令；安装器不会覆盖有差异的文件。安装脚本检查 Node、准备锁定运行时并运行 HyperFrames doctor；它不会安装操作系统级 Python。

## 3. 官方配套 Skill 和图像依赖

执行官方安装器，将配套 Skills 安装到其支持的 AI 客户端：

```sh
npx hyperframes@latest skills
```

至少准备 `hyperframes`、`hyperframes-cli`、`media-use`；涉及组件库、Figma、Remotion 或演示文稿时，再按需安装 `hyperframes-registry`、`figma`、`remotion-to-hyperframes`、`slideshow`。它们由 [HyperFrames 官方项目](https://github.com/heygen-com/hyperframes)维护，不由本仓库冒充或重新授权。若安装器界面、权限或网络失败，记录实际原因并按官方说明解决。

绿宝石的物件 PNG 导入需要 Pillow。在用户选定的工作区建立一个新虚拟环境（目录不存在时），再安装 Pillow。Windows PowerShell：

```powershell
python -m venv .venv-xiangsu
.\.venv-xiangsu\Scripts\python.exe -m pip install Pillow
```

macOS/Linux：

```sh
python3 -m venv .venv-xiangsu
.venv-xiangsu/bin/python -m pip install Pillow
```

后续运行需要 Pillow 的命令时，使用该环境的 Python 路径。不要重建或替换用户已有虚拟环境。

## 4. 验证及启动

把下列 `<skills>` 换成实际安装目录。检查以下命令成功后重新加载 AI 会话：

```sh
node "<skills>/xiangsu-mg/scripts/hyperframes.mjs" doctor --json
node "<skills>/xiangsu-lvbaoshi/scripts/with-runtime.mjs" python --version
node "<skills>/xiangsu-lvbaoshi/scripts/build_preview.mjs" --effect L07 --motion A --sound camera --out "<新的空预览目录>"
```

macOS/Linux 可将 `python` 换成 `python3` 或虚拟环境的 Python 路径。`with-runtime.mjs` 为其子命令临时设置锁定运行时的 FFmpeg/FFprobe PATH；正式运行 `prepare.py` 也使用此入口，例如：

```sh
node "<skills>/xiangsu-lvbaoshi/scripts/with-runtime.mjs" python "<skills>/xiangsu-lvbaoshi/scripts/prepare.py" --source "<粗剪.mp4>" --project "<新工程目录>" --end <秒数> --timing "<可信时间JSON>"
```

在新会话中说「用 $xiangsu-lvbaoshi 包装这段粗剪」或「用 $xiangsu-mg 做解释动画」。按 Skill 工作流读取输入、产生计划并审看；安装成功不代表新视频已通过艺术验收。Lemo-Opuscar 是可选制作方，需要时按其[上游说明](https://github.com/lemomo-ai/lemo-opuscar)安装。Pixel2All 在线物件和第三方素材适用各自条款。
