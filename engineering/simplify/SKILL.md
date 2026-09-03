---
name: simplify
description: "用于审计或移除已有代码或当前 diff 中的偶然复杂度；审计只读，修改需明确授权。"
---

# Simplify

减少代码库需要长期保持一致的概念、状态、契约和维护义务。删除代码行只是结果，不是目标；没有安全可删项也是有效结果。

尤其关注由 AI coding、测试便利、历史实验和推测性扩展产生，但没有当前生产职责的维护义务。测试可运行、抽象规范或代码“看起来专业”都不能单独证明某个生产接口值得长期存在。

## 模式

- **审查模式**：用户要求审计、发现或评估简化机会时，只读调查并返回证据排序。适合长期 AI coding 后的周期性累积复杂度清理。
- **修改模式**：用户明确要求简化、删除、合并或收缩实现时，在授权范围内修改并验证。

默认聚焦当前任务 diff 或用户明确指定的职责范围。只有显式全库/多候选请求才使用全库审查；全库审查或涉及动态架构时读取 `references/investigation.md`。

## 流程

1. 固定对比基准、当前任务 diff、既有改动、行为来源、允许修改的职责范围，以及必须保留的 SPEC、协议和外部可观察行为。
2. 阅读生产调用方、测试调用方、组装点和外部边界；对消费者区分 `runtime`、`support-only`、`uncertain`。静态搜索和 smell 只能生成线索，不能单独作为删除依据；需要更完整调查时读取 `references/investigation.md`。
3. 使用 `references/candidates.md` 寻找维护义务：优先处理同一事实存在多份表示、没有实际需求支撑的扩展性、纯转发层、重复状态机、辅助用途维持的无效接口、已移除功能的残留，以及无生产消费者的接口或抽象。对 injection point、测试接缝、callback、hook、wrapper、factory、strategy、fallback 和 debug state，额外检查它们是否主要由验证需求而不是生产需求驱动。
4. 对疑似为测试便利引入的生产架构，先回答：没有测试时它是否仍需要存在；是否有真实生产消费者需要替换该 dependency；是否对应真实 ownership / failure / process / I/O boundary；删除后是否仍能通过公开生产行为验证 correctness。`No / No / No / Yes` 是强候选信号，但不是自动删除授权。
5. 优先完整移除一个职责边界内的维护义务，而不是局部减少代码；检查对应 declaration、wiring、state、tests、config、docs、generated artifacts 和 dependency，保留项需有明确理由。
6. 保留输入校验、错误处理、安全、权限、可访问性、真实外部 adapter、持久化兼容、取消/dispose、事务和必要状态门禁。存在未解决的动态/外部消费者、迁移问题或行为保持证据不足时返回 `blocked`。
7. 修改后至少执行残留检查、能够发现误删的最小必要验证，以及差异审查。若改变需求、公开约定或验收，停止并转回 `grilling` / `to-spec`；若只改变多处实现共用的职责归属、共享设计约束、依赖方向或集成约束，停止并转回 `high-level-design`。上游产物修订后，再由 `quick-implement` 或 `loop` 按原执行范围继续。

## 输出

- 审查模式：Markdown receipt，包含结果（`completed | no_change | blocked | failed`）、coverage、排序候选、rejected/unresolved 项、证据与下一项所需事实。
- 修改模式：Markdown receipt，包含结果、改动文件、移除的维护义务、接口变化、保持的不变量、验证、剩余风险；有不可逆副作用时补充恢复方式。
