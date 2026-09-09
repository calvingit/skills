---
name: quick-implement
description: "在已确认目标及存在时的 SPEC/HLD 约束下完成无需 execution graph 的单次实现、验证和审查。"
---

# Quick Implement

在一个 fresh context 内完成已确认目标的单一范围，并在同目录存在时遵守 `SPEC.md` 与 `HLD.md`，交付可复核 evidence。目标契约可以只存在于当前会话；Quick 表示不需要 execution graph，不表示跳过概要设计检查、调查、验证、简化或审查。任务文档定义契约，不是代码配方；实现前必须重新调查当前仓库。

## 入口

开始前确认目标、范围和可判定结果；有 `SPEC.md`、独立 `ACCEPTANCE.md` 或 `HLD.md` 时读取并遵守，没有这些文件不阻塞。确认整个范围能够在当前 context 内可靠完成。

- 目标、范围或结果仍未明确时，交回 `grilling` / `wayfinding`；只有需要持久化、共享或版本化需求时才调用 `to-spec` 创建 `SPEC.md`。
- 没有 HLD，但存在跨 Module、跨调用方或跨实现任务的共享类型、Interface、状态 / 错误语义、依赖方向或集成选择时，交回 `high-level-design`。
- HLD 存在冲突、缺口或已被代码事实证明不可行时停止，由 `high-level-design` 修订，不能在实现中静默改变共享 contract。
- 范围需要多个执行单元、依赖关系或跨多个 fresh context 时，交给 `to-tickets` 创建 graph，再由 `loop` 执行。
- 已经存在 ticket graph 时，不使用本 Skill，直接使用 `loop`。

## 调查与方案

1. 记录 `HEAD`、staged / unstaged / untracked 状态和 baseline，保护既有改动；
2. 动态发现仓库指导文件、coding standards、领域词汇、长期决策、相关代码、调用链、错误路径、测试和配置；适用 `AGENTS.md` 存在 `Engineering Skills Profile` 时把它作为项目入口索引，没有时继续发现现有结构；
3. 形成当前交付的最小实现方案；HLD 已约束的共享 contract 必须遵守，只对局部实现空间内的 Module 内部结构、private helper、文件组织和算法应用 `codebase-design` 或作局部详细设计；
4. 发现会改变行为、公开约定、权限、验收或范围的新事实时停止并交回 `grilling` / `wayfinding` / `to-spec`；只改变多处实现共用的技术设计时交回 `high-level-design`。

## 实现循环

- 每个 delivery slice 先确定外部可观察行为和真实生产 Seam，再写最小实现。
- 当任务适合 test-first、需求已有可独立判定的 expected behavior 且存在稳定 Seam 时，应用 `tdd` 的 red → green vertical-slice 循环。
- TDD 不适用时，使用目标仓库已有的最小充分反馈循环，不为测试制造生产接口。
- 实现过程中持续运行当前 slice 的定向测试和相关 typecheck，不把反馈全部留到收尾。

## 收尾

1. 当前 diff 存在明确复杂度问题或用户要求时执行 `simplify`；否则跳过并说明；
2. 按 [references/verification-and-review.md](references/verification-and-review.md) 运行定向验证和项目定义的适用交付 gate；
3. 按同一 reference 使用 `code-review` 的 implementation mode 完成 Contract、Change-surface、Exploratory 三层审查，将项目规范、SPEC 和适用 HLD 作为依据；修复审查发现后重新运行受影响验证与审查；
4. 只有全部适用 Acceptance Criteria 有可观察 evidence，必要验证和审查通过且没有未解决高风险问题时才宣告完成；
5. 只有用户明确授权时才 commit；不自动 push，提交范围只含本任务改动。

## 边界

- 不修改 SPEC / HLD 以迎合实现；需求或验收变化交回 `to-spec`，概要技术设计变化交回 `high-level-design`。
- 不创建 ticket、维护 execution graph 或调度其他工作单元。
- 不把当前完整工作再次委托给另一个实现者；reviewer 或其他专门角色仍按其 Skill 职责使用。
- 不覆盖既有改动，不静默吞错。
- 不把模型自报、单次测试通过或实现细节检查当作完整验收证据。
- 不把项目规则塞回通用 Skill。

输出实现回执，列明适用的 SPEC / ACCEPTANCE / HLD、baseline、既有改动、实际改动、验收 evidence、验证、按需 simplification、审查结果和未验证项。
