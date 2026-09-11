# Engineering Skills

本目录提供通用工程 Coding 流程，不绑定语言、框架、项目目录或 Agent Runtime。它以证据驱动、职责单一、可组合和渐进式上下文为原则；项目规则、领域术语、ADR、Git 规则和测试约定仍由目标仓库维护。

## 设计原则

- 通用优先，不把项目实现细节写进通用 Skill。
- 单一职责，每个 Skill 只拥有一种工程问题或执行职责。
- 可组合，workflow 调用 discipline，但不复制其规则。
- 证据优先，代码、SPEC、测试、运行结果和 review evidence 高于模型自报。
- 状态分离，Runtime 管理会话上下文；Engineering Skills 管理规范、执行图、交付进度和 evidence。

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

`loopx` 是 `to-tickets` 和 `loop` 使用的 graph 工具；Loop 是正常执行期间唯一的 graph writer。

`grilling` 仅在验收结论需要持久化、跨会话继续或交接时生成 `acceptance-draft.md`；同一会话内直接进入实现的简单讨论，在会话中保留已确认的验收结论、预期结果和证据来源即可。

`ACCEPTANCE.md` 是按需使用的独立验收文档；普通任务的验证由 verify 记录，Loop 只聚合任务证据。

## 从需求到执行

Engineering Skills 按职责拆分，但阶段边界不需要逐一人工确认。每个 Skill 完成自己的职责后，如果当前需求依据和代码事实足以确定下一阶段，就直接继续；只有新的用户决策、缺失的需求依据、无法确认的关键技术路径或额外授权才暂停。

| 阶段 | 职责与下游 |
| --- | --- |
| `grilling` | 确认开放的需求选择；需要持久化、共享或版本管理时继续 `to-spec`，简单任务可在授权范围内直接实现。 |
| `to-spec` | 维护规范性需求；需要共享设计时继续 `high-level-design`，否则判断执行路径。 |
| `high-level-design` | 维护多处实现共享的技术设计，然后判断执行路径。 |
| 执行路径 | 单一范围且无需执行图时使用 `quick-implement`；需要拆分任务或管理依赖时继续 `to-tickets`。 |
| `to-tickets` | 依据已确认的 SPEC / HLD 拆分任务、校验依赖；已获实现授权时继续 `loop`。 |

普通交接不需要用户再次输入下一个 Skill 名称。普通拆票由 `to-tickets` 判断粒度和真实阻塞依赖；若拆分暴露未确定的产品、范围、优先级、发布、兼容、验收或共享设计选择，则交还对应上游 Skill，不能把它写成任务假设。

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

例如 Loop 执行期间新增取消语义：先暂停派发任务，停止仍在写入的 subagents 并保留部分结果；若取消行为尚有开放选择，`grilling` 只确认这些选择；随后由 `to-spec` 修订需求，必要时由 `high-level-design` 修订受影响的设计，再由 `to-tickets` 协调执行图，最后恢复 Loop。

**向上只重新打开受影响的决定。** 与本次变化无关的已确认需求和设计继续有效，保留原有 R / AC / D ID；HLD 单独变化不反向修改 SPEC。

**向下只传播实际影响。** 未受影响的 ticket 保留 ID、生命周期和仍然有效的证据，但必须核对其在新依据下仍然适用，不能只凭 ID 未变就沿用。新增行为使用 amendment ticket；原交付约定被替换时使用 `superseded` 加 replacement / correction。需求变化本身不能简单把历史 `done` 改回 `open`；`reopen` 仅用于依据未变、但原 ticket 没有满足原交付约定的缺陷。

工作流图：

[![Engineering Skills 工作流](./engineering-workflow.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/engineering-workflow.html)

## Ticket 执行

Loop 默认通过当前 Runtime 的 subagents 串行执行 implement → verify → code-review，再阅读结果决定 complete、retry 或 block。不同阶段使用独立上下文。只有任务依赖和写入范围相互独立时才并行，确需隔离时使用 Runtime 已有的 worktree 能力。

结果直接使用文本或 Markdown。Loop 保留原文、核对证据并决定下一步；`loopx` 只记录 tickets、attempt、已确认的验收证据和交付状态，不解析审查报告，也不启动或管理 Agent。没有原生 subagents 时应说明限制，不静默改用外部 CLI。

执行期间发现需求或共享设计变化时，Loop 先停止派发任务和仍在写入的 subagents，再把变化交还对应上游 Skill。上游修订完成并由 `to-tickets` 更新执行图后再恢复执行。历史 done 和证据按“需求和设计变更”规则处理。全部 tickets 完成后，由原生 verify / code-review 执行整体验收；脚本只校验当前快照和调用方提交的状态记录。

完成一张 ticket 后立即继续下一张。仅在最终交付通过、用户停止，或剩余工作依赖无法取得的外部输入/能力时停止。Runtime 结束后，Skill 不承诺后台自行继续。

状态命令、输入与边界见 [Loop 与 Runtime 的职责](./loop-runtime.md)；可执行检查见 [loopx 验收协议](./loopx-acceptance.md)。

Ticket 生命周期图：

[![本地 Ticket 生命周期](./ticket-lifecycle.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/ticket-lifecycle.html)

## 使用规则

- 先读取用户要求、目标仓库指令、SPEC / HLD、相关代码和测试。
- 下游 Skill 不静默改写上游产物。
- 不自动 commit、push、建分支或改写历史。
- 具体执行规则以各目录中的 `SKILL.md` 为准。
