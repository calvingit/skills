---
name: quick-implement
description: "在已确认的 SPEC 与可选 HLD 约束下完成无需 ticket graph 的单次实现、验证和审查。"
---

# Quick Implement

在一个 fresh context 内完成已确认 `SPEC.md` 的单一范围，并在同目录存在时遵守 `HLD.md`，交付可复核 evidence。Quick 表示不需要 execution graph，不表示跳过概要设计检查、调查、验证、简化或审查。任务文档定义契约，不是代码配方；实现前必须重新调查当前仓库。

## 入口

开始前读取完整 `SPEC.md`，以及同目录存在的完整 `HLD.md`，确认需求、Solution Constraints、测试决策、边界、Acceptance Criteria 和适用 D IDs 已经确定，并且整个范围能在当前 context 内可靠完成。

- 没有已确认 SPEC 时，交回 `grilling` / `wayfinding` / `to-spec` 收敛需求契约；
- 没有 HLD，但存在跨 Module、跨调用方或跨 execution unit 的共享类型、Interface、状态/错误语义、依赖方向或集成选择时，交回 `high-level-design`；
- HLD 存在冲突、缺口或已被代码事实证明不可行时停止，由 `high-level-design` 修订，不能在实现中静默改变共享 contract；
- 范围需要多个执行单元、dependency edge 或跨多个 fresh context 时，交给 `to-tickets` 创建 graph，再由 `loop` 执行；
- 已经存在 ticket graph 时，不使用本 skill，直接使用 `loop`。

## 调查与方案

1. 记录 `HEAD`、staged/unstaged/untracked 状态和 baseline，保护既有改动；
2. 动态发现仓库指导文件、coding standards、领域词汇、长期决策、相关代码、调用链、错误路径、测试和配置；适用 `AGENTS.md` 存在 `Engineering Skills Profile` 时把它作为项目入口索引，没有时继续发现现有结构；
3. 形成当前交付的最小实现方案；HLD 已约束的共享 contract 必须遵守，只对 Local Design Freedom 内的 Module 内部结构、private helper、文件组织和算法应用 `codebase-design` 或作局部详细设计；
4. 发现会改变行为、公开 contract、权限、验收或范围的新事实时停止并回到 `grilling` / `wayfinding` / `to-spec`；只改变跨局部技术设计时回到 `high-level-design`。

## 实现循环

- 每个 delivery slice 先确定外部可观察行为和真实生产 Seam，再写最小实现；
- 当任务适合 test-first、需求已有可独立判定的 expected behavior 且存在稳定 Seam 时，应用 `tdd` 的 red → green vertical-slice 循环；
- TDD 不适用时，使用目标仓库已有的最小充分反馈循环，不为测试制造生产接口；
- 实现过程中持续运行当前 slice 的定向测试和相关 typecheck，不把反馈全部留到收尾。

## 收尾

1. 基于当前交付的完整 diff 执行 `simplify`；没有本任务代码改动则记录 `no_change`；
2. 按 [references/verification-and-review.md](references/verification-and-review.md) 运行定向验证和项目定义的适用交付 gate；
3. 按同一 reference 使用 `code-review` 的 implementation mode 分别审查 Standards、SPEC，以及存在 HLD 时的 HLD conformance；修复 findings 后重新运行受影响验证与审查；
4. 只有全部 Acceptance Criteria 都有可观察 evidence 时才宣告完成；
5. 只有用户明确授权时才 commit；不自动 push，提交范围只含本任务改动。

## 边界

- 不修改 SPEC/HLD 以迎合实现；需求或验收变化回到 `to-spec`，概要技术设计变化回到 `high-level-design`；
- 不创建 ticket、维护 execution graph 或调度其他工作单元；
- 不把当前完整工作再次委托给另一个 implementer；reviewer 或其他专门角色仍按其 Skill 职责使用；
- 不覆盖既有改动，不静默吞错；
- 不把模型自报、单次测试通过或实现细节检查当作完整验收证据；
- 不把项目规则塞回通用 Skill。

输出 implementation receipt，列明 SPEC/HLD、baseline、既有改动、实际 landed changes、逐条验收 evidence、验证、simplification、Standards / SPEC / HLD 条件式审查和未验证项。
