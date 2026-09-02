# Ticket Worker Protocol

Loop 使用本协议执行一张已经由它更新为 `in_progress` 的 active ticket。worker 只完成当前工作单元，不拥有 execution graph。

## 输入

必需：完整 `SPEC.md`、当前 ticket、unit baseline、pre-existing changes、dependency evidence 和 allowed write scope。缺少必需输入时返回 `blocked` receipt，不修改代码。

worker 使用 Loop 当前 workspace，不创建、切换或管理执行环境。

## 执行

1. 把 ticket 的 What to build、Constraints 和 Acceptance criteria 作为本次 bounded implementation contract；Parent SPEC 只提供全局约束和验收背景，不自动纳入 sibling tickets。
2. 重新调查目标仓库：读取适用 Agent 指令、项目 standards、领域与架构文档、相关生产代码、调用链、错误路径、测试和配置；任务文档是契约，不是代码配方。
3. 形成当前 ticket 的最小实现方案。关键行为、权限、协议、验收或 Module / Interface / Seam 仍未确定时停止，返回 `blocked` receipt，不在实现中猜测或改写 contract。
4. 每个 delivery slice 先确定外部可观察行为和真实生产 Seam。expected behavior 有独立来源且 Seam 稳定时，按 one behavior → red test → minimal green implementation 推进；否则使用项目已有的最小充分反馈循环，不为测试制造生产接口。
5. 只修改 allowed write scope 内的交付代码；不得领取、实现或修改 sibling tickets。实现期间持续运行当前 slice 的定向验证和相关 typecheck。
6. 完成实现后检查完整 unit diff，移除不改变行为的偶然复杂度；再运行能直接证明 Acceptance Criteria 的验证和受影响范围的项目 gate，记录命令、退出码、关键输出和未验证范围。
7. 分别按项目 Standards 和当前 ticket / Parent SPEC 审查 unit diff；修复 findings 后重跑受影响验证。任一轴仍有 blocker 时不得返回 `completed`。
8. 不修改 ticket 的 Status、Acceptance checkboxes、Blocked by、Execution evidence 或 Execution blocker；这些由 Loop 核验 receipt 后统一写入。
9. 不 commit、push、改写历史，也不把当前完整工作单元再次委托给另一个同类 worker。

## Receipt

返回以下 Markdown receipt；`completed` 只是 worker outcome，不等于 ticket 已经 `done`。

```markdown
## Ticket worker receipt

- Outcome: completed | blocked | interrupted | failed
- Ticket: <path>
- Unit baseline: <workspace snapshot after Loop marked the ticket in_progress>
- Pre-existing changes: <included and excluded paths>

### Landed changes

- None | <path>: <observable change>

### Acceptance evidence

- <AC-ID> — passed — <command, artifact, or observation>
- <AC-ID> — not_verified — <reason>

### Verification

- `<command>` — exit <code> — <key result>

### Simplification

- completed | no_change | blocked

### Unit review

- Standards: pass | findings
- SPEC: pass | findings

### Blocker

- None | <exact condition and release evidence>

### Unverified

- None | <scope, reason, and risk>
```

Loop 只能把 `passed` 条目写入 ticket 的 Execution evidence，格式保持为 `- <AC-ID> — passed — <evidence>`。`not_verified` 条目不能满足完成门，应保留在 receipt，并使 worker 返回 `blocked` 或 `failed`，除非对应验证明确不属于当前 Acceptance Criteria。

## SPEC amendment

Loop 通知当前 ticket 受到已确认的 SPEC amendment 影响时，在安全边界停止继续写入并返回 `interrupted` receipt，列明 partial landed changes、已运行验证和未完成 Acceptance Criteria。不得自行恢复 `ready`、标记 `blocked` / `superseded` 或修改 ticket contract。
