# Agent Skills

个人 Agent Skills 集合。以 Engineering 工作流为主（调研 → 需求 → 设计 → 实现 → 验证 → 审查），并包含后端生产实践、文档处理和工作会话/工具能力。可用于 Claude Code、Codex、Cursor 等 Coding Agent，不绑定单一框架或 Runtime。

> 本 README 是仓库唯一入口。维护前先读[维护规则](#maintenance-rules维护规则)：Engineering Skills 处于收敛期，优先修正已有职责与入口，勿轻易新增全局工程 Skill。

## Getting Started（安装）

### 插件安装

整个仓库是一个插件 `zstack`，四个工具都实测过。更新、本地调试和发版说明见 [`docs/install.md`](./docs/install.md)。

| 工具 | 安装 |
| --- | --- |
| Claude Code | `/plugin marketplace add calvingit/skills`，再 `/plugin install zstack@calvingit` |
| Codex | `codex plugin marketplace add calvingit/skills`，再在 Plugins Directory 安装 ZStack |
| Cursor | `cursor-agent plugin marketplace add https://github.com/calvingit/skills`，再在 `/plugins` → Marketplace 安装 |
| ZCode | 设置 → 插件 → 创建 → 添加插件市场，填 `calvingit/skills`，再在 个人 分段安装 |

### 手动安装

把本仓库里需要的 Skill 目录放到所用 Agent 的 Skills 搜索路径；每个 Skill 是一个含 `SKILL.md` 的独立文件夹。

常见做法：

1. 克隆或加为子模块到本机，例如 `~/skills/calvingit-skills`。
2. 按需把 Skill 目录链接到 Agent 的 skills 根目录（文件夹名保持不变），例如：
   - Claude Code / 兼容实现：`~/.claude/skills/<skill-name> -> <repo>/<category>/<skill-name>`
   - 项目内：`.agents/skills/<skill-name>`，或工具文档指定的路径
3. 不要把整库当成单个 Skill 安装。`docs/`、`scripts/` 只用于维护本仓库，不是 Skill。
4. 带 `scripts/` 的 Skill（如 `agent-tool`、`url-to-markdown`、`graph-workflow`）需要本机有对应依赖（多为 Python 3 / Bash）；缺依赖时按该 Skill 正文说明处理。
5. 若曾从 `global/` 安装 Skill，需按新路径重装：`context-audit` 与 `agent-tool` 现位于 `engineering/`，其余原 `global/` Skill 现位于 `work/`。

## 目录

| 目录 | 内容 |
| --- | --- |
| [`engineering/`](./engineering/) | 调研、需求、设计、实现、验证、审查与维护（不绑定具体框架） |
| [`backend/`](./backend/) | 后端技术栈规范、生产实践与疑难问题处理 |
| [`documents/`](./documents/) | 文档转换、中英文润色、中文术语与事实同步 |
| [`work/`](./work/) | 跨领域工具、会话辅助与学习 |
| [`docs/`](./docs/) | 插件安装与发版、Graph Workflow/Runtime 说明、图示和仓库评估记录（`docs/evaluation/`） |
| [`scripts/`](./scripts/) | 仓库检查脚本 |

许可见根目录 [`LICENSE`](./LICENSE)；第三方来源见 [`ATTRIBUTIONS.md`](./ATTRIBUTIONS.md)。

## Skills Overview

### Engineering Skills

| Skill | 用途 |
| --- | --- |
| [`grilling`](./engineering/grilling/SKILL.md) | 访谈收敛尚未决定的需求与选择。 |
| [`wayfinding`](./engineering/wayfinding/SKILL.md) | 跨会话理清依赖决策与探索路径。 |
| [`to-spec`](./engineering/to-spec/SKILL.md) | 把已确认需求写成规范性 SPEC。 |
| [`solution-design`](./engineering/solution-design/SKILL.md) | 对照 SPEC 与代码库确定或修订技术方案和设计决策。 |
| [`to-tickets`](./engineering/to-tickets/SKILL.md) | 拆出可调度的交付 ticket 图。 |
| [`graph-workflow`](./engineering/graph-workflow/SKILL.md) | 推进 ticket 图：派发、证据与状态。 |
| [`quick-implement`](./engineering/quick-implement/SKILL.md) | 无需执行图的小范围入口，不替代 graph-workflow；实现后收尾验证与审查。 |
| [`ticket-implement`](./engineering/ticket-implement/SKILL.md) | 在约定写范围内实现单张 ticket。 |
| [`tdd`](./engineering/tdd/SKILL.md) | 用红-绿-重构驱动单个行为。 |
| [`verify`](./engineering/verify/SKILL.md) | 独立按 AC 判断 PASS/FAIL/NOT VERIFIED。 |
| [`code-review`](./engineering/code-review/SKILL.md) | 审查缺陷、回归与无必要复杂度。 |
| [`simplify`](./engineering/simplify/SKILL.md) | 审查或去掉无当前职责的复杂度。 |
| [`debug`](./engineering/debug/SKILL.md) | 复现与诊断疑难缺陷（修复需授权）。 |
| [`test-audit`](./engineering/test-audit/SKILL.md) | 审计测试有效性与维护成本。 |
| [`project-setup`](./engineering/project-setup/SKILL.md) | 探测并持久化工程 Profile。 |
| [`verification-setup`](./engineering/verification-setup/SKILL.md) | 从仓库证据盘点、建立或刷新本地验证方法。 |
| [`domain-modeling`](./engineering/domain-modeling/SKILL.md) | 术语表与长期架构决策。 |
| [`codebase-design`](./engineering/codebase-design/SKILL.md) | 深模块、缝与依赖方向的共用词汇。 |
| [`review-architecture`](./engineering/review-architecture/SKILL.md) | 只读架构符合性审查与候选发现。 |
| [`challenge`](./engineering/challenge/SKILL.md) | 对已有方案做有边界的对抗式审查。 |
| [`tech-research`](./engineering/tech-research/SKILL.md) | 基于证据的技术调研与选型建议。 |
| [`find-docs`](./engineering/find-docs/SKILL.md) | 按版本查找官方文档。 |
| [`how`](./engineering/how/SKILL.md) | 用户手动调用：解释当前代码如何运行。 |
| [`why`](./engineering/why/SKILL.md) | 用户手动调用：追查设计或限制成因。 |
| [`improve-agents-md`](./engineering/improve-agents-md/SKILL.md) | 创建或优化多工具适用的 AGENTS.md。 |
| [`context-audit`](./engineering/context-audit/SKILL.md) | 审查 Agent 上下文中的重复、冲突、过时内容和职责错位。 |
| [`agent-tool`](./engineering/agent-tool/SKILL.md) | 手动调用 Claude Code、Codex、Kimi、Pi 或 Grok 的统一 CLI 封装。 |
| [`fuck-my-shit-mountain`](./engineering/fuck-my-shit-mountain/SKILL.md) | Project Audit：多维证据审计；仅显式调用（目录名保持兼容，界面显示名为 Project Audit）。 |

共享契约与状态工具见 [`engineering/shared/`](./engineering/shared/)（含 `check.py`、ticket graph）。跨 Skill 导航另见 [`docs/`](./docs/)。

### Backend Skills

| Skill | 用途 |
| --- | --- |
| [`backend-development`](./backend/backend-development/SKILL.md) | 后端 API、服务、持久化、集成和后台处理的工程实践。 |
| [`api-contracts`](./backend/api-contracts/SKILL.md) | API 与事件 Schema 的契约一致性、兼容性和演进验证。 |
| [`event-driven-backend`](./backend/event-driven-backend/SKILL.md) | 消息、Webhook 与后台任务的投递、消费、重放和副作用检查。 |
| [`java-coding-guidelines`](./backend/java-coding-guidelines/SKILL.md) | Java 编写、修改和审查规范。 |
| [`mysql-best-practices`](./backend/mysql-best-practices/SKILL.md) | MySQL 生产问题诊断和高风险数据库变更审查。 |
| [`redis-best-practices`](./backend/redis-best-practices/SKILL.md) | Redis 建模、缓存与协调逻辑审查，运行诊断和恢复风险评估。 |
| [`mongodb-best-practices`](./backend/mongodb-best-practices/SKILL.md) | MongoDB 文档模型、查询索引、并发更新与运行变更审查。 |

`backend-development` 按改动边界加载检查项；`api-contracts` / `event-driven-backend` 分别管契约与异步副作用。实现、验证与审查流程仍由 Engineering Skills 负责。本仓库后端 Skill 的维护评估见[后端评估记录](./docs/evaluation/backend-skills-evaluation.md)。

### Work Skills

| Skill | 用途 |
| --- | --- |
| [`explain-that`](./work/explain-that/SKILL.md) | 解释指定的局部内容，或用更少术语重述上一条完整回复。 |
| [`handoff`](./work/handoff/SKILL.md) | 整理可供下一次会话接续的交接文档。 |
| [`prompt-optimizer`](./work/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`show-me`](./work/show-me/SKILL.md) | 按理解难点选择最小必要的文本、表格、图示、图片或交互式 HTML。 |
| [`tavily-search`](./work/tavily-search/SKILL.md) | 为 Harness 提供基于 Tavily 的网页搜索。 |
| [`teach`](./work/teach/SKILL.md) | 组织连续的主题学习、参考资料和学习记录。 |

### Documents Skills

以文档或说明性文本本身为处理对象。工程决策、技术资料查询和会话状态管理仍由各自的 Skill 负责。

| Skill | 用途 |
| --- | --- |
| [`document-sync`](./documents/document-sync/SKILL.md) | 检查文档与当前实现和规范是否一致，只更新受影响内容。 |
| [`unslop`](./documents/unslop/SKILL.md) | 润色已有文本，去掉 AI 味、翻译腔和模板表达，保留原意、专业性与作者口吻；按正文语言加载中英文规则。 |
| [`url-to-markdown`](./documents/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |
| [`terminology-zh`](./documents/terminology-zh/SKILL.md) | 审校中文技术术语并同步多载体表达。 |

## Engineering Kernel

[Engineering Kernel](./engineering/shared/ENGINEERING_KERNEL.md) 是跨 Skill 的不变量基线（范围、知识、决策、行动、证据）。它不代替项目契约、角色写入边界或强制门禁。

## Responsibilities（职责）

[Engineering Responsibilities](./engineering/shared/engineering-responsibilities.md) 回答“谁负责什么”：每个 Skill 能做哪些决定、写哪些产物、哪些事实以谁为准。跨 Skill 交接的目标、范围、验收和边界见[任务契约](./engineering/shared/task-contract.md)。

## Invocation Contract（调用关系）

[Engineering Invocation](./engineering/shared/engineering-invocation.md) 回答“谁可以调用谁”：用户入口、受调度角色和辅助能力三类，以及 graph-workflow、ticket-implement、verify 的调用规则。Graph Workflow 与 Runtime 的关系见 [Graph Workflow 与 Runtime](./docs/graph-workflow-runtime.md)。

## Skill Selection（如何选用）

完整规则见 [Engineering Skills Guide](./engineering/shared/engineering-skills.md)。按当前目标选入口，不必走完所有阶段：

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | [`grilling`](./engineering/grilling/SKILL.md) |
| 技术路径要跨会话理清 | [`wayfinding`](./engineering/wayfinding/SKILL.md) |
| 需要持久化规范 | [`to-spec`](./engineering/to-spec/SKILL.md) |
| 多模块方案设计约束 | [`solution-design`](./engineering/solution-design/SKILL.md) |
| 多执行单元与调度 | [`to-tickets`](./engineering/to-tickets/SKILL.md) → [`graph-workflow`](./engineering/graph-workflow/SKILL.md) |
| 单一范围、无执行图 | [`quick-implement`](./engineering/quick-implement/SKILL.md) |
| 缺可重复验证方法 | [`verification-setup`](./engineering/verification-setup/SKILL.md) |

入口按风险选择的规则见[流程选择](./engineering/shared/workflow-policy.md)。

[![Engineering Skills 工作流](./docs/diagrams/engineering-workflow.svg)](./docs/diagrams/engineering-workflow.svg)

[![本地 Ticket 生命周期](./docs/diagrams/ticket-lifecycle.svg)](./docs/diagrams/ticket-lifecycle.svg)

## Maintenance Rules（维护规则）

完整治理规则见 [Maintenance](./engineering/shared/maintenance.md)。要点：

- 收敛期：暂停新增全局工程 Skill，只有真实任务证明现有职责无法承接时才提出新增；新增的 Skill 须原子、独立、不绑定 Runtime。
- 不新增 Runtime 抽象、通用编排层，也不添加 CI（`.github/workflows`）。
- 文档用自然的中文，避免 AI 腔和翻译腔。
- 维护某个 Skill 时只读相关文档，普通修改不要求预读全部 Skills 或建立完整 SPEC / tickets。
- 提交前运行 `python3 scripts/check_repo.py`（链接、Skill 元数据，并调用 `engineering/shared/check.py` 跑状态脚本测试）和 `git diff --check`；改动插件清单时运行 `claude plugin validate .`。这些检查不能代替 Skill 行为、GUI 或 Runtime 验证，较大流程改动按维护规则做行为演练。
