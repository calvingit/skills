---
name: implement
description: "在 Loop 分配的写入范围内实现一个 ticket 的交付行为。"
---

# Implement

负责当前 ticket 的代码实现和必要的 simplification。只修改 Loop 提供的 allowed write scope，返回实现结果；不修改 SPEC、ACCEPTANCE、HLD、ticket / graph，不调度 sibling ticket，也不提交版本控制变更。

实现完成后返回 landed changes、simplification 状态和 capability receipt。验证或审查发现的问题由 Loop 通过新的 attempt 重新传入。

implement 不执行或填写 verify 的命令退出码，也不伪造 evidence；验证由 verify 负责。

CLI capability 输出遵守 [Runtime 输出契约](../../docs/loop-runtime.md#capability-result)，由 runtime 随 prompt 传入当前角色 schema。
