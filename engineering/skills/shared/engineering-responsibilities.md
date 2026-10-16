# Engineering Skills 职责与边界

本文只回答“谁负责什么”：每个 Skill 能做哪些决定、写哪些产物、哪些事实以谁为准。谁可以调用谁见[调用关系](engineering-invocation.md)，什么时候选哪个入口见[使用指南](engineering-skills.md)。

## 核心原则

> A Skill owns decisions and artifacts within its responsibility. A Skill must respect upstream contracts and downstream boundaries.

每个 Skill 只在自己的职责内做决定、写产物；上游已确认的契约不能改，下游的工作不能代做。遇到超出职责的问题，交回调用方或负责的 Skill。

Skill 负责需求、设计、执行图和交付判断，Runtime 负责会话和 worker 的生命周期。各角色保留已确认需求、独立验收和状态约束，不复制另一角色的执行协议。

## 职责地图

| Skill | 负责 | 不负责 |
| --- | --- | --- |
| `grilling` | 追问到关键选择确定，记录用户确认的决定 | 替用户做需求选择；写 SPEC、技术方案或实现 |
| `to-spec` | 把已确认需求写成 `SPEC.md`（R / AC），按需维护 ACCEPTANCE | 设计内部实现；补写未决的业务决定 |
| `solution-design` | 根据 SPEC、现有代码和约束确定技术方案，记录设计决策 | 改 SPEC 含义；拆票；局部实现细节 |
| `to-tickets` | 用脚本创建或协调 `tickets/*.md`，确定拆分与真实依赖 | 引入新需求或设计；领取和执行 ticket |
| `graph-workflow` | 选 ticket、派发原生 worker、核对证据、用状态命令写入 `.loop/` 运行状态和交付记录 | 改产品代码；改写 ticket 契约；管理 Runtime 会话 |
| `ticket-implement` | 在约定写范围内实现一张 ticket，补必要测试，报告实际自检 | 改 SPEC、技术方案或 tickets；调度其他任务 |
| `quick-implement` | 无执行图时由主 Agent 实现单一范围，再派发 simplify、verify、code-review 收尾 | 建立或维护执行图；替代 graph-workflow |
| `verify` | 独立逐条判断 AC 证据，输出 PASS / FAIL / NOT VERIFIED | 修复问题；改执行状态；调度 Agent |

## 产物归属速查

下表只列主流程产物的写入方，权威来源和下游使用规则见[事实与产物归属](#事实与产物归属)。

| 产物 | 写入方 |
| --- | --- |
| 需求决定（`decisions.md`） | 用户确认，`grilling` 记录 |
| `SPEC.md` | `to-spec` |
| 技术方案与设计决策 | `solution-design` |
| `tickets/*.md` 契约与依赖 | `to-tickets`（create / reconcile 命令） |
| 运行状态（lifecycle、attempt、证据与阻塞）、`.loop/state.json` 与最终交付记录 | `graph-workflow`（`update-status` 命令） |
| 源代码与仓库测试 | 有图时为 `ticket-implement` worker，无图时为 `quick-implement` |
| 验证证据与逐 AC 结论 | `verify`（只写调用方允许的隔离资源） |

## 事实与产物归属

每项事实只维护一个当前权威来源。引用、派生的交付条件和历史快照可以有多份，但须能追溯来源及版本，不能自行改变原意。下表分别列出规范、持久化工程状态、原始观察和 Runtime 执行状态的维护责任。

| 事实 | 权威来源 | 写入责任 | 下游使用方式 |
| --- | --- | --- | --- |
| 需求、目标、任务范围、SPEC AC | 简单任务使用经确认的会话内容，保存为文档后，以 SPEC 中的工程需求快照为准 | 用户确认需求选择，由 `to-spec` 维护快照 | 技术方案、tickets、实现与验收引用当前快照，新输入改变快照时先修订 SPEC。 |
| 独立维护版本的验收场景与证据规则 | 按需建立的 ACCEPTANCE | `to-spec` | 场景引用 SPEC R / AC，不再维护另一份同名 AC 定义，与 SPEC 有冲突时，停止受影响的工作并交回负责方。 |
| 交付的技术方案与设计决策 | 以 `solution-design` 记录的技术方案为准，长期项目决策由已有架构文档 / ADR 维护 | 技术方案由 `solution-design` 维护，长期记录由项目约定的负责方和 `domain-modeling` 维护 | 引用 D ID 或项目来源，技术方案不自行取代长期约束，也不反向修改需求。 |
| 交付拆分、依赖、本地 AC 与约束 | `tickets/*.md` 的正文（标题、Delivery、Constraints、Delivery Acceptance）与 frontmatter 引用/依赖；执行不修改这些契约 | `to-tickets` 通过 create / reconcile 命令 | 通过 `covers` 与 D 引用追溯上游，本地 AC 细化本次交付，其 ID 与 SPEC AC 分属不同命名空间。 |
| ticket 生命周期、当前执行尝试（attempt）、已接受证据及执行阻塞 | 任务目录 `.loop/state.json`（不进入 Git） | `graph-workflow` 通过状态命令 | frontier 返回的 ready / blocked 状态由计算得出，不另建持久化进度表，worker 只返回原始结果；状态丢失时停止执行，需用户明确要求才重新初始化。 |
| 最终交付候选与状态 | `.loop/delivery.json` | `graph-workflow` 通过 delivery 命令 | 查询当前快照，并将原始报告保留在 `.loop/`，不以摘要替换报告。 |
| 项目稳定工程知识与导航 | 使用已有项目指令、术语表、领域模型和架构资料，通过 Profile 定位来源 | 项目资料由各自的维护者负责，术语、已有领域模型和 ADR 由 `domain-modeling` 维护，`project-setup` 维护 Profile | 按需引用，不把当前任务、运行结果或授权复制进 Profile。任务中的长期发现按[长期知识回写](knowledge-protocol.md)交给负责方。 |
| 可执行验证方法与能力范围 | 现有项目脚本 / CI / 本地验证 Skill | 项目工具由其维护者负责，`verification-setup` 维护方法与导航摘要 | Profile 只提供链接和摘要，方法说明不成为需求来源，冒烟检查记录也不作为当前任务已通过验收的依据。 |
| 当前候选的实际观察与审查结论 | 原执行者的命令记录、产物、verify / review 原文 | 实现者、验证者与审查者分别记录，由调用方判断适用性 | 状态脚本保存接受的事实，不解析报告、证明真实性或认证独立性。 |
| 原生 worker 是否运行、已停止或可恢复 | Runtime 原生状态 | Runtime | 工程记录可以引用执行句柄（handle），但不重建会话状态机，记录的执行状态不能证明写入方已停止。 |

交接摘要须标明来源与候选快照，恢复执行时与当前内容核对，不能因 ID 相同就认定语义未变。修订只同步受影响的派生产物和证据，保留仍有效的结果和历史 done 记录，规范变化通过协调执行图或安排修正交付处理，不能用历史记录证明当前任务已经完成。

## 行为实例的归属

Requirement 定义目标，AC 定义必须满足的行为；Scenario / Example 只是 AC 的具体实例，不产生新业务规则。已确认行为由 `to-spec` 表达，会改变业务行为的未决选择由 `grilling` 澄清；`tdd` 按行为风险选择测试，不按实例数量生成测试；`verify` 判断证据是否充分支持 AC，不以场景执行完毕代替验收。不新增 Scenario ID、状态或追踪矩阵，保留 Requirement → AC、Ticket → AC、Evidence → AC。实例的选择与停止规则见 [to-spec](../to-spec/SKILL.md#select-behaviour-examples-only-when-useful)。

## 边界示例

- **实现不做设计**：`ticket-implement` 发现技术方案不成立时，不自行改接口或设计决策，而是把冲突报告给调用方；`graph-workflow` 暂停受影响的工作，交回 `solution-design` 修订，再由 `to-tickets` 协调执行图。
- **工作流不改代码**：`graph-workflow` 需要修正时不直接改源代码，而是记录 correction attempt，派发 worker 加载 `ticket-implement` 处理。
- **验证不修复**：`verify` 发现缺陷只报告结论和证据，不改代码。调用方（`graph-workflow` 或 `quick-implement`）据此安排修正：有图时交给 `ticket-implement`，修正后重新验证受影响的证据。

## 相关契约

任务契约（目标、范围、验收、决策边界和证据）及其六类边界属于跨 Skill 交接的共同依据，统一维护在[任务契约](task-contract.md)；六类边界是 [Engineering Kernel](ENGINEERING_KERNEL.md) 不变量在工作流层的表述，本文不重复，也不改写。

## 职责审计

以下是维护者审计表，不要求每个 Skill 复制同一套章节或加载整张表，执行规则以各 Skill 为准。同一份测试或代码可用于不同判断，重复调查对象不等于职责重复。

| Skill | 范围及可修改产物 | 决策与停止点 | 结论依据 |
| --- | --- | --- | --- |
| project-setup | 稳定 Profile、AGENTS.md 入口及获准迁移 | 固化已确认配置，不建设验证工具与方法，也不决定验收 | 项目已有约定、源文件及用户选择 |
| verification-setup | 本地验证方法、必要辅助脚本、验证导航和摘要 | 盘点方法与限制；或创建/刷新并试运行方法，将依赖、CI 或产品变更另交实现 | 盘点：依据配置，标明未执行；建立：实际启动、驱动、观察、清理与保留证据 |
| improve-agents-md | 获准的项目指令修改 | 判断指令是否有依据，不自行重配 Profile | 仓库规则、真实命令与适用范围 |
| find-docs | 只读文档检索 | 回答指定产品/版本的问题，不开展完整选型 | 官方资料、明确版本、未执行限制 |
| tech-research | 有边界的技术调研 | 提供推荐和采用条件，不直接实施 | 官方/工程资料、现状约束、已执行实验与推断区分 |
| grilling | 访谈及 decisions.md，并组合记录术语/ADR | 重要需求选择由用户决定，grilling 不决定局部实现，也不重写下游 | 当前事实、用户确认、未决 frontier |
| wayfinding | MAP.md 与决策文件 | 解决跨会话依赖决策，不交付产品 | 可追溯答案、调查或实验，HITL 不由 Agent 代答 |
| to-spec | SPEC、按需 ACCEPTANCE | 维护确认需求和验收语义，不设计内部实现 | 需求 authority、确认决策、外部契约 |
| solution-design | 技术方案与设计决策（`SOLUTION.md`） | 决定技术方案，长期方向须经 review gate，不改需求或拆票 | SPEC、真实调用方、项目约束和代码事实 |
| to-tickets | 通过脚本创建/协调 tickets | 决定交付拆分与真实依赖，不引入新需求/设计 | 已确认 SPEC / 技术方案、覆盖及图校验 |
| quick-implement | 调用者选定范围的实现、自检与收尾 | 不使用执行图，既有独立收尾规则仍适用 | 当前契约、真实 diff、自检与独立报告 |
| ticket-implement | 当前 ticket 的代码、必要测试和局部简化 | 决定局部实现，将契约问题交回调用方 | 已确认行为、项目方法和实际本地检查 |
| graph-workflow | attempt、状态、报告及交付记录 | 选工作、调用角色、判断结果、流转状态，不管理 Runtime | 全部相关 AC 证据、原始报告、有效候选快照 |
| verify | 只读验收，以及获准隔离资源中的探针/证据 | 逐条报告 PASS / FAIL / NOT VERIFIED，不修复或改状态 | 需求独立预期、可观察执行、证据可信度与覆盖限制 |
| code-review | 只读改动审查 | 找具体缺陷、回归和无必要复杂度，不代替逐条验收 | 可达场景、调用/保护/测试与反证 |
| test-audit | 指定测试审计，以及获准的限定清理 | 给出保留/合并/重写/删除建议，不成为固定交付门 | 独立预期、真实执行、独有保护与维护成本 |
| tdd | 实现中的行为测试、代码及局部重构 | 按 Red → Green → Refactor 执行，不拥有最终验收或任务调度 | 已实际运行的有效 Red/Green、独立预期与回归 |
| codebase-design | 指定 Module / Interface / Seam 的局部设计判断 | 推荐局部形状，不扫描整体架构或替代领域语言 | 真实调用、信息隐藏、变化原因与删除试验 |
| domain-modeling | 领域词汇、已有领域模型与符合门槛的 ADR | 澄清模型，记录确认语义，不拥有访谈节奏或改需求 | 当前领域约定、契约、确认术语及真实取舍 |
| review-architecture | 只读架构审查，以及显式候选发现 | 判断现状与影响，不预先实施目标架构 | 项目约束、路径/所有权、适用官方指导与反证 |
| simplify | Review 或获准的限定修改 | 删除无当前职责的复杂度，不改变确认行为 | 实际使用方、持久化/外部契约与修改后验证 |
| debug | 复现、诊断，以及获准的最小修复 | 先建立问题反馈，不扩大到架构重做 | 已运行的症状复现、可证伪假设及原复现回归 |
| challenge | 只读地挑战已有判断 | 检验结论，不扩成需求访谈或完整重设计 | 已有约束、反证、影响及尚未确认事实 |
| how | 手动触发的当前代码解释 | 回答如何运行，不追溯历史或提出目标设计 | 当前真实生产路径与明确未观察范围 |
| why | 手动触发的历史依据调查 | 区分事实、推断、假设和未知，不因历史证明现状正确 | Git/ADR/issue 等历史与当前代码的关联 |
| show-me | 手动触发的可视化解释 | 按理解难点选最小表达形式，不默认输出 HTML | 当前话题与用户指定的格式 |
| visual-pr | 手动触发的 PR 描述起草 | 只读，只在对话里给出描述；不提交、不建或改 PR | 完整 diff、PR 元数据与用户指向的 ticket/spec |
| fuck-my-shit-mountain | 显式项目审计、综合报告 | 负责选定维度覆盖，不自动修复或启动交付链 | 各维度证据、可达影响、反证及覆盖限制 |

## 已收敛的职责

- Profile 字段语义、读取和迁移集中在 project-setup 的[引用说明](../project-setup/references/profile.md)，使用方读取相关设置，不绑定 AGENTS.md 内嵌格式，并保留旧持久化配置直到获准迁移。
- verification-setup 盘点并维护方法和能力摘要，verify 只为当前 AC 查找方法并判断证据是否充分。没有另一套验证命令配置或强制工具选择。
- verify 保留当前证据可信度检查，test-audit 保留系统测试价值审计，code-review 保留改动风险判断，不让任何一个报告替代另一个角色的验收责任。
- ticket-implement 已负责当前变化造成的必要简化，simplify 检查仍存在且有证据的问题。Graph Workflow 保留已有最终 simplify 角色契约，不新增逐 ticket 审计。
- Graph Workflow 首次交付执行全量 simplify、独立逐 AC verify 和 broad code-review；correction 默认定向重验和审查，同时执行 mandatory gates、确认其余 AC 证据仍有效。实际影响扩大时升级 broad review，规则只维护在[最终验收](../graph-workflow/references/delivery-review.md)，不新增状态字段。
- Graph Workflow 删除固定无活动阈值、soft-ping 协议、活动时间及性能台账，不再要求固定 context 文件对，但保留原生 worker 执行、独立最终角色、证据失效重验和停止旧写入方的要求。
- codebase-design 的分析术语限定在设计讨论中，不要求项目把 service/API 等既有名称改成通用词汇。
- 其他现有入口有不同的判断目标和停止点，本轮保留，不因检查同一份代码就合并。

领域语言默认模板使用 [GLOSSARY-FORMAT.md](../domain-modeling/GLOSSARY-FORMAT.md)，保留项目既有 CONTEXT / DOMAIN / TERMS 等 authority。`project_context`、`domain_glossary` 和 ADR 分别定位项目背景、领域词汇与架构决策。

## 文档归属

本文（谁负责什么）、[长期知识回写](knowledge-protocol.md)（长期发现交给谁）、[调用关系](engineering-invocation.md)（谁可以调用谁）和[使用指南](engineering-skills.md)（什么时候选哪个入口）放在 `engineering/skills/shared/`，治理规则见[维护规范](maintenance.md)，仓库入口是根目录 README。插件安装和发版写在仓库根的 INSTALL.md、RELEASING.md，Graph Workflow / Runtime 关系写在 `engineering/docs/`，`scripts/` 放仓库检查脚本；具体执行规则、格式与示例由所属 Skill 及其参考资料维护。图示的 JSON 源文件与 SVG 一起保存在 `engineering/docs/diagrams/`。变更时更新受影响的入口，不另建重复协议。
