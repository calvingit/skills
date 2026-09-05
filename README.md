# Agent Skills

个人 Agent Skills 集合。

## 目录

- `backend/`：后端技术栈规范、生产实践与疑难问题处理。
- `global/`：通用工具、文档、委托和工作流 Skills。
- `engineering/`：通用工程 Coding 流程，不绑定具体框架或项目结构。

## Backend Skills

| Skill | 用途 |
| --- | --- |
| [`java-coding-guidelines`](./backend/java-coding-guidelines/SKILL.md) | Java 编写、修改和审查规范。 |
| [`mysql-best-practices`](./backend/mysql-best-practices/SKILL.md) | MySQL 生产问题诊断和高风险数据库变更审查。 |

## Global Skills

| Skill | 用途 |
| --- | --- |
| [`claude-coder`](./global/claude-coder/SKILL.md) | 将明确的编码、修复、重构或测试任务委托给 Claude Code。 |
| [`codex-executor`](./global/codex-executor/SKILL.md) | 将边界清晰的编码任务委托给 Codex CLI 子智能体。 |
| [`explain-that`](./global/explain-that/SKILL.md) | 重新解释未理解的回复内容。 |
| [`find-docs`](./global/find-docs/SKILL.md) | 查询开发技术、库、SDK 和 CLI 的最新文档。 |
| [`fuck-my-shit-mountain`](./global/fuck-my-shit-mountain/SKILL.md) | 对项目进行证据驱动的全面工程审计。 |
| [`handoff`](./global/handoff/SKILL.md) | 整理可供下一次会话接续的交接文档。 |
| [`humanizer-zh`](./global/humanizer-zh/SKILL.md) | 清理中文文本中的 AI 味、翻译腔和模板化表达。 |
| [`improve-agents-md`](./global/improve-agents-md/SKILL.md) | 创建或优化项目 `AGENTS.md`。 |
| [`kimi-worker`](./global/kimi-worker/SKILL.md) | 将明确的编码任务委托给 Kimi CLI。 |
| [`pi-agent`](./global/pi-agent/SKILL.md) | 使用 Pi CLI 获取第二意见、委员会审查或受限实现。 |
| [`prompt-optimizer`](./global/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`resolving-merge-conflicts`](./global/resolving-merge-conflicts/SKILL.md) | 调查并解决 Git merge/rebase 冲突。 |
| [`show-me`](./global/show-me/SKILL.md) | 使用最小必要的图示、代码结构或 HTML 帮助理解。 |
| [`tavily-best-practices`](./global/tavily-best-practices/SKILL.md) | 设计 Tavily 搜索、提取、爬取和研究集成。 |
| [`tavily-cli`](./global/tavily-cli/SKILL.md) | 通过 Tavily CLI 进行网页搜索、提取、爬取和研究。 |
| [`tavily-crawl`](./global/tavily-crawl/SKILL.md) | 批量爬取网站并提取多个页面内容。 |
| [`tavily-dynamic-search`](./global/tavily-dynamic-search/SKILL.md) | 编程式筛选网页搜索结果。 |
| [`tavily-extract`](./global/tavily-extract/SKILL.md) | 从指定 URL 提取干净的 Markdown 或文本。 |
| [`tavily-map`](./global/tavily-map/SKILL.md) | 发现网站 URL 结构，不提取页面正文。 |
| [`tavily-research`](./global/tavily-research/SKILL.md) | 基于多来源开展带引用的深度研究。 |
| [`tavily-search`](./global/tavily-search/SKILL.md) | 获取面向 Agent 优化的 Tavily 搜索结果。 |
| [`teach`](./global/teach/SKILL.md) | 组织连续的主题学习、参考资料和学习记录。 |
| [`url-to-markdown`](./global/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |
| [`zh-terminology`](./global/zh-terminology/SKILL.md) | 审校中文技术术语并同步多载体表达。 |

## Engineering Skills

Engineering Skills 负责需求收敛、概要设计、实现、验证、审查和 ticket 执行。它们遵循职责单一、证据优先、可组合和不接管项目规则的原则。

完整的类型划分、选择指南、产物职责、Loop 执行约束和 ticket 生命周期见：

**[Engineering Skills 详情](./docs/engineering-skills.md)**

具体 Skill：

- [Workflow Skills](./engineering/)
- [Code Review](./engineering/code-review/SKILL.md)
- [Implement](./engineering/implement/SKILL.md)
- [Verify](./engineering/verify/SKILL.md)
- [Loop](./engineering/loop/SKILL.md)

文档：

- [Engineering Skills 详情](./docs/engineering-skills.md)
- [Loop Runtime 与 Backend Contract](./docs/loop-runtime.md)
- [Engineering workflow 图示](./docs/engineering-workflow.html)
- [Ticket lifecycle 图示](./docs/ticket-lifecycle.html)

按需读取目标 Skill 目录，具体执行规则以其中的 `SKILL.md` 为准。
