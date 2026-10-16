# zstack-work

跨领域的日常工作辅助：解释、会话交接、提示词优化、网页搜索和连续学习。

## 安装

```bash
claude plugin marketplace add calvingit/skills
claude plugin install zstack-work@calvingit
```

Codex：`codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-work@calvingit`。ZCode 和更新、卸载的做法见 [INSTALL.md](../INSTALL.md)。

## 怎么用

多数需要你点名调用（Claude Code 里 `/名字`，Codex 里 `$名字`）。`tavily-search` 依赖本机的 [Tavily CLI](https://docs.tavily.com/)。

## Skills

| Skill | 用途 |
| --- | --- |
| [`explain-that`](./skills/explain-that/SKILL.md) | 解释指定的局部内容，或用更少术语重述上一条完整回复。 |
| [`handoff`](./skills/handoff/SKILL.md) | 整理可供下一次会话接续的交接文档。 |
| [`prompt-optimizer`](./skills/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`tavily-search`](./skills/tavily-search/SKILL.md) | 为 Harness 提供基于 Tavily 的网页搜索。 |
| [`teach`](./skills/teach/SKILL.md) | 组织连续的主题学习、参考资料和学习记录。 |
