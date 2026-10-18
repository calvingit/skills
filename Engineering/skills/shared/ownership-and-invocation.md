# 职责归属与调用关系

本文供 Agent 执行时加载，说明「谁负责什么事实与产物」和「谁可以调用谁」。面向人的选用指南和 Skills 一览放在插件 README 中；执行规则以本文和各 Skill 为准，不依赖 README。

什么时候按风险选流程见 [workflow-policy](workflow-policy.md)；跨 Skill 交接的目标、范围、验收见 [task-contract](task-contract.md)；收尾角色分工见 [closeout-roles](closeout-roles.md)。

## 核心原则

> A Skill owns decisions and artifacts within its responsibility. A Skill must respect upstream contracts and downstream boundaries.

每个 Skill 只在自己的职责内做决定、写产物；上游已确认的契约不能改，下游的工作不能代做。遇到超出职责的问题，交回调用方或负责的 Skill。

Skill 负责需求、设计、执行图和交付判断，Runtime 负责会话和 worker 的生命周期。各角色保留已确认需求、独立验收和状态约束，不复制另一角色的执行协议。

## 事实与产物归属

每项事实只维护一个当前权威来源。引用、派生的交付条件和历史快照可以有多份，但须能追溯来源及版本，不能自行改变原意。

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

主流程产物写入方速查：`decisions.md` 由用户确认、`grilling` 记录；`SPEC.md` 由 `to-spec`；技术方案由 `solution-design`；`tickets/*.md` 由 `to-tickets`；`.loop/state.json` 与交付记录由 `graph-workflow`；源代码与仓库测试有图时为 `ticket-implement`、无图时为 `quick-implement`；验证证据与逐 AC 结论由 `verify`（只写调用方允许的隔离资源）。

## 行为实例的归属

Requirement 定义目标，AC 定义必须满足的行为；Scenario / Example 只是 AC 的具体实例，不产生新业务规则。已确认行为由 `to-spec` 表达，会改变业务行为的未决选择由 `grilling` 澄清；`tdd` 按行为风险选择测试，不按实例数量生成测试；`verify` 判断证据是否充分支持 AC，不以场景执行完毕代替验收。不新增 Scenario ID、状态或追踪矩阵，保留 Requirement → AC、Ticket → AC、Evidence → AC。实例的选择与停止规则见 [to-spec](../to-spec/SKILL.md#select-behaviour-examples-only-when-useful)。

## 边界示例

- **实现不做设计**：`ticket-implement` 发现技术方案不成立时，把冲突交回调用方，不自行变更接口或设计决策；`graph-workflow` 暂停受影响的工作，交回 `solution-design` 修订，再由 `to-tickets` 协调执行图。
- **工作流不改代码**：`graph-workflow` 不直接改源代码。需要修正时记录 correction attempt，派发 worker 加载 `ticket-implement` 处理。
- **验证不修复**：`verify` 发现缺陷只报告结论和证据，不改代码。调用方（`graph-workflow` 或 `quick-implement`）据此安排修正：有图时交给 `ticket-implement`，修正后重新验证受影响的证据。

任务契约（目标、范围、验收、决策边界和证据）及其六类边界属于跨 Skill 交接的共同依据，统一维护在 [task-contract](task-contract.md)；六类边界是 [Engineering Kernel](ENGINEERING_KERNEL.md) 不变量在工作流层的表述，本文不重复，也不改写。

## 调用原则

调用关系只说明三件事：谁可以发起调用，谁作为 worker 被派发，调用后各自的职责边界在哪里。它不描述 Runtime 如何创建或等待 worker，不定义生命周期，也不是新的 Skill metadata、注册表或依赖图。

- 调用方负责选择下游、交代输入和范围，并消费下游的原始结果。
- 被调用方只在自己的职责内工作；遇到超出职责的问题，交回调用方处理。
- 调用不扩大授权。交接不授予提交、推送、分支操作或外部发布权限，规划交接也不授予实现权限。

## 调用模型

| 类别 | 隐式选择 | 显式调用 | 当前对齐的 Skills |
| --- | --- | --- | --- |
| Human Entry Point（用户工作流入口） | 不允许模型仅凭任务匹配自行启动 | 用户启动；已授权工作流可按明确交接继续下游入口，不必逐步要求用户重新输入名称，但不得因此扩展授权 | `grilling`、`to-spec`、`to-tickets`、`wayfinding`、`graph-workflow`、`project-setup`、`verification-setup`、`improve-agents-md` |
| Orchestrated Role（受调度角色） | 不允许自由选择 | 用户可直接调用；已授权的调用方可显式指定角色和范围，通过 Runtime 派发 | `ticket-implement`、`verify`、`code-review`、`simplify` |
| Model-discoverable Helper（模型可主动选择的辅助能力） | 允许在当前任务与权限内按需选择 | 也可由用户或调用方明确指定 | `debug`；`tdd` 和 `domain-modeling` 作为实现 / 领域方法按需组合 |

用户可以直接启动这三类 Skill，但仍须满足该 Skill 的输入与授权边界。禁用隐式调用不等于仅限人类调用。

仅用户手动触发的 Skill（当前明确包括 `how`、`why`、`show-me`、`visual-pr`）不得由其他 Skill 通过 Skill tool 代为拉起；需要时告诉用户自己运行。

宿主若支持 `policy.allow_implicit_invocation`（如 OpenAI `agents/openai.yaml`），入口和受调度角色显式为 `false`，`debug` 为 `true`；未设置的 Skill 使用该宿主默认策略。上表不是全仓强制重分类。

## 三种写法

- **方法引用**：如 ticket-implement 中加载 `tdd`，表示在当前实现职责内采用该方法，不另启交付流程，也不因此创建 worker。写成 `Call the Skill tool with "tdd"`，不要写成散文式的 `run /tdd`。
- **角色派发**：如 `graph-workflow → native worker → ticket-implement / verify`，由调用方明确指定 Skill、输入、范围、候选与证据要求，worker 加载相应指令；独立角色不能用同一执行者自检代替。派发时同样点名 Skill（用 Skill tool 或把已解析的 `SKILL.md` 交给 worker），不要只丢一个斜杠命令指望宿主猜。
- **Skill 调用**：让宿主加载明确指定的 Skill，或按其 policy 隐式发现。操作步骤写成 `Call the Skill tool with "grilling"`，一次一个名字，要两个就写两次。导航表、README 和只给人看的路由说明可以用 Skill 名作标签，那不算调用。文档提到 Skill 名不证明调用成功；其他 Runtime 是否识别 metadata、worker 是否加载了指令，须按实际能力验证，不从 YAML 推断。

## 主流程交接要点

grilling → to-spec → solution-design → to-tickets → graph-workflow → ticket-implement → verify

各环节按需组合，不是必经阶段。前五个是 Human Entry Point，上一环完成后，已授权的工作流按交接继续下一环；`ticket-implement` 和 `verify` 是由 `graph-workflow` 派发的 Orchestrated Role。`to-spec` 在确认 SPEC 后独立判断共享设计和交付拆分：必要时显式调用 `solution-design`，消费返回结果后统一推荐 Quick 或 Tickets。`solution-design` 由 `to-spec` 调用时返回调用方，不接管下游路由；用户直接调用时可在授权内推荐并交接。`quick-implement` 执行调用者选定的范围，不因规模或独立单元数量自动切换到 Graph Workflow，仍自行派发 simplify、verify 和 code-review 收尾。

- 每个 Skill 完成职责后，由调用方按当前依据继续下游，普通交接无需用户再次输入 Skill 名称；继续时用 Skill tool 调用，不写散文式的 `run /xxx`。
- 只要求规划时，在所需规划产物完成后停止；仅要求 SPEC 和必要设计不授权创建 tickets；已授权实现时，继续相应实现路径。`to-tickets → graph-workflow` 仍以用户已授权实现为前提。
- 新的需求决策交回用户；技术方案的取舍按 solution-design 的 Design Review Gate 处理；普通实现细节由 Agent 判断。
- `debug` 按需调用 `simplify` 时，仍需明确范围和修改授权。

## 调用规则

### graph-workflow

- graph-workflow 为每个角色派发原生 worker，不在自己的上下文里内联执行这些 Skill：`ticket-implement` 负责实现与修正，`simplify`、`verify`、`code-review` 负责最终收尾。三个收尾角色的分工见 [closeout-roles](closeout-roles.md)。
- 它自己只写 `.loop/` 运行状态（phase、attempt、证据）和交付记录，不修改 ticket 契约或源代码；需要修正时记录 correction attempt，再派发 `ticket-implement`。
- 收到 `verify` 或 `code-review` 的问题后，由它判断影响，重新派发修正和受影响的复验；需求或技术方案冲突交回对应上游 Skill。

### ticket-implement

- 可以在约定写范围内修改代码和测试，并按需组合 `tdd`、`codebase-design` 等方法。
- 不得修改 SPEC、ACCEPTANCE、技术方案、tickets 或 Git 历史，也不调度其他任务。
- 发现需求、设计或范围问题时报告给调用方，由调用方交回上游负责方，不自行解决。

### verify

- 可以检查代码、运行测试，并在调用方允许的隔离资源中建立探针、临时测试和证据文件。
- 不得修改交付的代码、仓库测试或验收条件，不自行修复问题，也不改 `.loop/state.json` 执行状态或调度 Agent。
- 发现的缺陷、契约冲突和能力缺口返回给调用方；修复后由调用方重新派发验证。
