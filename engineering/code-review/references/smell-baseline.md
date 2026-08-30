# Fowler Smell Baseline

这些 smell 是 judgement call，不是硬规则。项目明确标准优先，工具已强制的项目跳过。只报告本次 diff 引入或扩大的具体问题。

- **Mysterious Name**：名称无法说明内容或职责；重命名，若找不到准确名称则重新检查设计。
- **Duplicated Code**：多个 hunk 或文件出现相同逻辑形状；提取真正共享的行为。
- **Feature Envy**：一个方法理解其他 Module 的数据多于自身；把行为移到拥有数据的 Module。
- **Data Clumps**：一组字段或参数反复一起出现；把它们代表的领域概念归并为一个类型。
- **Primitive Obsession**：primitive 或 string 代替了值得建模的领域概念；建立小而明确的类型。
- **Repeated Switches**：多个位置按同一类型重复 switch/if cascade；集中分派逻辑。
- **Shotgun Surgery**：一个逻辑变化迫使大量分散编辑；把一起变化的知识收回同一 Module。
- **Divergent Change**：同一文件因多个不相关原因反复变化；按变化原因分离 ownership。
- **Speculative Generality**：spec 没有要求的 abstraction、hook 或 parameter；删除多余部分，只保留当前真实需要。
- **Message Chains**：调用方依赖长串内部导航；由起点 Module 提供一个能隐藏导航的 Interface。
- **Middle Man**：Module 主要只转发；删除或让它承担真实复杂度。
- **Refused Bequest**：继承者忽略或覆盖大部分继承行为；放弃继承，改用组合。
