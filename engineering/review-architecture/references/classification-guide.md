# Architecture Review Lenses

这些 lenses 用于提出和检验 architecture findings，不是固定架构模板、必填 checklist 或技术栈分类。只使用与当前 scope 和 evidence 直接相关的部分。

| Lens | 核心问题 | 常见 evidence |
|---|---|---|
| Boundary / Ownership | 变更、状态、知识和副作用是否集中在真正拥有该行为的 Module？ | 调用方分布、变更历史、状态写入点、生命周期 |
| Interface / Depth | 调用方必须知道的事实是否接近 Implementation 的复杂度？ | 参数、不变量、调用顺序、错误模式、透传方法 |
| Seam / Adapter | Seam 是否放在真实变化的位置，Adapter 是否代表真实替换或外部边界？ | 多种实现、传输/存储差异、测试替身、泄漏细节 |
| Dependency Direction | 依赖方向、循环或跨 Module 知识是否放大变更？ | import/call graph、构建依赖、初始化顺序、反向调用 |
| State / Lifecycle | 状态 owner 和生命周期是否与使用范围匹配？ | 全局可变状态、并发访问、创建/释放、恢复行为 |
| Data / Control Flow | 数据、错误和副作用是否跨 boundary 泄漏或被多处解释？ | 转换链、错误映射、分支、重试、缓存、事件传播 |
| Testability | 测试能否通过与生产调用方相同的 Interface 验证行为？ | 穿透内部状态、脆弱 mock、测试专用入口 |
| Standards Conformance | 当前设计是否违反项目已声明架构约束，或与当前场景直接相关的官方技术栈规则？ | ADR、project rules、architecture guard、官方文档 |
| Evolution Cost | 正常需求是否需要跨过多 owners、同步多个事实或修改不相关区域？ | 高频共同改动、重复 wiring、并行状态、跨层 feature 修改 |

## Deep-read method

1. 从用户动作、公开入口或上游调用方开始，追踪到最终副作用或持久化位置。
2. 标出沿途 Module ownership、Interface、dependency direction 和 state ownership。
3. 查看与 hypothesis 直接相关的测试、配置、规则和必要历史；不扫描无关目录。
4. 区分 project policy 与 design judgment：规则命中证明不合规，但仍要解释实际 impact。
5. 若引用技术栈最佳实践，优先使用当前官方资料，并明确它是 hard constraint 还是 guidance。
6. 主动寻找反证。若现有结构保护了真实 compatibility、failure isolation、lifecycle ownership 或替换边界，记录为 Not Finding 或降低严重度。

## Finding gate

候选进入 Findings 至少需要：

- 一个可定位的当前 evidence；
- 一个明确的 architecture concern；
- 一个实际 impact、风险或持续维护摩擦；
- 一个不包含文件级实现步骤的 recommendation direction。

只有风格差异、目录偏好、静态 smell 或未经确认的“最佳实践”不能单独成为 finding。
