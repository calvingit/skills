# Simplification Candidates

用维护义务而不是代码行数寻找简化机会。以下分类用于生成候选，不直接构成删除依据。

## 常见候选

- **无生产调用方的接口或扩展点**：export、hook、event、option、protocol field、command 或扩展点没有当前生产消费者。
- **同一事实存在多份表示**：多个 state、cache、summary、format 或 event family 表达同一事实，并要求长期同步。
- **没有实际需求支撑的扩展性**：strategy、fallback、flag、adapter 或 abstraction 为没有当前产品路径拥有的“未来可能”提供扩展性。
- **纯转发层**：wrapper、service、package 或 route 只是转发行为，没有降低耦合或建立真实边界。
- **重复状态机**：多个 flag、promise、queue、sentinel、controller 或 callback 描述同一生命周期转换。
- **重复建设的局部基础能力**：自定义 parsing、retry、diff、matching、scheduling 等能力可由项目既有能力、平台能力或已存在依赖承担，并能减少净维护责任。
- **辅助用途维持的无效接口**：tests、fixtures、snapshots、examples 或 docs 是某个生产上已无消费者的接口继续存在的主要原因。
- **已移除功能的残留**：功能已经移除或放弃，但 schema、config、compatibility logic、tests、docs 或设计记录仍保留其轮廓。
- **为测试便利引入的生产架构**：生产 Interface、dependency injection、hook、callback、debug state 或 extension point 的主要存在理由是让测试更容易控制或观察 Implementation，而不是满足真实生产 variability 或 boundary。
- **一次性验证脚手架**：为一次性验证、实验、迁移或 AI 自证正确性而加入的 helper、adapter、fallback、probe、compat path 或 instrumentation 在任务结束后继续留在生产路径。

视觉相似或代码重复只是线索。独立实现可能分别承担故障隔离、ownership、兼容性或边界职责。

## 为测试便利引入的生产架构检查

遇到 injection point、factory、strategy、callback、hook、clock、retry policy、debug accessor、mutable test state 或测试专用 wrapper 时，先问：

1. 如果没有测试，这个 Interface / injection point 还会存在吗？
2. 是否有真实生产调用方需要替换这个 dependency 或实现？
3. 它是否对应真实 ownership、failure、process、I/O、persistence 或 trust boundary？
4. 删除这个 seam 后，能否仍通过公开生产行为验证 correctness？

`No / No / No / Yes` 是强 simplification candidate，但不能单独作为删除依据。继续检查 runtime consumer、contract、dynamic registration、持久化格式、生命周期和 decisive behavior proof。

## AI-generated accidental complexity

长期 AI coding 特别容易沉积以下维护义务：

- 为了 mock 而把大量 dependency、clock、parser、logger、retry policy、callback 注入业务函数；
- interface → implementation → adapter → service → repository 等多层 relay，每层只有转发；
- 为测试观察内部执行过程而暴露 `retryCount`、`isInitialized`、`pendingOperations`、生命周期 callback 等生产 API；
- 在可信内部 handoff 上重复 validation、copy、fallback、rollback 和 defensive guards；
- 为“以后可能扩展”增加 factory、registry、strategy、plugin seam，但当前产品路径只有一个真实实现；
- 已完成实验、迁移或验证后仍保留 probe、feature flag、temporary adapter、compatibility branch、fixtures 或仅供测试或文档使用的 package。

判断重点不是“是不是 AI 写的”，而是这些能力是否存在当前生产职责。测试使用量大也不自动证明生产 contract 有价值。

## 判断净收益

候选只有在减少的长期维护义务大于新增的迁移、wrapper、dependency、同步或兼容成本时才算真正简化。

不要为了删除行数而：

- 把复杂度搬到调用方；
- 新增同步层维护两个表示；
- 用新依赖替换很小且稳定的本地逻辑；
- 删除仍有真实消费者或当前设计决策明确拥有的能力；
- 因为接口主要被测试使用就直接删除，而没有证明生产行为仍可可靠验证。

