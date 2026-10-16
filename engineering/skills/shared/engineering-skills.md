# Engineering Skills 使用指南

本目录提供软件项目的调研、开发、审查和维护能力，不绑定语言、框架或 Agent Runtime。本文只回答“什么时候选哪个入口”。谁负责什么见[职责与边界](engineering-responsibilities.md)，谁可以调用谁见[调用关系](engineering-invocation.md)，具体执行规则由各 Skill 维护。

## 按阶段选择

| 阶段 | 情况 | 使用 |
| --- | --- | --- |
| 需求 | 还有影响行为的选择没定 | [grilling](../grilling/SKILL.md)：把决定问清楚并记录 |
| 需求 | 需求已确认，需要持久化 | [to-spec](../to-spec/SKILL.md)：写 `SPEC.md` |
| 设计 | 多个模块或实现要共享技术约束 | [solution-design](../solution-design/SKILL.md)：输入 SPEC、现有代码和约束，确定技术方案和设计决策 |
| 执行 | 多个相关改动，有依赖或要统一调度 | [to-tickets](../to-tickets/SKILL.md) 拆票，再由 [graph-workflow](../graph-workflow/SKILL.md) 推进 |
| 执行 | 执行图中的单张 ticket | [ticket-implement](../ticket-implement/SKILL.md)，通常由 graph-workflow 派发 |
| 执行 | 范围单一、无需执行图 | [quick-implement](../quick-implement/SKILL.md) |
| 验证 | 需要独立证据判断 AC | [verify](../verify/SKILL.md) |

技术路径不清楚、需要跨会话调查时先用 [wayfinding](../wayfinding/SKILL.md)；验收缺少可用的验证方法时用 [verification-setup](../verification-setup/SKILL.md)。下面「选择入口」给出更完整的判断条件。

## 选择入口

分别判断需求与技术路径的不确定性、对调用方和共享资源的影响范围，以及取得充分证据的验证难度。不按代码行数或“小、中、大”标签决定流程。完整规则见[按风险选择流程](workflow-policy.md)。

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | [grilling](../grilling/SKILL.md) |
| 技术路径存在需要跨会话调查的迷雾 | [wayfinding](../wayfinding/SKILL.md) |
| 需求已收敛且需要持久化规范 | [to-spec](../to-spec/SKILL.md) |
| 多个模块、调用方或实现任务需要方案设计约束 | [solution-design](../solution-design/SKILL.md)，单一执行范围也可能需要技术方案。 |
| 需要多个执行单元、依赖或统一调度 | [to-tickets](../to-tickets/SKILL.md) → [graph-workflow](../graph-workflow/SKILL.md) |
| 单一范围、无需执行图 | [quick-implement](../quick-implement/SKILL.md)，默认推荐用于无需执行图的完整交付范围；用户也可明确选择它处理多个独立修复，契约和收尾标准不变。简单局部修改可以直接处理。 |
| 当前验收缺少充分、可重复的验证方法 | 先查找已有方法，再按需使用 [verification-setup](../verification-setup/SKILL.md)。 |

各入口按需组合，不构成必经阶段。上游调用方推荐路线，用户保留最终选择；`quick-implement` 不因多个执行单元或路线偏好自动转交 Graph Workflow。缺失需求或共享设计交回对应负责方，只暂停受影响操作；已有执行图和活跃写入者不得绕过，须先解决执行归属并遵守状态与停写保护。契约的来源、继承和授权规则见[任务契约](task-contract.md)。

入口之间如何交接、哪些 Skill 可以派发哪些角色，见[调用关系](engineering-invocation.md)。

## 项目准备

[project-setup](../project-setup/SKILL.md) 把工程原则连接到项目事实，维护稳定约束和按需读取入口。用户级原则可以包含 Ubiquitous Language、Tracer Bullet / Vertical Slice、Deep Modules / Information Hiding、Evidence-Based Completion 和 Minimum Necessary Complexity，项目指令仍应能独立使用。

Profile 默认保存为 `.agents/engineering-profile.md`，`AGENTS.md` 保留链接和读取条件。Profile 定位项目知识与验证方法，不保存当前任务契约或运行结果，未知字段、已确认设置和旧配置迁移按[Profile 约定](../project-setup/references/profile.md)处理。缺少 Profile 或字段为 `auto` 时继续发现，显式入口失效或冲突须报告。

[verification-setup](../verification-setup/SKILL.md) 有两种范围：只盘点现有验证方法及其限制，不创建也不运行；或复用仓库工具，创建或刷新项目本地验证方法并实际试运行。[使用示例](../verification-setup/references/usage.md)说明首次建立、多端入口和增量维护。已有方法足够时直接使用，无需先配置 Profile 或生成验证 Skill。

## 行为规格

需求已确认、只是表达有歧义时，在 [to-spec](../to-spec/SKILL.md#select-behaviour-examples-only-when-useful) 中按需补充 Example 或 Given / When / Then；行为本身还没定时先用 `grilling`。新增实例不要求独立 ACCEPTANCE、执行状态或更多测试，各方如何使用实例见[职责与边界](engineering-responsibilities.md#行为实例的归属)。

## 实现、测试与验收

| 情况 | 使用 |
| --- | --- |
| 实现执行图中的一张 ticket | [ticket-implement](../ticket-implement/SKILL.md)，通常由 graph-workflow 派发 |
| 实现中适合测试先行的单个行为 | [tdd](../tdd/SKILL.md)，Red → Green → Refactor |
| 需要独立判断 AC 是否满足 | [verify](../verify/SKILL.md) |
| 审查具体缺陷、回归风险和无必要复杂度 | [code-review](../code-review/SKILL.md) |
| 系统审计指定测试的有效性和维护成本 | [test-audit](../test-audit/SKILL.md)，按需使用，不是交付门 |
| 推进执行图、处理反馈并完成最终交付 | [graph-workflow](../graph-workflow/SKILL.md) |

验证方法试运行成功、本地测试通过和任务验收通过需要不同的证据，理由见 [Verify 证据说明](../verify/references/evidence.md)。缺少可重复的验证方法时用 verification-setup，缺少仓库测试时交给实现方。`quick-implement` 和 graph-workflow 的收尾都需要独立的 simplify、verify 和 code-review，分工见[收尾角色](closeout-roles.md)，correction 的复验范围见[最终验收](../graph-workflow/references/delivery-review.md)，状态命令和 Runtime 边界见 [Graph Workflow 说明](../../docs/graph-workflow-runtime.md)。

## 产物入口

简单任务可以把已确认契约留在会话中，按需持久化的产物如下，写入方和下游使用规则见[事实与产物归属](engineering-responsibilities.md#事实与产物归属)。

| 产物 | 入口 |
| --- | --- |
| `MAP.md` 与探索决策 | [wayfinding](../wayfinding/SKILL.md) |
| 访谈 `decisions.md`、术语与 ADR | [grilling](../grilling/SKILL.md) 组合 [domain-modeling](../domain-modeling/SKILL.md) |
| `SPEC.md` | [to-spec](../to-spec/SKILL.md) |
| 独立版本、跨 ticket 场景或复杂协议所需的 `ACCEPTANCE.md` | [验收模板](../to-spec/references/acceptance-template.md)，场景引用 SPEC R / AC。 |
| 技术方案与设计决策 | [solution-design](../solution-design/SKILL.md) |
| `tickets/*.md` 契约与依赖（Markdown 正文 + YAML frontmatter） | [to-tickets](../to-tickets/SKILL.md) |
| `.loop/state.json` 运行状态（phase、attempt、证据、阻塞）、attempt 报告与最终交付记录 | [graph-workflow](../graph-workflow/SKILL.md) |

领域术语默认模板见 [Glossary 格式](../domain-modeling/GLOSSARY-FORMAT.md)；既有 `CONTEXT.md`、`DOMAIN.md`、`TERMS.md` 等仍可作为 authority，不强制迁移。项目背景、领域词汇和架构决策分别使用各自来源。

## 需求和设计变更

开发中的变化不要求从头重跑整个流程。先判断由哪个 Skill 维护相应依据，再从该点增量修改，只同步受影响的下游。

| 变化 | 负责入口 | 后续 |
| --- | --- | --- |
| 产品选择、外部行为、范围、权限、兼容策略或验收仍有开放决定 | `grilling` → `to-spec` Amendment | 重新判断受影响的技术方案 / tickets。 |
| 已确认需求发生规范性变化 | `to-spec` Amendment | 同步受影响的技术方案 / tickets。 |
| SPEC 含义不变，只改变技术方案或设计决策 | `solution-design` Amendment | 由 `to-tickets` 协调受影响的执行图。 |
| SPEC 与技术方案不变，只改变拆票或依赖 | `to-tickets` | 只更新执行图。 |
| 仅有执行状态或验证证据变化 | 执行方（有图时为 `graph-workflow`） | 只更新执行记录，不修改 SPEC 或技术方案。 |
| 实现发现需求或技术方案无法成立 | `graph-workflow` 先暂停执行，再交还对应上游 Skill | 完成修订并协调执行图后恢复。 |

只同步受影响的下游，并核对保留的契约和证据在新依据下仍然适用。需求变化通过协调或修正交付处理，保留历史 done。`reopen` 仅用于原依据未变而原交付未满足的缺陷。执行中的写入方须先由 Runtime 停止，再修订上游和协调图。

## 独立调研、审查与维护

这些入口可以独立使用，不新增工程流程阶段，也不要求先运行 `project-setup` 或建立 SPEC / tickets。

| 当前目标 | 入口与职责 |
| --- | --- |
| 创建或维护项目验证方法、执行步骤和证据说明 | 使用 [verification-setup](../verification-setup/SKILL.md)。只盘点时报告方法与限制；建立或维护时生成或刷新本地 Skill，并记录实际试运行覆盖。 |
| 查询库、SDK 或服务在项目适用版本下的用法 | [find-docs](../find-docs/SKILL.md) |
| 比较技术方案，形成选型或探索依据 | [tech-research](../tech-research/SKILL.md) |
| 用户手动调用，理解当前代码、数据或控制流如何运行 | 使用 [how](../how/SKILL.md) 解释当前事实，不判断目标设计。 |
| 用户手动调用，追查当前设计、限制或兼容规则为何形成 | 使用 [why](../why/SKILL.md)，基于历史证据区分事实、推断和未知。 |
| 用户手动调用，换一种表达形式理解当前话题 | 使用 [show-me](../show-me/SKILL.md)，选最小够用的文本、表格、图示或 HTML。 |
| 用户手动调用，为一组改动起草 PR 描述 | 使用 [visual-pr](../visual-pr/SKILL.md)，在对话里给出描述，不创建或修改 PR。 |
| 检验已有技术判断是否站得住 | 使用 [challenge](../challenge/SKILL.md)，未决需求访谈仍由 `grilling` 负责。默认使用单 reviewer，高影响且关键判断仍证据不足时，可按需升级为独立多 reviewer。 |
| 审查代码变化、既有架构或无必要的复杂度 | 分别使用 `code-review`、`review-architecture`、`simplify` 的审查模式，`code-review` 对支撑安全性的非显然 invariant 做证据检查。默认使用单 reviewer，高影响且判断仍显著不确定时，可按需升级为独立多 reviewer。 |
| 专项检查测试有效性、重复保护或维护成本 | 使用 [test-audit](../test-audit/SKILL.md)，默认只读，明确要求清理时才修改，不增加固定验收关卡。 |
| 主动寻找架构改进候选 | 使用 `review-architecture` 的候选发现规则，仅在用户明确要求时扫描改进机会。 |
| 明确要求多维项目审计 | 使用 [fuck-my-shit-mountain](../fuck-my-shit-mountain/SKILL.md)，保留显式调用策略，由它维护覆盖与报告要求，判断标准复用已有审查技能。 |
| 创建或审校项目 Agent 指令 | 使用 [improve-agents-md](../improve-agents-md/SKILL.md)，`Engineering Skills Profile` 仍由 `project-setup` 维护。 |

文档转换、中文润色、术语审校与文档同步位于 `documents/`，会话交接与学习辅助位于 `work/`，上下文审查、外部 Agent CLI 封装和可视化解释（show-me）位于 `engineering/`，按技能负责的问题分类，不以是否输出 Markdown 分类。

## 图示

[![Engineering Skills 工作流](../../docs/diagrams/engineering-workflow.svg)](../../docs/diagrams/engineering-workflow.svg)

[![本地 Ticket 生命周期](../../docs/diagrams/ticket-lifecycle.svg)](../../docs/diagrams/ticket-lifecycle.svg)

维护本仓库时的约定见[维护规范](maintenance.md)；修订停写顺序见[任务契约 · Amendment](task-contract.md#amendment-stop-write-protocol)。
