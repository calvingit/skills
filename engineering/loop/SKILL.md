---
name: loop
description: "使用 loopx 消费 ticket graph，按 serial 或 multi-agents 模式调度执行单元并完成交付审查。"
---

# Loop

本 Skill 负责 ticket 选择、attempt、workspace baseline、调度模式、receipt acceptance 和完成门，具体执行由已安装的 `loopx` CLI 提供。

## 入口

开始或恢复时先检查 graph：

```bash
loopx loop status <task-dir>
loopx graph inspect <task-dir>
```

执行当前 ready ticket：

```bash
loopx loop run <task-dir> --scope <path>
```

执行模式只有两种：

- `serial`：在单一会话中按 implement → verify → code-review 顺序执行，默认模式。
- `multi-agents`：为独立 ticket 或 capability 创建多个 sub-agent；只有写入范围、共享副作用和集成顺序有隔离证据时启用。

## 规则

- 启动时加载任务已有的 `SPEC.md`、可选 `ACCEPTANCE.md`、可选 `HLD.md` 和 `tickets/*.json` 作为事实来源并保持 contract 不变。Loop 不为缺少可选协议、场景映射或 expected result 推导新条件；仅在 ticket 或 receipt 结构无法校验、必需证据缺失或边界被违反时阻断。
- 只有本 Skill 能通过 `loopx graph` 写入 `start`、`retry`、`block`、`unblock`、`complete` 和 `reopen`。Worker 只执行当前 ticket 的 capability，不调度 sibling、不修改 graph、不 commit 或 push。
- 根据实际 workspace、scope、验证输出、review 和 receipt 独立判断完成，不接受 Worker 的口头宣称。默认使用 `serial`；`multi-agents` 必须有依赖、写入范围、共享副作用和集成顺序的隔离证据。
- 完成门通过后默认不提交版本控制变更，除非调用方明确授权。只接受 ticket、SPEC 或任务明确启用的独立协议中的验收条件，以及命令输出、workspace diff、receipt 和 review evidence，不新增验收条件或用 Worker 自报替代独立 evidence。
- verify 负责执行任务所需命令并记录实际结果；Loop 只接受其 evidence、检查 scope/Git/graph 边界并执行 `unblock`、retry、block 或 complete。独立 `ACCEPTANCE.md` 仅在任务明确需要时使用，不是默认前置条件。

命令输入与中断、blocker、事务恢复步骤见 [Runtime 恢复契约](../../docs/loop-runtime.md#graph-mutation-与恢复)。
