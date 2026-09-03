---
name: loop
description: "依据 SPEC、可选 HLD 与 ticket 执行图持续执行和验证多个工作单元，维护状态、证据与整体交付审查。"
---

# Loop

以 `SPEC.md` 为需求规范、任务目录中存在的 `HLD.md` 为概要设计依据、`tickets/*.md` 为执行图，在调用方或 Agent Runtime 已经提供的当前 workspace 中持续推进可执行 ticket，直到交付通过整体交付审查或被明确阻塞。Loop 不创建、切换或管理执行环境；协议不依赖特定 Agent、子代理或会话机制。

## 权威与状态

- 当前 `SPEC.md`、存在时的 `HLD.md`、active tickets 和已落地代码/验证结果共同构成事实来源；调度回执不是完成证据。
- 首次开始时记录执行图基线与既有变更；恢复时从最早可信执行回执还原审查范围，无法还原则显式记录未覆盖范围。
- Active 状态为 `ready`、`blocked`、`in_progress`、`done`；`superseded` 仅保留历史，不进入当前可执行任务或完成判定。
- `to-tickets` 创建初始状态并处理 SPEC/HLD 修订与替代关系；本 skill 是正常执行期间任务执行图的唯一写入者，负责 `ready → in_progress → done|blocked`、`blocked → ready`，以及 SPEC/HLD 均未改变时审查修复中的 `done → ready`。
- ticket worker 只修改当前交付代码并返回执行回执，不修改上游产物、ticket 状态、验收勾选、Execution evidence、Execution blocker 或其他 tickets。
- 不在此处改写 SPEC/HLD、重新拆票或替执行单元实现 ticket。

## 检查执行图

在本 skill 目录解析出脚本路径，并运行：

```bash
python3 <skill-dir>/scripts/inspect_graph.py <task-dir>
```

脚本只读 Markdown，输出当前可执行任务、依赖已解除的 blocked tickets、进行中/完成/superseded tickets、完成门和结构问题。它同时检查 ticket 必需字段，以及 `done` ticket 的验收勾选与 Execution evidence；它是可选优化，不是新的权威状态。

若 Python 或脚本不可用，手工执行同等检查：读取全部 tickets，验证必需 sections、Status、Acceptance checkboxes、Execution evidence、Execution blocker 与 Blocked by；排除 superseded，验证依赖存在且无环，再计算所有依赖均为 `done` 的 `ready` 任务。存在 HLD 时还要验证 ticket 引用的文件和 D IDs 均存在。

只在状态边界重跑检查：开始或恢复时、执行单元返回后、状态或依赖变化后、审查修复后，以及最终完成前。不要轮询。

## 推进循环

1. 检查执行图；任何悬空/歧义/superseded 依赖、环路、状态矛盾、缺失 HLD 或无效 D 引用都先报告并停止错误分支。
2. `dependency_releasable` 只表示 ticket dependencies 已经完成。Loop 仍需读取 Execution blocker 并核验其 release evidence；所有解除条件明确满足后才清除 blocker、改为 `ready` 并重新检查。
3. 从当前可执行任务中选择 ticket，将其更新为 `in_progress`，再记录包含当前 staged、unstaged 和 untracked 文件清单的当前任务基线与既有改动；随后按 [references/ticket-worker.md](references/ticket-worker.md) 提供 `SPEC.md`、存在时的完整 `HLD.md`、ticket、当前任务基线、依赖证据和允许写入范围，执行一个工作单元。
4. 依据当前 workspace 的实际状态、相对当前任务基线的变化、验证输出和 worker 执行回执判断结果，不接受仅口头宣称完成。`completed` 只有在当前行为、全部 Acceptance Criteria、验证、简化检查与项目规范、SPEC，以及存在 HLD 时的概要设计审查均可复核时，才由 Loop 勾选验收，并为每个 AC ID 写入唯一的 `- <AC-ID> — passed — <evidence>`，清除 Execution blocker 后更新为 `done`；`blocked` 由 Loop 写入精确阻塞原因和解除证据后更新状态。
5. worker 返回 `failed` 时只对瞬时故障有限重试；返回 `interrupted` 时保留部分回执并进入对应的 SPEC/HLD 修订同步流程，不自行完成状态迁移。
6. 重新检查并继续，直到进入完成门或阻塞门。

默认串行，使后续 ticket 直接基于当前 workspace 中已经落地的前序代码继续工作。运行时支持子代理时可委派；只有 tickets 无依赖、写入范围和共享副作用均可证明隔离、集成顺序明确且并行确有收益时才并行。并行 worker 仍不得写 graph。

每轮必须新增一种可验证进展：落地变更、状态迁移、当前可执行任务变化、验证证据或新的审查发现。只对瞬时环境故障做有限重试；若一轮没有实质进展且不存在合理的下一动作，停止为 `no_progress`。调用方给出执行上限时遵守该边界，不自行提高上限。

## 完成门与修订

仅当检查结果无结构问题且 `all_active_done=true` 时进入整体交付审查。完成前必须确认：

- 从执行图基线到当前状态的完整变更已审查，既有/无关改动已排除；没有仍在运行或未集成的工作。
- 当前 SPEC 的需求和约束均被 active graph 覆盖；存在 HLD 时，每个有效 D 均被相关 active ticket 与已实现代码遵守；代码不存在仅由 superseded tickets 要求的行为。
- 分别执行项目规范审查、需求实现审查，以及存在 HLD 时的概要设计审查，再检查 tickets 是否正确覆盖当前要求；任一适用审查失败都不能宣告完成。

若 SPEC/HLD 均未变且发现属于现有 ticket，记录 evidence、将其重开为 `ready` 并继续循环；若发现 graph 缺口，交回 `to-tickets`；若发现需求契约缺口，交回 `to-spec`；若发现概要设计缺口或 HLD 已不可行，交回 `high-level-design`。

若 `SPEC.md` 或 `HLD.md` 在执行中被修订：暂停受影响的新调度，通知对应 worker 按 ticket-worker protocol 停止并回收部分回执，确认其不再写入后，交给 `to-tickets` 完成旧/新契约差异与执行图同步；确认保留、修正、迁移、替换或新增关系后再重新检查。不得继续依赖旧图，也不得把旧 `done` 自动视为新契约下的全部工作已完成。

## 结果

- `done`：完成门和整体交付审查均通过。
- `blocked`：没有合法的可执行任务、存在结构问题、依赖/权限/环境不可恢复，或修订尚未完成同步。
- `no_progress`：当前证据下没有能改变状态的合理动作。
- `budget_exhausted`：达到调用方明确给出的执行上限，且尚未进入其他结果。

`ready` 与 `in_progress` 仅是 ticket 状态，不是 Loop 的稳定结果。

不要接管运行时会话、长期目标管理或特定工具的调度语法，也不要隐式提交、推送或合并版本控制变更。
