# Loop Runtime

本文档是 Loop、execution graph、worker handoff 和 task-local artifact 的稳定参考。它记录当前已实现的 contract；具体项目的需求、设计和验收仍以目标任务的 `SPEC.md`、`HLD.md` 和 ticket graph 为准。

## 1. 职责边界

启动时 Loop 读取任务目录已有的 `SPEC.md`、可选 `ACCEPTANCE.md`、可选 `HLD.md` 和 tickets。Loop 不要求普通任务额外创建验收协议或 expected result；只在任务已声明的必需契约、ticket/receipt 结构或证据无法校验时阻断，不由 Loop 推导新条件。

```text
SPEC.md / HLD.md
        |
        v
tickets/*.json <---- loopx graph CLI
        ^
        |
      Loop
        |
        v
CapabilityAdapter ---- Backend
                         `-- Worker process
```

| 部件 | 拥有的职责 | 不拥有的职责 |
| --- | --- | --- |
| `loopx graph` | ticket schema、依赖、readiness、lifecycle、锁、transaction、recovery | worker dispatch、workspace 判断、worker session |
| Loop | ticket 选择、baseline、scope、dispatch、receipt acceptance、完成门、graph mutation | worker 运行时、需求改写、sibling ticket 拆分 |
| `CapabilityAdapter` | capability 顺序、session 生命周期、结果聚合 | ticket lifecycle、完成门、业务解释 |
| Worker runner | 启动 worker、传递 handoff、收集结果和事件 | graph、ticket JSON、最终 evidence 接受 |
| Worker/capability | 当前 ticket 的实现、验证或 review | graph mutation、sibling 调度、commit/push |

Loop 是正常执行期间唯一的 graph writer；所有状态写入都通过 `loopx graph` CLI。完成门通过后，只有调用方以 `commit_on_complete=True` 明确启用时，Loop 才提交当前 ticket 的归属变更；不会 push 或 merge。

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
- `retry`：提交 `expected_attempt`、新的 attempt checkpoint、初始既有改动分类、scope 和 `findings`；在 graph lock 内 compare-and-set 并递增 attempt。commit 判断仍以首次排除的既有改动和当前 ticket scope 为准，implement scope 必须非空。
- `block`：保存 blocker 和 Loop 接受的 evidence，ticket 回到 open projection。
- execution blocker 的 category 可以是 `requirement`、`design`、`dependency`、`environment`、`permission` 或 `external`；依赖阻塞仍是当前 ticket 的 execution fact，不等同于 graph dependency edge。
- `complete`：只有任务声明的本地 AC 全部有通过证据、必要 verification 成功、Markdown 审查报告经运行时转换后通过检查、没有阻断发现且 `unverified` 与 `unverified_scope` 为空时才成功。没有启用独立验收协议时，不因协议缺失阻断。
- `reopen`：仅适用于 upstream 未变的 done ticket，并要求 review finding 和失效 AC；SPEC / HLD amendment 不用它伪装。

Graph 发现 schema、authority、cycle、dependency、transaction 或 recovery 问题时，Loop 停止受影响分支，不直接编辑 JSON 绕过 CLI。

## 3. Execution Modes

当前共享工作区运行时仅串行执行：implement → verify → review。每次 `loop run` 处理一张 ticket 的一次 attempt，外层调用方继续驱动；有进行中的 attempt 时优先恢复。`dispatch_ready` 处理一个就绪批次，遇到 retry、blocked、interrupted 或 failed 即停止。运行时不提供多 ticket 并行或 verify/review 并行参数。

## 4. Worker Handoff Contract

统一生命周期：

```text
create(capability, bundle) -> handle
send(handle, bundle)
wait(handle) -> result
interrupt(handle)
close(handle)
```

handle 只存在当前 runtime，包含 worker session reference、capability 和 opaque `agent_instance_id`；不进入 ticket JSON。

独立 `ACCEPTANCE.md` 只在任务明确需要时作为额外契约；普通任务直接使用 SPEC 的验收条件。

每个 capability bundle 都是独立深拷贝，包含：

- 完整 ticket contract、SPEC、可选 HLD；
- current attempt、baseline、existing changes、当前 diff；
- dependency evidence、allowed write scope；
- 已有的 acceptance 约束和 verify evidence；
- prior capability receipts 和 repair findings。串行执行时，verify 收到 implement receipt，review 收到 implement 与 verify receipts。

Loop 只接收 worker capability result，不把 worker runtime 细节写入 graph。

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

Loop 将 implement / verify / review 结果聚合为稳定 worker receipt，再决定 `complete`、`retry` 或 `block`。失败或未验证结果不能降级为成功。

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
- Runtime heartbeat 可以提供 heartbeat freshness；
- progress freshness 可以识别 worker 长时间无业务进展；
- 没有预算或 freshness 阈值时持续等待 worker 终态或用户取消。

失败路由：

```text
verify/review business failure -> retry
worker / permission / environment / dependency failure -> block
interrupt / stale heartbeat -> cleanup, then caller decides retry or block
```

所有 active handle / process 必须在完成、失败、阻塞、取消或预算结束时清理。进程重启不恢复旧 worker handle，而是根据 current attempt 和 artifact 创建新 instance。verify / review 默认只能向 `.loop/tmp/` 写隔离缓存；其他临时路径必须由调用方显式分配。

## 7. Verification Status

loopx 的统一运行时验收入口从仓库根目录运行：`python3 tools/loopx/scripts/check.py all`。它检查 loopx 的单元测试、CLI、wheel 和干净 venv 安装；协议文档的一致性由 `to-spec`、`to-tickets`、`loop` 和 review / verify 各自按本协议负责。Worker runtime、生产副作用与吞吐仍须标记为未验证。

当前自动化覆盖：

- 测试命令和覆盖范围以 `tools/loopx/tests/` 当前测试文件为准；交付前运行 README 中的完整测试命令。
- Worker runner：命令构造、session / resume、权限参数、raw output、heartbeat freshness 和失败归一化。
- graph：retry stale attempt、空 scope、completion gate、transaction / recovery。
- workspace：scope、graph mutation、Git HEAD commit 防护。

尚未证明：真实 worker execution、生产级 API/数据库副作用、生产 transport 和生产吞吐。实现仍应把这些状态报告为未验证，不把本地 fake worker 测试当作 live execution acceptance。

## Capability result

CLI backend 从包内 worker receipt schema 派生当前角色的 response contract，随 handoff 一起发送；implement / verify 输出使用 `{"outcome":"completed|blocked|failed|interrupted","payload":{...}}`。review 始终输出可读 Markdown，由 CLI backend 转为内部 receipt。schema 是内部字段结构依据，Skill 是行为职责依据。

- implement 的成功 payload 必须包含 `landed_changes` 和 `simplification`。
- verify 的成功 payload 必须包含 `acceptance_evidence`；每项提供 `acceptance_id`、`passed|not_verified` 和 `summary`。验证命令和退出码由 verify 真实记录，不由 Loop 重跑。
- review 使用 code-review 的固定 Markdown 标题和结论值，正文使用用户语言。CLI backend 只转换最终助手消息（Codex 有最终消息文件时优先使用），保留完整报告和原始输出。Findings 进入 retry；Requirement gaps 和 Unverified 阻止完成；Follow-up 不阻断。格式缺失、重复或结论矛盾时阻塞等待修正报告，不能默认为通过。
- 转换后的 `review` 保留现有内部字段：需求或证据缺口使 `contract` 失败，当前缺陷或证据缺口使 `change_surface` 失败；`exploratory: pass` 表示不另设探索审查门槛，不声称做过全库审计。需求缺口对应 `protocol_health: gap`，其余为 `not_triggered`。审查者无需输出这些字段。
- 各角色均可报告 `blocking_findings`、`non_blocking_findings`、`acceptance_protocol_gaps`、`unverified_scope`、`unverified` 和 `blocker`。未知或失败范围不得省略成通过。blocked 必须给出 blocker 的 category、reason 和 release_condition。

verify 负责执行项目已有验证命令并记录实际结果。业务验证失败进入 retry；worker、权限和环境失败进入 blocker。capability 自报 completed 不能覆盖失败的 review 或 blocker。

保护检查覆盖 SPEC、ACCEPTANCE、HLD、tickets、Git 状态和 runtime 产物。检测到上游变化时停止并保留现场，不自动恢复旧文件；这是一种事后检查，不是操作系统写入隔离。

## Graph mutation 与恢复

`loopx graph <command> --help` 给出命令签名；`create-batch` 使用候选 key，`reconcile-batch` 支持 create、update_contract、supersede、replace_dependency、retain_contract。协调前必须停止 worker 并 block 所有 active attempts。

1. 环境或权限 blocker 解除后，Loop 先核验 release_condition，再通过 `unblock --input <request.json>` 提交 release_evidence，随后重新执行 `loop run`。
2. 用户中断后先运行 `loop status` 和 `graph inspect`；只有一个 in_progress ticket 时，下一次 `loop run` 会恢复它，并重新执行验证命令。多张 in_progress 需要调用方明确选择 ticket，公开 CLI 使用 `loop run --ticket <id> --scope <path>` 选择。
3. 上游被修改或 graph transaction 未完成时先停止 dispatch，保留修改和现有产物。上游合法修订由对应 owner 确认，再 reconcile；越界改动由调用方审查处理，不能自动覆盖。事务恢复使用 `graph recover <task-dir> <rollback|commit>`。
4. `reopen` 仅处理上游未变时的原交付缺陷；SPEC、ACCEPTANCE 或 HLD 修订走对应 owner 与 reconciliation。
5. 当前正式版未发布，不提供旧 schema 迁移；graph contract 变化时直接按当前规范重建任务图。


## 需求依据与最终交付

- `execution.authority` 记录需求文件和当前 ticket 契约的指纹及确认原因。CLI 创建 ticket 时绑定；未执行且未绑定的手工 ticket 在首次 start 时绑定。执行过的 ticket 缺少绑定时必须重新确认，不能默认为有效。
- start、retry、complete、reopen 及中断恢复检查绑定；当前依赖的证据也必须有效。指纹仅忽略文档末尾空行和平台换行编码，不自动判断需求语义等价。
- 需求新增/删除 ID 暂时破坏覆盖时，`graph block` 仍可保存已停止的旧 attempt；返回的 `remaining_problems` 保留待协调问题，不把无效图标成有效。
- `retain_contract` 由需求协调方明确确认未受影响的契约、依赖和证据后使用。它保留历史状态与证据，记录当前依据。受影响行为通过补充、修正或替换 ticket 处理。完成的 ticket 不允许原地改写契约或依赖。
- `stale_authority` 标记待确认的 ticket；`all_active_done` 仅反映历史状态。`delivery_ready` 表示可以开始整体验收，尚不代表交付完成。
- `loop delivery-prepare` 固定最终需求、任务图和代码快照；verify 与 code-review 完成整项验证后，`loop delivery-complete` 接受对应证据。`loop status` 的 `delivery_review` 返回 not_reviewed、pending、passed 或 stale。后续代码、需求、任务图、Git HEAD 或子模块变化会使结论失效。
- 验证命令仍由 verify 执行，CLI 不重复执行。历史证据复用需要确认其含义、代码、依赖与环境仍适用；文件指纹无法证明外部系统状态未变化。

命令和字段以 [最终交付审查](../engineering/loop/references/delivery-review.md) 为准。相关产物位于任务的 `.loop/`，该目录不得放置产品代码。
