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
| Workflow | `grilling`, `wayfinding`, `to-spec`, `high-level-design`, `to-tickets`, `quick-implement` | 收敛决策、规格化、概要设计、拆票和单次实现。 |
| Engineering Discipline | `tdd`, `codebase-design`, `domain-modeling`, `code-review`, `debug`, `simplify`, `review-architecture`, `improve-codebase-architecture` | 提供可复用的工程判断和实践。 |
| Capability | `implement`, `verify` | 在 Loop 分配的边界内实现和验证 ticket；review capability 复用 `code-review`。 |
| Execution Protocol | `loop` | 消费 ticket graph，调度工作单元，聚合 evidence 并执行完成门。 |

## 选择入口

| 当前状态 | 入口 |
| --- | --- |
| 需求、边界或验收未收敛 | `grilling` |
| 技术路径存在跨会话迷雾 | `wayfinding` |
| 需求已收敛，需要创建或修订规范 | `to-spec` |
| 多个 Module 或实现任务需要共享设计约束 | `high-level-design` |
| 需要多个可独立领取的执行单元 | `to-tickets` → `loop` |
| 单一范围、无需执行图 | `quick-implement` |

按需叠加 `debug`、`review-architecture`、`codebase-design`、`domain-modeling`、`tdd`、`simplify` 等 discipline。先判断是否真的需要 Skill；简单局部修改、事实查询和低风险机械修改通常直接处理即可。

## 产物和职责

```text
Runtime
    └── conversation / session / context recovery

Engineering workflow
    SPEC.md
       │
    HLD.md (when required)
       │
    tickets/*.json
       │
      loop
       └── frontier / lifecycle / evidence / completion gate
```

| 产物 | 维护者 | 回答的问题 |
| --- | --- | --- |
| `MAP.md` + `decisions/` | `wayfinding` | 路线不清楚时，哪些决策必须先解决？ |
| `SPEC.md` | `to-spec` | 要构建什么、范围是什么、如何验收？ |
| `HLD.md` | `high-level-design` | 多处实现共享哪些职责、接口和集成约束？ |
| `tickets/*.json` | `to-tickets` | 工作如何拆分，哪些任务真正阻塞？ |
| lifecycle/evidence/receipt | `loop` | 当前做到哪里，下一步能做什么？ |

`execution-graph` 是 `to-tickets` 和 `loop` 共同消费的内部 Module，不是独立 workflow Skill。它拥有 ticket schema、依赖校验、lifecycle、transaction、recovery 和 migration；Loop 是正常执行期间唯一的 graph writer。

工作流图：

[![Engineering Skills 工作流](./engineering-workflow.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/engineering-workflow.html)

## Ticket 执行

Loop 默认串行执行 ready ticket。只有依赖、写入范围、共享副作用和集成顺序均有证明，并且运行提供并发上限时才允许并行。

单张 ticket 的 capability 流程为：

```text
implement → verify + code-review → aggregate evidence → complete / retry / block
```

`implement` 可以写入 Loop 分配的范围；`verify` 和 `code-review` 独立只读。Worker/capability 不修改 ticket JSON、SPEC、HLD 或 sibling ticket。Loop 通过 execution-graph CLI 维护 `start`、`retry`、`block`、`unblock`、`complete` 和 `reopen` 等状态变更。

Loop 默认使用 native `multi-agents`；也支持 provider CLI `multi-threads`（默认 Codex，可选 Claude、Kimi、Pi）和当前 Manager session 的 `serial` 兜底模式。CLI backend 使用显式 session/resume 和 provider-specific full-access 参数，但不获得 graph 写权限。

长任务不以固定 wall-clock 时长判定失败：调用方可提供任务预算，Pi/CLI heartbeat 可提供 heartbeat freshness 和 progress freshness；Loop 保存 provider raw output 到 task-local artifact，深拷贝 capability handoff，并在 retry/完成门前检查 scope、graph 文件和 Git HEAD。

完整的 graph mutation、backend contract、provider 参数、artifact layout、失败路由和验证边界见：[Loop Runtime 与 Backend Contract](./loop-runtime.md)。

### Backend 设计

Loop 不直接调用 `claude-coder`、`codex-executor`、`kimi-worker` 或 `pi-agent` Skill；这些 Skill 是面向用户的委托规则。Loop 只依赖统一的 provider-neutral backend contract：

```text
Loop
  └── CapabilityAdapter
        └── Backend
              ├── native multi-agents
              └── CLI multi-threads
                    ├── Claude
                    ├── Codex
                    ├── Kimi
                    └── Pi
```

Backend 生命周期固定为 `create` → `send` → `wait`，并支持 `interrupt` 和 `close`。session/thread handle、provider assignment 和 `agent_instance_id` 只属于当前 runtime，不写入 ticket JSON。

执行模式边界：

- `multi-agents` 是默认模式。Manager 通过 Runtime 原生 `spawn_agent`、`send_input`、`wait_agent`、`close_agent` 管理 Worker；implement Worker 在 repair rounds 间复用，verify/review 每轮创建新 context。
- `multi-threads` 是 CLI session 模式，默认 Codex，也支持 Claude、Kimi、Pi；implement 使用显式 session/resume，verify/review 不复用 implement session。
- `serial` 是兼容性兜底，在当前 Manager session 内逐 capability 执行，不伪造独立 Agent context。

CLI backend 使用各 provider 的 full-access 参数，但 full-access 不等于 graph 权限：Worker 仍不能修改 ticket、SPEC、HLD、sibling ticket、提交版本或调度其他 Worker。Loop 通过 workspace diff、graph 文件和 Git HEAD revision 做事后校验。

每次 CLI capability 的完整 stdout/stderr/returncode/JSONL 事件保存到 task-local receipt artifact；只有 Loop 接受的 normalized evidence、verification、review 和 blocker facts 才进入 execution graph。长任务默认不设固定 wall-clock timeout，可由调用方提供任务预算，或通过 heartbeat/progress freshness 失鲜判定中断。

只有所有 ticket-local AC 有 passed evidence、验证成功、适用审查通过且没有未验证范围时，ticket 才能进入 `done`。上游 SPEC/HLD 变化由 `to-spec` / `high-level-design` 和 `to-tickets` 协调，不用 `reopen` 伪装。

Ticket 生命周期图：

[![本地 Ticket 生命周期](./ticket-lifecycle.svg)](https://htmlpreview.github.io/?https://github.com/calvingit/skills/blob/main/docs/ticket-lifecycle.html)

## 使用规则

- 先读取用户要求、目标仓库指令、SPEC/HLD、相关代码和测试。
- 下游 Skill 不静默改写上游产物。
- 不自动 commit、push、建分支或改写历史。
- 具体执行规则以各目录中的 `SKILL.md` 为准。
