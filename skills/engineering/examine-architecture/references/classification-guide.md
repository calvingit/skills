# Investigation Lenses

这些 lenses 用于提出和检验 candidate hypothesis，不是固定规则、必填 checklist 或技术栈分类。一个候选可以命中多个 lens；只使用能解释当前 evidence 的部分。

| Lens | 核心问题 | 常见 evidence |
|---|---|---|
| Ownership / Locality | 变更、状态和知识是否集中在真正拥有该行为的 Module？ | 调用方分布、变更历史、重复逻辑、生命周期 |
| Interface / Depth | 调用方必须知道的事实是否接近 Implementation 的复杂度？ | 参数、不变量、调用顺序、错误模式、透传方法 |
| Seam / Adapter | Seam 是否放在实际变化的位置，Adapter 是否代表真实替换？ | 多种实现、测试替身、传输或存储差异、泄漏细节 |
| Dependency | 依赖方向、循环或跨 Module 知识是否放大变更？ | import/call graph、构建依赖、初始化顺序 |
| State / Lifecycle | 状态 owner 和生命周期是否与使用范围匹配？ | 全局可变状态、并发访问、创建/释放路径、恢复行为 |
| Data / Control Flow | 数据、错误和副作用是否跨 Seam 泄漏或被多处解释？ | 转换链、错误映射、分支、重试、缓存、事件传播 |
| Test Surface | 测试能否通过与调用方相同的 Interface 验证行为？ | 必须穿透内部状态、脆弱 mock、测试与调用方使用不同入口 |

## Deep-read method

1. 从用户动作、公开入口或上游调用方开始，追踪到最终副作用或持久化位置。
2. 标出沿途每个 Module 的 Interface，以及调用方被迫知道的 Implementation 细节。
3. 查看与 hypothesis 直接相关的测试、配置和近期改动；不扫描无关目录。
4. 区分设计问题与项目政策：规则命中可以证明不合规，但仍要解释它造成的架构摩擦。
5. 寻找反证。若现有 Module 已经集中复杂度、保持 Locality，或额外 Seam 没有真实变化来源，将其记录为 Not Finding。

## Finding gate

候选进入 Findings 至少需要：

- 一个可定位的当前 evidence；
- 一个由该结构导致的实际摩擦或风险；
- 一个不包含代码级方案的 desired outcome。

证据不足但值得继续观察的候选标为 `Speculative`，不要包装成确定结论。
