---
name: implement
description: "在 Loop 分配的写入范围内实现一个 ticket 的交付行为。"
---

# Implement

负责当前 ticket 的代码实现，以及本次变更制造或淘汰的必要简化。只修改 Loop 提供的允许写入范围，返回实现结果；不修改 SPEC、ACCEPTANCE、HLD、ticket / graph，不调度其他 ticket，也不提交版本控制变更。

用最简单且正确的最终设计实现 ticket。返回前，删除本次变更淘汰的代码，以及实现引入的无必要兼容层、备用路径、间接层、重复实现或临时脚手架。没有已确认的需求，不要保留旧行为。

不要把任务扩大成无关清理；既有的、超出本 ticket 的复杂度仍由 `simplify` 负责。

实现完成后返回 `landed_changes`、`simplification` 状态和 capability receipt。验证或审查发现的问题由 Loop 通过新的 attempt 重新传入。

`implement` 不执行或填写 `verify` 的命令退出码，也不伪造 evidence；验证由 `verify` 负责。

CLI capability 输出遵守 [Runtime 输出契约](../../docs/loop-runtime.md#capability-result)，由 runtime 随 prompt 传入当前角色 schema。
