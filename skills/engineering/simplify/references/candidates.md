# Simplification Candidates

用维护义务而不是代码行数寻找简化机会。以下分类用于生成候选，不直接构成删除依据。

## 常见候选

- **Dormant contract**：export、hook、event、option、protocol field、command 或扩展点没有当前生产消费者。
- **Split truth**：多个 state、cache、summary、format 或 event family 表达同一事实，并要求长期同步。
- **Ownerless flexibility**：strategy、fallback、flag、adapter 或 abstraction 为没有当前产品路径拥有的“未来可能”提供扩展性。
- **Relay layer**：wrapper、service、package 或 route 只是转发行为，没有降低耦合或建立真实边界。
- **Parallel state machine**：多个 flag、promise、queue、sentinel、controller 或 callback 描述同一生命周期转换。
- **Local infrastructure**：自定义 parsing、retry、diff、matching、scheduling 等能力可由项目既有能力、平台能力或已存在依赖承担，并能减少净维护责任。
- **Support drag**：tests、fixtures、snapshots、examples 或 docs 是某个生产上已无消费者的接口继续存在的主要原因。
- **Feature fossil**：功能已经移除或放弃，但 schema、config、compatibility logic、tests、docs 或设计记录仍保留其轮廓。

视觉相似或代码重复只是线索。独立实现可能分别承担故障隔离、ownership、兼容性或边界职责。

## 判断净收益

候选只有在减少的长期维护义务大于新增的迁移、wrapper、dependency、同步或兼容成本时才算真正简化。

不要为了删除行数而：

- 把复杂度搬到调用方；
- 新增同步层维护两个表示；
- 用新依赖替换很小且稳定的本地逻辑；
- 删除仍有真实消费者或当前设计决策明确拥有的能力。
