---
name: to-tickets
description: "从已确认的 SPEC 与可选 HLD 派生带真实阻塞依赖的交付任务，或在上游修订后同步受影响 graph；不补做需求或概要设计、不实现代码。"
---

# To Tickets

把已确认的 `SPEC.md` 与任务目录中存在的 `HLD.md` 拆成同级 `tickets/` 下可领取的 **交付任务**。每个 ticket 都是一个可独立验证的端到端交付任务，并明确声明真正阻塞它开始的其他 tickets。SPEC 定义需求规范；HLD 如存在，定义多处实现需要共同遵守的概要设计。

`to-tickets` 是 `to-spec`，以及适用时 `high-level-design` 的下游。它处理交付分解，不重做 decision、需求规格或概要设计。完成的 Wayfinding Map 中影响需求的决定必须先经过 `to-spec`；纯技术决定在 SPEC 确认后由 `high-level-design` 吸收。没有 SPEC 时停止并交回 `to-spec`。

## 输入与准备

1. 读取完整 `SPEC.md`，包括 Destination、需求、边界、验收、Out of scope 和决策依据，不能只按标题猜测范围。
2. 若同一任务目录存在 `HLD.md`，读取完整 HLD、D IDs、局部实现空间、迁移与集成约束。若不存在，检查是否仍有跨 Module、跨调用方或跨实现任务的共享类型、Interface、状态/错误语义、依赖方向或集成选择；存在则停止并交回 `high-level-design`。
3. 按需调查目标仓库当前状态、适用 `AGENTS.md`、领域词汇、ADR、相关调用链和已有任务约定。只有这些事实会改变 ticket 的结果、粒度或依赖时才继续展开；不要为了拆 ticket 而做无关的代码探索。
4. ticket 标题和交付描述沿用项目的领域术语。发现未解决的需求、公开 contract、边界或验收决定时转回 `grilling` / `to-spec`；发现概要技术设计缺口时转回 `high-level-design`，不要把假设写成 ticket。

SPEC 是范围、验收与 Solution Constraints 的最终依据；HLD 如存在，是多处实现共用设计约束的最终依据；tickets 只是面向领取和协作派生出的任务执行图。发现冲突时回到对应产物的维护者修正，不能通过 ticket 静默改变上游语义。

`to-tickets` 不读取或解释 Profile 的 `requirement_authority`、外部 PRD 或聊天中的新需求；这些输入必须先由 `to-spec` 写入并确认到 SPEC。它也不把聊天中的技术偏好直接写入 ticket；影响多处实现的设计决定必须先进入 HLD。

## 拆分规则

优先按可独立验证的端到端交付任务拆分：

- 每个 ticket 穿过为交付行为所需的完整路径，必要时同时包含数据、接口、界面、测试和文档，而不是先按层分批；
- 完成后应从用户、调用方或验收视角独立演示或验证；
- 单个 ticket 应能在一次独立上下文内完成；
- 测试、验证和必要的局部整理默认属于对应 slice，不另建“统一补测试”“最后清理”之类没有独立交付的 ticket；
- 只有前置结果缺失会使 ticket 无法正确开始时，才建立阻塞依赖。没有阻塞项的 ticket 组成首批可执行任务；不得为了叙述顺序制造线性依赖，也不得保留循环依赖。

共享 contract 默认由第一个真实使用它的端到端交付任务落地，后续 tickets 仅在该 contract 尚不存在会导致无法正确开始时依赖它；不要默认创建“先建所有接口/枚举”的横向架构 ticket。只有 schema 生成、先扩展后收缩、兼容层或其他真实 blocker 才建立前置技术任务。宽范围机械重构按先扩展后收缩组织：先兼容性扩展，再按真实影响范围分批迁移，最后删除旧形式。每批尽量保持 CI 可绿；确实无法独立保持时说明共享 integration branch 的必要性，并增加最终集成验证 ticket。

ticket 应描述结果，不写易过期的文件路径、代码片段或逐步实现配方。存在 HLD 时，每张 ticket 只引用适用的 D IDs，并把这些决定派生为 Constraints，不复制完整 HLD。唯一例外是 HLD 明确要求落地的状态机、schema 或共享类型形状；只保留必要部分并注明 D ID。

## 确认拆分

写入前以编号列表向用户展示每个候选 ticket：

1. **标题**：简短、面向结果的名称；
2. **Blocked by**：真实前置 ticket，或“无（可立即开始）”；
3. **交付**：该 ticket 单独使什么端到端行为可验证；
4. **Design**：适用的 HLD D IDs，或 `None`。

请用户确认粒度是否合适、阻塞依赖是否只表达真实阻塞，以及是否需要合并或继续拆分。未经用户确认不得创建 tickets。

## 同步 SPEC / HLD amendment

已有 tickets 且 SPEC 或 HLD 已确认修订时，先确认 `loop` 已停止受影响的新 dispatch，并已终止或收回仍在写入的对应 worker；`to-tickets` 不自行管理 subagent。然后比较旧/新上游契约及现有 graph：

- 未受影响 ticket 保留 contract、Status 和 evidence。
- HLD design-only amendment 不改变已经满足 SPEC 的历史验收。既有 `done` 行为仍有效但不符合新设计时，保留其需求 evidence，创建明确的 correction/migration ticket 覆盖受影响 D；只有原 delivery contract 整体被替换时才 supersede。
- SPEC amendment 继续按需求契约变化处理；HLD 不得被用来暗中改变 R/AC。
- `ready` / `blocked` ticket 尚未产生已实现改动且仍是同一交付边界时，可以原位更新 contract，再按新依赖计算 `ready` / `blocked`；边界已经改变时将旧 ticket 标为 `superseded`，创建 replacement ticket。
- 受影响的 `in_progress` ticket 必须先由 `loop` 停止 worker 并回收 partial evidence。已经产生已实现改动时，保留原 ticket 与 evidence，将其标为 `superseded`，再创建 replacement/correction ticket；确认尚无已实现改动且交付边界未变时才允许原位更新并重算状态。
- `done` ticket 的既有 contract 与已实现行为对当前 SPEC 仍完全有效时保持 `done`。只需追加行为时保留原 ticket，另建 amendment ticket；原行为需要修改、替换或撤销时将旧 ticket 标为 `superseded`，并创建 replacement/correction ticket。
- 新端到端交付任务创建新 ticket。移除的需求若已有已实现行为，创建明确的 removal/correction ticket；不得只删除旧 ticket 或 evidence。

上游契约变更不得把既有 `done` ticket 直接恢复为 `ready`。`done → ready` 只表示 SPEC/HLD 均未变、整体交付审查发现原 ticket 没有正确满足原 contract。SPEC 或 HLD amendment 必须保留仍有效的 evidence，并用 amendment/correction/migration/replacement ticket 或必要的 `superseded` 表达变化。

向用户展示 impact plan 并确认后再写入。随后重算所有阻塞依赖、Status 与当前可执行任务；任何指向 `superseded` ticket 的依赖都必须删除、替换或重连，确保没有悬空引用或 dependency cycle。active worker 仍在写入同一 ticket 时必须停止同步，交回 `loop` 处理其 lifecycle。

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

## High-Level Design

- None | [HLD.md](../HLD.md): D1, D2

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

ticket 因已确认的 SPEC/HLD amendment 退出当前 graph 时保留原内容和 evidence，将原有 Status 更新为 `superseded`，再追加 lineage：

```markdown
## Status

superseded

## Superseded by

- [07-<replacement>.md](07-<replacement>.md)

## Supersession reason

<受影响的 R/AC 或 D、上游变化，以及已实现行为是保留、修改还是撤销。>
```

没有 blocker 的 ticket 初始状态为 `ready`；有未完成 blocker 的 ticket 初始状态为 `blocked`。`Execution evidence` 初始为 `Pending`，`Execution blocker` 初始为 `None`。初次拆分时，`to-tickets` 只写入初始状态；SPEC/HLD amendment 同步时，它按已确认 impact plan 修改受影响 contract、创建 correction/migration/replacement/amendment tickets，并负责必要的 `ready/blocked/in_progress/done → superseded`。正常执行期间由 `loop` 统一负责 `ready → in_progress → done|blocked`、`blocked → ready`、上游契约未变时的 `done → ready`、验收勾选、execution evidence 和 execution blocker。除已确认的 amendment 同步外，不得在执行中静默改写 ticket 契约。

## Handoff

写入后报告首批可执行任务、每个 ticket 的相对路径、适用的 D IDs，以及尚未解决的阻塞或未验证项。只要已经创建 execution graph，无论 active ticket 是一张还是多张，都调用 `loop` 维护 frontier、执行工作单元并核验 evidence；没有 graph 的单一 SPEC/HLD 才使用 `quick-implement`。

Ticket Status、Acceptance checkboxes、Execution evidence、Execution blocker 和当前可执行任务是 execution graph 的交付状态：`to-tickets` 只在初次拆分或已确认的 SPEC/HLD amendment reconciliation 中写入 graph，正常执行由 `loop` 统一核验和更新。

本 Skill 不自动领取 ticket、不实现代码，也不自动获得 commit、push、建分支或改写历史的授权。
