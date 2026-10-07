# Engineering Skills

本目录提供软件项目的调研、开发、审查和维护能力，不绑定语言、框架或 Agent Runtime。本文用于选择入口和理解组合关系，具体执行规则由各 Skill 维护，跨 Skill 的事实与产物归属见[职责与边界](engineering-responsibilities.md)，跨 Skill 不变量基线见 [Engineering Kernel](engineering-kernel.md)。

## 设计原则

- 通用优先，项目实现细节、领域术语、ADR、Git 规则和测试约定由目标仓库维护。
- 每个 Skill 有明确的判断目标和停止点，可以围绕不同目标检查同一份代码或测试。
- 通过组合复用规则，不复制另一 Skill 的执行细节。
- 能由确定性机制可靠保证的约束，不交给 Agent 记忆和判断。
- 以确认需求、代码、实际观察和独立报告为依据，不把自报或命令成功当成完成证明。
- Runtime 管理会话与 worker 生命周期，Engineering Skills 管理需求、设计、执行图和交付判断。

## 选择入口

分别判断需求与技术路径的不确定性、对调用方和共享资源的影响范围，以及取得充分证据的验证难度。不按代码行数或“小、中、大”标签决定流程。完整规则见[按风险选择流程](../engineering/shared/workflow-policy.md)。

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | [grilling](../engineering/grilling/SKILL.md) |
| 技术路径存在需要跨会话调查的迷雾 | [wayfinding](../engineering/wayfinding/SKILL.md) |
| 需求已收敛且需要持久化规范 | [to-spec](../engineering/to-spec/SKILL.md) |
| 多个模块、调用方或实现任务需要共享设计约束 | [high-level-design](../engineering/high-level-design/SKILL.md)，单一执行范围也可能需要 HLD。 |
| 需要多个执行单元、依赖或统一调度 | [to-tickets](../engineering/to-tickets/SKILL.md) → [loop](../engineering/loop/SKILL.md) |
| 单一范围、无需执行图 | [quick-implement](../engineering/quick-implement/SKILL.md)，简单局部修改可以直接处理。 |
| 当前验收缺少充分、可重复的验证方法 | 先查找已有方法，再按需使用 [verification-setup](../engineering/verification-setup/SKILL.md)。 |

各入口按需组合，不构成必经阶段。实现前以已确认的 AC 明确观察方法、前置条件和覆盖限制，会话中的简要说明或已有任务记录即可。安全且不受影响的工作可以继续，证据缺口不能写成通过。契约的来源、继承和授权规则见[任务契约](../engineering/shared/task-contract.md)。

各 Skill 完成职责后，由调用方按当前依据继续下游，普通交接无需用户再次输入 Skill 名称。只要求规划时，在所需规划产物完成后停止；已授权实现时，继续相应实现路径。新的需求决策交回用户，共享设计按 HLD 的 Design Review Gate 处理，普通实现细节由 Agent 判断。交接不授予提交、推送或分支操作权限。

调用分为用户工作流入口（Human Entry Point）、受调度角色（Orchestrated Role）和模型可主动选择的辅助能力（Model-discoverable Helper）。禁用隐式调用不等于仅限人类调用；已有授权下的显式交接与 worker 派发仍可继续。分类、当前 policy 与方法引用的区别见[调用契约](engineering-responsibilities.md#调用契约invocation-contract)。

## 项目准备

[project-setup](../engineering/project-setup/SKILL.md) 把工程原则连接到项目事实，维护稳定约束和按需读取入口。用户级原则可以包含 Ubiquitous Language、Tracer Bullet / Vertical Slice、Deep Modules / Information Hiding、Evidence-Based Completion 和 Minimum Necessary Complexity，项目指令仍应能独立使用。

Profile 默认保存为 `.agents/engineering-profile.md`，`AGENTS.md` 保留链接和读取条件。Profile 定位项目知识与验证方法，不保存当前任务契约或运行结果，未知字段、已确认设置和旧配置迁移按[Profile 约定](../engineering/project-setup/references/profile.md)处理。缺少 Profile 或字段为 `auto` 时继续发现，显式入口失效或冲突须报告。

[verification-setup](../engineering/verification-setup/SKILL.md) 复用仓库工具，创建或刷新项目本地验证方法并实际试运行，[使用示例](../engineering/verification-setup/references/usage.md)说明首次建立、多端入口和增量维护。已有方法足够时直接使用，无需先配置 Profile 或生成验证 Skill。

## 实现、测试与验收的组织

| 能力 | 主要责任 |
| --- | --- |
| [implement](../engineering/implement/SKILL.md) | 实现当前行为、补必要测试与局部简化，报告实际自检结果和缺口。 |
| [tdd](../engineering/tdd/SKILL.md) | 在实现中采用 Red → Green → Refactor 小步循环。 |
| [verify](../engineering/verify/SKILL.md) | 独立逐条判断 AC 与证据，输出 PASS / FAIL / NOT VERIFIED。 |
| [code-review](../engineering/code-review/SKILL.md) | 检查具体缺陷、回归风险和无必要复杂度。 |
| [test-audit](../engineering/test-audit/SKILL.md) | 按需系统审计指定测试的有效性、独有保护和维护成本。 |
| [loop](../engineering/loop/SKILL.md) | 派发 ticket、处理反馈、维护状态并判断最终交付。 |

项目验证方法提供执行能力，需求定义预期行为，实现者和验证者选择足够的检查。验证方法试运行成功、本地测试通过和任务验收通过分别有不同的证据要求，独立验收的理由见 [Verify 证据说明](../engineering/verify/references/evidence.md)。GUI 行为、视觉符合性和交互体验须分别有对应证据。

`verify` 自己判断当前 AC 的证据可信度，`test-audit` 不替代这项责任，也不自动成为交付门。缺失的仓库测试交给实现方，失效的验证方法交给 verification-setup，环境或权限存在缺口时，说明解除条件。修复后即使产品代码未变，也要重新判断受影响的证据。

单一范围进入 `quick-implement` 时，保留其专用 simplify Review、独立 verify 和 code-review 收尾要求，简化候选只有在用户明确授权后才修改。进入 Loop 后，每张 ticket 由原生 worker 实现和本地检查，ticket done 放行依赖，最终交付仍需专用 simplify、独立 verify / code-review 和有效快照。首次收尾覆盖全量改动；correction 默认仅定向重验受影响 AC、原 regression 并执行项目 mandatory gates，独立 targeted review 检查累积修正，复核其他 AC 证据仍有效。实际影响扩大才升级 broad review，具体规则见[最终验收](../engineering/loop/references/delivery-review.md)。状态命令、部署要求及 Runtime 边界见 [Loop 说明](loop-runtime.md)。

## 产物入口

简单任务可以把已确认契约留在会话中，按需持久化的产物如下，写入责任和下游使用规则统一见[事实与产物归属](engineering-responsibilities.md#事实与产物归属)。

| 产物 | 入口 |
| --- | --- |
| `MAP.md` 与探索决策 | [wayfinding](../engineering/wayfinding/SKILL.md) |
| 访谈 `decisions.md`、术语与 ADR | [grilling](../engineering/grilling/SKILL.md) 组合 [domain-modeling](../engineering/domain-modeling/SKILL.md) |
| `SPEC.md` | [to-spec](../engineering/to-spec/SKILL.md) |
| 独立版本、跨 ticket 场景或复杂协议所需的 `ACCEPTANCE.md` | [验收模板](../engineering/to-spec/references/acceptance-template.md)，场景引用 SPEC R / AC。 |
| 共享技术设计 `HLD.md` | [high-level-design](../engineering/high-level-design/SKILL.md) |
| `tickets/*.json` 契约与依赖 | [to-tickets](../engineering/to-tickets/SKILL.md) |
| attempt、已接受证据与最终交付记录 | [loop](../engineering/loop/SKILL.md) |

领域术语默认模板见 [Glossary 格式](../engineering/domain-modeling/GLOSSARY-FORMAT.md)；既有 `CONTEXT.md`、`DOMAIN.md`、`TERMS.md` 等仍可作为 authority，不强制迁移。项目背景、领域词汇和架构决策分别使用各自来源。

## 需求和设计变更

开发中的变化不要求从头重跑整个流程。先判断由哪个 Skill 维护相应依据，再从该点增量修改，只同步受影响的下游。

| 变化 | 负责入口 | 后续 |
| --- | --- | --- |
| 产品选择、外部行为、范围、权限、兼容策略或验收仍有开放决定 | `grilling` → `to-spec` Amendment | 重新判断受影响的 HLD / tickets。 |
| 已确认需求发生规范性变化 | `to-spec` Amendment | 同步受影响的 HLD / tickets。 |
| SPEC 含义不变，只改变共享技术设计 | `high-level-design` Amendment | 由 `to-tickets` 协调受影响的执行图。 |
| SPEC / HLD 不变，只改变拆票或依赖 | `to-tickets` | 只更新执行图。 |
| 仅有执行状态或验证证据变化 | 执行方（有图时为 `loop`） | 只更新执行记录，不修改 SPEC / HLD。 |
| 实现发现需求或 HLD 无法成立 | `loop` 先暂停执行，再交还对应上游 Skill | 完成修订并协调执行图后恢复。 |

只同步受影响的下游，并核对保留的契约和证据在新依据下仍然适用。需求变化通过协调或修正交付处理，保留历史 done。`reopen` 仅用于原依据未变而原交付未满足的缺陷。执行中的写入方须先由 Runtime 停止，再修订上游和协调图。

## 独立调研、审查与维护

这些入口可以独立使用，不新增工程流程阶段，也不要求先运行 `project-setup` 或建立 SPEC / tickets。

| 当前目标 | 入口与职责 |
| --- | --- |
| 创建或维护项目验证方法、执行步骤和证据说明 | 使用 [verification-setup](../engineering/verification-setup/SKILL.md) 复用已有工具，生成或刷新本地 Skill，并记录实际试运行覆盖。 |
| 查询库、SDK 或服务在项目适用版本下的用法 | [find-docs](../engineering/find-docs/SKILL.md) |
| 比较技术方案，形成选型或探索依据 | [tech-research](../engineering/tech-research/SKILL.md) |
| 用户手动调用，理解当前代码、数据或控制流如何运行 | 使用 [how](../engineering/how/SKILL.md) 解释当前事实，不判断目标设计。 |
| 用户手动调用，追查当前设计、限制或兼容规则为何形成 | 使用 [why](../engineering/why/SKILL.md)，基于历史证据区分事实、推断和未知。 |
| 检验已有技术判断是否站得住 | 使用 [challenge](../engineering/challenge/SKILL.md)，未决需求访谈仍由 `grilling` 负责。默认使用单 reviewer，高影响且关键判断仍证据不足时，可按需升级为独立多 reviewer。 |
| 审查代码变化、既有架构或无必要的复杂度 | 分别使用 `code-review`、`review-architecture`、`simplify` 的审查模式，`code-review` 对支撑安全性的非显然 invariant 做证据检查。默认使用单 reviewer，高影响且判断仍显著不确定时，可按需升级为独立多 reviewer。 |
| 专项检查测试有效性、重复保护或维护成本 | 使用 [test-audit](../engineering/test-audit/SKILL.md)，默认只读，明确要求清理时才修改，不增加固定验收关卡。 |
| 主动寻找架构改进候选 | 使用 `review-architecture` 的候选发现规则，仅在用户明确要求时扫描改进机会。 |
| 明确要求多维项目审计 | 使用 [fuck-my-shit-mountain](../engineering/fuck-my-shit-mountain/SKILL.md)，保留显式调用策略，由它维护覆盖与报告要求，判断标准复用已有审查技能。 |
| 创建或审校项目 Agent 指令 | 使用 [improve-agents-md](../engineering/improve-agents-md/SKILL.md)，`Engineering Skills Profile` 仍由 `project-setup` 维护。 |

文档转换、中文润色、术语审校与文档同步位于 `documents/`，会话交接、上下文审查及外部 Agent CLI 封装位于 `global/`，按技能负责的问题分类，不以是否输出 Markdown 分类。

会话级系统性问题先按 [Retro 实验规范](../.agents/skills/verify-engineering/references/retro-evaluation.md)收集真实证据并路由到现有 owner，不新增正式 Skill 或默认交付阶段。

## 图示与仓库维护

[![Engineering Skills 工作流](diagrams/engineering-workflow.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/diagrams/engineering-workflow.html)

[![本地 Ticket 生命周期](diagrams/ticket-lifecycle.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/diagrams/ticket-lifecycle.html)

维护 Skill 时按需读取[职责与边界](engineering-responsibilities.md)，上游适配规范也集中在那里。本仓库的检查与行为评估入口是 [verify-engineering](../.agents/skills/verify-engineering/SKILL.md)，静态检查和状态脚本测试只能支持各自覆盖范围的结论。
