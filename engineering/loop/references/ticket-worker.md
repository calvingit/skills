# Ticket Worker Protocol

Loop 使用本协议执行一张已经由 `start` 命令确认进入 `in_progress` 的 ticket。每个 capability 只完成自己的工作，不拥有 execution graph。

## 输入

必需：完整 `SPEC.md`、当前 JSON ticket、persisted current attempt、既有改动分类、依赖 evidence 和允许写入范围。任务目录存在 `HLD.md`，或 ticket 引用 D ID 时，完整 HLD 也是必需输入。缺少必需输入时返回 `blocked` receipt，不修改代码。

worker 使用 Loop 当前 workspace。Loop 可以通过 native sub-agent、provider CLI session 或当前 Manager session执行本协议；worker 不自行创建、切换或管理执行环境。

## 执行

1. `implement` 把 ticket 的 `what_to_build`、`constraints` 和 ticket-local `acceptance_criteria` 作为实现要求；`verify` 只核验外部完成条件；`review` 只完成 standards、SPEC 与适用 HLD 审查。Parent SPEC 提供需求背景，HLD 如存在提供概要技术约束，二者都不自动把 sibling tickets 纳入范围。
2. 重新调查目标仓库：读取适用 Agent 指令、项目 standards、领域与架构文档、相关生产代码、调用链、错误路径、测试和配置；task artifacts 是 contract，不是代码配方。
3. 形成当前 ticket 的最小实现方案。遵守适用 D IDs，只在 HLD 的局部实现空间内完成局部详细设计。需求、公开约定或验收未定时返回 requirement blocker；HLD 缺失、冲突或被代码事实证明不可行时返回 design blocker，不在实现中猜测或改写上游 contract。
4. `implement` 先确定外部可观察行为和真实生产 Seam；适用时按 one behavior → red test → minimal green implementation 推进，并完成必要 simplification。它只能修改允许写入范围内的交付代码。
5. `verify` 在实现后的 workspace 中运行能直接证明 ticket-local AC 的验证和必要项目 gate，记录命令、退出码、关键输出与未验证范围。只允许 Loop 分配的临时写入范围。
6. `review` 接收 implement 与 verify 的 capability receipts，在当前 diff 上分别完成项目 Standards、ticket / Parent SPEC，以及存在 HLD 时的适用 D IDs 审查。
7. 每个 capability 不修改 SPEC、HLD、ticket JSON 或 sibling tickets；不 commit、push、改写历史，也不再次委托同类 worker。

## Execution modes

- `multi-agents`：implement worker 在 repair rounds 间复用同一个 `agent_id`；verify/review 每轮使用新 context。Manager 负责 `spawn_agent`、`send_input`、`wait_agent` 和 `close_agent`。
- `multi-threads`：provider CLI session 在 repair rounds 间使用显式 session ID/path resume；verify/review 不复用 implement session。默认 provider 是 Codex，也可由调用方选择 Claude、Kimi 或 Pi。
- `serial`：当前 Manager session 逐 capability 执行，不创建外部 Agent 或 CLI session；必须显式报告 context isolation 降级。

`multi-threads` 的 provider CLI 默认使用该工具的最大权限参数。权限不改变 worker 的 allowed write scope，也不允许 worker 修改 graph。

长任务的等待不以固定 wall-clock 时长判断失败。Manager 可提供任务预算、heartbeat freshness 和 progress freshness 阈值；无阈值时持续等待 provider 终态，heartbeat/progress 失鲜时先中断并保留原始输出。

## Receipt

返回 JSON capability result：`outcome` 为 `completed`、`blocked`、`failed` 或 `interrupted`，并在 `payload` 中提供本 capability 的结果。Loop 依次把 prior capability receipts 放入 handoff bundle，聚合为符合 [worker-receipt.schema.json](../../execution-graph/schemas/worker-receipt.schema.json) 的 JSON。worker 的 `completed` 不等于 ticket 已 `done`：Loop 必须独立核验 workspace、attempt baseline、verification 和 reviews，随后才可把已接受的 facts 提交给 `complete`、`block` 或其他命名 mutation。

```json
{
  "schema_version": 1,
  "outcome": "completed",
  "ticket_id": "T004",
  "current_attempt": 1,
  "landed_changes": [{"path": "path/to/file", "summary": "observable change"}],
  "acceptance_evidence": [{"acceptance_id": "AC1", "result": "passed", "summary": "command, artifact, or observation"}],
  "verification": [{"command": "command", "exit_code": 0, "summary": "key result"}],
  "simplification": {"result": "completed"},
  "review": {"standards": "pass", "spec": "pass", "hld": "pass"},
  "blocker": null,
  "unverified": []
}
```

`not_verified` 不得进入 ticket 的 current evidence，也不能满足完成门。worker 发现 requirement/design/dependency/environment 等问题时应在 receipt 中如实返回 blocker；Loop 判断它是 execution blocker、graph gap 还是上游 amendment，并选择对应路由。

## SPEC / HLD amendment

Loop 通知当前 ticket 受到已确认的 SPEC/HLD amendment 影响时，worker 在安全边界停止继续写入并返回 `interrupted` receipt，列明部分已实现改动、已运行验证和未完成 Acceptance Criteria。不得自行恢复 lifecycle、supersede ticket 或修改上游与 ticket contract。
