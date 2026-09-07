# SPEC.md 模板

Create 与 Amendment 使用同一结构。章节必须具体；不适用的写明原因，不用占位符。

```markdown
# <Spec title>

## Problem Statement

<从用户或调用方视角说明什么缺失或有问题，以及为什么值得解决。>

## Requirement Authority

- Mode: <repository | integrated | external-manual | auto>
- Source: <项目内入口、已配置集成或用户确认的快照，不得编造链接>
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

## Solution Constraints

- <由需求权威、用户或项目规则已经固定、概要设计不得改变的技术与公开 contract 约束，没有则写 None。>

## Testing Decisions

- <已确认的测试 seam、覆盖行为、测试层级、expected result 来源和相关 prior art。>

## Acceptance Criteria

- **AC1** — Covers: R1. <可在不查看实现细节的情况下独立判定的结果。> Expected source: <用户确认、decision、公开 contract、协议、worked example 或其他权威依据>.

## Out of Scope

- <明确不属于本次交付的内容。>

## Further Notes

- <必要的决策依据、相对链接或无法放入以上章节但下游必须保留的信息。>
```

## 写作规则

- User Stories 使用稳定 `R1`、`R2`…，列出一份可独立检查的详尽行为清单，覆盖功能的所有已确认情形。每条说明 actor、行为与价值。没有传统终端用户时，使用真实的领域角色或调用方，不虚构 persona。
- Solution Constraints 只记录上游已经确认、HLD 不得改变的技术或公开 contract 约束，不记录由 Agent 推导的模块划分、内部 Interface、共享类型或依赖方向。原型产出的公开状态机、schema 或类型形状比文字更准确时，可以内联必要片段并注明来源。
- 旧 SPEC 中已有 `Implementation Decisions` 时，先区分上游固定约束与派生设计：前者迁入 Solution Constraints，后者由 `high-level-design` 在用户确认后迁入 HLD。迁移完成前不得在两处维护同一决定。
- Testing Decisions 必须记录已确认的 seam、选择依据、从该 seam 观察哪些外部行为、expected result 的独立来源，以及可参考的现有测试。
- Acceptance Criteria 使用稳定 `AC1`、`AC2`…并明确覆盖的 `R`。每个 in-scope `R` 至少被一个 `AC` 覆盖。`AC` 验证外部行为，不锁定类名、文件结构、内部调用顺序或某种实现方案，除非它们本身就是明确 contract。
- 从 Map 压缩而来时，影响需求或公开 contract 的决定记录在 Solution Constraints 或 Further Notes，纯技术决定交给 HLD，并保留必要的相对链接或名称供后续 session 追溯。
