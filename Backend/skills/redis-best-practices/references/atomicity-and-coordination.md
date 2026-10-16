# 原子性与协调

## 原子操作不等于业务事务

检查读取、条件判断、写入与过期设置之间的竞争窗口。单条命令具有原子性，不代表多次调用合起来也具有原子性；单纯的命令流水线（pipelining）用于批量传输，本身不提供事务隔离；客户端名为 pipeline 的 API 是否同时启用了 MULTI/EXEC，需核对具体驱动和配置。使用条件写入、WATCH、事务或脚本前，确定要保护的不变量以及客户端的重试语义。

Redis 事务不提供传统数据库式的运行时错误回滚。Lua/Functions 的原子执行也不能保证外部数据库写入或网络操作与脚本一起原子提交；脚本应限制执行时间、集合规模和返回量。

## 锁与租约

先确认是否真的需要跨进程协调。获取、续期和释放必须绑定锁持有者，释放时不能无条件删除可能已属于新持有者的 Key。TTL 只限制租约期限，不会停止旧进程：暂停的执行者恢复后仍可能写入业务系统。

如果旧执行者在租约过期后继续写入会破坏业务不变量，应确认被保护资源能否拒绝它的写入，例如校验单调递增的 fencing token（由被保护资源校验，用于拒绝旧持有者写入）或业务版本。不要只增加续期就声称解决了问题，也不机械为每个任务引入 fencing。分析复制、故障转移及网络分区对锁持有权的影响。

## 消息与计数

- 限流与计数检查更新和过期的原子性、窗口边界、热点及 Redis 不可用时的业务策略。
- Pub/Sub 不作为可重放的可靠任务队列。使用 Streams 时检查消费组、确认时机、待确认消息（pending）的处理、重新领取和裁剪策略。
- 业务副作用完成后、确认前中断可能导致重投。核对重复处理和旧消费者继续执行的影响，不声称使用消费组就实现了恰好一次处理（exactly-once）。

控制操作交错顺序来验证：租约过期后旧执行者恢复、两个消费者重复处理、副作用成功但响应丢失。没有真实环境时只报告机制分析，不声称故障转移测试通过。

来源：[事务](https://redis.io/docs/latest/develop/using-commands/transactions/)、[redis-py pipeline 与事务](https://redis.readthedocs.io/en/stable/advanced_features.html)、[分布式锁](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/)、[Streams](https://redis.io/docs/latest/develop/data-types/streams/)。
