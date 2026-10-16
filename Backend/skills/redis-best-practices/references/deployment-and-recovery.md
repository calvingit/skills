# 部署与恢复

## 集群和读路径

确认使用单机（standalone）、Sentinel、Cluster 还是托管代理拓扑。Cluster 中需要原子执行的多 Key 命令、事务及脚本按实际命令核对同槽约束；hash tag 只用于确需放在同一槽的数据，避免把全部租户压到一个槽。

区分单个多 Key 命令和由多个独立命令组成的 pipeline。支持 Cluster 的客户端可能按节点拆分非事务 pipeline，不能一概要求所有命令同槽；同时不能把这种拆分当成跨槽原子性。迁槽、重定向与重试行为以客户端文档为准。

使用副本读取前，应确认业务允许数据滞后到什么程度，尤其要核对会话、权限、幂等和协调状态。不能只因读请求多就把所有读取迁到副本。

## 持久化与故障转移

分别确认业务允许的数据丢失时间窗口（RPO 要求）、恢复时长、复制和持久化配置。默认异步复制可能在故障转移时丢失已确认写入；WAIT 的副本确认不使系统自动获得强一致性。RDB、AOF、备份与复制各自解决不同问题，副本不等于独立备份。

变更前核对磁盘空间、重写或快照的资源成本、全量同步影响和恢复演练证据。恢复流程要考虑数据正确性、流量切换与缓存集中重建，不只验证进程启动。没有隔离环境和授权，不执行故障注入，也不用恢复操作覆盖现有数据。

## 安全和变更

按实际部署核对网络隔离、TLS、ACL 的命令和 Key 范围；保护凭证及诊断输出。不要以关闭认证、开放公网或扩大管理权限解决连接问题。

写入、批量清理、持久化配置、ACL 和拓扑变更前明确目标、范围、授权、观测指标及停止条件。按应用版本、旧 Key 和回滚读写路径规划迁移；无法恢复已删除数据时明确说明，不把配置回退当成数据恢复。

来源：[复制](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)、[持久化](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)、[Cluster 规范](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)、[redis-py Cluster pipeline](https://redis.readthedocs.io/en/stable/clustering.html)、[安全](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)。
