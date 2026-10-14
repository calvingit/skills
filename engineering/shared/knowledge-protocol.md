# 长期知识回写

本文是 [Engineering Kernel](ENGINEERING_KERNEL.md) K03–K05 在长期项目知识上的具体应用，只回答一个问题：任务中发现了一个以后还需要知道的事实，接下来怎么办。它不是 Skill，也不是新的存储位置。

## Purpose

把任务中得到的长期认知写回项目已有的权威来源，并让以后的任务能通过 Profile 找到它。项目不另建知识库、候选清单或统一状态。

## Durable knowledge

只有以后的任务仍可能用到、且不只是当前执行状态的信息，才考虑长期保留。

- “当前 ticket 已完成”是执行状态，留在 ticket 和交付记录里。
- “Refund 只有在 Payment captured 后才允许发生”可能是长期领域知识。

拿不准时先不保留，在交接中作为发现报告。

## Authority ownership

实现、验证、审查、调试和调研中看到的内容，首先只是观察。被观察到不等于成为项目事实。每项事实只有一个当前权威来源，由它的负责方维护；先判断它是什么事实、归谁负责：

| 发现 | 负责方 | 写入位置 |
| --- | --- | --- |
| 新领域概念或词义变化 | `domain-modeling` | 项目已有的术语来源 |
| 领域关系、生命周期、不变量 | `domain-modeling` | 项目已有的领域模型来源，没有则不强建 |
| 本次交付的设计决定 | `solution-design` | 技术方案（`HLD.md`） |
| 难以撤回、需要背景才能理解的长期决定 | `domain-modeling`（ADR 门槛） | 项目已有的 ADR / 决策记录 |
| 验证方法或能力缺口 | `verification-setup` | 项目验证方法与导航摘要 |
| 稳定工程配置与资料位置 | `project-setup` | Profile |
| 需求或验收含义 | 用户确认，`to-spec` 维护 | SPEC / ACCEPTANCE |

其他项目资料（API 文档、编码规范、运维手册）由项目约定的维护者负责。负责方以[职责与边界](engineering-responsibilities.md)为准。

## Promotion

1. 判断是否值得长期保留。
2. 找到负责这类事实的权威来源。
3. 交给负责方按其规则更新；当前角色没有写权限时，在报告里写明发现、依据和建议的负责方，由调用方安排。
4. 只有路径或入口变化时，才请 `project-setup` 更新 Profile 导航。

复用项目已有文件和格式，不为此迁移目录，也不新建 `docs/engineering/`、`KNOWLEDGE.md` 或 `knowledge/`。

## Retrieval

以后的任务按 [Profile 解析](../project-setup/references/profile.md#resolve-and-load)只读取与任务相关的来源。Profile 只做导航，不复制知识内容。

## Conflict and change

新发现与现有来源冲突时，列出双方依据，交给负责方或用户决定，不擅自覆盖。不建立独立的知识生命周期；各权威来源按自身规则维护演进，需要状态时由它自己表达，例如 ADR 的 Superseded。

## Boundaries

本文不新增 Skill、Agent、存储、候选 ID、生命周期、注册表、后台同步或 Profile 字段，也不改变各 Skill 的现有门槛。各负责方的具体写法仍以其 Skill 为准。
