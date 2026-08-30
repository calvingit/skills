---
name: codebase-design
description: "用于设计或评估具体模块、接口、依赖方向和可测试边界。"
---

# Codebase Design

用于在具体设计点上判断代码应该如何分层、暴露什么 Interface、复杂度应该由谁拥有，以及生产代码与测试应该在哪个 Seam 相遇。它是一套可复用设计纪律，不绑定架构流派、语言、框架或目录结构。

重点回答：**一个已经明确需要处理的 Module / Interface / Seam 应该 HOW 设计。** 它不负责判断整个现有架构是否 sound，也不负责主动扫描代码库寻找架构问题；这类任务使用 `review-architecture`。

## Canonical terms

讨论这些概念时，统一使用以下术语，不用 component、service、API 或 boundary 替代。目标项目不必采用同名文件或类型，但各 Skill 必须共享同一套语义。

- **Module**：任何同时拥有 Interface 与 Implementation 的单元，可以是函数、类、package 或跨层 vertical slice。
- **Interface**：调用方正确使用 Module 必须知道的全部表面，不只有类型签名，还包括不变量、顺序约束、错误模式、所需配置和性能特征。
- **Implementation**：Module 内部为了兑现 Interface 而存在的代码和行为。它不同于 Adapter；Implementation 描述内部，Adapter 描述在 Seam 上承担的角色。
- **Depth**：衡量 Interface 带来的杠杆。调用方需要理解的内容越少、获得的能力越多，Module 越 deep；Interface 与 Implementation 几乎一样复杂的 Module 较 shallow。
- **Seam**：无需在该位置编辑代码，就能改变行为的位置；也就是 Module 的 Interface 所在之处。Seam 是“放在哪里”的设计决定，不等同于一般意义的 boundary。
- **Adapter**：在某个 Seam 上满足 Interface 的具体实现角色，不限于外部系统转换器。
- **Leverage**：Depth 为调用方带来的收益，体现一个 Interface 能以多小的理解成本，为生产调用方和测试提供多少能力。
- **Locality**：Depth 为维护者带来的收益；变化、知识、不变量、bug 和验证是否集中在一个 Module 内，而不是扩散到调用方。

这些概念的关系是：Module 对调用方提供一个 Interface；Depth 相对于该 Interface 判断；Seam 是 Interface 所在的位置；Adapter 位于 Seam 并满足 Interface；生产调用方和测试通过同一个 Interface 使用 Module。

## Core principles

### 1. Hide complexity behind the right owner

复杂度如果是完成行为所必需的，应由最了解它的 Module 吸收，而不是向所有调用方扩散。优先让调用方表达“要什么”，避免让调用方重复知道“内部怎么做”。

警惕：

- 多个调用方重复相同 wiring、校验或协议步骤；
- 调用方必须知道内部状态机顺序；
- 一个简单行为需要跨多个文件拼装低层细节；
- 为了测试把内部开关、noop、delay、callback 或 mutable state 暴露成生产 API。

### 2. Design the Interface from observable behavior

先描述调用方真正需要的 capability、输入、输出、失败语义、生命周期和取消/并发约束，再决定 Interface。不要从现有实现类、数据库结构或第三方 API 反推公共接口。

Interface 应尽量：

- 小而完整；
- 表达领域/任务意图；
- 不泄漏无关实现细节；
- 对真实错误和生命周期约束保持明确；
- 能被真实生产调用方自然使用。

### 3. Put Seams at real variation points

好的 Seam 通常已经存在于真实变化点：公共 Interface、I/O Adapter、process boundary、clock/random source、external system、storage 或 UI/user interaction 等位置。

不要仅因为“测试不好写”就新增 Seam。先问：

1. 生产代码本身是否也从这个边界获益？
2. 这个边界是否代表真实 ownership 或变化原因？
3. 测试能否通过现有公开 Interface 验证行为？

若只有测试需要而生产调用方不需要，默认不扩大生产 Interface。

一个 Adapter 只说明存在假想 Seam，两个有真实理由存在的 Adapter 才说明 Seam 成立，常见组合是 production Adapter 与 test Adapter。不要为单一实现增加只有转发作用的 port。

### 4. Keep adapters at the edge

第三方 SDK、HTTP、数据库、文件系统、平台 API 等外部形状应尽量停留在 Adapter 一侧。核心 Module 不应无必要地传播 vendor-specific 类型、错误或配置。

但不要机械地给每个依赖加 wrapper；只有当 Adapter 能占据真实稳定的 Seam、隔离变化或提供更合适的内部 contract 时才值得存在。

### 5. Prefer locality over speculative reuse

让会一起变化的规则尽量一起存在。抽象只有在已有多个真实调用者/变化证据，或一个明确边界需要隐藏复杂度时才建立。

不要为了潜在复用提前增加 generic layer、factory、strategy、repository、manager、service 等名字；名称不证明抽象成立。

## Deletion test

判断一个 Module 是否只是薄包装时，做概念上的 deletion test：

> 如果删除这个 Module，并让调用方直接使用它的下游依赖，系统是否几乎不损失抽象、约束、稳定性或理解成本？

如果答案是“几乎没有损失”，它可能是无价值 middle layer；如果它集中协议、状态、不变量、错误语义、缓存/事务边界或大量复杂度，则可能很 deep。

Deletion test 只判断 Module 的价值和深度，不证明它位于正确 Seam，也不证明 dependency direction 正确。

## Workflow

1. 明确当前设计问题、目标调用方和需要形成的 Module / Interface / Seam；不要自动扩大成全仓架构评审。
2. 读取目标 Module、代表性生产调用方、composition/configuration 入口、下游依赖和相关测试。
3. 写出当前 observable behavior、ownership、必须保留的不变量和真实外部边界。
4. 判断当前 Interface、Depth、Seam、Adapter、dependency direction 和 Locality；区分 Observed / Inferred / Unknown。
5. 给最多 2-3 个真实候选设计，说明各自收益、成本、迁移影响和 test seam；不制造伪选项。
6. 推荐最简单、能把必要复杂度放到正确 owner 且不扩大公共表面的方案。
7. 本 skill 默认停在设计判断；需要落盘契约交给 `grilling` / `to-spec`，需要实现交给 `implement`。

当依赖类型会影响 Module 的深化方式时，读取 [DEEPENING.md](DEEPENING.md)。只有用户明确要求比较候选 Interface，或单一方案不足以形成可靠判断时，才读取 [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md)，使用其中的多方案比较流程。

## Boundaries

- 评审现有架构是否合理、是否符合项目/技术栈约束，或发现架构债和治理候选：使用 `review-architecture`。
- 已确认某个 Module / Interface / Seam 需要调整，需要形成目标设计：使用 `codebase-design`。
- 需求或行为尚未决定：使用 `grilling`。
- bug 根因调查：使用 `debug`。
- 行为不变的 diff 收缩：使用 `simplify`。
- 不强制 Clean Architecture、DDD、Hexagonal、MVC、MVVM 等任何固定架构流派；只根据当前证据判断 ownership、Interface 和 Seam。
