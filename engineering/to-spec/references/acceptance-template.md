# ACCEPTANCE.md 模板

Create 必须与 `SPEC.md` 同时生成。Amendment 保留未受影响场景，受影响场景原位更新。章节名称具有规范性，不得改名或省略；不适用的写明原因，不用占位符。

```markdown
---
protocol_version: 1
spec_snapshot: <version, date, or content fingerprint>
status: draft | confirmed | superseded
owner: to-spec
verification_owner: loop
---

# Acceptance Protocol

## Public Interface

- <CLI / HTTP / JSON / schema / 退出码 / 权限或 artifact 边界；没有则写 None 及原因>

## Observable Behavior

- <不查看实现即可观察的外部行为>

## Success Matrix

| ID | Covers | Scenario | Expected result | Evidence |
|---|---|---|---|---|
| S1 | R1, AC1 | <场景> | <可判定结果> | <可执行命令或证据类型> |

## Failure Matrix

| ID | Covers | Scenario | Expected result | Evidence |
|---|---|---|---|---|
| F1 | R2, AC2 | <失败 / 取消 / 超时 / 权限 / 环境> | <可判定结果> | <可执行命令或证据类型> |

## Evidence Rules

- <什么算通过、什么必须保留、什么不得用模型自报替代>

## Verification Commands

- <可执行命令；不可执行的标入 Unverified Coverage>

## Environment Prerequisites

- <运行验证所需环境；没有则写 None>

## Unverified Coverage

- <未验证路径及原因，或 None>

## Change History

- v1: <本次创建或修订摘要>
```

## 写作规则

- 头部固定为 `protocol_version`、`spec_snapshot`、`status`、`owner: to-spec`、`verification_owner: loop`。
- 公开行为、错误或取消语义、CLI/JSON/schema/退出码、权限或 artifact 边界变化必须递增 `protocol_version`。内部重构和新增测试不升级。
- 写入前执行 `R → AC → scenario → expected result → executable evidence` 双向检查。协议缺口交回 `grilling`，不伪装成实现任务。
- 每个场景至少引用一个当前 `R` 和一个 `AC`，写明 expected result 和可执行证据。当前所有 `R` 与 `AC` 都必须被场景覆盖。
- 成功、失败、取消、超时、权限和环境路径必须明确写出。
- HLD 负责共享技术约束；ticket 负责执行，不在本文件发明验收语义。
