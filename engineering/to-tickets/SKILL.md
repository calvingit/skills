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

已有 tickets 且 SPEC 已确认修订时，先确认 `loop` 已停止受影响的新 dispatch，并已终止或收回仍在写入的对应 implementer；`to-tickets` 不自行管理 subagent。然后比较旧/新契约及现有 graph：

- 未受影响 ticket 保留 contract、Status 和 evidence；
- 受影响的 `ready` / `blocked` ticket 在确认后更新或替换；
- 受影响的 `in_progress` ticket 停止继续写入，保留 landed evidence，再更新或重新规划；
- 受影响的 `done` ticket 若原 contract 仍适用则重开并更新，否则创建 correction 或 replacement ticket；
- 新 vertical slice 创建新 ticket；移除的需求不能只删除文件，必须说明既有落地内容是否需要回退或保留。

向用户展示 impact plan 并确认后再写入。随后重算所有 blocking edges、Status 与 ready frontier，确保没有悬空引用或 dependency cycle。active implementer 仍在写入同一 ticket 时必须停止同步，交回 `loop` 处理其 lifecycle。

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

## Status

ready
```

没有 blocker 的 ticket 初始状态为 `ready`；有未完成 blocker 的 ticket 初始状态为 `blocked`。初次拆分时，`to-tickets` 只写入初始状态；SPEC amendment 同步时，它按已确认 impact plan 修改受影响 contract 和相应状态。正常执行期间由 `loop` 在证据表明阻塞已经解除后维护 `blocked → ready`，并在 whole-graph review 发现既有范围内缺陷时维护 `done → ready`；由 `implement` 负责 `ready → in_progress → done/blocked`、验收勾选和 execution evidence。除已确认的 amendment 同步外，不得在执行中静默改写 ticket 契约。

## Handoff

写入后报告 initial ready frontier、每个 ticket 的相对路径，以及尚未解决的阻塞或未验证项：

- execution graph 只有一张 ticket，或用户明确只要求处理其中一张 ticket 时，调用 `implement`；
- execution graph 有多张 tickets 时，调用 `loop` 维护 frontier 与调度，即使 initial ready frontier 只有一张；具体每张 ticket 仍由独立的 `implement` 执行。

Ticket Status、acceptance evidence 和 ready frontier 是 execution graph 的交付状态，由 `implement` 与 `loop` 按各自职责消费和更新。

本 Skill 不自动领取 ticket、不实现代码，也不自动获得 commit、push、建分支或改写历史的授权。
