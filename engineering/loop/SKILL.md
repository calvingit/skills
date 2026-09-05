---
name: loop
description: "依据 SPEC、可选 HLD 与 JSON ticket 执行图持续执行和验证多个工作单元，维护进度、证据与整体交付审查。"
---

# Loop

以 `SPEC.md` 为需求规范、任务目录中存在的 `HLD.md` 为概要设计依据、`tickets/*.json` 为唯一 execution graph，在调用方或 Agent Runtime 已经提供的当前 workspace 中持续推进可执行 ticket，直到交付通过整体交付审查或被明确阻塞。Loop 不创建、切换或管理执行环境；协议不依赖特定 Agent、子代理或会话机制。

## 权威与状态

- 当前 SPEC、存在时的 HLD、active JSON tickets、已落地代码和验证结果共同构成事实来源；worker receipt 不是完成证据。
- 首次开始时记录 execution graph 基线与既有改动；恢复时从 ticket 的 current attempt、当前 workspace 和可信 receipt 还原审查范围，无法还原时显式记录未覆盖范围。
- Ticket 持久 lifecycle 只有 `open`、`in_progress`、`done`、`superseded`。`ready` 与 `blocked` 只对 `open` ticket 动态计算：所有 dependencies 为 done 且没有 execution blocker 时为 ready，否则为 blocked。
- `to-tickets` 只通过 `create-batch` 和 `reconcile-batch` 创建/协调 contract graph。正常执行期间，Loop 只通过 `start`、`block`、`unblock`、`complete`、`reopen` 维护 execution facts 和 lifecycle。
- Ticket worker 只修改当前交付代码并返回 versioned JSON receipt；不修改 SPEC、HLD、ticket document 或 sibling tickets。
- 不在此处改写 SPEC/HLD、重新拆票或替上游 owner 作出 contract reconciliation 决定。

## 检查 execution graph

从本 Skill 目录解析 sibling `../execution-graph/` Module 的 CLI 路径，并运行：

```bash
python3 <execution-graph-dir>/scripts/ticket_graph.py inspect <task-dir>
```

CLI 读取全部 JSON tickets、SPEC 和可选 HLD，输出稳定 JSON envelope。它校验 schema version、稳定 ID、上游 R/AC/D 引用、dependencies、cycle、supersession lineage、coverage、lifecycle/evidence 关系和 transaction state，并计算 frontier、blocked reasons、active progress 与完成门。

按需使用：

```bash
python3 <execution-graph-dir>/scripts/ticket_graph.py list <task-dir> --readiness ready
python3 <execution-graph-dir>/scripts/ticket_graph.py show <task-dir> <ticket-id>
```

只在状态边界重跑检查：开始或恢复时、worker 返回后、状态/依赖变化后、审查修复后，以及最终完成前。不要轮询。`recovery_required`、schema/graph/authority problem 或无合法 frontier 时停止受影响分支；不要直接编辑 JSON 绕过 CLI。

## 推进循环

1. 运行 `inspect`。任何悬空/歧义/superseded dependency、cycle、状态矛盾、缺失 HLD、无效 D 引用、coverage gap 或 unfinished transaction 都先报告并停止错误分支。
2. 从 `list --readiness ready` 或 inspect frontier 选择 ticket，再用 `show` 读取单票 contract。Loop 不自行全文解析 ticket files。
3. 先观察当前 workspace 的 staged、unstaged、untracked 文件和既有改动分类，构造包含 baseline、existing changes 与 allowed write scope 的 JSON request，调用 `start`。只有 CLI 确认后才把 ticket 视为 in progress。
4. 向 worker 提供完整 SPEC、存在时的完整 HLD、show 返回的 ticket/current attempt、依赖 evidence 和允许写入范围。worker 按 [references/ticket-worker.md](references/ticket-worker.md) 返回 JSON receipt。
5. 根据实际 workspace、相对 persisted baseline 的变化、验证输出和 receipt 独立判断结果，不接受口头完成宣称。所有 ticket-local AC 均有 Loop 核验的 `passed` evidence、验证成功、适用 reviews 通过且无 unverified scope 时，调用 `complete`；遇到非派生阻塞时调用 `block`；解除 blocker 前核验 release evidence 后调用 `unblock`。
6. 仅当 SPEC/HLD 都未变、整体交付审查发现原 contract 内缺陷时，调用 `reopen` 并给出 review finding、失效 AC IDs 与 upstream unchanged confirmation。SPEC/HLD amendment 必须先停止受影响 worker，再交给 `to-tickets` 通过 `reconcile-batch` 协调 graph。
7. 重新检查并继续，直到进入完成门或阻塞门。

默认串行，使后续 ticket 直接基于当前 workspace 中已落地的前序代码继续工作。只有 tickets 无依赖、写入范围和共享副作用均可证明隔离、集成顺序明确且并行确有收益时才并行；并行 worker 仍不得写 graph。

每轮必须新增一种可验证进展：落地变更、CLI 确认的状态迁移、当前可执行任务变化、验证 evidence 或新的审查发现。只对瞬时环境故障做有限重试；若一轮没有实质进展且不存在合理的下一动作，停止为 `no_progress`。调用方给出执行上限时遵守该边界，不自行提高上限。

## 完成门与修订

仅当 `inspect` 无结构问题且 `all_active_done=true` 时进入整体交付审查。完成前必须确认：

- 从 execution graph 基线到当前状态的完整变更已审查，既有/无关改动已排除；没有仍在运行或未集成的工作。
- 当前 SPEC 的需求和约束均被 active graph 覆盖；存在 HLD 时，每个有效 D 均被相关 active ticket 与已实现代码遵守；代码不存在仅由 superseded tickets 要求的行为。
- 分别执行项目规范审查、需求实现审查，以及存在 HLD 时的概要设计审查，再检查 tickets 是否正确覆盖当前要求；任一适用审查失败都不能宣告完成。

若 SPEC/HLD 均未变且发现属于现有 ticket，记录 evidence、调用 `reopen` 并继续循环；若发现 graph 缺口，交回 `to-tickets`；若发现需求契约缺口，交回 `to-spec`；若发现概要设计缺口或 HLD 已不可行，交回 `high-level-design`。

## 结果

- `done`：完成门和整体交付审查均通过。
- `blocked`：没有合法可执行 ticket、存在结构问题、依赖/权限/环境不可恢复，或修订尚未完成协调。
- `no_progress`：当前证据下没有能改变状态的合理动作。
- `budget_exhausted`：达到调用方明确给出的执行上限，且尚未进入其他结果。

`ready` 与 `in_progress` 仅是 ticket projection/lifecycle，不是 Loop 的稳定结果。不要接管运行时会话、长期目标管理或特定工具的调度语法，也不要隐式提交、推送或合并版本控制变更。
