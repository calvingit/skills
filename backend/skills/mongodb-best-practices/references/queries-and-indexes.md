# 查询与索引

## 优化前保留语义

收集完整的过滤条件、排序、投影、limit、collation、聚合阶段和现有索引，并核对代表性数据分布、返回数量、应用延迟及执行计划。保留授权与租户过滤；优化前后比较结果集合和排序，不只比较耗时。

从实际计划判断扫描、读取和排序成本。结合 nReturned、totalKeysExamined、totalDocsExamined、排序或落盘（spill）、分片路由及采样窗口判断，不能仅凭单个比值、COLLSCAN 或一次耗时就认定需要索引。

## 索引候选

结合等值、排序、范围条件和选择性判断字段顺序；ESR 是起点，不是无需验证的固定答案。检查 multikey、partial、sparse、unique 和 collation 的适用限制。覆盖索引还需权衡索引体积、写入放大、内存与其他查询，不追求所有查询都覆盖。

没有现场证据时可提出候选及验证步骤，但不能声称已经解决慢查询。删除索引前检查完整业务周期、后台任务及其他读路径；短期未使用不能证明永久无用。

## 聚合与分页

先检查过滤能否在不改变语义的前提下提前，再查看关联基数、排序所需内存、返回体积和应用端往返次数。allowDiskUse 不替代查询成本分析。

分页沿用现有接口约定；大偏移量（offset）分页的成本确有问题时才考虑范围游标，并包含稳定排序与用于打破排序并列的唯一键，说明并发写入下的可见性。不要把迁移分页策略当成无兼容影响的局部优化。

优先读取已有计划或 queryPlanner；执行统计需先确认成本、环境和查询性质，并设置适用的时间预算。不能默认用生产高成本查询做基准测试。

来源：[Explain 结果](https://www.mongodb.com/docs/manual/reference/explain-results/)、[索引](https://www.mongodb.com/docs/manual/indexes/)、[ESR](https://www.mongodb.com/docs/manual/tutorial/equality-sort-range-guideline/)、[聚合优化](https://www.mongodb.com/docs/manual/core/aggregation-pipeline-optimization/)。
