# 并发与一致性

## 明确不变量与原子边界

单文档更新具有原子性，不意味着先读后写的业务流程无竞争。需要条件状态转换时，将期望状态或版本放入更新过滤条件，并检查 matched/modified 结果；对计数等使用符合业务语义的更新操作，不把旧值整体覆盖回去。

跨请求唯一性优先评估数据库唯一约束，但先核对历史重复值、缺失/null、部分索引及分片限制。upsert 本身不替代唯一约束。

多文档原子性确有需要时评估事务及拓扑支持。事务不能让外部服务的操作与数据库写入一起原子提交，还需核对事务持续时间、冲突和重试。驱动事务回调可能重新运行，不把扣款、发邮件等非幂等副作用无条件放入回调。

## 读写保证

分别确认 read preference（读取路由选择）、read concern（读取隔离与一致性级别）、write concern（写入确认条件）和 session（会话）的实际设置。write concern 包含复制确认、journal 及等待超时等相关条件，不只是是否收到网络响应。副本读取不保证能读到自己刚写入的数据；read concern 的 majority 与 write concern 中的 w: "majority" 也不是同一设置，不能笼统等同于最新读取或线性一致性。

当业务需要因果顺序、快照或更强一致性时，核对相应的 session、concern 设置，以及拓扑和版本前提。不要为普通查询统一提高保证，也不要为降低延迟静默削弱已确认保证。

## 结果不确定与重试

区分确定失败与结果未知。按错误标签、操作类型和驱动版本判断可重试写入及提交重试；不要因为驱动支持重试，就认为整个业务流程都能安全重放。记录或复用业务操作标识，必要时查询结果，避免响应丢失后重复产生副作用。

验证相关竞争与故障窗口：并发条件更新、重复 upsert、事务冲突或提交响应丢失。生产禁止未经授权的故障注入；无真实环境时保留验证缺口。

来源：[原子性与事务](https://www.mongodb.com/docs/manual/core/write-operations-atomicity/)、[读取隔离与一致性](https://www.mongodb.com/docs/manual/core/read-isolation-consistency-recency/)、[可重试写入](https://www.mongodb.com/docs/manual/core/retryable-writes/)、[Read Concern](https://www.mongodb.com/docs/manual/reference/read-concern/)、[Write Concern](https://www.mongodb.com/docs/manual/reference/write-concern/)。
