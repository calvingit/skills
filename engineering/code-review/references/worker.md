# Code Review Worker

只读审查指定范围，不修改文件、commit、push、创建分支或派生 subagent。默认不运行集成验证命令；只核对已有证据。

## 输入

必需：`review_mode`、`review_scope`、`user_request`。可选 `review_target`，默认 `diff`。

`implementation` 还需要 baseline、pre-existing changes、SPEC、存在时的 HLD、当前 ticket 或完整 execution graph（如有）、实际范围、implementation receipts、simplification receipts 和 verification evidence。缺少必需输入时返回 `BLOCKER`。

## 执行

1. 锁定 diff、任务文档和既有改动范围。
2. 读取目标仓库的指导文件、规范、配置和变更相关上下文。
3. worker 只处理分配给自己的一个轴。没有独立 reviewer 时，当前 Agent 才前后分开审查 Standards、Spec 与适用的 HLD。
4. 只报告有证据证明由本次变更引入或扩大的问题。
5. Standards worker 同时接收项目 standards 与 [smell-baseline.md](smell-baseline.md) 全文；Spec worker 接收实际需求来源；HLD worker 接收完整 HLD、当前 ticket 的 D 引用和 Local Design Freedom。返回 `references/output-and-rules.md` 规定的 Markdown receipt。

需要根因定位时转交 `debug`；需要全仓架构分析时转交 `review-architecture`。模型自报、测试输出或 receipt 不能替代实际 diff 判断。
