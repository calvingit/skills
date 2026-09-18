# Agent Skills

个人 Agent Skills 集合。

## 目录

- `backend/`：后端技术栈规范、生产实践与疑难问题处理。
- `global/`：跨领域的 Agent 工具、上下文管理、会话辅助与持续学习。
- `documents/`：文档与文本的转换、表达审校和事实同步。
- `engineering/`：软件项目的调研、需求、设计、实现、验证、审查与维护，不绑定具体框架。
- `docs/`：本仓库的使用说明、协议文档和图示。

## Backend Skills

| Skill | 用途 |
| --- | --- |
| [`backend-development`](./backend/backend-development/SKILL.md) | 后端 API、服务、持久化、集成和后台处理的工程实践。 |
| [`java-coding-guidelines`](./backend/java-coding-guidelines/SKILL.md) | Java 编写、修改和审查规范。 |
| [`mysql-best-practices`](./backend/mysql-best-practices/SKILL.md) | MySQL 生产问题诊断和高风险数据库变更审查。 |

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
| [`zh-terminology`](./documents/zh-terminology/SKILL.md) | 审校中文技术术语并同步多载体表达。 |

## Engineering Skills

Engineering Skills 包含工程流程、可组合的判断方法，以及调研和维护工具。目录归类不代表必经阶段；独立调研、审查或冲突处理不要求先建立 SPEC 或 ticket。


具体见**[Engineering Skills 详情](./docs/engineering-skills.md)**，里面包含完整的类型划分、选择指南、产物职责、Loop 执行约束和 ticket 生命周期。


其他文档：

- [Loop 与 Runtime 的职责](./docs/loop-runtime.md)
- [状态脚本](./docs/workflow-scripts.md)
- [状态脚本验收协议](./docs/loopx-acceptance.md)
- [Engineering Acceptance 协议](./docs/engineering-acceptance.md)
- [独立 Verify 说明](./docs/verify.md)
- [Engineering workflow 图示](./docs/engineering-workflow.html)
- [Ticket lifecycle 图示](./docs/ticket-lifecycle.html)

按需读取目标 Skill 目录，具体执行规则以其中的 `SKILL.md` 为准。
