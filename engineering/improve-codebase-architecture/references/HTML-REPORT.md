# HTML Report

报告写入系统临时目录，文件名使用 `architecture-review-<UTC timestamp>.html`。样式使用内联 CSS；只有图形关系确实需要时，才通过 CDN 使用 Mermaid。报告应是单个可直接在浏览器中打开的 HTML 文件，不写入仓库。

每张候选卡片都要说明涉及的 Modules、当前摩擦、建议的 deepening 方向、Leverage 与 Locality 收益、测试如何改进，并提供 before/after 视觉和推荐强度。报告最后给出 Top recommendation，解释为什么它最值得先进入 `grilling`。

不要在候选报告阶段设计最终 Interface，也不要把文件数量、目录风格或个人审美当成架构问题。与 ADR 冲突的候选只有在摩擦证据足以重新打开决定时才保留，并明确标出冲突。
