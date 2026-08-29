# Multi-task Orchestration

仅在 PLAN 有多个 task 或存在真实 blocking edge 时使用；单 task 不需要本文件。

## 并行条件

- task 位于同一 ready frontier，互不依赖。
- 写入文件、公共接口、共享配置和外部资源没有重叠或冲突。
- 每个 worker 有明确 ownership、验收映射和验证目标。

任一条件无法证明时保持串行，或拆到独立 worktree。

## 派发与集成

1. 每个 worker 只负责一个 task unit，不回退他人改动，不 commit/push，不派生 subagent。
2. 传入用户请求、task 契约、SPEC/PLAN、baseline、既有改动、ownership 和验证目标。
3. worker 超出 ownership 时返回 `ownership_request`，不得用 callback、测试钩子或 wrapper 绕过边界。
4. 主 agent 收齐 receipt 后重新读取实际 diff，检查越界、重叠、行为和集成，再更新 task 状态并计算下一轮 ready frontier。
