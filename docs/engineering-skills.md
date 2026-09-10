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
| 会话文档（默认 `${TMPDIR:-/tmp}/grilling-*/`） | `grilling` | 访谈确认了哪些决策、术语和 ADR，哪些尚未落盘？ |
| `SPEC.md` | `to-spec` | 需要持久化时，要构建什么、范围是什么？ |
| `ACCEPTANCE.md`（按需） | `to-spec` | 复杂或共享验收协议如何独立版本化？ |
| `HLD.md` | `high-level-design` | 多处实现共享哪些职责、接口和集成约束？ |
| `tickets/*.json` | `to-tickets` | 工作如何拆分，哪些任务真正阻塞？ |
| lifecycle/evidence/receipt | `loop` | 当前做到哪里，下一步能做什么？ |

`loopx` 是 `to-tickets` 和 `loop` 使用的 graph 工具；Loop 是正常执行期间唯一的 graph writer。

`grilling` 仅在验收结论需要持久化、跨会话继续或交接时生成 `acceptance-draft.md`；同一会话内直接进入实现的简单讨论，在会话中保留已确认的验收结论、预期结果和证据来源即可。

`ACCEPTANCE.md` 是按需使用的独立验收文档；普通任务的验证由 verify 记录，Loop 只聚合任务证据。

工作流图：

[![Engineering Skills 工作流](./engineering-workflow.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/engineering-workflow.html)

## Ticket 执行

Loop 默认通过当前 Runtime 的 subagents 串行执行 implement → verify → code-review，再阅读结果决定 complete、retry 或 block。不同阶段使用独立上下文。只有任务依赖和写入范围相互独立时才并行，确需隔离时使用 Runtime 已有的 worktree 能力。

结果直接使用文本或 Markdown。Loop 保留原文、核对证据并决定下一步；`loopx` 只记录 tickets、attempt、已确认的验收证据和交付状态，不解析审查报告，也不启动或管理 Agent。没有原生 subagents 时应说明限制，不静默改用外部 CLI。

需求变更时先通过 Runtime 停止相关 subagents，再协调上游文档和 tickets。历史 done 保留，旧证据需确认仍适用。全部 tickets 完成后，由原生 verify / code-review 执行整体验收；脚本只校验当前快照和调用方提交的状态记录。

完成一张 ticket 后立即继续下一张。仅在最终交付通过、用户停止，或剩余工作依赖无法取得的外部输入/能力时停止。Runtime 结束后，Skill 不承诺后台自行继续。

状态命令、输入与边界见 [Loop 与 Runtime 的职责](./loop-runtime.md)；可执行检查见 [loopx 验收协议](./loopx-acceptance.md)。

Ticket 生命周期图：

[![本地 Ticket 生命周期](./ticket-lifecycle.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/ticket-lifecycle.html)

## 使用规则

- 先读取用户要求、目标仓库指令、SPEC / HLD、相关代码和测试。
- 下游 Skill 不静默改写上游产物。
- 不自动 commit、push、建分支或改写历史。
- 具体执行规则以各目录中的 `SKILL.md` 为准。
