# zstack-work

跨领域的日常工作辅助：解释、会话交接、提示词优化、网页搜索、连续学习，以及上下文审查、AGENTS.md 优化、官方文档查询和外部 Agent CLI。

## 安装

```bash
claude plugin marketplace add calvingit/skills
claude plugin install zstack-work@calvingit
```

Codex：`codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-work@calvingit`。ZCode 和更新、卸载的做法见 [INSTALL.md](../INSTALL.md)。

## 怎么用

多数需要你点名调用（Claude Code 里 `/名字`，Codex 里 `$名字`）。`tavily-search` 依赖本机的 [Tavily CLI](https://docs.tavily.com/)。`find-docs` 可在查官方文档时自动选用。

## Skills

| Skill | 用途 |
| --- | --- |
| [`explain-that`](./skills/explain-that/SKILL.md) | 解释指定的局部内容，或用更少术语重述上一条完整回复。 |
| [`handoff`](./skills/handoff/SKILL.md) | 整理可供下一次会话接续的交接文档。 |
| [`prompt-optimizer`](./skills/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`tavily-search`](./skills/tavily-search/SKILL.md) | 为 Harness 提供基于 Tavily 的网页搜索。 |
| [`teach`](./skills/teach/SKILL.md) | 组织连续的主题学习、参考资料和学习记录。 |
| [`context-audit`](./skills/context-audit/SKILL.md) | 审查 Agent 上下文中的重复、冲突、过时内容和职责错位。 |
| [`improve-agents-md`](./skills/improve-agents-md/SKILL.md) | 创建或优化适用于多种 Coding Agent 的 AGENTS.md。 |
| [`find-docs`](./skills/find-docs/SKILL.md) | 按相关版本查找库或服务的官方文档。 |
| [`agent-tool`](./skills/agent-tool/SKILL.md) | 统一封装并观察 Claude Code、Codex、Kimi、Pi 或 Grok 等外部 Agent CLI。 |
