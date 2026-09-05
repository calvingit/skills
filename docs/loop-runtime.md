# Loop Runtime

本文档是 Loop、execution graph、capability backend 和 task-local artifact 的稳定参考。它记录当前已实现的 contract；具体项目的需求、设计和验收仍以目标任务的 `SPEC.md`、`HLD.md` 和 ticket graph 为准。

## 1. 职责边界

```text
SPEC.md / HLD.md
        |
        v
tickets/*.json <---- execution-graph CLI
        ^
        |
      Loop
        |
        v
CapabilityAdapter ---- Backend
                         |-- native multi-agents
                         `-- CLI multi-threads
                              `-- Claude / Codex / Kimi / Pi
```

| 部件 | 拥有的职责 | 不拥有的职责 |
| --- | --- | --- |
| `execution-graph` | ticket schema、依赖、readiness、lifecycle、锁、transaction、recovery | worker dispatch、workspace 判断、provider session |
| Loop | ticket 选择、baseline、scope、dispatch、receipt acceptance、完成门、graph mutation | provider 细节、需求改写、sibling ticket 拆分 |
| `CapabilityAdapter` | capability 顺序、session 生命周期、结果聚合 | ticket lifecycle、完成门、业务解释 |
| Backend/CLI driver | create/send/wait/interrupt/close、session、事件和 provider 参数 | graph、ticket JSON、最终 evidence 接受 |
| Worker/capability | 当前 ticket 的实现、验证或 review | graph mutation、sibling 调度、commit/push |

Loop 是正常执行期间唯一的 graph writer；所有状态写入都通过 `ticket_graph.py` CLI。完成门通过后，Loop 默认提交当前 ticket 的干净基线变更；不会 push 或 merge。

## 2. Graph Contract

### 持久状态

ticket 的持久 lifecycle 只有：

```text
open -> in_progress -> done
  ^         |
  |         +-- retry -> in_progress
  +-- block/unblock
```

`superseded` 只由 `to-tickets` 的 reconciliation 表达。`ready` 和 `blocked` 是由依赖与 execution blocker 计算出的 projection，不写入 ticket。

正常执行使用：

```text
inspect / list / show
start / retry / block / unblock / complete / reopen
```

### 关键 mutation

- `start`：提交 `baseline`、`existing_changes`、`allowed_write_scope`，将 ready 的 open ticket 进入 `in_progress`。
- `retry`：提交 `expected_attempt`、新的 baseline/change classification/scope 和 `findings`；在 graph lock 内 compare-and-set 并递增 attempt。implement scope 必须非空。
- `block`：保存 blocker 和 Loop 接受的 evidence，ticket 回到 open projection。
- execution blocker 的 category 可以是 `requirement`、`design`、`dependency`、`environment`、`permission` 或 `external`；依赖阻塞仍是当前 ticket 的 execution fact，不等同于 graph dependency edge。
- `complete`：只有所有本地 AC 通过、verification 命令成功、适用 standards/SPEC/HLD review 通过且 `unverified` 为空时才成功。
- `reopen`：仅适用于 upstream 未变的 done ticket，并要求 review finding 和失效 AC；SPEC/HLD amendment 不用它伪装。

Graph 发现 schema、authority、cycle、dependency、transaction 或 recovery 问题时，Loop 停止受影响分支，不直接编辑 JSON 绕过 CLI。

## 3. Execution Modes

用户可在调用 Loop 时明确声明模式；未声明时默认 `multi-agents`。

### `multi-agents`

Manager 使用 Runtime 原生 Agent API：

```text
worker_id = spawn_agent(...)
send_input(worker_id, round_1)
wait_agent(worker_id)
send_input(worker_id, round_2)
wait_agent(worker_id)
close_agent(worker_id)
```

implement Worker 在 repair rounds 间复用同一个 `agent_id`；verify/review 每个 attempt 使用 fresh context。native spawn 不可用时降级为 `serial`，并报告 requested/effective mode。

### `multi-threads`

使用 provider CLI 的显式 session/resume：

```text
implement session: resume across repair attempts
verify session: fresh per attempt
review session: fresh per attempt
```

默认 provider 为 Codex，也可选择 Claude、Kimi 或 Pi。明确选择的 provider 不可用时返回 provider blocker，不隐式切换到其他 provider。

### `serial`

在当前 Manager session 内逐 ticket、逐 capability 执行，不创建外部 Agent 或 CLI session，也不伪造独立 context。它是兼容性兜底，必须报告 context isolation 降级。

## 4. Backend Contract

统一生命周期：

```text
create(capability, bundle) -> handle
send(handle, bundle)
wait(handle) -> result
interrupt(handle)
close(handle)
```

handle 只存在当前 runtime，包含 provider/session reference、capability 和 opaque `agent_instance_id`；不进入 ticket JSON。

每个 capability bundle 都是独立深拷贝，包含：

- 完整 ticket contract、SPEC、可选 HLD；
- current attempt、baseline、existing changes、当前 diff；
- dependency evidence、allowed write scope；
- prior receipt 和 repair findings。

### Provider 参数

| Provider | 初始 session | 后续 resume | full-access |
| --- | --- | --- | --- |
| Claude | `claude -p --session-id ... --output-format stream-json` | `--resume <id>` | `--dangerously-skip-permissions` + `bypassPermissions` |
| Codex | `codex exec --json` | `codex exec resume <id> --json` | `--dangerously-bypass-approvals-and-sandbox` |
| Kimi | `kimi --auto --output-format stream-json -p ...` | `--session <id>` | `--auto` |
| Pi | `pi -p --mode json --session-id ...` | `--session <id/path>` | `--approve` + 完整工具集 |

禁止使用 `--last`、`--continue` 或模糊 session picker 作为多 Worker 恢复依据。global CLI Skills 是委托规则，不是 Loop backend API。

Full-access 只改变 CLI 的执行权限，不授予 Worker 修改 graph、SPEC/HLD、ticket、sibling 或版本历史的权限。Loop 通过 workspace diff、graph 文件和 Git HEAD revision 做事后校验。

## 5. Receipt and Artifact

### Capability result

每个 capability result 关联：

```text
capability
ticket_id
current_attempt
agent_instance_id
outcome: completed | blocked | failed | interrupted
payload
```

Loop 将 implement/verify/review 结果聚合为现有 v1 worker receipt，再决定 `complete`、`retry` 或 `block`。失败或未验证结果不能降级为成功。

### Artifact layout

```text
.loop/receipts/<ticket>/attempt-<n>/
  implement.json
  verify.json
  review.json
  aggregate.json
```

artifact 原子写入并校验 ticket、attempt、capability、instance identity 和路径边界。CLI backend 的完整 stdout、stderr、returncode 和 JSONL 事件保存在 capability payload 的 `_cli_raw` 中；raw 数据不进入 execution graph。

## 6. 等待、失败与恢复

长任务默认不设固定 wall-clock timeout：

- 调用方可以提供任务预算；
- Pi/CLI heartbeat 可以提供 heartbeat freshness；
- progress freshness 可以识别 provider 长时间无业务进展；
- 没有预算或 freshness 阈值时持续等待 provider 终态或用户取消。

失败路由：

```text
verify/review business failure -> retry
provider / permission / environment / dependency failure -> block
interrupt / stale heartbeat -> cleanup, then caller decides retry or block
```

所有 active handle/process 必须在完成、失败、阻塞、取消或预算结束时清理。进程重启不恢复旧 provider handle，而是根据 current attempt 和 artifact 创建新 instance。

## 7. Verification Status

当前自动化覆盖：

- Loop：52 个测试；
- execution-graph：34 个测试；
- CLI backend：四个 provider 的命令构造、session/resume、权限参数、raw output、heartbeat freshness 和失败归一化；
- graph：retry stale attempt、空 scope、completion gate、transaction/recovery；
- workspace：scope、graph mutation、Git HEAD commit 防护。

尚未证明：真实 Claude/Codex/Kimi/Pi provider turn、生产级 API/数据库副作用、Codex App Server transport 和生产吞吐。实现仍应把这些状态报告为未验证，不把本地 fake/backend 测试当作 live provider acceptance。
