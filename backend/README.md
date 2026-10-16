# zstack-backend

后端技术栈规范、生产实践与疑难问题处理：API 契约、事件驱动、Java，以及 MySQL、MongoDB、Redis 的建模、诊断和变更审查。

## 安装

```bash
claude plugin marketplace add calvingit/skills
claude plugin install zstack-backend@calvingit
```

Codex：`codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-backend@calvingit`。Cursor、ZCode 和更新、卸载的做法见 [INSTALL.md](../INSTALL.md)。

## 怎么用

这些 skill 在写、改或审查后端代码时由 Agent 自动选用。实现、验证与审查流程仍由 zstack-engineering 负责，两者可以一起装。

## Skills

| Skill | 用途 |
| --- | --- |
| [`backend-development`](./skills/backend-development/SKILL.md) | 后端 API、服务、持久化、集成和后台处理的工程实践。 |
| [`api-contracts`](./skills/api-contracts/SKILL.md) | API 与事件 Schema 的契约一致性、兼容性和演进验证。 |
| [`event-driven-backend`](./skills/event-driven-backend/SKILL.md) | 消息、Webhook 与后台任务的投递、消费、重放和副作用检查。 |
| [`java-coding-guidelines`](./skills/java-coding-guidelines/SKILL.md) | Java 编写、修改和审查规范。 |
| [`mysql-best-practices`](./skills/mysql-best-practices/SKILL.md) | MySQL 生产问题诊断和高风险数据库变更审查。 |
| [`redis-best-practices`](./skills/redis-best-practices/SKILL.md) | Redis 建模、缓存与协调逻辑审查，运行诊断和恢复风险评估。 |
| [`mongodb-best-practices`](./skills/mongodb-best-practices/SKILL.md) | MongoDB 文档模型、查询索引、并发更新与运行变更审查。 |

`backend-development` 按改动边界加载检查项；`api-contracts` / `event-driven-backend` 分别管契约与异步副作用。实现、验证与审查流程仍由 Engineering Skills 负责。

`backend-development` 按改动边界加载检查项；`api-contracts` 和 `event-driven-backend` 分别管契约和异步副作用。
