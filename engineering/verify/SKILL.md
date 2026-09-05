---
name: verify
description: "在独立只读上下文中验证 ticket 的 Acceptance Criteria。"
---

# Verify

针对 Loop 提供的 implementation snapshot 验证 ticket-local Acceptance Criteria。重点回答“是否按要求工作、证据是什么”，不评价代码或设计质量。

## 与 `code-review` 的边界

只验证可观察结果和完成条件，不检查代码规范、设计质量、代码异味、抽象合理性或实现风格；这些属于 `code-review`。

## 流程

1. 从用户要求、SPEC、ticket 和 handoff bundle 提取可验证的完成条件；没有明确条件时，只验证能够客观确认的部分，不自行扩展需求。
2. 根据变更范围和风险选择最小必要验证：针对性测试、lint、类型检查、构建、运行时检查、接口调用、静态搜索、差异检查或项目已有验证入口。
3. 优先复用仓库现有脚本、Make target、CI 命令和测试入口，不为验证新增生产代码或测试专用接口。
4. 记录实际执行的命令、关键输出和失败项；无法执行的检查明确标为未验证，不能用代码阅读代替运行证据。
5. 对照完成条件逐项返回 `verified`、`failed` 或 `not_verified`，并附上可复核证据。

## 边界

默认只读：不修改代码、SPEC、HLD、ticket/graph 或外部业务状态，只允许隔离的临时测试产物和缓存。发现失败时返回 evidence；需要定位原因交给 `debug`，需要评价实现质量交给 `code-review`。

完成后返回 capability receipt，至少包含 ticket/attempt identity、AC evidence、verification、unverified scope 和 outcome。不得调度 sibling ticket、修改 graph 或提交版本控制变更。
