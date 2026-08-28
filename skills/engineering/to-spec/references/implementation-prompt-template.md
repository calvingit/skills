# Implementation Handoff Prompt

这是 `to-spec` skill 为跨 session、跨 Agent Runtime 或用户明确要求交接的任务生成的短执行 envelope，不是第三份需求文档。`SPEC.md` 与 `PLAN.md` 是唯一契约来源；envelope 携带 `loop` 的执行语义和交接参数，生成时只替换 `<...>` 占位符。

```text
按 loop 语义完成 <TASK_DIRECTORY> 中 SPEC.md 和 PLAN.md 定义的任务：仓库存在 .agents/skills/loop/SKILL.md 时以它为执行规则，本提示词只补充交接参数。

一轮 = 从当前 ready task 推进到集成验证与两轴审查完成，含强制 simplify 和审查修复循环。退出条件：所选 task 全部完成，每条 AC 有 verification evidence，审查没有未处理的必须修复，simplification gate 已执行；满足后按 commit 授权 <COMMIT_AUTHORIZED> 收尾（是：只提交本任务文件，message 遵循 docs/rules/git-commit.rules.md，不 push；否：不 commit）。退出判定只引用已存在的证据。

停止条件：出现必须先收敛需求的新事实（契约冲突、方案失效、scope 变化）、同一 finding 无新证据重复出现、达到 <MAX_ROUNDS> 轮上限（默认 3）、没有站得住脚的下一步。停止时保留断点（STATUS.md、receipts 摘要、已用轮数、baseline 与 pre-existing patch snapshot 引用），汇报已尝试路径、证据、阻塞点和继续所需输入。

每轮开始先重读 SPEC/PLAN 与断点，重新核对工作区状态；保留 dirty worktree 中的既有改动，不吞并，不扩大 SPEC/PLAN 的契约范围。完成时汇报 task/AC 状态、实际改动、验证与审查结果和未验证项。
```

## 生成规则

- 默认不生成；仅在 multi-task、来自 wayfinding、跨 session、其他 Agent Runtime 或用户明确要求交接时生成。目的是让接收方按 `loop` 语义自动推进到收尾，不是复述 SPEC/PLAN 的内容。
- 占位符来源：`<TASK_DIRECTORY>` 填任务目录；`<COMMIT_AUTHORIZED>` 只在用户已明确授权收尾 commit 时填「是」，默认「否」；`<MAX_ROUNDS>` 填用户指定的轮数上限，未指定保留默认 3，交接时已有进行中的 loop 则填剩余轮数。
- 最终汇报同时提供 `IMPLEMENT_PROMPT.md` 路径和完整可复制文本。
- 实现阶段若提示词与 SPEC/PLAN 冲突，以 SPEC/PLAN 为准并停止处理冲突。
- `IMPLEMENT_PROMPT.md` 不进入 living spec，也不作为长期需求来源。
