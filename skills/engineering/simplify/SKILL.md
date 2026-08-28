---
name: simplify
description: "Used when 需要在行为不变前提下收缩当前任务改动或生产接口时（触发词：简化代码、删除过度设计、收缩 diff）。"
---

# Simplify

在不改变 SPEC、协议、外部可观察行为、并发、生命周期和失败语义的前提下，删除当前任务引入的偶然复杂度。

## 流程

1. 固定 baseline、当前任务 diff、既有改动、行为来源和允许修改的 ownership。
2. 阅读生产调用方、测试调用方、组装点、外部边界和相关验证；无法证明改动归属或行为保持时返回 `blocked`。
3. 优先删除纯转发层、重复 wiring、无生产调用者的抽象、测试专用接口和重复断言；复用已有能力，不把复杂度搬到调用方。
4. 保留输入校验、错误处理、安全、可访问性、真实外部 adapter、取消/dispose、事务、权限和必要状态门禁。
5. 每次收缩后运行受影响的最小验证；若改变契约、ownership、验收或阻塞关系，停止并转回 `grilling` / `to-spec` / `implement`。

## 输出

只返回 Markdown receipt：结果（`completed | no_change | blocked | failed`）、改动文件、移除内容、接口变化、保持的不变量、验证和剩余风险。
