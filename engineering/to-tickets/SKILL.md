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

- 未受影响 ticket 保留 immutable ID、contract 和 current evidence。
- HLD design-only amendment 不改变已经满足 SPEC 的历史验收。既有 `done` 行为仍有效但不符合新设计时，保留其需求 evidence，创建明确的 correction/migration ticket 覆盖受影响 D；只有原 delivery contract 整体被替换时才 supersede。
- SPEC amendment 继续按需求契约变化处理；HLD 不得被用来暗中改变 R/AC。
- 尚未开始的 `open` ticket 在交付边界不变时可由 reconciliation 原位更新 contract；边界已经改变时将旧 ticket 标为 `superseded`，创建 replacement ticket。`ready` / `blocked` 是动态 projection，不是可直接写入的 lifecycle。
- 受影响的 `in_progress` ticket 必须先由 `loop` 停止 worker 并回收 partial receipt。已经产生已实现改动时，保留原 ticket 与 evidence，将其标为 `superseded`，再创建 replacement/correction ticket；确认尚无已实现改动且交付边界未变时才允许原位更新。
- `done` ticket 的既有 contract 与已实现行为对当前 SPEC 仍完全有效时保持 `done`。只需追加行为时保留原 ticket，另建 amendment ticket；原行为需要修改、替换或撤销时将旧 ticket 标为 `superseded`，并创建 replacement/correction ticket。
- 新端到端交付任务创建新 ticket。移除的需求若已有已实现行为，创建明确的 removal/correction ticket；不得只删除旧 ticket 或 evidence。

上游契约变更不得把既有 `done` ticket 直接 `reopen`。`done → open` 只表示 SPEC/HLD 均未变、整体交付审查发现原 ticket 没有正确满足原 contract。SPEC 或 HLD amendment 必须保留仍有效的 evidence，并用 amendment/correction/migration/replacement ticket 或必要的 `superseded` 表达变化。

向用户展示 impact plan 并确认后再调用 `reconcile-batch`。CLI 验证所有 dependencies、lineage、coverage 与 current lifecycle，并重新计算 readiness；任何指向 `superseded` ticket 的依赖都必须删除、替换或重连，确保没有悬空引用或 dependency cycle。active worker 仍在写入同一 ticket 时必须停止同步，交回 `loop` 处理其 lifecycle。

`superseded` 是 terminal、non-active lifecycle：不进入 frontier，不作为当前 SPEC 的验收覆盖，也不等同于失败。保留原 ticket 的 evidence，并写入 supersession reason 与 nullable replacement lineage。

## 写入本地 tickets

`tickets/*.json` 是唯一 execution graph。`to-tickets` 不直接写 JSON 文件、不扫描最大 ID，也不维护 readiness、checkbox 或 evidence。它先向用户确认候选 tickets，再构造 `create-batch` JSON request：每项提供临时 key、title、covers、适用 D IDs、what to build、constraints、ticket-local Acceptance Criteria 和以临时 key 表达的真实 dependencies。

确认后通过统一 CLI 写入：

```bash
python3 <execution-graph-dir>/scripts/ticket_graph.py create-batch <task-dir> --input <request.json>
```

CLI 分配不可变 `T001` 式 ID、解析批次内 dependencies、写入初始 `open` lifecycle/空 execution facts，并返回 key/ID/path mapping 与完整 graph projection。Ticket document 的 schema、filename slug、证据、blocker、current attempt、supersession lineage 与动态 readiness 均由 graph tool 拥有；不得在 Skill 中维护第二份 JSON template。

同一 ticket 内的 AC ID 必须唯一；其完整 evidence identity 是 ticket ID 加 local AC ID。ticket 通过 `covers.requirements`、`covers.spec_acceptance` 和 `design_decisions` 引用上游 contract，而不复制 SPEC/HLD 描述。普通 delivery ticket 必须覆盖至少一个当前 R 或 SPEC AC；design-only correction/migration 至少引用一个 D ID。

初次 graph 创建后，`to-tickets` 报告 CLI 计算的 frontier、blocked reasons、ID/path mapping、适用 D IDs 与未验证项。只要 execution graph 已存在，无论 active ticket 是一张还是多张，都调用 `loop`；没有 graph 的单一 SPEC/HLD 才使用 `quick-implement`。

## 同步 amendment

SPEC/HLD amendment 已确认且 Loop 已停止受影响 worker 后，`to-tickets` 先形成 impact plan，再通过 `reconcile-batch` 一次提交 contract update、new ticket、supersede 和 dependency replacement。CLI 先在内存构造并验证完整 prospective graph，再以 transaction 提交；不得逐文件修改、直接删除 formal ticket，或用 `reopen` 表达上游 contract 变化。

`superseded` 是 terminal、non-active lifecycle：保留有效 evidence，并包含 reason 与 nullable replacement lineage。未受影响 ticket 保留 ID、contract 和 evidence；done ticket 的有效需求 evidence 不因 design-only amendment 自动失效。没有可用 JSON schema migration 时，显式 `migrate --check` 只报告计划；读取与普通写入都不隐式迁移。

## Handoff

`to-tickets` 不自动领取 ticket、不实现代码，也不自动获得 commit、push、建分支或改写历史的授权。

本 Skill 不自动领取 ticket、不实现代码，也不自动获得 commit、push、建分支或改写历史的授权。
