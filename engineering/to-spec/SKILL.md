---
name: to-spec
description: "根据需求权威、已收敛对话与代码库事实创建或修订规范性 SPEC.md 与 ACCEPTANCE.md，区分需求约束与概要技术设计，并判断下游是否需要 HLD 或执行图，不拆 ticket 或实现。"
---

# To Spec

把已收敛共识、需求权威和代码库事实写入任务目录的 `SPEC.md` 与 `ACCEPTANCE.md`。没有 SPEC 时用 Create；已有 SPEC 且需求新增、修改、删除或澄清时用 Amendment 修订同一文件。不重新做全面需求访谈，不拆 ticket，不实现代码。

`SPEC.md` 是工作流唯一的本地需求规范快照，说明问题、方案、行为、Solution Constraints、测试决策、边界与验收。它不包含派生概要设计、执行图或实现配方。外部 PRD 或用户输入可以是上游 requirement authority，但不能替代已确认 SPEC 直接驱动 HLD、tickets 或实现。除非用户明确要求，不向外部 tracker 发布，也不创建 `SPEC-v2.md` 等并行 authority。

`HLD.md` 如存在，是从 SPEC 与代码库事实派生的概要技术设计权威，不能改变需求语义。跨 Module、调用方或实现任务的共享设计由 `high-level-design` 维护；单一范围明确的单项任务交给 `quick-implement`；多个执行单元由 `to-tickets` 派生 graph，再由 `loop` 执行。

## 入口边界

- 需求来源按「用户本次指定 → 适用 Profile 的 `requirement_authority` → 仓库事实 → Skill 默认」解析。`external-manual` 只能使用用户提供的当前快照，并标明未验证的原始外部内容，不得假装已访问飞书、企业微信或其他系统。
- 需求、外部行为、业务边界、权限、公开 contract 或验收仍有会改变方案的未决选择时，停止并交回 `grilling`。
- Destination 可以命名，但关键路径仍有技术迷雾且需要跨会话调查时，停止并交回 `wayfinding`。
- 用户提供已完成 `MAP.md` 时：确认 `Frontier` 为空，`Not yet specified` 中没有仍指向 Destination 的 Fog，阻塞性 decision 均已最终确认；读取 Map 的 low-resolution view，以及会影响需求、公开 contract、边界、测试或验收的 decision 文件。纯技术概要决定留给 `high-level-design`。
- 模块职责、内部 Interface、共享类型、依赖方向或集成策略尚未确定时不阻塞规格，记为 design concern，SPEC 确认后路由到 `high-level-design`。
- 不编造缺失字段、错误、公开 contract、测试 seam、Solution Constraint 或 expected result。能从代码库验证的继续调查；必须由用户决定的停止并说明。

## 模式选择

- **Create**：任务目录没有 `SPEC.md`，从已收敛输入生成 `SPEC.md` 与 `ACCEPTANCE.md`。
- **Amendment**：已有 `SPEC.md`，读取完整现有 `SPEC.md` 与 `ACCEPTANCE.md` 及本次 delta 后原位更新。保留未受影响的 `R`/`AC`；受影响场景原位更新。公开行为、错误或取消语义、CLI/JSON/schema/退出码、权限或 artifact 边界变化时递增 `protocol_version`；内部重构和新增测试不升级。
- SPEC 语义未变、只有 ticket 粒度、依赖或执行事实变化时，交给 `to-tickets` 或对应执行 owner，不触碰 SPEC。

## Process

### 1. 汇集已确认上下文

整理对话、用户文档、已完成 decision 和 requirement authority。只保留已明确的事实、约束、术语、取舍和 Out of scope，不为填满模板扩张范围。

任务目录：用户本次指定 → 适用 `AGENTS.md` 的 `Engineering Skills Profile` → 仓库已有任务文档约定。没有 Profile 不阻塞；只有落盘位置或需求语义仍无法确定时才询问。

Amendment 先把 delta 分为 `added` / `changed` / `removed` / `no normative effect`，列出受影响的 `R`、`AC`、边界、Solution Constraints 与测试决策。已有 HLD 或 tickets 时只读检查相关 D、ticket contract、Status 和 evidence，报告哪些设计与交付可能仍有效、需要追加、替换或撤销，不修改下游 artifact。保留既有 `R`/`AC` ID；新需求追加新 ID；删除项保留可追踪说明且不重新编号。未决产品选择只把受影响分支交回 `grilling`；需求已定但新增技术路径仍处于 Fog 时，才做定向 `wayfinding`。

### 2. 调查代码库

当前会话调查不足时，写 SPEC 前查清：

- 适用 `AGENTS.md`、领域 glossary、架构说明和相关 ADR；
- 当前外部行为、相关模块与调用关系、既有公开 contract；
- 现有测试用哪些 seam 验证相似行为，以及可沿用的 prior art；
- 用户已有工作区改动，避免覆盖或把无关变化纳入规格。

使用项目领域语言。调查到足以确定范围、公开 contract 和验收边界即停，不进入概要设计或实现。

### 3. 确认验收 seam

写正式文档前，草拟这次变更应通过哪些外部 seam 验收：只定可观察行为、测试层级和 expected result 来源。不设计内部 Module、共享类型或依赖方向，那是 HLD 的 Verification Seams。

Amendment 只重评受影响 seam。既有测试决策仍覆盖变更后行为时保留，并在 impact summary 说明，无需再确认；seam、覆盖行为或 expected result 来源变化时才请用户确认。

- 优先既有外部 seam；新增公开 contract 必须是需求的一部分，不是为测试暴露内部结构。
- 一个稳定 seam 能覆盖整项变更时只用一个。
- 说明每个 seam 覆盖的行为、expected result 来源，以及仓库中可参考的相似测试。
- 不为测试预设内部 Interface，也不把文件路径、内部调用顺序或 mock 结构当成 contract。

向用户说明建议的 seam、依据和取舍并请确认。出现新的产品、协议、架构、范围或验收选择时，先交回 `grilling` 或 `wayfinding`。

### 4. 写 SPEC.md 与 ACCEPTANCE.md

用户确认 seam 后按模板落盘。写入前读取：

- [references/spec-template.md](references/spec-template.md)
- [references/acceptance-template.md](references/acceptance-template.md)

写入前对协议做 `R → AC → scenario → expected result → executable evidence` 双向检查。协议缺口交回 `grilling`，不伪装成实现任务。

### 5. 一致性检查

1. Problem、Solution 与 Destination 描述同一问题和目标。
2. `R` 与 `AC` ID 唯一且稳定；每个 in-scope `R` 至少被一个 `AC` 覆盖。
3. 每个 `AC` 可独立判定，并能追溯到已确认需求或权威 expected source。
4. Solution Constraints 都有上游依据，未混入应由 HLD 拥有的派生技术设计。
5. Testing Decisions 完整记录用户确认的 seam，并尽可能从最高层 seam 验证外部行为。
6. Boundaries、默认行为、Out of Scope 与验收无冲突、无悄然扩张。
7. 无占位符、未处理冲突、虚构事实或被静默跳过的 blocker。
8. Requirement Authority 如实记录来源、快照边界和未验证项。
9. 每个当前 `R`/`AC` 都被 `ACCEPTANCE.md` 场景覆盖；成功、失败、取消、超时、权限和环境路径已写明。
10. Amendment 保留未受影响的 `R`/`AC` ID，并对整份 `SPEC.md` 与 `ACCEPTANCE.md` 复查，不只检查 delta。

能根据已确认上下文或代码库修正的直接修正；需要新决策时停止并交回 `grilling` 或 `wayfinding`。

### 6. 落盘与 handoff

确认一致性后写入任务目录。Create 报告路径、验收 seam、Solution Constraints、design concerns、HLD/graph 路由和未验证项。Amendment 先展示需求 delta、规范影响与可能受影响的 HLD decisions / tickets，确认后再原位更新，并报告保留、新增或移除的 `R`/`AC`。

不修改 HLD、ticket contract、Status 或 evidence；不在 SPEC 中维护 task、frontier、status、retry、Agent 分配或其他执行图。

SPEC 确认后分别判断两条路径，不能用 ticket 数量替代设计判断：

1. **概要设计**：存在跨 Module、跨调用方或跨实现任务的共享类型、Interface、状态或错误语义、依赖方向、迁移或集成约束时先调用 `high-level-design`，否则记录 `hld_not_required` 及依据。
2. **执行**：单一范围明确且不需要执行图时交给 `quick-implement`；需要多个实现任务、依赖关系或统一调度时调用 `to-tickets`，再由 `loop` 推进。

需要 HLD 时必须先完成 HLD 才能进入任一执行路径。本 Skill 只预判是否需要多个实现任务，不决定 ticket 数量或拆分。

不自动获得外部发布、commit、push、建分支或改写历史的授权。

## 变更规则

- **规范性变化** → Amendment。更新同一份 `SPEC.md` 与 `ACCEPTANCE.md` 并重新确认受影响决定；testing seam 未受影响时不强制再确认。已有 HLD 时先由 `high-level-design` 同步受影响 D，再由 `to-tickets` 协调 graph。受影响 ticket 正在执行时，先请求 `loop` 停止相关 dispatch、回收 worker 并保留 evidence。
- **概要设计变化** → 不改 SPEC。由 `high-level-design` 修订 HLD，再由 `to-tickets` 协调受影响 graph。
- **执行拆分变化** → 只由 `to-tickets` 调整 tickets，不能反向改写上游。
- **执行变化** → 只更新对应 ticket 或执行证据，不改 SPEC / HLD。
