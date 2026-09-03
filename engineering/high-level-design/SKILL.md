---
name: high-level-design
description: "为已确认的 SPEC 创建或修订任务级 HLD.md，确定跨局部实现的模块职责、共享契约、依赖方向、数据/控制流与集成约束；不处理 UI/UX、ticket 拆分或局部详细设计。"
---

# High-Level Design

以已确认的 `SPEC.md` 和当前代码库事实为输入，为一次交付形成概要技术设计。只有存在不能安全留给单个 implementer 决定的跨局部技术契约时才创建任务目录中的 `HLD.md`；不要为了流程完整生成空文档。

`HLD.md` 是当前交付的概要技术设计权威，约束跨 Module、跨调用方或跨 execution unit 的实现。它不是 UI/UX、视觉或交互稿，也不规定 private method、局部 helper、单一调用方的内部 callback 等详细设计。

## 权威与边界

- `SPEC.md` 决定需求、外部行为、验收、业务边界和已确认的 Solution Constraints。
- `HLD.md` 从 SPEC 与代码库事实推导模块职责、共享类型、内部 Interface、依赖方向、数据/控制流、状态与错误语义、迁移和集成约束。
- `tickets/*.md` 只派生交付分解和 blocking edges；实现代码负责 HLD 未约束的局部详细设计。
- HLD 不得改变 SPEC。两者冲突时停止，由 `to-spec` 先修正规范或由本 Skill 修正设计，不能自行选择一份继续实现。
- 本 Skill 可以应用 `codebase-design` 判断具体 Module / Interface / Seam，但不复制其通用设计规则。

## 是否需要 HLD

先读取完整 SPEC、适用 Agent 指令、架构/领域文档、ADR、相关代码与调用链。出现以下任一情况时需要 HLD：

- 多个 Module、调用方或 execution unit 必须共享类型、枚举、schema、事件、错误模型或 callback contract；
- 需要新增或改变公共/跨模块 Interface、ownership、dependency direction 或稳定 Seam；
- 多处实现必须遵守同一状态机、生命周期、并发、取消或调用顺序；
- 需要 expand-contract、数据迁移、兼容窗口或明确的集成顺序；
- 用户或项目规则明确要求一项跨局部实现的技术约束。

ticket 数量不是判断条件：单一执行单元也可能需要 HLD，多个相互独立的 tickets 也可能不需要。若以上条件均不成立，报告 `hld_not_required` 及依据，不创建 `HLD.md`。

需求、外部 contract、权限、范围或验收仍未确定时停止并交回 `grilling` / `to-spec`。关键技术路径仍处于需要跨 session 探索的 Fog 时交回 `wayfinding`；完成的纯技术 decision 可以由本 Skill 吸收，若它改变 SPEC 则必须先回到 `to-spec`。

## 模式

- **Create**：需要 HLD，且任务目录中不存在 `HLD.md`。
- **Amendment**：已有 HLD，且 SPEC、代码库事实或已确认设计发生变化；只修订同一文件，不创建并行版本。
- **Not required**：不存在跨局部技术契约；仅报告判断，不写 artifact。

## Process

1. 固定当前 SPEC、代码库 baseline、既有改动和适用项目约束。
2. 描述当前调用链、ownership、已有 Interface、共享数据形状、外部边界和必须保留的不变量；区分 Observed / Inferred / Unknown。
3. 找出下游实现若各自决定会产生不一致的设计点。只为这些点形成目标设计，局部实现继续保留自由。
4. 对关键 Module / Interface / Seam 应用 `codebase-design`。有多个真实候选时最多比较 2–3 个，说明收益、成本、迁移影响和验证方式。
5. 为每项规范性概要决定分配稳定的 `D1`、`D2`… ID，并标明它约束的 SPEC R/AC、调用方或模块。
6. 向用户展示设计摘要、关键取舍、Local Design Freedom 和未验证项；确认后创建或修订 HLD。
7. 检查 HLD 与 SPEC、项目 ADR、现有架构事实和自身各章节一致；没有未处理冲突或会改变方案的 Unknown 才完成。

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

<与本次设计相关的现有调用链、ownership、Interface 和约束。>

## Design Decisions

- **D1** — <跨局部设计决定>
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

- <共享 contract 在哪个 vertical slice 落地、迁移顺序、兼容窗口和删除条件>

## Verification Seams

- <如何验证概要设计和跨模块行为，不复制 SPEC 的 Acceptance Criteria>

## Local Design Freedom

- <留给 implementer 决定的局部类、函数、文件组织和算法>

## Open Questions

- None
```

不要默认枚举所有 class、文件或方法。只有名称或签名本身会被多个消费者共享、承担真实 contract，或是用户/项目明确约束时才写入。不要为尚无真实调用方的抽象预建 Interface。

## Amendment

先比较旧/新 SPEC、当前 HLD、代码库事实和现有 tickets，把设计变化分类为 `added`、`changed`、`removed` 或 `no design effect`：

- 保留未受影响的 D ID；新增决定追加新 ID，不重新编号。
- 需求或外部行为变化先由 `to-spec` 修订 SPEC，再修订 HLD。
- 设计变化但需求不变时，只更新 HLD，不反向改写 SPEC。
- 已有 graph 时只读检查哪些 ticket 引用了受影响 D、哪些 landed behavior 仍有效，以及需要 amendment、correction、migration 或 replacement；不修改 ticket。
- 受影响 worker 仍在写入时，请求 `loop` 停止新 dispatch、回收 partial receipt 并确认不再写入。
- 向用户展示 design delta 与 ticket impact，确认后更新同一份 HLD，再交给 `to-tickets` 协调 graph。

实现中发现 HLD 无法成立时，worker 必须返回 blocker；不能自行改变共享 contract 后继续。修订 HLD 后再按实际影响恢复执行。

## Handoff

完成后报告 HLD 路径、D IDs、Local Design Freedom、未验证项和下游影响：

- 无需 execution graph：交给 `quick-implement`；
- 需要多个 execution units、blocking edges 或统一调度：交给 `to-tickets`；
- 已有 graph 且发生 HLD amendment：交给 `to-tickets` 同步受影响 tickets。

本 Skill 不拆 ticket、不实现代码、不制作 UI/UX 稿，也不自动获得 commit、push、建分支或改写历史的授权。
