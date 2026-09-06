---
name: loop
description: "使用 loopx 消费 ticket graph，调度 worker capability，聚合 evidence 并完成交付审查。"
---

# Loop

`loop` 负责 ticket 选择、attempt、workspace baseline、worker dispatch、receipt acceptance 和完成门。实现细节由已安装的 `loopx` CLI 提供。

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

## 规则

- SPEC.md、可选 HLD.md 和 `tickets/*.json` 是事实来源；Loop 不改写 SPEC/HLD 或 ticket contract。
- 只有 Loop 通过 `loopx graph` 写入 `start`、`retry`、`block`、`unblock`、`complete` 和 `reopen`。
- Worker 只执行当前 ticket 的 capability，不调度 sibling、不修改 graph、不 commit 或 push。
- 根据实际 workspace、scope、验证输出、review 和 receipt 独立判断完成，不接受 worker 口头完成宣称。
- 默认串行；只有依赖、写入范围、共享副作用和集成顺序都有证据时才允许并行。
- 完成门通过后默认不提交版本控制变更，除非调用方明确授权。
