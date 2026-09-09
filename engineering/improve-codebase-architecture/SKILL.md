---
name: improve-codebase-architecture
description: "扫描代码库中的 shallow Modules 与 deepening 机会，生成可视化候选报告，并在用户选择后收敛目标设计。"
---

# Improve Codebase Architecture

本内容是 `review-architecture` 的主动候选模式，不是独立流程。需要主动寻找 shallow Module 的 deepening opportunity 时，在架构审查中启用本模式；普通架构审查不加载本文件。

## Process

1. **确定扫描范围**：如果用户指定了 Module、子系统或痛点，就以此为范围；否则读取一段 Git history，寻找高频变化的热点。开始扫描前，先读项目 glossary、相关 ADR 和 `codebase-design` 的 canonical vocabulary。
2. **寻找候选**：调查理解一个概念是否需要跨越多个 shallow Modules、Interface 是否接近 Implementation、测试是否越过 Interface、耦合是否泄漏，以及 deletion test 是否表明复杂度会扩散回调用方。不要按固定 checklist 制造候选。
3. **生成报告**：按 [references/HTML-REPORT.md](references/HTML-REPORT.md) 在系统临时目录生成自包含 HTML，不写入仓库。每个候选包含涉及 Modules、实际摩擦、deepening 方向、Leverage / Locality / 测试收益、before / after 图和 `Strong | Worth exploring | Speculative` 推荐强度。
4. **等待选择**：先展示报告路径和最高推荐，不提前设计 Interface。用户选定候选后，使用 `grilling` 收敛约束、依赖、目标 Module、Seam 和测试；`grilling` 会通过 domain-modeling discipline 同步维护 glossary 与必要 ADR。
5. **深入设计**：依赖分类复杂时读取 `../codebase-design/DEEPENING.md`；用户要求多方案或单一方案不足以判断时读取 `../codebase-design/DESIGN-IT-TWICE.md`。

本模式只调查和报告，不修改业务代码。形成需求契约交给 `to-spec`；需要共享设计约定时交给 `high-level-design`，再按范围进入 `quick-implement` 或 `loop`。
