---
name: to-tickets
description: "将已确认的 SPEC 拆成带真实 blocking edges 的 delivery tickets，或在 SPEC 修订后同步受影响的 execution graph；不解释外部需求、实现代码或管理执行进度。"
---

# To Tickets

把已确认的 `SPEC.md` 拆成同一任务目录 `tickets/` 下可领取的 **delivery tickets**。每个 ticket 是一个能独立验证的 tracer-bullet vertical slice，并明确声明真正阻塞它开始的其他 tickets。

`to-tickets` 是 `to-spec` 的下游。它处理交付分解，不重做 `wayfinding` 的 decision ticket，也不重新解释 SPEC 已确认的行为、范围或验收。完成的 Wayfinding Map 必须先经过 `to-spec` 压缩为 SPEC；没有 SPEC 时停止并交回 `to-spec`。

## 输入与准备

1. 读取完整 `SPEC.md`，包括 Destination、需求、边界、验收、Out of scope 和决策依据，不能只按标题猜测范围。
2. 按需调查目标仓库当前状态、适用 `AGENTS.md`、领域词汇、ADR、相关调用链和已有任务约定。只有这些事实会改变 ticket 的结果、粒度或依赖时才继续展开；不要为了拆 ticket 而做无关的代码探索。
3. ticket 标题和交付描述沿用项目的领域术语。发现来源尚未解决的产品、协议、架构、边界或验收决策时停止拆分，明确指出问题并转回 `grilling` / `wayfinding`，不要把假设写成 ticket。

SPEC 是范围、验收与约束的 authority；tickets 只是面向领取和协作的派生 execution graph。发现 SPEC 与拆分结果不一致时，回到 `to-spec` 修正契约，不能通过 ticket 静默改变其语义。

`to-tickets` 不读取或解释 Profile 的 `requirement_authority`、外部 PRD 或聊天中的新需求；这些输入必须先由 `to-spec` 写入并确认到 SPEC。

## 拆分规则

优先按 tracer-bullet vertical slice 拆分：

- 每个 ticket 穿过为交付行为所需的完整路径，必要时同时包含数据、接口、界面、测试和文档，而不是先按层分批；
- 完成后应从用户、调用方或验收视角独立演示或验证；
- 单个 ticket 应能在一个 fresh context 内完成；
- 测试、验证和必要的局部整理默认属于对应 slice，不另建“统一补测试”“最后清理”之类没有独立交付的 ticket；
- 只有前置结果缺失会使 ticket 无法正确开始时，才建立 blocking edge。没有 blocker 的 ticket 组成 initial ready frontier；不得为了叙述顺序制造线性依赖，也不得保留 dependency cycle。

先完成确实能降低后续实现难度的 prefactor。宽范围机械重构是 vertical slicing 的例外：若一次替换会同时破坏大量调用点，按 expand–contract 组织：先兼容性扩展，再按包或目录等真实 blast radius 分批迁移，最后在所有迁移完成后删除旧形式。每批应尽量保持 CI 可绿；确实无法独立保持时，说明共享 integration branch 的必要性，并额外建立最终集成验证 ticket。

ticket 应描述结果，不写易过期的文件路径、代码片段或逐步实现配方。唯一例外是原型产出的状态机、reducer、schema 或类型形状等决策性片段；只保留必要部分，并注明其来源。

## 确认拆分

写入前以编号列表向用户展示每个候选 ticket：

1. **标题**：简短、面向结果的名称；
2. **Blocked by**：真实前置 ticket，或“无（可立即开始）”；
3. **交付**：该 ticket 单独使什么端到端行为可验证。

请用户确认粒度是否合适、blocking edge 是否只表达真实阻塞，以及是否需要合并或继续拆分。未经用户确认不得创建 tickets。

## 同步 SPEC amendment

已有 tickets 且 SPEC 已确认修订时，先确认 `loop` 已停止受影响的新 dispatch，并已终止或收回仍在写入的对应 worker；`to-tickets` 不自行管理 subagent。然后比较旧/新契约及现有 graph：

- 未受影响 ticket 保留 contract、Status 和 evidence。
- `ready` / `blocked` ticket 尚未产生 landed changes 且仍是同一交付边界时，可以原位更新 contract，再按新依赖计算 `ready` / `blocked`；边界已经改变时将旧 ticket 标为 `superseded`，创建 replacement ticket。
- 受影响的 `in_progress` ticket 必须先由 `loop` 停止 worker 并回收 partial evidence。已经产生 landed changes 时，保留原 ticket 与 evidence，将其标为 `superseded`，再创建 replacement/correction ticket；确认尚无 landed changes 且交付边界未变时才允许原位更新并重算状态。
- `done` ticket 的既有 contract 与 landed behavior 对当前 SPEC 仍完全有效时保持 `done`。只需追加行为时保留原 ticket，另建 amendment ticket；原行为需要修改、替换或撤销时将旧 ticket 标为 `superseded`，并创建 replacement/correction ticket。
- 新 vertical slice 创建新 ticket。移除的需求若已有 landed behavior，创建明确的 removal/correction ticket；不得只删除旧 ticket 或 evidence。

需求变更不得把既有 `done` ticket 直接恢复为 `ready`。`done → ready` 只表示 SPEC 未变、whole-graph review 发现原 ticket 没有正确满足原 contract。需求契约变化必须保留有效的 `done`，或使用 `superseded` 加新 ticket 表达。

向用户展示 impact plan 并确认后再写入。随后重算所有 blocking edges、Status 与 ready frontier；任何指向 `superseded` ticket 的依赖都必须删除、替换或重连，确保没有悬空引用或 dependency cycle。active worker 仍在写入同一 ticket 时必须停止同步，交回 `loop` 处理其 lifecycle。

`superseded` 是 terminal、non-active 状态：不进入 frontier，不作为当前 SPEC 的验收覆盖，也不等同于失败。保留原 ticket 的 acceptance 勾选、receipt 和 evidence，将既有 Status 值更新为 `superseded`，并追加 `Superseded by` 与 `Supersession reason`；没有 replacement 时将 `Superseded by` 写为 `None` 并说明原因。

## 写入本地 tickets

使用本地 Markdown。`to-tickets` 在 `SPEC.md` 所在任务目录下创建 `tickets/`，按 dependency order 从 `01` 编号，一个 ticket 一个文件：

```text
SPEC.md
tickets/
  01-<ticket>.md
  02-<ticket>.md
```

```markdown
# 01 — <Ticket title>

## Specification

- [SPEC.md](../SPEC.md)

## What to build

<从用户或调用方视角描述该 ticket 独立交付的端到端行为。>

## Constraints

- <从 SPEC 派生的、此 ticket 必须保持的边界。>

## Acceptance criteria

- [ ] AC1 — <可独立判定的结果>
- [ ] AC2 — <可独立判定的结果>

## Blocked by

- None (can start immediately)

## Execution evidence

- Pending

## Execution blocker

- None

## Status

ready
```

同一 ticket 内的 AC ID 必须唯一。正常执行时，Loop 只把已经核验通过的条目写入 Execution evidence，并与 AC ID 一一对应：

```markdown
## Execution evidence

- AC1 — passed — `<command>` exited 0 and <observable result>
- AC2 — passed — <artifact or runtime observation>
```

`not_verified`、未知 AC ID、重复 evidence ID 或缺少对应 evidence 的 AC 都不能进入 `done`。

ticket 因 SPEC amendment 退出当前 graph 时保留原内容和 evidence，将原有 Status 更新为 `superseded`，再追加 lineage：

```markdown
## Status

superseded

## Superseded by

- [07-<replacement>.md](07-<replacement>.md)

## Supersession reason

<受影响的 R/AC、需求变化，以及 landed behavior 是保留、修改还是撤销。>
```

没有 blocker 的 ticket 初始状态为 `ready`；有未完成 blocker 的 ticket 初始状态为 `blocked`。`Execution evidence` 初始为 `Pending`，`Execution blocker` 初始为 `None`。初次拆分时，`to-tickets` 只写入初始状态；SPEC amendment 同步时，它按已确认 impact plan 修改受影响 contract、创建 replacement/amendment tickets，并负责 `ready/blocked/in_progress/done → superseded`。正常执行期间由 `loop` 统一负责 `ready → in_progress → done|blocked`、`blocked → ready`、契约未变时的 `done → ready`、验收勾选、execution evidence 和 execution blocker。除已确认的 amendment 同步外，不得在执行中静默改写 ticket 契约。

## Handoff

写入后报告 initial ready frontier、每个 ticket 的相对路径，以及尚未解决的阻塞或未验证项。只要已经创建 execution graph，无论 active ticket 是一张还是多张，都调用 `loop` 维护 frontier、执行工作单元并核验 evidence；没有 graph 的单一 SPEC 才使用 `quick-implement`。

Ticket Status、Acceptance checkboxes、Execution evidence、Execution blocker 和 ready frontier 是 execution graph 的交付状态：`to-tickets` 只在初次拆分或已确认的 SPEC amendment reconciliation 中写入 graph，正常执行由 `loop` 统一核验和更新。

本 Skill 不自动领取 ticket、不实现代码，也不自动获得 commit、push、建分支或改写历史的授权。
