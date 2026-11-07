# 柔和边缘暗角

2026-10-14 用户要求参照 MAV 的压暗效果，并优先采用所附画面的类似效果。图中可观察到四周较暗、脸部附近较亮；判断属于与 MAV 柔和边缘暗角相近的视觉语言。单帧无法分离现场灯光、原片调色与后期暗角，也不能据此确定原作参数。本次复用 MAV 已保存的中性透明黑层，保留中心亮度与宽幅柔和过渡；不复制截图里的 UI、字幕、布景或额外模糊。

唯一参数与 SHA 来源为 `assets/host-edge-shadow/preset.json`，配套 `soft-edge-v1.png` 是从 MAV 冻结的程序生成 RGBA 素材。1920×1080 中心透明，边缘中点约 13% 黑色，角落约 28%，采用 smootherstep。预设中的历史批准记录属于 MAV 原样段，不能视为 像素·绿宝石 新片的艺术验收。

## 已接入接口

独立样本生成器接受 `--host-finish soft-edge-v1` 或 `--host-finish off`；也可以在 `--content` JSON 内写：

```json
{"hostFinish":{"enabled":true,"preset":"soft-edge-v1"}}
```

命令行选项覆盖内容中的设置，省略两者默认关闭；决定随 `preview-input.json` 保存。`GLRuntime.mount` 消费同一 `data.hostFinish`；交互预览可调用 `previewSetHostFinish(true/false)`，内容或动作重建后保留选择。每期用户明确指定时直接使用，未指定时先确认是否启用。

`runtime.js` 从自身脚本路径解析资源位置，框架内联脚本时采用独立工程的 `assets/` 路径；`common.css` 只给 `.background.host` 添加静态伪元素。暗角在背景与前景之间，玻璃采样包含暗角的真实背景；文字和字幕不被统一压暗。切到点阵背景时不显示，完整 MG、媒体窗和截图保留自身像素。它不识别人脸、不跟踪人物，也不修正曝光；偏心构图需要审看是否压到脸部。

正片 compiler 已接入同一 `hostFinish` 配置，仅在编排的host窗口装配背景修饰。动态口播与跨镜剪接仍须随真实样段验证。
