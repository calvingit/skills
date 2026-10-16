# 版本与平台差异

本 Skill 以 MySQL 8.0 与 8.4 LTS 为主要范围。MySQL 5.7 只做遗留兼容分析；MariaDB、Aurora MySQL、RDS、Cloud SQL、Vitess、PlanetScale 等需要额外核实各自文档。

## 先识别环境

在允许只读查询时，可从以下信息开始，但不要据此推断全部平台能力：

```sql
SELECT VERSION(), @@version_comment;
```

还需确认：

- 精确补丁版本、云厂商 engine version 与参数组；
- 单机、异步复制、Group Replication、托管高可用或分片代理拓扑；
- 读写端点、故障转移机制、连接代理和一致性语义；
- 可用权限、Performance Schema/sys schema、备份和审计能力；
- DDL 工具链、维护窗口及厂商限制。

## 高风险差异点

| 主题 | 必须核实的差异 |
| --- | --- |
| DDL | `INSTANT`/`INPLACE` 支持矩阵、是否重建、锁行为、厂商在线变更机制 |
| 优化器 | 统计信息、直方图、默认 optimizer switches、hint 与执行计划字段 |
| 复制 | 术语、状态表/命令、并行应用、一致性和故障转移行为 |
| 权限 | 动态权限、托管服务禁止的管理权限、`DEFINER` 与审计能力 |
| 参数 | 默认值、动态/持久化方式、参数组生效与重启要求 |
| 观测 | Performance Schema consumers、sys schema、日志访问和指标口径 |
| SQL 语义 | `sql_mode`、字符集/排序规则、时区、保留字和废弃特性 |

不要把搜索结果中的旧命令直接复制到新版本。例如复制术语已逐步转向 source/replica，旧名称是否仍可用取决于版本；输出建议时采用目标版本官方术语，并在兼容旧环境时单独标注。

## 版本结论写法

涉及版本敏感行为时，答案应包含：

1. 已确认的产品与精确版本；
2. 该结论适用的版本/平台范围；
3. 官方文档或运行时证据；
4. 尚未验证的兼容实现差异；
5. 升级、降级或跨平台迁移时的复测项目。

官方入口：[MySQL 8.4 Reference Manual](https://dev.mysql.com/doc/refman/8.4/en/)、[MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)、[MySQL Release Model](https://dev.mysql.com/doc/refman/8.4/en/mysql-releases.html)。
