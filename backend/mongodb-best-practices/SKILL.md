---
name: mongodb-best-practices
description: "设计或审查 MongoDB 文档模型、查询索引和并发更新，诊断连接与性能问题，并评估数据迁移和运行变更风险。"
---

# MongoDB 工程实践

根据真实访问模式、数据规模和一致性要求判断设计，先取证再优化。不把关系模型直接改写为文档，也不默认嵌入全部数据、增加索引、使用事务或分片。

## 工作方式

1. 确认实现、审查、诊断或运行变更的范围与授权，读取实际查询、写入路径和业务不变量。
2. 核对服务端版本与 featureCompatibilityVersion、驱动及 ORM 版本、单机、副本集或分片（standalone/replica set/sharded）拓扑和部署平台。Atlas、Community、Enterprise 及兼容服务的能力不能混用。
3. 按相关主题读取下表资料。使用脱敏文档样本、索引、查询形态、执行计划、配置和同一时间窗口的指标；不要求先安装 MCP 或配置 Atlas。
4. 区分代码或现场已证明的事实与候选方案。缺少执行计划、数据分布或负载信息时，索引或模型修改建议仍是待验证方案，不能认定为修复。
5. 验证业务结果，以及受影响的性能、并发或迁移行为；记录实际命令、证据、未验证范围和运行变更的停止与恢复条件。内存中的测试替身不能证明真实索引、复制或事务语义。

## 按需资料

| 任务 | 资料 |
| --- | --- |
| 嵌入与引用、增长、验证器、结构演进、回填 | [模型与演进](references/modeling-and-evolution.md) |
| 查询、聚合、分页、索引和执行计划 | [查询与索引](references/queries-and-indexes.md) |
| 条件更新、唯一性、事务、读写一致性和重试 | [并发与一致性](references/concurrency-and-consistency.md) |
| 连接、超时、运行故障、安全与高风险变更 | [连接与运行](references/connections-and-operations.md) |

只加载受影响主题。Atlas Search、Vector Search、流处理和分片设计需要具体任务及对应版本资料，不作为普通 CRUD 的默认前置流程。

## 操作边界

- 诊断和审查默认只读。对实际数据库的数据写入、索引或验证器变更、profiling 设置、终止操作、拓扑变更及恢复操作，需要明确授权和目标；已有授权不重复询问。
- 只读查询也可能消耗大量资源。控制采样、返回体积与执行时间；先看已有计划和指标，必要时从 queryPlanner 开始。executionStats/allPlansExecution 会执行查询计划，不是无成本的静态分析。
- 聚合不一定只读：执行前检查管道是否包含 `$out` 或 `$merge`。不要为了诊断默认开启 profiler、扫描全库或导出敏感数据。
- 超时、连接断开或write concern（写入确认条件）相关错误不自动等于未写入。按实际错误、驱动和操作语义确认结果后再决定重试。
- 保留租户、权限和软删除过滤；不能为了覆盖索引或提升查询速度改变业务结果。

## 来源与适配

参考 [MongoDB 官方 Agent Skills](https://github.com/mongodb/agent-skills) 的 schema-design、connection 和 query-optimizer 主题，独立编写以下工程检查。保留访问模式与上下文优先的思路；移除对 MCP/Atlas 的强制依赖、通用连接参数及仅凭查询形态就认定索引方案的做法。具体机制以目标版本、驱动和官方文档为准。
