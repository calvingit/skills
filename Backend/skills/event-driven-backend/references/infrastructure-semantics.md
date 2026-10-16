# 基础设施核对

只查实际使用的产品及版本，无需逐项加载表中所有文档。根据客户端、部署方式和配置核对实际保证，不提供脱离环境的通用参数值。

| 基础设施 | 优先核对 | 官方入口 |
| --- | --- | --- |
| Kafka | 生产者确认与幂等、事务及隔离、分区范围的顺序、消费位点（offset）提交、并行完成与重平衡；Kafka 内事务不自动原子提交外部数据库 | [Kafka 4.1 设计说明](https://kafka.apache.org/41/design/design/)（使用时切换到目标版本） |
| RabbitMQ | 发布确认（publisher confirms）、路由与返回处理、持久化和队列类型、消费成功确认或否定确认（consumer ack/nack）、预取（prefetch）、重新入队（requeue）与死信队列（DLQ）；确认发布不等于消费成功 | [Confirms 与 acknowledgements](https://www.rabbitmq.com/docs/confirms) |
| Redis Streams | 消费组、待确认消息（pending）、确认（ack）、重新领取（claim）、裁剪与持久化；具体存储风险按 Redis 版本和部署核对 | [Streams](https://redis.io/docs/latest/develop/data-types/streams/) |
| SQS | Standard/FIFO、去重范围与期限、消息组（message group）、可见性超时（visibility timeout）、删除（delete）与死信队列（DLQ）；业务副作用是否幂等单独判断 | [Visibility timeout](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html) |
| Webhook | 供应方签名算法、原始载荷、投递标识、响应期限、重试与顺序保证；不要假定供应方都相同 | 读取当前供应方的官方协议 |

遇到“恰好一次语义（exactly-once semantics）”的说明，明确它覆盖哪些操作、存储边界、客户端配置与失败模式；不能扩展为任意数据库或外部付款只发生一次。托管服务兼容某种协议也不证明所有投递保证相同。
