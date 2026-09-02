---
name: to-spec
description: "根据项目需求权威、已收敛对话与代码库事实创建规范性 SPEC.md，或在后续需求新增、修改、删除时修订同一份 SPEC 并评估下游影响；不拆 ticket 或实现。"
---

# To Spec

把当前对话中已经达成的共识、适用的需求权威和代码库事实整理成任务目录中的 `SPEC.md`。支持两种模式：没有 SPEC 时创建；已有 SPEC 且用户补充、修改或删除需求时，修订同一文件。不要重新进行一轮全面需求访谈；只处理当前创建范围或变更影响面。

`SPEC.md` 是本仓库工作流的规范性需求来源，说明问题、解决方案、行为、实现决策、测试决策、边界与验收。它不包含 delivery ticket graph、执行状态或逐步实现配方。单一 scoped task 直接交给 `quick-implement`；需要多个执行单元时，由 `to-tickets` 从 SPEC 派生 graph，再由 `loop` 执行。

任务目录中的 `SPEC.md` 是工程工作流唯一的本地规范快照，供 `to-tickets` 直接读取。外部 PRD 或用户输入可以是上游 requirement authority，但不能替代已确认的 SPEC 直接驱动 tickets 或实现。除非用户明确要求，否则不向外部 tracker 发布，也不创建 `SPEC-v2.md` 等并行 authority。

## 入口边界

- 先按用户本次指定、适用 Profile 的 `requirement_authority`、仓库事实和 Skill 默认规则解析需求来源。`external-manual` 模式下，只能使用用户提供的当前快照，并明确未验证的原始外部内容；不得假装已访问飞书、企业微信或其他系统。
- 需求、行为、边界或接口仍有会改变方案的未决选择时，停止并交回 `grilling`。
- Destination 可以命名，但关键路径仍处于 Fog of war 且需要跨 session 调查时，停止并交回 `wayfinding`。
- 用户提供一份已完成的 `MAP.md` 时，确认 `Frontier` 为空，`Not yet specified` 中没有仍指向 Destination 的 Fog，阻塞性 decision 均已完成且结论得到最终确认。读取 Map 的 low-resolution view，以及所有会影响需求、接口、边界、测试或验收的 decision 文件。
- 不编造缺失的字段、错误、接口、模块、测试 seam、实现选择或 expected result。发现缺口时先判断性质：能从代码库验证的事实继续调查，必须由用户决定的内容则停止并说明。

## 模式选择

- **Create**：当前任务没有 `SPEC.md`，从已收敛输入生成新规格。
- **Amendment**：已有 `SPEC.md`，且出现需求新增、修改、删除或澄清；读取完整现有 SPEC 与本次 delta，更新同一文件。
- 如果 SPEC 语义没有变化，只有 ticket 粒度、依赖或执行事实变化，停止并交给 `to-tickets` 或对应执行 owner，不触碰 SPEC。

## Process

### 1. 汇集已确认上下文

整理当前对话、用户提供的文档、已完成的 decision 和 requirement authority，保留已经明确的事实、约束、术语、取舍和 Out of scope，不要为了填满模板而扩张范围。

任务目录优先采用用户本次指定，其次采用适用 `AGENTS.md` 的 `Engineering Skills Profile`，再沿用仓库已有任务文档约定。需求权威按“用户本次明确指定 → Profile → 仓库事实 → 动态发现”解析；Profile 只提供稳定入口。没有 Profile 不阻塞本 Skill；仍无法确定且会改变需求语义或落盘位置时再询问用户。

Amendment 模式先把 delta 分类为 `added`、`changed`、`removed` 或 `no normative effect`，列出受影响的 R、AC、边界、实现决策与测试决策。已有 tickets 时，只读检查其 contract、Status 和 evidence，报告哪些交付可能仍有效、需要追加、需要替换或需要撤销，但不修改 ticket。未受影响内容保持不动：保留既有 R/AC ID，新需求追加新 ID，删除项保留可追踪的变更说明，不重新编号。若 delta 引入未决产品选择，只将受影响分支交回 `grilling`；若需求已定但新增技术路径仍处于 Fog，才进行定向 `wayfinding`。

### 2. 调查代码库

如果当前会话还没有完成足够的调查，写 SPEC 前先查清：

- 适用的 `AGENTS.md`、领域 glossary、架构说明和相关 ADR；
- 当前外部行为、相关模块与调用关系、既有接口和约束；
- 现有测试通过哪些 seam 验证相似行为，以及有哪些 prior art 可以沿用；
- 用户已有工作区改动，避免覆盖或把无关变化纳入规格。

SPEC 使用项目自身的领域语言。调查到足以确定范围、接口和验证边界即可，不进入实现阶段。

### 3. 设计并确认测试 seam

在写正式 SPEC 前，先草拟这次变更应通过哪些 seam 测试，并寻找可以形成 deep module 的边界：用小而稳定的接口封装较多功能，让测试约束外部行为，而不是内部结构。

Amendment 模式只重新评估受影响的 seam；既有测试决策仍覆盖变更后行为时，保留原决定并在 impact summary 中说明，无需再次确认。只有 seam、覆盖行为或 expected result 来源变化时才重新请求确认。

- 优先使用既有 seam；确需新增时，选择能够覆盖目标行为的最高层 seam。
- seam 越少越好；如果一个稳定 seam 足以覆盖整项变更，优先只使用一个。
- 说明每个 seam 覆盖哪些行为、expected result 的来源，以及仓库中是否有相似测试可供参考。
- 不为了方便测试而预设不必要的生产接口，也不把文件路径、内部调用顺序或 mock 结构当成 contract。

向用户简洁说明建议的 seam、选择依据和必要取舍，并请用户确认。这一步只确认实现与测试边界，不重新进行全面的需求访谈。如果确认过程中出现新的产品、协议、架构、范围或验收选择，先回到 `grilling` 或 `wayfinding` 收敛，再继续生成 SPEC。

### 4. 写 SPEC.md

Create 模式在用户确认测试 seam 后使用以下结构写正式文档；Amendment 模式保持同一结构并原位更新受影响章节。章节内容必须具体；不适用的内容明确说明为什么不适用，不使用占位符。

```markdown
# <Spec title>

## Problem Statement

<从用户或调用方视角说明什么缺失或有问题，以及为什么值得解决。>

## Requirement Authority

- Mode: <repository | integrated | external-manual | auto>
- Source: <项目内入口、已配置集成或用户确认的快照；不得编造链接>
- Snapshot boundary: <本 SPEC 覆盖的需求版本、日期或本次输入边界>
- Unverified: <未从原始来源验证的内容，或 None>

## Solution

<从用户或调用方视角描述解决方案的整体方向，不写逐步实现配方。>

## Destination

<全部 in-scope 行为完成后可观察的目标状态与边界。>

## User Stories

1. **R1** — As a <domain actor>, I want <behavior>, so that <benefit>.
2. **R2** — ...

## Boundaries and Defaults

- <输入来源、默认行为、失败/取消行为、权限或兼容性边界。>

## Implementation Decisions

- <已确认的模块、稳定接口、架构、schema、API contract 或交互决策。>

## Testing Decisions

- <已确认的测试 seam、覆盖行为、测试层级、expected result 来源和相关 prior art。>

## Acceptance Criteria

- **AC1** — Covers: R1. <可在不查看实现细节的情况下独立判定的结果。> Expected source: <用户确认、decision、公开 contract、协议、worked example 或其他权威依据>.

## Out of Scope

- <明确不属于本次交付的内容。>

## Further Notes

- <必要的决策依据、相对链接或无法放入以上章节但下游必须保留的信息。>
```

写作规则：

- User Stories 使用稳定 `R1`、`R2`…，列出一份详尽的行为清单，逐项编号并确保可以独立检查，覆盖功能的所有已确认情形。每条说明 actor、行为与价值。如果工作没有传统终端用户，就使用真实的领域角色或调用方，不虚构 persona。
- Implementation Decisions 记录已经确定的模块、接口和技术选择，但不写容易过期的具体文件路径或代码片段。唯一例外是原型产出的状态机、reducer、schema 或类型形状比文字描述更准确时，可以内联最能体现决策的必要片段，并注明来源。
- Testing Decisions 必须记录已确认的 seam、为什么选择它、从该 seam 观察哪些外部行为、expected result 的独立来源，以及可参考的现有测试。
- Acceptance Criteria 使用稳定 `AC1`、`AC2`…，明确覆盖的 `R`；每个 in-scope `R` 至少被一个 AC 覆盖。AC 验证外部行为，不锁定类名、文件结构、内部调用顺序或某种实现方案，除非它们本身就是明确 contract。
- 从 Map 压缩而来时，在 Implementation Decisions 或 Further Notes 中记录必要 decision 的相对链接或名称，使后续 session 能追溯“决定了什么、为什么”。

### 5. 一致性检查

生成后静态检查：

1. Problem、Solution 与 Destination 描述的是同一个问题和目标；
2. `R` 与 `AC` ID 唯一且稳定，每个 in-scope `R` 至少被一个 AC 覆盖；
3. 每个 AC 都可独立判定，并能追溯到已确认需求或权威 expected source；
4. Implementation Decisions 与已调查的代码库、glossary 和 ADR 一致；
5. Testing Decisions 完整记录用户确认的 seam，并尽可能从最高层 seam 验证外部行为；
6. Boundaries、默认行为、Out of Scope 与验收没有冲突或悄然扩张；
7. 文档中没有占位符、未处理冲突、虚构事实或被静默跳过的 blocker。
8. Requirement Authority 如实记录来源、快照边界和未验证项；外部系统不可访问时没有虚构验证。
9. Amendment 模式保留未受影响的 R/AC ID，并对整份 SPEC 重新完成一致性检查，而不只检查 delta。

能根据已确认上下文或代码库事实修正的问题直接修正；需要新决策时，停止并交回 `grilling` 或 `wayfinding`。

### 6. 落盘与 handoff

确认一致性后写入任务目录 `SPEC.md`。Create 模式报告路径、采用的测试 seam、关键实现/测试决策和未验证项；Amendment 模式先展示需求 delta、规范影响与可能受影响的 tickets，取得确认后原位更新，并报告保留/新增/移除的 R/AC。`to-spec` 不修改 ticket contract、Status 或 evidence；这些由 `to-tickets` 在 SPEC 确认后协调。不要在 SPEC 中维护 task、frontier、status、retry、Agent 分配或其他 execution graph。

SPEC 获确认后：

- 单一 scoped task、不需要 execution graph 时，直接交给 `quick-implement`；
- 需要多个可独立领取的工作单元、dependency edge 或统一调度时，调用 `to-tickets`；由它提出拆分、取得确认并创建 `tickets/`，再交给 `loop` 推进完整 graph。

本 Skill 不拆 tickets、不实现业务代码，也不自动获得外部发布、commit、push、建分支或改写历史的授权。

## 变更规则

- **规范性变化**：进入 Amendment 模式。需求、范围、接口 contract、testing decision、acceptance criterion 或明确约束变化时，更新同一份 SPEC 并重新确认受影响决策；testing seam 未受影响时不强制重新确认。已有 graph 且受影响 ticket 正在执行时，请求 `loop` 停止新的相关 dispatch、终止或收回对应 worker 并保留 evidence；确认其不再写入后，再由 `to-tickets` 同步受影响 tickets。
- **执行拆分变化**：SPEC 语义不变，但 ticket 粒度或依赖经新事实证明不合理时，仅由 `to-tickets` 调整 tickets，不能反向改写 SPEC。
- **执行变化**：ticket 完成、验证失败、retry、frontier 或 execution evidence 变化只更新对应 ticket 或执行证据，不改 SPEC。
