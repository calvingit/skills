# HLD 创建

需要 HLD 且任务目录中不存在 `HLD.md` 时读取本文件。判断是否需要 HLD 时不要加载本文件。

## Process

1. 固定当前 SPEC、代码库对比基准、既有改动和适用项目约束。
2. 先进行广度调查，再深入核对 1–3 个最相关的参考实现；记录路径、symbol 和选择依据。
3. 描述当前调用链、职责归属、已有 Interface、共享数据形状、外部边界和必须保留的不变量；区分已观察事实 / 推断 / 未知。
4. 找出下游实现若各自决定会产生不一致的设计点。只为这些点形成目标设计，局部实现继续保留自由。
5. 对每个设计点优先 `Reuse`，其次 `Extend`；只有现有结构不能满足 SPEC 时才 `New` 或 `Replace`。后两者必须说明为什么 `Reuse` / `Extend` 不成立、迁移影响和控制范围。
6. 对关键 Module / Interface / Seam 应用 `codebase-design`。只有证据不足以确定单一方案时才比较最多 2–3 个真实候选；普通工程取舍由本 Skill 推荐并决定。
7. 为每项规范性概要决定分配稳定的 `D1`、`D2`… ID，标明变化性质、参考实现，以及它约束的 SPEC `R`/`AC`、调用方或模块。
8. 检查 HLD 与 SPEC、项目 ADR、现有架构事实和自身各章节一致；执行多实现者一致性检查，没有未处理冲突或会改变方案的未知项才创建 HLD。

## HLD.md

只保留适用章节，不为填满模板虚构内容：

```markdown
# <Change title> — High-Level Design

## Authority

- Specification: [SPEC.md](SPEC.md)
- Baseline: <commit or equivalent fixed point>
- Scope: <covered R/AC>
- Unverified: <items or None>

## Current Structure

<与本次设计相关的现有调用链、职责归属、Interface 和约束；列出 1–3 个主要参考实现及路径 / symbol。>

## Design Decisions

- **D1** — <影响多处实现的设计决定>
  - Change: <Reuse | Extend | New | Replace>
  - 参考实现：<existing path / symbol or None>
  - Covers: <R/AC、Module 或调用方>
  - Rationale: <为什么>
  - Consequences: <下游必须遵守什么>

## Modules and Ownership

- <Module>: <拥有的状态、规则、外部交互或稳定边界>

## Shared Contracts

- <共享类型、枚举、schema、event、callback、Interface、错误或生命周期语义>

## Data and Control Flow

<只描述跨模块的重要流程。>

## Dependency Direction

- <允许和禁止的依赖方向>

## Integration and Migration

- <共享设计约束在哪个端到端交付任务落地、迁移顺序、兼容窗口和删除条件>

## Verification Seams

- <如何验证概要设计和跨模块行为，不复制 SPEC 的 Acceptance Criteria>

## 局部实现空间

- <留给实现者决定的局部类、函数、文件组织和算法>

## Open Questions

- None
```

不要默认枚举所有 class、文件或方法。只有名称或签名本身会被多个调用方共享、承担真实接口约定，或是用户/项目明确约束时才写入。不要为尚无真实调用方的抽象预建 Interface。

`New` / `Replace` 必须解释现有参考实现为什么不能满足 SPEC。不要为追求理论一致性引入新的架构流派、平行抽象体系、基础设施改造或与当前交付无关的 cleanup。

## Done when

- 每个影响多处实现的设计决定都有代码库证据、变化性质和稳定 D ID。
- 方案优先复用或扩展现有结构，任何 `New` / `Replace` 都有必要性和迁移边界。
- 两个不共享实现上下文的实现者仅凭 SPEC、HLD 和各自 ticket，也会对共享类型、Interface 语义、职责归属、依赖方向和集成顺序作出一致选择。
- private helper、局部类、算法和文件组织仍保留在局部实现空间。
- 已有架构问题未被无授权地扩展为当前任务重构。
- 不存在必须由用户决定的未处理 SPEC 冲突。
