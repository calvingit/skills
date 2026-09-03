---
name: improve-codebase-architecture
description: "扫描代码库中的 shallow Modules 与 deepening 机会，生成可视化候选报告，并在用户选择后收敛目标设计。"
---

# Improve Codebase Architecture

寻找能把 shallow Modules 深化为 deep Modules 的架构候选，以提高 Leverage、Locality、可测试性和 Agent 可导航性。本 Skill 不替代只读的 `review-architecture`：后者判断当前设计是否 sound，本 Skill 则主动寻找并推进 deepening opportunity。

## Process

1. **确定扫描范围**：如果用户指定了 Module、子系统或痛点，就以此为范围；否则读取一段 Git history，寻找高频变化的热点。开始扫描前，先读项目 glossary、相关 ADR 和 `codebase-design` 的 canonical vocabulary。
2. **寻找候选**：调查理解一个概念是否需要跨越多个 shallow Modules、Interface 是否接近 Implementation、测试是否越过 Interface、耦合是否泄漏，以及 deletion test 是否表明复杂度会扩散回调用方。不要按固定 checklist 制造候选。
3. **生成报告**：按 [references/HTML-REPORT.md](references/HTML-REPORT.md) 在系统临时目录生成自包含 HTML，不写入仓库。每个候选包含涉及 Modules、实际摩擦、deepening 方向、Leverage/Locality/测试收益、before/after 图和 `Strong | Worth exploring | Speculative` 推荐强度。
4. **等待选择**：先展示报告路径和最高推荐，不提前设计 Interface。用户选定候选后，使用 `grilling` 收敛约束、依赖、目标 Module、Seam 和测试；`grilling` 会通过 domain-modeling discipline 同步维护 glossary 与必要 ADR。
5. **深入设计**：依赖分类复杂时读取 `../codebase-design/DEEPENING.md`；用户要求多方案或单一方案不足以判断时读取 `../codebase-design/DESIGN-IT-TWICE.md`。

本 Skill 只调查、报告和收敛设计，不修改业务代码。形成需求契约交给 `to-spec`；已确认 SPEC 存在跨局部技术契约时交给 `high-level-design` 汇总为 `HLD.md`，再由 `quick-implement` 或 `loop` 按 execution routing 执行。
