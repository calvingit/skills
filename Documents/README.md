# zstack-documents

以文档和说明性文字本身为处理对象：文档与实现同步、去 AI 腔润色、中文术语审校、网页转 Markdown。

## 安装

```bash
claude plugin marketplace add calvingit/skills
claude plugin install zstack-documents@calvingit
```

Codex：`codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-documents@calvingit`。ZCode 和更新、卸载的做法见 [INSTALL.md](../INSTALL.md)。

## 怎么用

处理文档时由 Agent 自动选用，也可以点名调用。工程决策、技术资料查询和会话状态仍由各自的 skill 负责。

## Skills

| Skill | 用途 |
| --- | --- |
| [`document-sync`](./skills/document-sync/SKILL.md) | 检查文档与当前实现和规范是否一致，只更新受影响内容。 |
| [`unslop`](./skills/unslop/SKILL.md) | 润色已有文本，去掉 AI 味、翻译腔和模板表达，保留原意、专业性与作者口吻；按正文语言加载中英文规则。 |
| [`url-to-markdown`](./skills/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |
| [`terminology-zh`](./skills/terminology-zh/SKILL.md) | 审校中文技术术语并同步多载体表达。 |
