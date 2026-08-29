# Implementation Handoff Prompt

仅用于跨 session、跨 runtime 或用户明确要求交接；`SPEC.md` 与 `PLAN.md` 是唯一需求来源。

```text
按 <TASK_DIRECTORY> 中的 SPEC.md 和 PLAN.md 完成任务。每轮从 ready task 推进到验证、simplify 和 code-review 完成。退出条件：所选 task 完成、每条 AC 有证据、没有未处理的必须修复 finding。commit 授权：<COMMIT_AUTHORIZED>；轮数上限：<MAX_ROUNDS>。

每轮开始重新读取 SPEC/PLAN、断点和工作区状态，保留既有改动。出现契约冲突、范围变化、重复无进展或没有可行下一步时停止，保留 STATUS.md、receipts、轮数和 baseline 证据，并报告阻塞点。
```

不要把提示词升级为第三份需求文档；与 SPEC/PLAN 冲突时以它们为准。
