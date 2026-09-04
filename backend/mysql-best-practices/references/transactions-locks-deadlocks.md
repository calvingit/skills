# 事务、锁等待与死锁

用于区分行锁等待、死锁、长事务和元数据锁，并在不扩大事故影响的前提下建立阻塞关系。

## 先分类

| 现象 | 核心特征 | 首要证据 |
| --- | --- | --- |
| 锁等待 | 请求正在等待其他事务持有的锁 | `performance_schema.data_lock_waits` 与相关事务 |
| 死锁 | 形成等待环，InnoDB 回滚其中一个事务 | 最近死锁信息、应用错误与事务重试行为 |
| 长事务 | 长时间持有快照或锁，可能放大 undo、purge 和复制问题 | `information_schema.innodb_trx`、会话与调用方 |
| 元数据锁 | DDL 或对象访问被未结束事务/语句阻塞 | `performance_schema.metadata_locks` |

这些现象可以同时存在。锁等待超时不是死锁；死锁也不必等到超时才被发现。

## 安全采集

以下查询是起点，不是完整结论；不同版本、发行版和权限下字段可见性可能不同：

```sql
SELECT *
FROM performance_schema.data_lock_waits
LIMIT 200;

SELECT *
FROM performance_schema.metadata_locks
WHERE LOCK_STATUS = 'PENDING'
LIMIT 200;

SELECT *
FROM information_schema.innodb_trx
ORDER BY trx_started
LIMIT 200;
```

将 waiting lock、blocking lock、线程、当前语句和事务关联后再判断责任方。采集结果可能包含 SQL 与业务数据，分享前脱敏。

死锁优先收集 `SHOW ENGINE INNODB STATUS` 中最近一次死锁，并与同时间应用日志对齐。`innodb_print_all_deadlocks` 会增加错误日志内容，只能在明确授权、确认日志容量和脱敏风险后临时启用，并约定关闭时间。

## 根因检查

- 事务是否过大、包含外部 RPC/人工等待，或因异常路径未及时提交/回滚；
- 并发事务是否以不同顺序访问相同表或记录；
- 缺失或不合适的索引是否扩大扫描与加锁范围；
- 当前隔离级别、范围条件与不存在记录是否引入 gap/next-key lock；
- DDL 是否在等待旧事务释放元数据锁，同时阻塞后续请求形成队列；
- 应用重试是否没有上限、没有退避，或只重试半个业务操作。

## 处置护栏

- 不因“存在阻塞”就立即 `KILL`。先确认线程归属、事务内容、已运行时长、回滚成本、复制影响和业务补偿方式。
- 必须终止会话时，明确目标线程、批准人、预期释放的资源、回滚观测和失败升级路径；不要批量猜测式终止。
- 死锁重试必须位于完整事务边界，操作需具备幂等或去重保障，并采用有上限的退避；无限即时重试会放大拥塞。
- 根治通常是缩短事务、统一访问顺序、减小锁定范围、补足合适索引或改变并发模型，而不是简单延长超时。
- 元数据锁事故中，先识别最早阻塞者和等待队列；盲目重复 DDL 会增加排队与处置难度。

参考：[MySQL 8.4 `data_lock_waits`](https://dev.mysql.com/doc/refman/8.4/en/performance-schema-data-lock-waits-table.html)、[MySQL 8.4 Deadlock Handling](https://dev.mysql.com/doc/refman/8.4/en/innodb-deadlocks-handling.html)。
