# Engineering Skills 调用关系

本文只回答“谁可以调用谁”。谁负责什么见[职责与边界](engineering-responsibilities.md)，什么时候选哪个入口见[使用指南](engineering-skills.md)。

## 调用原则

调用关系只说明三件事：谁可以发起调用，谁作为 worker 被派发，调用后各自的职责边界在哪里。它不描述 Runtime 如何创建或等待 worker，不定义生命周期，也不是新的 Skill metadata、注册表或依赖图。

- 调用方负责选择下游、交代输入和范围，并消费下游的原始结果。
- 被调用方只在自己的职责内工作；超出职责的问题交回调用方，而不是自行扩大范围。
- 调用不扩大授权。交接不授予提交、推送、分支操作或外部发布权限，规划交接也不授予实现权限。

## 调用模型

| 类别 | 隐式选择 | 显式调用 | 当前对齐的 Skills |
| --- | --- | --- | --- |
| Human Entry Point（用户工作流入口） | 不允许模型仅凭任务匹配自行启动 | 用户启动；已授权工作流可按明确交接继续下游入口，不必逐步要求用户重新输入名称，但不得因此扩展授权 | `grilling`、`to-spec`、`to-tickets`、`wayfinding`、`graph-workflow`、`project-setup`、`verification-setup`、`improve-agents-md` |
| Orchestrated Role（受调度角色） | 不允许自由选择 | 用户可直接调用；已授权的调用方可显式指定角色和范围，通过 Runtime 派发 | `ticket-implement`、`verify`、`code-review`、`simplify` |
| Model-discoverable Helper（模型可主动选择的辅助能力） | 允许在当前任务与权限内按需选择 | 也可由用户或调用方明确指定 | `debug`；`tdd` 和 `domain-modeling` 作为实现 / 领域方法按需组合 |

用户可以直接启动这三类 Skill，但仍须满足该 Skill 的输入与授权边界。禁用隐式调用不等于仅限人类调用。

仅用户手动触发的 Skill（当前明确包括 `how`、`why`）不得由其他 Skill 通过 Skill tool 代为拉起；需要时告诉用户自己运行。

### 与宿主 policy 的对应

[OpenAI 的调用策略说明](https://learn.chatgpt.com/docs/build-skills#optional-metadata)规定 `agents/openai.yaml` 中 `policy.allow_implicit_invocation: false` 禁用隐式调用，保留显式调用；它不表示 human-only，也不授予 worker 调度权限。上表的入口和角色显式设为 `false`；`debug` 显式为 `true`；`tdd`、`domain-modeling` 未设置 policy，使用该宿主的默认隐式策略。其他 Skills 保持各自现有策略，上表不是全仓强制重分类。

### 三种写法

- **方法引用**：如 ticket-implement 中加载 `tdd`，表示在当前实现职责内采用该方法，不另启交付流程，也不因此创建 worker。写成 `Call the Skill tool with "tdd"`，不要写成散文式的 `run /tdd`。
- **角色派发**：如 `graph-workflow → native worker → ticket-implement / verify`，由调用方明确指定 Skill、输入、范围、候选与证据要求，worker 加载相应指令；独立角色不能用同一执行者自检代替。派发时同样点名 Skill（用 Skill tool 或把已解析的 `SKILL.md` 交给 worker），不要只丢一个斜杠命令指望宿主猜。
- **Skill 调用**：让宿主加载明确指定的 Skill，或按其 policy 隐式发现。操作步骤写成 `Call the Skill tool with "grilling"`，一次一个名字，要两个就写两次。导航表、README 和只给人看的路由说明可以用 Skill 名作标签，那不算调用。文档提到 Skill 名不证明调用成功；其他 Runtime 是否识别 metadata、worker 是否加载了指令，须按实际能力验证，不从 YAML 推断。

## 主流程

grilling → to-spec → solution-design → to-tickets → graph-workflow → ticket-implement → verify

各环节按需组合，不是必经阶段。前五个是 Human Entry Point，上一环完成后，已授权的工作流按交接继续下一环；`ticket-implement` 和 `verify` 是由 `graph-workflow` 派发的 Orchestrated Role。`to-spec` 在确认 SPEC 后独立判断共享设计和交付拆分：必要时显式调用 `solution-design`，消费返回结果后统一推荐 Quick 或 Tickets。`solution-design` 由 `to-spec` 调用时返回调用方，不接管下游路由；用户直接调用时可在授权内推荐并交接。`quick-implement` 执行调用者选定的范围，不因规模或独立单元数量自动切换到 Graph Workflow，仍自行派发 simplify、verify 和 code-review 收尾。

交接规则：

- 每个 Skill 完成职责后，由调用方按当前依据继续下游，普通交接无需用户再次输入 Skill 名称；继续时用 Skill tool 调用，不写散文式的 `run /xxx`。
- 只要求规划时，在所需规划产物完成后停止；仅要求 SPEC 和必要设计不授权创建 tickets；已授权实现时，继续相应实现路径。`to-tickets → graph-workflow` 仍以用户已授权实现为前提。
- 新的需求决策交回用户；技术方案的取舍按 solution-design 的 Design Review Gate 处理；普通实现细节由 Agent 判断。
- `debug` 按需调用 `simplify` 时，仍需明确范围和修改授权。

## 调用规则

### graph-workflow

- graph-workflow 不在自己的上下文里内联执行这些 Skill，而是为每个角色派发原生 worker：`ticket-implement` 负责实现与修正，`simplify`、`verify`、`code-review` 负责最终收尾。三个收尾角色的分工见[收尾角色](closeout-roles.md)。
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
