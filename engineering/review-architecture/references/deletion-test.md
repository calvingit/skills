# Deletion Test

Deletion Test 只回答 Module 是否通过 Interface 集中了复杂度，不判断它是否位于正确的 boundary、拥有正确的状态或遵守正确的依赖方向。

假设删除目标 Module：

- 复杂度基本消失，调用方只需直接调用底层能力：`pass-through`。
- 调用方只需补回少量与原 Interface 相近的逻辑：`shallow`。
- 被隐藏的规则、顺序、错误处理或副作用分散回多个调用方：`deep`。

检查调用方需要重新知道什么，而不是比较代码行数。记录依据，例如调用顺序、不变量、错误模式、重试、缓存或状态协调会落到哪些调用方。

## Interpretation

- `pass-through` / `shallow`：说明当前 Module shape 可能缺少 leverage，值得作为 architecture review candidate。
- `deep`：说明 Module 正在集中复杂度；不要仅因内部实现很大而拆散它。
- `deep` 不是架构豁免。若 ownership、boundary、lifecycle 或 dependency direction 错误，仍按对应 evidence 保留 finding。

结合“Interface is the test surface”判断：如果生产调用方和测试都必须绕过 Interface 才能验证关键行为，问题可能是 Interface 或 boundary，而不是 Implementation 大小。
