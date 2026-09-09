# ACCEPTANCE.md 模板

只有需要独立版本、跨 ticket 复用场景或复杂协议矩阵时才创建。Create 与 Amendment 保留当前任务需要的章节；不适用的写明原因，不用占位符。

````markdown
---
protocol_version: 1
status: draft | confirmed | superseded
owner: to-spec
---

# Acceptance Protocol

## Public Interface

- <CLI / HTTP / JSON / schema / 退出码 / 权限或 artifact 边界；没有则写 None 及原因>

## Observable Behavior

- <不查看实现即可观察的外部行为>

## Acceptance Criteria / Scenarios

- <验收条件或场景；仅在需要独立协议时填写>

## Failure and Environment Notes

- <失败、取消、超时、权限和环境约束；没有则写 None>

## Evidence Rules

- <什么算通过、什么必须保留、什么不得用模型自报替代>

## Unverified Coverage

- <未验证路径及原因，或 None>

## Change History

- v1: <本次创建或修订摘要>
````

## 写作规则

- `protocol_version` 是从 1 开始的任务验收修订号；公开行为、错误或取消语义、CLI/JSON/schema/退出码、权限或 artifact 边界变化时递增。内部重构和新增测试不升级。
- 写入前执行 `R → AC → scenario → expected result → executable evidence` 双向检查。协议缺口交回 `grilling`，不伪装成实现任务。
- 每个场景至少引用一个当前 `R` 和 `AC`，写明 expected result 和证据类型；只有启用独立场景协议时才要求机器可读映射。
- 成功、失败、取消、超时、权限和环境路径必须明确写出。
- HLD 负责共享技术约束；ticket 负责执行，不在本文件发明验收语义。
