# Agent Skills

个人 Agent Skills 集合。以 Engineering 工作流为主（调研 → 需求 → 设计 → 实现 → 验证 → 审查），并包含后端生产实践、文档处理和工作会话/工具能力。可用于 Claude Code、Codex、Cursor 等 Coding Agent，不绑定单一框架或 Runtime。

> 本 README 是仓库唯一入口。维护前先读[维护规则](#maintenance-rules维护规则)：Engineering Skills 处于收敛期，优先修正已有职责与入口，勿轻易新增全局工程 Skill。

## Getting Started（安装）

### 插件安装

仓库按分类拆成四个插件，都在市场 `calvingit` 里，按需装：

| 插件 | 内容 |
| --- | --- |
| `zstack-engineering` | 工程工作流：需求、设计、拆票、实现、调试、评审、验证 |
| `zstack-backend` | 后端：API 契约、事件驱动、Java、MySQL/MongoDB/Redis |
| `zstack-documents` | 文档：同步、中文术语、去 AI 腔、网页转 Markdown |
| `zstack-work` | 日常工作：讲解、交接、提示词优化、搜索、教学 |

各工具的装法（以 `zstack-engineering` 为例，其他插件换个名字）：

| 工具 | 安装 |
| --- | --- |
| Claude Code | `/plugin marketplace add calvingit/skills`，再 `/plugin install zstack-engineering@calvingit` |
| Codex | `codex plugin marketplace add calvingit/skills`，再 `codex plugin add zstack-engineering@calvingit` |
| Cursor | `cursor-agent plugin marketplace add https://github.com/calvingit/skills`，再在 `/plugins` → Marketplace 安装 |
| ZCode | 设置 → 插件 → 创建 → 添加插件市场，填 `calvingit/skills`，再在 个人 分段安装 |

更新、本地调试和发版说明见 [`docs/install.md`](./docs/install.md)。原来的 `zstack` 插件已经删除，装过的话先卸载它再装新插件。

### 外部引用的插件

市场里还挂了一个外部插件 `supply-chain-risk-auditor`，来自 [trailofbits/skills](https://github.com/trailofbits/skills/tree/5c99c03fb8a9ea568432ecbcba5d86e9f4ac2bf0/plugins/supply-chain-risk-auditor)，用来审计 npm、PyPI、Go 依赖的供应链风险。它的许可证是 CC BY-SA 4.0，所以没有复制进本仓库，市场条目只是指向原仓库，并固定在提交 `5c99c03`。要跟进上游，改各个 `marketplace.json` 里的提交号即可。

```bash
claude plugin install supply-chain-risk-auditor@calvingit
```

运行它需要 uv 和 Python 3.11 以上，最好也装上 `gh`。

另外三个前端相关的外部插件，同样只是引用、固定在某个提交：

| 插件 | 来源 | 许可证 |
| --- | --- | --- |
| `react-best-practices` | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/063bee94c3f4df8453406c830b0a7df0f2860278/skills/react-best-practices)，提交 `063bee9` | MIT（仓库没有 LICENSE 文件，只在 README 和 SKILL.md 里声明） |
| `vue-best-practices` | [vuejs-ai/skills](https://github.com/vuejs-ai/skills/tree/c9d355ff23f654309dd02006be671859df0a134c/skills/vue-best-practices)，提交 `c9d355f` | MIT |
| `web-quality-skills` | [addyosmani/web-quality-skills](https://github.com/addyosmani/web-quality-skills/tree/afa8da942115f2961fdbfa80807ea0b232ff6c00)，提交 `afa8da9`，含性能、Core Web Vitals、可访问性、SEO 等 6 个 skill | MIT |

Codex 不认没有插件清单的单个 skill 目录：市场里能看到 React 和 Vue 这两个，装上也用不了。在 Codex 里改用 `npx skills` 装：

```bash
npx skills add vercel-labs/agent-skills --skill vercel-react-best-practices
npx skills add vuejs-ai/skills --skill vue-best-practices
```

这样装的是上游最新版本，不跟着本仓库固定的提交走。

### 手动安装

把本仓库里需要的 Skill 目录放到所用 Agent 的 Skills 搜索路径；每个 Skill 是一个含 `SKILL.md` 的独立文件夹。

常见做法：

1. 克隆或加为子模块到本机，例如 `~/skills/calvingit-skills`。
2. 按需把 Skill 目录链接到 Agent 的 skills 根目录（文件夹名保持不变），例如：
   - Claude Code / 兼容实现：`~/.claude/skills/<skill-name> -> <repo>/<category>/skills/<skill-name>`
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
| [`docs/`](./docs/) | 插件安装与发版、Graph Workflow/Runtime 说明和图示 |
| [`scripts/`](./scripts/) | 仓库检查脚本 |

许可见根目录 [`LICENSE`](./LICENSE)；第三方来源见 [`ATTRIBUTIONS.md`](./ATTRIBUTIONS.md)。

## Skills Overview

### Engineering Skills

| Skill | 用途 |
| --- | --- |
| [`grilling`](./engineering/skills/grilling/SKILL.md) | 访谈收敛尚未决定的需求与选择。 |
| [`wayfinding`](./engineering/skills/wayfinding/SKILL.md) | 跨会话理清依赖决策与探索路径。 |
| [`to-spec`](./engineering/skills/to-spec/SKILL.md) | 把已确认需求写成规范性 SPEC。 |
| [`solution-design`](./engineering/skills/solution-design/SKILL.md) | 对照 SPEC 与代码库确定或修订技术方案和设计决策。 |
| [`to-tickets`](./engineering/skills/to-tickets/SKILL.md) | 拆出可调度的交付 ticket 图；ticket 是稳定交付契约。 |
| [`graph-workflow`](./engineering/skills/graph-workflow/SKILL.md) | 推进 ticket 图：派发（默认 serial，用户可显式要求 swarm）、证据与 `.loop/state.json` 运行状态。 |
| [`quick-implement`](./engineering/skills/quick-implement/SKILL.md) | 无需执行图的小范围入口，不替代 graph-workflow；实现后收尾验证与审查。 |
| [`ticket-implement`](./engineering/skills/ticket-implement/SKILL.md) | 在约定写范围内实现单张 ticket。 |
| [`tdd`](./engineering/skills/tdd/SKILL.md) | 用红-绿-重构驱动单个行为。 |
| [`verify`](./engineering/skills/verify/SKILL.md) | 独立按 AC 判断 PASS/FAIL/NOT VERIFIED。 |
| [`code-review`](./engineering/skills/code-review/SKILL.md) | 审查缺陷、回归与无必要复杂度。 |
| [`simplify`](./engineering/skills/simplify/SKILL.md) | 审查或去掉无当前职责的复杂度。 |
| [`debug`](./engineering/skills/debug/SKILL.md) | 复现与诊断疑难缺陷（修复需授权）。 |
| [`test-audit`](./engineering/skills/test-audit/SKILL.md) | 审计测试有效性与维护成本。 |
| [`project-setup`](./engineering/skills/project-setup/SKILL.md) | 探测并持久化工程 Profile。 |
| [`verification-setup`](./engineering/skills/verification-setup/SKILL.md) | 从仓库证据盘点、建立或刷新本地验证方法。 |
| [`domain-modeling`](./engineering/skills/domain-modeling/SKILL.md) | 术语表与长期架构决策。 |
| [`codebase-design`](./engineering/skills/codebase-design/SKILL.md) | 深模块、缝与依赖方向的共用词汇。 |
| [`review-architecture`](./engineering/skills/review-architecture/SKILL.md) | 只读架构符合性审查与候选发现。 |
| [`challenge`](./engineering/skills/challenge/SKILL.md) | 对已有方案做有边界的对抗式审查。 |
| [`tech-research`](./engineering/skills/tech-research/SKILL.md) | 基于证据的技术调研与选型建议。 |
| [`find-docs`](./engineering/skills/find-docs/SKILL.md) | 按版本查找官方文档。 |
| [`how`](./engineering/skills/how/SKILL.md) | 用户手动调用：解释当前代码如何运行。 |
| [`why`](./engineering/skills/why/SKILL.md) | 用户手动调用：追查设计或限制成因。 |
| [`show-me`](./engineering/skills/show-me/SKILL.md) | 按理解难点选择最小必要的文本、表格、图示、图片或交互式 HTML。 |
| [`visual-pr`](./engineering/skills/visual-pr/SKILL.md) | 用户手动调用：起草带结构图的 PR 描述，只给出文本，不改 PR。 |
| [`improve-agents-md`](./engineering/skills/improve-agents-md/SKILL.md) | 创建或优化多工具适用的 AGENTS.md。 |
| [`context-audit`](./engineering/skills/context-audit/SKILL.md) | 审查 Agent 上下文中的重复、冲突、过时内容和职责错位。 |
| [`agent-tool`](./engineering/skills/agent-tool/SKILL.md) | 手动调用 Claude Code、Codex、Kimi、Pi 或 Grok 的统一 CLI 封装。 |
| [`fuck-my-shit-mountain`](./engineering/skills/fuck-my-shit-mountain/SKILL.md) | Project Audit：多维证据审计；仅显式调用（目录名保持兼容，界面显示名为 Project Audit）。 |

共享契约与状态工具见 [`engineering/skills/shared/`](./engineering/skills/shared/)（含 `check.py`、ticket graph）。跨 Skill 导航另见 [`docs/`](./docs/)。

### Backend Skills

| Skill | 用途 |
| --- | --- |
| [`backend-development`](./backend/skills/backend-development/SKILL.md) | 后端 API、服务、持久化、集成和后台处理的工程实践。 |
| [`api-contracts`](./backend/skills/api-contracts/SKILL.md) | API 与事件 Schema 的契约一致性、兼容性和演进验证。 |
| [`event-driven-backend`](./backend/skills/event-driven-backend/SKILL.md) | 消息、Webhook 与后台任务的投递、消费、重放和副作用检查。 |
| [`java-coding-guidelines`](./backend/skills/java-coding-guidelines/SKILL.md) | Java 编写、修改和审查规范。 |
| [`mysql-best-practices`](./backend/skills/mysql-best-practices/SKILL.md) | MySQL 生产问题诊断和高风险数据库变更审查。 |
| [`redis-best-practices`](./backend/skills/redis-best-practices/SKILL.md) | Redis 建模、缓存与协调逻辑审查，运行诊断和恢复风险评估。 |
| [`mongodb-best-practices`](./backend/skills/mongodb-best-practices/SKILL.md) | MongoDB 文档模型、查询索引、并发更新与运行变更审查。 |

`backend-development` 按改动边界加载检查项；`api-contracts` / `event-driven-backend` 分别管契约与异步副作用。实现、验证与审查流程仍由 Engineering Skills 负责。

### Work Skills

| Skill | 用途 |
| --- | --- |
| [`explain-that`](./work/skills/explain-that/SKILL.md) | 解释指定的局部内容，或用更少术语重述上一条完整回复。 |
| [`handoff`](./work/skills/handoff/SKILL.md) | 整理可供下一次会话接续的交接文档。 |
| [`prompt-optimizer`](./work/skills/prompt-optimizer/SKILL.md) | 优化任务提示词的目标、上下文、边界、输出和验证条件。 |
| [`tavily-search`](./work/skills/tavily-search/SKILL.md) | 为 Harness 提供基于 Tavily 的网页搜索。 |
| [`teach`](./work/skills/teach/SKILL.md) | 组织连续的主题学习、参考资料和学习记录。 |

### Documents Skills

以文档或说明性文本本身为处理对象。工程决策、技术资料查询和会话状态管理仍由各自的 Skill 负责。

| Skill | 用途 |
| --- | --- |
| [`document-sync`](./documents/skills/document-sync/SKILL.md) | 检查文档与当前实现和规范是否一致，只更新受影响内容。 |
| [`unslop`](./documents/skills/unslop/SKILL.md) | 润色已有文本，去掉 AI 味、翻译腔和模板表达，保留原意、专业性与作者口吻；按正文语言加载中英文规则。 |
| [`url-to-markdown`](./documents/skills/url-to-markdown/SKILL.md) | 将公开网页转换为本地 Markdown 文件。 |
| [`terminology-zh`](./documents/skills/terminology-zh/SKILL.md) | 审校中文技术术语并同步多载体表达。 |

## Engineering Kernel

[Engineering Kernel](./engineering/skills/shared/ENGINEERING_KERNEL.md) 是跨 Skill 的不变量基线（范围、知识、决策、行动、证据）。它不代替项目契约、角色写入边界或强制门禁。

## Responsibilities（职责）

[Engineering Responsibilities](./engineering/skills/shared/engineering-responsibilities.md) 回答“谁负责什么”：每个 Skill 能做哪些决定、写哪些产物、哪些事实以谁为准。跨 Skill 交接的目标、范围、验收和边界见[任务契约](./engineering/skills/shared/task-contract.md)。

## Invocation Contract（调用关系）

[Engineering Invocation](./engineering/skills/shared/engineering-invocation.md) 回答“谁可以调用谁”：用户入口、受调度角色和辅助能力三类，以及 graph-workflow、ticket-implement、verify 的调用规则。Graph Workflow 与 Runtime 的关系见 [Graph Workflow 与 Runtime](./docs/graph-workflow-runtime.md)。

## Skill Selection（如何选用）

完整规则见 [Engineering Skills Guide](./engineering/skills/shared/engineering-skills.md)。按当前目标选入口，不必走完所有阶段：

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | [`grilling`](./engineering/skills/grilling/SKILL.md) |
| 技术路径要跨会话理清 | [`wayfinding`](./engineering/skills/wayfinding/SKILL.md) |
| 需要持久化规范 | [`to-spec`](./engineering/skills/to-spec/SKILL.md) |
| 多模块方案设计约束 | [`solution-design`](./engineering/skills/solution-design/SKILL.md) |
| 多执行单元与调度 | [`to-tickets`](./engineering/skills/to-tickets/SKILL.md) → [`graph-workflow`](./engineering/skills/graph-workflow/SKILL.md) |
| 单一范围、无执行图 | [`quick-implement`](./engineering/skills/quick-implement/SKILL.md) |
| 缺可重复验证方法 | [`verification-setup`](./engineering/skills/verification-setup/SKILL.md) |

入口按风险选择的规则见[流程选择](./engineering/skills/shared/workflow-policy.md)。

[![Engineering Skills 工作流](./docs/diagrams/engineering-workflow.svg)](./docs/diagrams/engineering-workflow.svg)

[![本地 Ticket 生命周期](./docs/diagrams/ticket-lifecycle.svg)](./docs/diagrams/ticket-lifecycle.svg)

## Maintenance Rules（维护规则）

完整治理规则见 [Maintenance](./engineering/skills/shared/maintenance.md)。要点：

- 收敛期：暂停新增全局工程 Skill，只有真实任务证明现有职责无法承接时才提出新增；新增的 Skill 须原子、独立、不绑定 Runtime。
- 不新增 Runtime 抽象、通用编排层，也不添加 CI（`.github/workflows`）。
- 文档用自然的中文，避免 AI 腔和翻译腔。
- 维护某个 Skill 时只读相关文档，普通修改不要求预读全部 Skills 或建立完整 SPEC / tickets。
- 提交前运行 `python3 scripts/check_repo.py`（链接、Skill 元数据，并调用 `engineering/skills/shared/check.py` 跑状态脚本测试）和 `git diff --check`；改动插件清单时运行 `claude plugin validate .`。这些检查不能代替 Skill 行为、GUI 或 Runtime 验证，较大流程改动按维护规则做行为演练。
