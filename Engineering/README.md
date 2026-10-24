# zstack-engineering

给编码 Agent 用的工程工作流：从需求收敛、编写规范、确定技术方案、拆 ticket，到实现、调试、验证和审查。不绑定语言、框架或 Agent Runtime；项目规则和验证入口留在目标仓库。

## 第一次怎么用

- 已有 ticket，且写入范围清楚：[`ticket-implement`](./skills/ticket-implement/SKILL.md)。
- 单一范围、无执行图：默认 [`quick-implement`](./skills/quick-implement/SKILL.md)。
- 需求、边界或验收还没说清：先 [`grilling`](./skills/grilling/SKILL.md)。
- 多个相关改动要一起调度：走下面「一条主链路」（拆票再推进）。
- 多模块要共享契约或技术方案：用 [`solution-design`](./skills/solution-design/SKILL.md)。
- 技术路径要跨会话理清：[`wayfinding`](./skills/wayfinding/SKILL.md)。
- 缺可重复的验证方法：先找项目里已有的方法，不够再用 [`verification-setup`](./skills/verification-setup/SKILL.md)。

各 Skill 的启动与调度边界见下文「三类角色」。

## 按当前状态选入口

选择流程时，看需求和技术路径还有哪些不确定之处、改动会影响哪些调用方和共享资源、收集完整验收证据有多难；不要按代码行数或「小、中、大」标签判断。细则见[按风险选择流程](./skills/shared/workflow-policy.md)。

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | [`grilling`](./skills/grilling/SKILL.md) |
| 技术路径要跨会话理清 | [`wayfinding`](./skills/wayfinding/SKILL.md) |
| 需要持久化规范 | [`to-spec`](./skills/to-spec/SKILL.md) |
| 多模块要共享设计约束 | [`solution-design`](./skills/solution-design/SKILL.md) |
| 多执行单元与调度 | [`to-tickets`](./skills/to-tickets/SKILL.md) → [`graph-workflow`](./skills/graph-workflow/SKILL.md) |
| 单一范围、无执行图 | [`quick-implement`](./skills/quick-implement/SKILL.md) |
| 缺可重复验证方法 | [`verification-setup`](./skills/verification-setup/SKILL.md) |

- 单一执行范围也可能需要技术方案；简单局部修改可以直接做。
- `quick-implement` 也可在明确指定时处理多个独立修复，契约和收尾标准不变；不得因执行单元多或偏好某条路线就自动转交 Graph Workflow。
- 缺需求或共享设计时，只暂停受影响的操作，并交回负责方处理。
- 缺验证方法时，先找项目已有的方法，不够再考虑 `verification-setup`。
- 入口可按需组合；上游可以推荐，最终由你选择。

## 一条主链路

grilling → to-spec → solution-design → to-tickets → graph-workflow → ticket-implement → verify

不必走完每一环。执行时，有图就按 `graph-workflow` 的派发实现与收尾；无图且范围单一时默认 [`quick-implement`](./skills/quick-implement/SKILL.md)，不自动切到 Graph Workflow。除非任务明确要求收敛需求，否则不要自行从 `grilling` 重开主链路。`to-spec` 确认 SPEC 后可按需交给 `solution-design`，再推荐 Quick 或 Tickets。Graph Workflow 与 Runtime 见 [Graph Workflow 与 Runtime](./docs/graph-workflow-runtime.md)。各环节的真实产物形态见[全链示例](./docs/example-task/README.md)。

[![Engineering Skills 工作流](./docs/diagrams/engineering-workflow.svg)](./docs/diagrams/engineering-workflow.svg)

*工程工作流总览：从需求与设计到拆票、实现与验收。*

[![本地 Ticket 生命周期](./docs/diagrams/ticket-lifecycle.svg)](./docs/diagrams/ticket-lifecycle.svg)

*本地 ticket 生命周期：就绪、执行、证据与交付状态。*

## 需求和设计变了怎么办

不必从头重跑。先确定谁维护相应依据，由负责方修订，只同步受影响的下游。

| 情况 | 怎么做 |
| --- | --- |
| 产品选择、行为、范围、权限、兼容或验收仍有未决 | `grilling` → `to-spec` Amendment，再重看受影响的技术方案 / tickets |
| 已确认需求的规范含义变了 | `to-spec` Amendment，再同步受影响的技术方案 / tickets |
| SPEC 含义不变，只改技术方案或设计决策 | `solution-design` Amendment，再由 `to-tickets` 协调执行图 |
| SPEC 与方案不变，只改拆票或依赖 | `to-tickets`，只更新执行图 |
| 只有执行状态或验证证据变了 | 执行方更新记录（有图时为 `graph-workflow`），不动 SPEC 或方案 |
| 实现时发现需求或方案不成立 | `graph-workflow` 先暂停，交回上游；修订并协调图后再恢复 |

检查已有契约和证据在新依据下是否仍成立。需求变化通过协调或修正交付处理，保留历史 done。`reopen` 只用于原依据未变、但原交付未满足要求的缺陷。须先由 Runtime 停止执行中的写入方，再修订上游和协调图；停写顺序见[任务契约 · Amendment](./skills/shared/task-contract.md#amendment-stop-write-protocol)。

## 三类角色

| 类别 | 要点 |
| --- | --- |
| 用户工作流入口 | 须由你启动，或已授权工作流按交接继续；模型不能只靠任务匹配自行启动。如 `grilling`、`to-spec`、`to-tickets`、`graph-workflow`、`project-setup` |
| 受调度角色 | 可由用户启动，也可由已授权方经 Runtime 派发。如 `ticket-implement`、`verify`、`code-review`、`simplify` |
| 可主动选择的辅助 | 在当前任务与权限内按需选用。如 `debug`；`tdd`、`domain-modeling` 作方法组合 |

`how`、`why`、`show-me`、`visual-pr` 仅限用户显式调用，其他 Skill 不得代为拉起。调用不扩大授权，不因此获得提交、推送、发布或实现权限。细则见 [职责归属与调用关系](./skills/shared/ownership-and-invocation.md)。

### 项目准备（可选）

[`project-setup`](./skills/project-setup/SKILL.md) 对照项目现状落实工程原则，维护 Profile（默认 `.agents/engineering-profile.md`）；Profile 记录知识与验证方法的位置，不保存当前任务契约或运行结果。

[`verification-setup`](./skills/verification-setup/SKILL.md) 可只盘点现有验证方法及其限制，也可复用仓库工具创建或更新本地方法并试跑。已有方法够用时直接用，不必先配置 Profile。

## 附录：谁负责什么

每个 Skill 只在自己的职责内做决定、写产物；不得改动上游已确认的契约，也不得代做下游的工作。

| Skill | 负责 | 不负责 |
| --- | --- | --- |
| `grilling` | 追问到关键选择确定，记录用户确认的决定 | 替用户做需求选择；写 SPEC、技术方案或实现 |
| `to-spec` | 把已确认需求写成 `SPEC.md`（R / AC），按需维护 ACCEPTANCE | 设计内部实现；补写未决的业务决定 |
| `solution-design` | 根据 SPEC、现有代码和约束确定技术方案，记录设计决策 | 改 SPEC 含义；拆票；局部实现细节 |
| `to-tickets` | 用脚本创建或协调 `tickets/*.md`，确定拆分与真实依赖 | 引入新需求或设计；领取和执行 ticket |
| `graph-workflow` | 选 ticket、派发原生 worker、核对证据、写入 `.loop/` 运行状态和交付记录 | 改产品代码；改写 ticket 契约；管理 Runtime 会话 |
| `ticket-implement` | 在约定写范围内实现一张 ticket，补必要测试，报告实际自检 | 改 SPEC、技术方案或 tickets；调度其他任务 |
| `quick-implement` | 无执行图时实现单一范围，再派发 simplify、verify、code-review 收尾 | 建立或维护执行图；替代 graph-workflow |
| `verify` | 独立逐条判断 AC 证据，输出 PASS / FAIL / NOT VERIFIED | 修复问题；改执行状态；调度 Agent |

| 产物 | 写入方 |
| --- | --- |
| 需求决定（`decisions.md`） | 用户确认，`grilling` 记录 |
| `SPEC.md` | `to-spec` |
| 技术方案与设计决策 | `solution-design` |
| `tickets/*.md` | `to-tickets` |
| 运行状态与最终交付记录 | `graph-workflow` |
| 源代码与仓库测试 | 有图：`ticket-implement`；无图：`quick-implement` |
| 验证证据与逐 AC 结论 | `verify` |

更细的事实归属见 [职责归属与调用关系](./skills/shared/ownership-and-invocation.md#事实与产物归属)。交接的目标、范围、验收和边界见[任务契约](./skills/shared/task-contract.md)。

## 附录：共享契约

`skills/shared/` 给 Agent 加载，不是 skill。

| 文档 | 内容 |
| --- | --- |
| [Engineering Kernel](./skills/shared/engineering-kernel.md) | 跨 Skill 的不变量基线 |
| [任务契约](./skills/shared/task-contract.md) | 目标、范围、验收、决策边界、证据与 Amendment 停写 |
| [职责归属与调用关系](./skills/shared/ownership-and-invocation.md) | 事实权威来源、调用模型、三种写法、角色边界 |
| [流程选择](./skills/shared/workflow-policy.md) | 按风险选择流程 |
| [收尾角色](./skills/shared/closeout-roles.md) | simplify / verify / code-review 分工 |
| [长期知识回写](./skills/shared/knowledge-protocol.md) | 长期发现交给谁 |
| [Graph Workflow 与 Runtime](./docs/graph-workflow-runtime.md) | Manager、Runtime、状态脚本与图示 |

`check.py`、schema 和 `ticket_graph/` 支撑 ticket 图与运行状态。仓库维护规则见根目录 [README · 维护规则](../README.md#maintenance-rules维护规则)。

## 附录：全部 Skills

### 需求与设计

| Skill | 用途 |
| --- | --- |
| [`grilling`](./skills/grilling/SKILL.md) | 访谈收敛尚未决定的需求与选择 |
| [`wayfinding`](./skills/wayfinding/SKILL.md) | 跨会话理清依赖决策与探索路径 |
| [`to-spec`](./skills/to-spec/SKILL.md) | 把已确认需求写成规范性 SPEC |
| [`solution-design`](./skills/solution-design/SKILL.md) | 对照 SPEC 与代码库确定或修订技术方案和设计决策 |
| [`domain-modeling`](./skills/domain-modeling/SKILL.md) | 术语表与长期架构决策 |
| [`codebase-design`](./skills/codebase-design/SKILL.md) | 深模块、缝与依赖方向的共用词汇 |

### 拆票与实现

| Skill | 用途 |
| --- | --- |
| [`to-tickets`](./skills/to-tickets/SKILL.md) | 拆出可调度的交付 ticket 图 |
| [`graph-workflow`](./skills/graph-workflow/SKILL.md) | 推进 ticket 图（默认 serial，可显式 swarm） |
| [`quick-implement`](./skills/quick-implement/SKILL.md) | 无执行图时实现单一范围并收尾 |
| [`ticket-implement`](./skills/ticket-implement/SKILL.md) | 受调度：在约定写范围内实现单张 ticket |
| [`tdd`](./skills/tdd/SKILL.md) | 用红-绿-重构驱动单个行为 |

### 验证与审查

| Skill | 用途 |
| --- | --- |
| [`verify`](./skills/verify/SKILL.md) | 受调度：独立按 AC 判断 PASS / FAIL / NOT VERIFIED |
| [`code-review`](./skills/code-review/SKILL.md) | 受调度：审查缺陷、回归与不必要的复杂度 |
| [`simplify`](./skills/simplify/SKILL.md) | 受调度：审查或去掉与当前职责无关的复杂度 |
| [`debug`](./skills/debug/SKILL.md) | 复现与诊断疑难缺陷（修复需授权） |
| [`test-audit`](./skills/test-audit/SKILL.md) | 审计测试有效性与维护成本 |
| [`review-architecture`](./skills/review-architecture/SKILL.md) | 只读架构符合性审查与候选发现 |
| [`challenge`](./skills/challenge/SKILL.md) | 对已有方案做有边界的对抗式审查 |
| [`verification-setup`](./skills/verification-setup/SKILL.md) | 盘点、建立或更新本地验证方法 |

### 调研与项目

| Skill | 用途 |
| --- | --- |
| [`tech-research`](./skills/tech-research/SKILL.md) | 有证据支撑的技术调研与选型建议 |
| [`find-docs`](./skills/find-docs/SKILL.md) | 按版本查找官方文档 |
| [`project-setup`](./skills/project-setup/SKILL.md) | 探测并持久化工程 Profile |
| [`improve-agents-md`](./skills/improve-agents-md/SKILL.md) | 创建或优化多工具适用的 AGENTS.md |
| [`context-audit`](./skills/context-audit/SKILL.md) | 审查 Agent 上下文中的重复、冲突、过时与职责错位 |
| [`agent-tool`](./skills/agent-tool/SKILL.md) | Claude Code / Codex / Kimi / Pi / Grok 的统一 CLI 封装 |

### 仅显式调用

| Skill | 用途 |
| --- | --- |
| [`how`](./skills/how/SKILL.md) | 仅显式调用：解释当前代码如何运行 |
| [`why`](./skills/why/SKILL.md) | 仅显式调用：追查设计或限制的成因 |
| [`show-me`](./skills/show-me/SKILL.md) | 仅显式调用：根据理解难点选择够用的文本、表格、图示或 HTML |
| [`visual-pr`](./skills/visual-pr/SKILL.md) | 仅显式调用：起草带结构图的 PR 描述（只出文本，不改 PR） |

调研、审查与维护类可单独用，不必先跑 `project-setup` 或先建 SPEC / tickets。文档转换与中文润色在 `Documents/`，会话交接与学习辅助在 `Work/`。
