# Agent Skills

个人 Agent Skills 集合。

## 目录

- `backend/`：后端技术栈规范、生产实践与疑难问题处理。
- `global/`：跨领域的 Agent 工具、上下文管理、会话辅助与持续学习。
- `documents/`：文档与文本的转换、表达审校和事实同步。
- `engineering/`：软件项目的调研、需求、设计、实现、验证、审查与维护，不绑定具体框架。
- `docs/`：使用总览、跨 Skill 职责、Loop 说明与成套图示，执行参考资料由所属 Skill 维护。

## Backend Skills

| Skill | 用途 |
| --- | --- |
| [`backend-development`](./backend/backend-development/SKILL.md) | 后端 API、服务、持久化、集成和后台处理的工程实践。 |
| [`api-contracts`](./backend/api-contracts/SKILL.md) | API 与事件 Schema 的契约一致性、兼容性和演进验证。 |
| [`event-driven-backend`](./backend/event-driven-backend/SKILL.md) | 消息、Webhook 与后台任务的投递、消费、重放和副作用检查。 |
| [`java-coding-guidelines`](./backend/java-coding-guidelines/SKILL.md) | Java 编写、修改和审查规范。 |
| [`mysql-best-practices`](./backend/mysql-best-practices/SKILL.md) | MySQL 生产问题诊断和高风险数据库变更审查。 |
| [`redis-best-practices`](./backend/redis-best-practices/SKILL.md) | Redis 建模、缓存与协调逻辑审查，运行诊断和恢复风险评估。 |
| [`mongodb-best-practices`](./backend/mongodb-best-practices/SKILL.md) | MongoDB 文档模型、查询索引、并发更新与运行变更审查。 |

`backend-development` 按改动边界加载检查项，外部写入结果与重试、运行生命周期与资源限制的细节按需读取。`api-contracts` 统一检查 API 与事件 Schema 兼容性，`event-driven-backend` 负责异步投递与副作用生命周期。Java Skill 负责编码规约，MySQL、Redis 和 MongoDB Skills 负责各自数据库的机制、现场和变更风险，实现、验证与审查流程仍由 Engineering Skills 负责。后端 Skill 的维护评估入口见[本仓库验证方法](./.agents/skills/verify-engineering/SKILL.md)。

## Global Skills

| Skill | 用途 |
| --- | --- |
| [`context-audit`](./global/context-audit/SKILL.md) | 审查 Agent 上下文中的重复、冲突、过时内容和职责错位。 |
| [`bro`](./global/bro/SKILL.md) | 仅限用户手动调用，用更少术语重新表达上一条完整回复。 |
| [`explain-that`](./global/explain-that/SKILL.md) | 重新解释未理解的回复内容。 |
| [`handoff`](./global/handoff/SKILL.md) | 整理可供下一次会话接续的交接文档。 |
| [`prompt-optimizer`](./global/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`show-me`](./global/show-me/SKILL.md) | 使用最小必要的图示、代码结构或 HTML 帮助理解。 |
| [`tavily-search`](./global/tavily-search/SKILL.md) | 为 Harness 提供基于 Tavily 的网页搜索。 |
| [`teach`](./global/teach/SKILL.md) | 组织连续的主题学习、参考资料和学习记录。 |
| [`agent-tool`](./global/agent-tool/SKILL.md) | 手动调用 Claude Code、Codex、Kimi、Pi 或 Grok 的统一 CLI 封装。 |

## Documents Skills

以文档或说明性文本本身为处理对象。工程决策、技术资料查询和会话状态管理仍由各自的 Skill 负责。

| Skill | 用途 |
| --- | --- |
| [`document-sync`](./documents/document-sync/SKILL.md) | 检查文档与当前实现和规范是否一致，只更新受影响内容。 |
| [`humanizer-zh`](./documents/humanizer-zh/SKILL.md) | 清理中文文本中的 AI 味、翻译腔和模板化表达。 |
| [`url-to-markdown`](./documents/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |
| [`terminology-zh`](./documents/terminology-zh/SKILL.md) | 审校中文技术术语并同步多载体表达。 |

## Engineering Skills

Engineering Skills 提供按需组合的调研、需求、设计、实现、验证与审查能力，目录归类不代表必经阶段，独立任务无需先建立 SPEC 或 ticket。

- [使用总览与选择入口](./docs/engineering-skills.md)：按当前目标选择能力，查找项目准备、交付与图示入口。
- [职责与产物归属](./docs/engineering-responsibilities.md)：维护跨 Skill 边界、权威来源与适配规范。
- [Loop 与 Runtime](./docs/loop-runtime.md)：理解 ticket 执行、状态脚本部署和最终交付。
- [本仓库验证方法](./.agents/skills/verify-engineering/SKILL.md)：按改动选择静态检查、状态协议回归和行为评估。

按需读取目标 Skill，具体执行规则以其 `SKILL.md` 和参考资料为准。
