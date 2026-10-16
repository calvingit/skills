# 模型与演进

## 从访问模式判断文档边界

先列出需要一起读取、更新和保持一致的数据，再确认关联基数、文档增长、热点、保留期与查询频率。嵌入适合共同访问且增长受控的数据；引用可减少数据重复，以及单个文档内缺少明确上界的增长（unbounded growth），但增加读取与一致性维护成本。两者都不是默认答案。

核对文档大小与数组增长，不能因为当前样本小就假定长期使用也安全。冗余字段必须明确由谁更新，以及允许数据滞后到什么程度；不要只为省一次查询就复制权威数据。计量单位、日期、精确数值与缺失/null 语义保持项目约定。

## 结构变更与历史数据

检查驱动、ORM、验证器和旧应用对新旧字段的处理。新增验证器前评估已有数据及 validationLevel/validationAction，验证器不会自动清洗历史记录；缺失字段与 null 也不能无条件等同。

回填时限制每批处理量，并记录进度以便中断后继续。条件更新应避免覆盖期间的新写入；重跑和中断后的结果要可核对，不能只统计脚本处理条数。确认旧版本读取新文档的能力，再删除旧字段或路径。

TTL 删除是异步清理，不是精确时刻的业务失效机制。授权、会话等需要在读取时满足业务规定的有效期。变更 TTL 前评估可能集中到期的数据量和删除负载。

来源：[数据建模](https://www.mongodb.com/docs/manual/data-modeling/)、[无界数组](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/unbounded-arrays/)、[Schema Validation](https://www.mongodb.com/docs/manual/core/schema-validation/)、[TTL 索引](https://www.mongodb.com/docs/manual/core/index-ttl/)。
