---
name: review-architecture
description: "评审既有架构是否符合项目约束与相关技术标准，输出有证据支撑的只读 findings；目标模块或边界设计使用 codebase-design。"
---

# Review Architecture

## Goal

对现有代码库或指定子系统执行只读架构评审，判断当前设计是否合理、是否符合项目已声明的架构约束，以及在相关技术栈存在明确官方指导时是否存在有实际影响的偏离。

重点回答：**当前 architecture 是否 sound，问题在哪里，为什么是问题，影响是什么。** 不负责设计最终目标架构，也不在本 Skill 内实施重构。

与 `codebase-design` 的边界：本 Skill 负责判断 **WHETHER 当前设计合理**；当某个 finding 已确认需要调整后，由 `codebase-design` 判断 **HOW 目标 boundary / Interface / Seam 应该设计**。

## Review authority

按以下优先级判断，不把个人偏好包装成规范：

1. 用户明确要求和当前任务约束；
2. 仓库级 Agent 指令、架构文档、ADR、coding standards 和测试/构建规则；
3. 当前代码、调用链、运行路径、测试和可执行检查证明的事实；
4. 与当前问题直接相关、可确认仍有效的技术栈官方架构或最佳实践；需要外部最新依据时使用 `find-docs`，并区分项目规则与外部建议；
5. 通用设计原则只作为分析 lens，不能单独证明“不合规”。

需要讨论 Module、Interface、Depth、Seam、Adapter、Leverage、Locality 等概念时，可参考 `codebase-design` 的共享设计纪律；但本 Skill 的职责是 **review current design**，不是提前完成 redesign。

## Boundaries

- 默认只读；不修改源码、测试、配置、规则、baseline 或架构文档。
- 不负责形成具体目标架构；需要设计目标 boundary / Interface / Seam 时转给 `codebase-design`。
- 不把目录结构、命名风格或“看起来不优雅”自动升级为架构问题。
- 不把普通 bug、局部代码质量或性能问题纳入，除非证据表明根因来自 ownership、boundary、dependency、state lifecycle 或 architecture policy。
- 不强行套用 Clean Architecture、DDD、MVVM 等固定风格；只有项目选择了该约束，或技术栈官方规则与当前问题直接相关时才检查符合度。
- finding 必须包含当前 evidence、实际影响和期望的架构结果；候选阶段不写文件级实现配方。
- 范围未覆盖的部分明确列为 blind spot，不假装完成全仓库审计。

## Workflow

### 1. Define scope and review question

先明确本轮评审对象和判断标准。

- 用户指定 Module、子系统、feature 或痛点时，以该范围及其直接调用方、依赖和 composition 边界为主。
- 用户要求全局架构评审时，先建立顶层 runtime / module map，再按 responsibility 分区；不要按文件数量机械抽样。
- 范围过大时说明本轮 coverage 和未覆盖部分，并优先评审高耦合、高变更或关键 runtime path。

### 2. Discover current architecture and rules

适用 `AGENTS.md` 的 `Engineering Skills Profile` 指定 architecture authorities 时，将其作为项目声明入口并继续用当前代码验证；没有 Profile 时沿用动态发现，不自动运行 setup。

按实际存在情况读取：

- README、CONTRIBUTING、Agent 指令、architecture docs、ADR / decision records；
- 入口、composition/configuration、Module/package 边界、依赖声明和测试布局；
- 与范围相关的 lint、dependency checks、architecture guards、build/test commands；
- 技术栈官方规则，仅在其会实质影响当前判断时查询。

文档声明不是自动事实：检查当前代码是否仍与其一致。历史记录用于解释设计理由，不替代当前 evidence。

### 3. Review through architecture lenses

按需读取 `references/classification-guide.md`。重点检查：

- **Boundary / Ownership**：职责、状态、知识和副作用是否由正确 Module 拥有；
- **Dependency direction**：依赖是否跨越不应跨越的层或形成循环、反向知识泄漏；
- **Interface / Depth**：Interface 是否隐藏复杂度，调用方是否被迫理解 Implementation；
- **State / Lifecycle**：状态 owner、并发、初始化、取消、释放和恢复是否与使用范围一致；
- **Data / Control Flow**：数据转换、错误、事件和副作用是否被多处重复解释；
- **Testability / Replaceability**：测试是否通过生产 Interface 验证行为，Seam 是否代表真实变化边界；
- **Standards conformance**：是否违反项目已声明约束或与当前场景直接相关的官方技术栈规则；
- **Evolution cost**：一个正常需求是否需要跨越过多 owners、同步多个事实或修改不相关区域。

这些是 investigation lenses，不是必须逐项打分的 checklist。

### 4. Deep-read and seek counter-evidence

只对最强候选追踪完整关系：目标 Module、代表性调用方、下游依赖、composition 入口、相关测试，以及必要的数据流或控制流。

每个结论明确区分：

- **Observed**：当前代码、symbol、调用关系、测试、规则或命令直接证明；
- **Inferred**：由多项 Observed evidence 推导，明确说明推理；
- **External guidance**：来自技术栈官方资料，标明它是项目硬约束还是建议；
- **Unknown**：信息不足，不能假设成立。

主动寻找反证。现有设计如果确实隔离 failure domain、保护兼容性、集中复杂度或满足真实替换边界，应降级或否定 candidate。

### 5. Classify findings by impact

finding 不按“违反了多少原则”排序，而按 evidence 与实际影响排序：

- `Critical`：可能导致数据、安全、权限、持久化兼容或系统级生命周期错误；
- `High`：持续造成明显变更扩散、错误 ownership、依赖失控或难以可靠验证；
- `Medium`：存在稳定的架构摩擦和维护成本，但影响局部且可控；
- `Low`：轻微偏离或改进机会，不足以单独推动架构变更；
- `Speculative`：信号存在但关键事实未知，不作为确定 finding。

没有成立问题时明确输出 `no finding`；不要为了报告完整度制造架构债。

### 6. Report and stop

使用 `references/report-template.md` 输出 Markdown 架构评审。报告应明确：

- scope / coverage / blind spots；
- 当前 architecture 与适用 authorities；
- findings 及 evidence、impact、rule/guidance basis；
- not findings / counter-evidence；
- recommendation direction 和需要进一步确认的问题。

本 Skill 到评审结论为止。若用户选择处理某项 finding：

- 需要收敛目标 boundary / Interface → `codebase-design`；
- 需求或权衡未确定 → `grilling`；
- 需要正式任务契约 → `to-spec`；
- 已有明确方案 → `implement`；
- 目标只是删除已证明不必要的复杂度 → `simplify`。

## Done when

- 已说明评审范围、判断依据和未覆盖部分；
- 当前架构事实来自代码、关系、测试或可运行检查，而非只复述文档；
- 项目规则、外部官方 guidance 与通用设计判断被明确区分；
- 每个 finding 都有 evidence、impact 和对应的 architecture concern；
- 已寻找并记录重要反证，不把合理 trade-off 误判成问题；
- 报告给出 `Critical/High/Medium/Low/Speculative` 或 `no finding` 的明确结论；
- 没有在架构评审阶段越权进入 redesign 或 implementation。
