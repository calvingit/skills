# MySQL 安全规范

用于审查连接、身份、权限、查询构造、敏感数据、数据库对象和备份恢复风险。

## 查询与输入

- 值使用预编译语句或参数绑定，不用字符串拼接。
- 表名、列名、排序方向等不能作为普通参数绑定的结构片段，必须由服务端映射到有限 allow-list；无法安全映射时重构查询。
- 参数化只能防止语法注入，不能替代业务授权。多租户查询需要在可信上下文中绑定 tenant 范围，并用数据库约束保护关键唯一性。
- 动态查询生成器、ORM 原生 SQL、报表筛选、导入任务和运维脚本同样属于注入边界。

## 身份与权限

- 运行时、只读分析、迁移、备份和管理账号分离，按实际对象和操作授予最小权限；应用不使用管理员或共享个人账号。
- 凭据放入受控密钥系统，支持轮换和吊销；不写入仓库、镜像、命令历史、工单或诊断输出。
- 定期审查闲置账号、通配 host、匿名账号、过期授权和高危全局权限。
- 审查 view、procedure、function、trigger、event 的 `DEFINER` 与执行上下文，防止对象迁移后出现权限提升或失效账户。
- 权限变更先证明调用路径需要，不用“先给大权限再说”规避诊断。

## 连接与传输

远程连接使用加密协议，并在客户端/平台支持时验证服务端身份和主机名。仅“开启 TLS”但不验证证书，仍可能无法抵御中间人攻击。核实云平台证书轮换与客户端信任链。

网络隔离、私网、堡垒机和安全组是纵深防御，不能替代数据库认证与最小权限。管理端口不应向不受信网络暴露。

## 日志、监控与诊断

- 慢日志、general log、审计日志、Performance Schema、错误日志和 APM 可能包含 SQL、参数、账号与业务标识；限制访问、保留期限和导出范围。
- 分享 `SHOW PROCESSLIST`、死锁、事务或 digest 输出前，对字面量、个人信息、令牌和业务标识脱敏。
- 排障时不要要求用户粘贴口令或完整连接串；使用占位符描述所需字段。
- 启用高体量日志前评估磁盘、I/O、隐私和关闭时间，事故后恢复原配置。

## 数据与恢复

- 敏感数据的静态加密、字段级保护、掩码和密钥托管应匹配威胁模型与合规要求。
- 备份与 binlog 具有与生产数据相同的敏感级别；限制访问、加密、校验保留，并周期性执行恢复演练。
- 删除或匿名化需求需覆盖副本、备份、搜索索引、缓存与分析链路，明确法律保留要求。

参考：[OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)、[MySQL 8.4 Security Guidelines](https://dev.mysql.com/doc/refman/8.4/en/security-guidelines.html)、[MySQL 8.4 Encrypted Connections](https://dev.mysql.com/doc/refman/8.4/en/using-encrypted-connections.html)。
