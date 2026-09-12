# Engineering Skills

本目录提供通用工程 Coding 流程，不绑定语言、框架、项目目录或 Agent Runtime。它以证据驱动、职责单一、可组合和渐进式上下文为原则；项目规则、领域术语、ADR、Git 规则和测试约定仍由目标仓库维护。

## 设计原则

- 通用优先，不把项目实现细节写进通用 Skill。
- 单一职责，每个 Skill 只拥有一种工程问题或执行职责。
- 可组合，workflow 调用 discipline，但不复制其规则。
- 证据优先，代码、SPEC、测试、运行结果和 review evidence 高于模型自报。
- 状态分离，Runtime 管理会话上下文；Engineering Skills 管理规范、执行图、交付进度和 evidence。

## 上游适配与维护规范

对于源自 Matt Pocock 的 Skill，以上游原版为基础，只添加 Engineering Skills 确有需要的适配。自行设计的 Skill 不强行套用上游结构。

- 保留原版的核心机制、关键术语和交互节奏；改动前先核对原文，记录来源与适配理由。
- 适配集中在项目约定、文档位置、必要的技能组合及 Runtime 能力差异。不把下游流程说明塞进每个 Skill。
- 新增限制必须对应明确需求或已观察到的问题。通用常识、重复要求、分类教学和假设性防护不进入正文。
- 通过组合复用已有规则，不复制另一 Skill 的细节。精简时也不能静默删掉已确认的能力，例如自动记录 decisions、术语对齐和 ADR。
- 优先修正有问题的局部；不要因一次输出不理想反复重写整体流程，也不以行数作为质量指标。
- 声称效果改善前，用相同任务、模型和上下文比较关键遗漏、无效追问、用户纠正及阅读负担。静态检查只能证明格式与规则一致，不能证明实际效果更好。

当前 grilling 基于 [Matt 的原版](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md)，保留 design tree、frontier 和 round，以及每轮批量提出整个 frontier 的机制。本地适配包括紧凑的快捷回复格式、通用事实调查、项目内决策记录，以及与 domain-modeling 组合写入术语和 ADR。尚未完成行为对比验证。

## 类型

| 类型 | Skills | 职责 |
| --- | --- | --- |
| Project Setup | `project-setup` | 配置需求权威、项目上下文和协作入口。 |
| Workflow | `grilling`, `wayfinding`, `to-spec`, `high-level-design`, `to-tickets`, `quick-implement` | 按需收敛决策、规格化、概要设计、拆票和实现。 |
| Engineering Discipline | `tdd`, `codebase-design`, `domain-modeling`, `code-review`, `debug`, `simplify`, `review-architecture` | 提供可复用的工程判断和实践。 |
| Loop 内部 capability | `implement`, `verify` | 由 Loop 交给当前 Runtime 的 subagents 执行。 |
| Execution Protocol | `loop` | 消费 ticket graph，调度工作单元，聚合 evidence 并执行完成门。 |

## 选择入口

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | `grilling` |
| 技术路径存在跨会话迷雾 | `wayfinding` |
| 需求已收敛且需要持久化规范 | `to-spec` |
| 多个 Module 或实现任务需要共享设计约束 | `high-level-design` |
| 需要多个可独立领取的执行单元 | `to-tickets` → `loop` |
| 单一范围、无需执行图 | `quick-implement`；简单改动可直接实现 |

按需叠加 `debug`、`review-architecture`、`codebase-design`、`domain-modeling`、`tdd`、`simplify` 等 discipline。先判断是否真的需要 Skill；简单局部修改、事实查询和低风险机械修改通常直接处理即可。

## 产物和职责

```text
Runtime
    └── conversation / session / context recovery

Engineering workflow
    SPEC.md
       └── ACCEPTANCE.md (when needed)
       │
    HLD.md (when required)
       │
    tickets/*.json (when collaboration is needed)
       │
      loop (when tickets exist)
       └── frontier / lifecycle / evidence / completion gate
```

| 产物 | 维护者 | 回答的问题 |
| --- | --- | --- |
| `MAP.md` + `decisions/` | `wayfinding` | 路线不清楚时，哪些决策必须先解决？ |
| 会话文档（项目内 `task_contract` 任务目录） | `grilling` | 访谈确认了哪些决策、术语和 ADR，哪些尚未落盘？ |
| `SPEC.md` | `to-spec` | 需要持久化时，要构建什么、范围是什么？ |
| `ACCEPTANCE.md`（按需） | `to-spec` | 复杂或共享验收协议如何独立版本化？ |
| `HLD.md` | `high-level-design` | 多处实现共享哪些职责、接口和集成约束？ |
| `tickets/*.json` | `to-tickets` | 工作如何拆分，哪些任务真正阻塞？ |
| lifecycle/evidence/receipt | `loop` | 当前做到哪里，下一步能做什么？ |

`to-tickets/scripts` 创建、校验、迁移和协调执行图；`loop/scripts` 查询进度、记录 attempt 和状态。两者共享 `engineering/shared/ticket-schema.json` 与图存储实现，无需全局安装 CLI。Loop 是正常执行期间唯一的 graph writer。

`grilling` 每轮自动更新任务目录中的 `decisions.md`，记录已确认决定、理由、验收结论和未决问题；组合 `domain-modeling`，在术语或符合 ADR 门槛的决定确认后立即写入。优先复用项目已有 glossary 和 ADR，缺少约定时使用会话目录。`acceptance-draft.md` 仅在需要独立验收草稿时生成，避免重复记录。

`ACCEPTANCE.md` 是按需使用的独立验收文档；普通任务的验证由 verify 记录，Loop 只聚合任务证据。

## 需求、设计与交付验收

决策所有权统一如下：

| 内容 | Owner |
| --- | --- |
| 业务行为 | `grilling` + `SPEC` |
| 技术约束 | `SPEC` |
| 架构方向 | HLD review |
| 实现方案 | Agent |
| 任务拆分 | `to-tickets` |

`grilling` 负责识别并向用户提出需求决策；API contract、字段语义、后端状态和协议限制，只要定义了所需行为，就作为技术约束进入 SPEC。架构边界和长期设计选择留给 HLD review。

SPEC 是工程需求快照，记录为什么做、做什么、范围、行为、业务约束、外部技术约束、兼容约束和完成标准；不写类、模块、内部接口、实现方案、文件改动或测试实现。Acceptance Seam 可以观察用户行为或外部契约行为，例如 API 响应、UI 操作或导出文件。

HLD 基于 SPEC 技术约束和已有代码定义共享技术方案。遇到新公共抽象、领域模型、API/Event contract、数据/权限模型或长期架构方向时，先经过 Design Review Gate；确认后的决定写入 HLD 的 `## Design Decisions`，每个 D 引用 SPEC R / AC 或具体代码事实，并说明理由和取舍。Verification Seam 是检验技术方案的边界，例如 repository 集成测试或事件契约测试。HLD 可以记录技术集成顺序，但不拆 ticket。

Ticket 使用 `referenced_design_decisions` 引用 HLD，使用 `delivery_acceptance` 描述本次交付如何覆盖 SPEC。它构成执行图，不新增设计或需求，也不规定逐个方法的修改步骤。

脚本分工、部署目录和旧图迁移见 [状态脚本说明](./workflow-scripts.md)。这些调整不增加工作流阶段，HLD 和执行图仍按需使用。

## 从需求到执行

Engineering Skills 按职责拆分，但阶段边界不需要逐一人工确认。每个 Skill 完成自己的职责后，如果当前需求依据和代码事实足以确定下一阶段，就直接继续；只有新的用户决策、缺失的需求依据、无法确认的关键技术路径或额外授权才暂停。

| 阶段 | 职责与下游 |
| --- | --- |
| `grilling` | 按需求决策、设计边界 concern、实现细节分类开放选择；需求决策进入 `to-spec`，设计 concern 作为 HLD 输入，实现细节由 Agent 决定。 |
| `to-spec` | 维护工程需求快照；将需求决策写入 SPEC，将设计 concern 保留为 HLD 输入，然后判断执行路径。 |
| `high-level-design` | 调查代码、形成设计候选并经过 Design Review Gate；维护多处实现共享的技术设计，然后判断执行路径。 |
| 执行路径 | 单一范围且无需执行图时使用 `quick-implement`；需要拆分任务或管理依赖时继续 `to-tickets`。 |
| `to-tickets` | 依据已确认的 SPEC / HLD 拆分任务、校验依赖；已获实现授权时继续 `loop`。 |

跨阶段路由由调用方依据本流程处理；独立的 grilling 不承担下游 Skill 的调度说明。普通交接不需要用户再次输入下一个 Skill 名称。普通拆票由 `to-tickets` 判断粒度和真实阻塞依赖；若拆分暴露未确定的产品、范围、优先级、发布、兼容、验收或共享设计选择，则交还对应上游 Skill，不能把它写成任务假设。

是否进入实现遵循用户当前授权：只要求规划时，在所需规划产物完成后停止；已授权实现时，继续进入 `quick-implement` 或 `loop`。连续交接不会自动授予提交、推送或分支操作权限。

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

例如 Loop 执行期间新增取消语义：先暂停派发任务，停止仍在写入的 subagents 并保留部分结果；若取消行为尚有开放选择，`grilling` 只确认需求决策并由 `to-spec` 修订需求；若出现共享设计或长期方向选择，由 `high-level-design` 经过 Design Review Gate 后修订受影响的设计；再由 `to-tickets` 协调执行图，最后恢复 Loop。

**向上只重新打开受影响的决定。** 与本次变化无关的已确认需求和设计继续有效，保留原有 R / AC / D ID；HLD 单独变化不反向修改 SPEC。

**向下只传播实际影响。** 未受影响的 ticket 保留 ID、生命周期和仍然有效的证据，但必须核对其在新依据下仍然适用，不能只凭 ID 未变就沿用。新增行为使用 amendment ticket；原交付约定被替换时使用 `superseded` 加 replacement / correction。需求变化本身不能简单把历史 `done` 改回 `open`；`reopen` 仅用于依据未变、但原 ticket 没有满足原交付约定的缺陷。

工作流图：

[![Engineering Skills 工作流](./engineering-workflow.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/engineering-workflow.html)

## Ticket 执行

Loop 默认通过当前 Runtime 的 subagents 串行执行 implement → verify → code-review，再阅读结果决定 complete、retry 或 block。不同阶段使用独立上下文。只有任务依赖和写入范围相互独立时才并行，确需隔离时使用 Runtime 已有的 worktree 能力。

结果直接使用文本或 Markdown。Loop 保留原文、核对证据并决定下一步；Skill 内的状态脚本只记录 tickets、attempt、已确认的验收证据和交付状态，不解析审查报告，也不启动或管理 Agent。没有原生 subagents 时应说明限制，不静默改用外部 CLI。

执行期间发现需求或共享设计变化时，Loop 先停止派发任务和仍在写入的 subagents，再把变化交还对应上游 Skill。上游修订完成并由 `to-tickets` 更新执行图后再恢复执行。历史 done 和证据按“需求和设计变更”规则处理。全部 tickets 完成后，由原生 verify / code-review 执行整体验收；脚本只校验当前快照和调用方提交的状态记录。

完成一张 ticket 后立即继续下一张。仅在最终交付通过、用户停止，或剩余工作依赖无法取得的外部输入/能力时停止。Runtime 结束后，Skill 不承诺后台自行继续。

状态命令、输入与边界见 [Loop 与 Runtime 的职责](./loop-runtime.md)；可执行检查见 [状态脚本验收协议](./loopx-acceptance.md)。

Ticket 生命周期图：

[![本地 Ticket 生命周期](./ticket-lifecycle.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/ticket-lifecycle.html)

## 使用规则

- 先读取用户要求、目标仓库指令、SPEC / HLD、相关代码和测试。
- 下游 Skill 不静默改写上游产物。
- 不自动 commit、push、建分支或改写历史。
- 具体执行规则以各目录中的 `SKILL.md` 为准。
