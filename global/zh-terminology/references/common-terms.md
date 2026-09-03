# 常用技术术语参考

这是一组审校候选，不是固定词典。先确认语境，再从“推荐表达”中选择；项目已有准确约定时沿用项目约定。

## 目录

- [架构与文档](#架构与文档)
- [实现与 API 设计](#实现与-api-设计)
- [系统与交付](#系统与交付)
- [Agent 与 AI 工程](#agent-与-ai-工程)
- [通常保留的英文](#通常保留的英文)

## 架构与文档

| 英文或生硬表达 | 推荐表达 | 语境说明 |
| --- | --- | --- |
| single source of truth | 唯一依据 / 权威来源 | 文档或配置决定最终结果时，不必翻成“唯一事实来源” |
| requirement authority | 需求权威来源 / 最终需求依据 | 强调哪一来源有最终决定权 |
| ownership | 职责归属 / 维护责任 | 只有法律或资源归属语境才译为“所有权” |
| owner | 维护者 / 负责方 | 组件 owner 通常不是“所有者” |
| contract | 接口约定 / 需求约束 / 设计约定 | 按 API、需求或架构语境分别处理 |
| concern | 职责 / 问题 / 关注点 | separation of concerns 可译为“职责分离” |
| boundary | 边界 / 职责边界 | 通常已有自然译法，不必扩写成抽象术语 |
| surface area | 影响范围 / 对外接口范围 / 维护范围 | 不译为“表面积” |
| seam | 可替换边界 / 测试切入点 | 仅在项目已采用该术语时保留 Seam |
| primitive | 基础能力 / 底层构件 | 编程语言理论语境可保留“原语” |
| first-class | 原生支持 / 核心能力 | “一等公民”虽常见，但不总能直接说明作用 |
| opinionated | 约定明确 / 限制较多 | 根据褒贬语境说明具体约束 |
| ergonomics | 易用性 / 调用是否顺手 | 软件 API 语境不译为“人体工程学” |
| artifact | 产物 / 交付物 / 构建产物 | 仅在制品库等固定语境使用“制品” |
| consumer | 使用方 / 调用方 | 消息系统语境可使用“消费者” |
| producer | 提供方 / 生成方 | 消息系统语境可使用“生产者” |
| gate | 判定条件 / 进入条件 / 审批节点 | 根据自动判断或人工审批区分 |
| execution graph | 执行图 / 任务依赖图 | 后者更适合需要直接解释 graph 的场景 |
| frontier | 当前可执行任务 / 待解决问题 | 调度和探索语境的含义不同 |
| source of truth drift | 权威来源与实际状态不一致 | 不必压缩成“事实源漂移” |

## 实现与 API 设计

| 英文或生硬表达 | 推荐表达 | 语境说明 |
| --- | --- | --- |
| boilerplate | 模板代码 / 重复样板代码 | 强调可机械生成或没有业务信息的部分 |
| plumbing | 基础连接代码 / 胶水代码 | 根据中性或负面语气选择 |
| escape hatch | 特殊处理入口 / 绕过机制 | 不译为“逃生舱” |
| footgun | 容易误用的设计 / 高风险用法 | 直接说明风险 |
| happy path | 正常流程 / 主流程 | 不译为“快乐路径” |
| edge case | 边界情况 / 少见异常 | 不要把所有异常都归为 edge case |
| fallback | 备用方案 / 失败后的降级处理 | 区分主动备用与失败回退 |
| best effort | 尽力执行 / 不保证成功 | 必要时直接写清不保证的内容 |
| breaking change | 不兼容变更 | “破坏性变更”已常见，但前者更直接 |
| deprecation | 弃用 | 与已经删除或不可用区分 |
| backward compatibility | 向后兼容 | 已有稳定译名 |
| graceful shutdown | 平滑关闭 | 不必写“优雅关闭” |
| graceful degradation | 平稳降级 | 说明故障时仍保留的能力更重要 |
| hot path | 性能关键路径 | 不译为“热路径” |
| blast radius | 影响范围 | 需要时补充受影响的系统、用户或数据 |
| rollout | 逐步启用 / 分批发布 | 区分功能开关与版本发布 |
| rollback | 回滚 | 已有稳定译名 |
| canary release | 小范围试发布 / 金丝雀发布 | 面向非专业读者优先前者 |
| dogfooding | 内部试用 / 用自己的产品验证 | 不译为“吃狗粮” |
| headless component | 无预设样式的组件 / 只提供行为逻辑的组件 | 按组件实际能力说明，不写“无头组件” |
| hydration | 客户端接管 / 水合 | 面向框架用户可首次写“水合（客户端接管）” |
| tree shaking | 移除未使用代码 / Tree Shaking | 不造“摇树优化”等难懂表达 |
| eject | 脱离默认配置 / 导出底层配置 | 按工具实际行为描述 |

## 系统与交付

| 英文或生硬表达 | 推荐表达 | 语境说明 |
| --- | --- | --- |
| trade-off | 取舍 | 通常比“权衡关系”更自然 |
| resilience | 容错与恢复能力 | “韧性”无法说明具体系统能力时展开写 |
| backpressure | 背压 | 分布式系统中已有稳定译名 |
| eventual consistency | 最终一致性 | 已有稳定译名 |
| idempotency | 幂等性 | 已有稳定译名 |
| observability | 可观测性 | 已有稳定译名 |
| circuit breaker | 熔断 | 已有稳定译名 |
| fan-out | 并行分发 / 扇出 | 面向一般读者优先说明行为 |
| drain | 停止接收新任务并等待存量完成 | 进程退出或流量迁移语境中直接说明动作 |
| shadow traffic | 复制线上流量进行验证 / 影子流量 | 首次出现时解释用途 |
| cold start | 冷启动 | 已有稳定译名 |
| zero-downtime deployment | 无停机发布 | 比“零宕机部署”更自然 |
| migration window | 迁移时段 / 迁移窗口期 | 根据是否强调时间限制选择 |
| maintenance burden | 维护负担 / 后续维护成本 | 不必写成“维护义务面” |
| operational overhead | 运维成本 / 额外操作成本 | 按责任主体区分 |

## Agent 与 AI 工程

| 英文或生硬表达 | 推荐表达 | 语境说明 |
| --- | --- | --- |
| agentic | 由 Agent 自主执行 / Agent 工作流 | 不笼统译为“智能体式” |
| autonomy | 自主执行范围 / 自主程度 | 强调系统被允许自行决定什么 |
| grounding | 基于可信资料作答 / 事实校准 | 不译为“接地” |
| guardrail | 行为约束 / 安全边界 / 保护措施 | 根据限制目标选择 |
| human in the loop | 人工参与环节 / 需要人工确认 | 直接说明人在何时介入 |
| approval gate | 审批节点 / 需确认的步骤 | 区分正式审批与普通确认 |
| elicitation | 向用户补充询问 / 信息采集 | 根据交互目的选择 |
| handoff | 交接 | 已有自然译法 |
| checkpoint | 阶段记录 / 检查点 | 区分恢复状态与质量检查 |
| orchestration | 编排 / 调度 | 多步骤协作常用“编排”，任务分配常用“调度” |
| routing | 路由 / 分流 | 请求转发用“路由”，分类派发可用“分流” |
| tool schema | 工具参数定义 | 强调结构格式时可写“工具 Schema” |
| tool calling | 工具调用 | 已有自然译法 |
| context compaction | 上下文压缩 | 已有自然译法 |
| memory | 会话记忆 / 长期记忆 / 持久化记录 | 先区分模型上下文、产品记忆和外部存储 |
| capability | 能力 / 功能 | 不需要为了专业感固定保留 capability |
| trace | 调用轨迹 / 执行记录 | 根据调试、审计或链路追踪语境选择 |
| agent runtime | Agent Runtime / Agent 运行环境 | Runtime 是特定产品概念时保留英文 |
| prompt injection | 提示词注入攻击 | 安全语境中补出“攻击”可减少歧义 |

## 通常保留的英文

以下内容通常不需要强行中文化：

- 产品名、框架名、协议名和标准缩写，如 Flutter、React、HTTP、MCP。
- 代码中的类名、函数名、字段名、配置项、命令和文件路径。
- API、SDK、CLI、Agent、Runtime、Token、Prompt 等中国技术团队普遍直接使用的词；面向非技术读者时再按需解释。
- 会因翻译丢失检索能力的新概念。首次使用可写“中文说明（English term）”，后续沿用约定名称。

保留英文不等于中英混排越多越好。英文只是名词时，仍应使用自然中文句法组织整句。
