# Ticket Worker Protocol

Loop 使用本协议执行一张已经由 `start` 命令确认进入 `in_progress` 的 ticket。worker 只完成当前工作单元，不拥有 execution graph。

## 输入

必需：完整 `SPEC.md`、当前 JSON ticket、persisted current attempt、既有改动分类、依赖 evidence 和允许写入范围。任务目录存在 `HLD.md`，或 ticket 引用 D ID 时，完整 HLD 也是必需输入。缺少必需输入时返回 `blocked` receipt，不修改代码。

worker 使用 Loop 当前 workspace，不创建、切换或管理执行环境。

## 执行

1. 把 ticket 的 `what_to_build`、`constraints` 和 ticket-local `acceptance_criteria` 作为本次限定的实现要求；Parent SPEC 提供需求背景，HLD 如存在提供概要技术约束，二者都不自动把 sibling tickets 纳入范围。
2. 重新调查目标仓库：读取适用 Agent 指令、项目 standards、领域与架构文档、相关生产代码、调用链、错误路径、测试和配置；task artifacts 是 contract，不是代码配方。
3. 形成当前 ticket 的最小实现方案。遵守适用 D IDs，只在 HLD 的局部实现空间内完成局部详细设计。需求、公开约定或验收未定时返回 requirement blocker；HLD 缺失、冲突或被代码事实证明不可行时返回 design blocker，不在实现中猜测或改写上游 contract。
4. 每个 delivery slice 先确定外部可观察行为和真实生产 Seam。expected behavior 有独立来源且 Seam 稳定时，按 one behavior → red test → minimal green implementation 推进；否则使用项目已有的最小充分反馈循环，不为测试制造生产接口。
5. 只修改允许写入范围内的交付代码；不得领取、实现或修改 sibling tickets。实现期间持续运行当前 slice 的定向验证和相关 typecheck。
6. 完成实现后检查完整 unit diff，移除不改变行为的偶然复杂度；再运行能直接证明 ticket-local AC 的验证和受影响范围的项目 gate，记录命令、退出码、关键输出和未验证范围。
7. 分别按项目 Standards、当前 ticket / Parent SPEC，以及存在 HLD 时的适用 D IDs 审查 unit diff；修复审查发现后重跑受影响验证。任一适用轴仍有 blocker 时不得返回 `completed`。
8. 不修改 SPEC、HLD 或 ticket JSON；Loop 是唯一调用 graph mutation command 的 owner。
9. 不 commit、push、改写历史，也不把当前完整工作单元再次委托给另一个同类 worker。

## Receipt

返回符合 [worker-receipt.schema.json](../../execution-graph/schemas/worker-receipt.schema.json) 的 JSON。`completed` 只是 worker outcome，不等于 ticket 已 `done`：Loop 必须独立核验 workspace、attempt baseline、verification 和 reviews，随后才可把已接受的 facts 提交给 `complete`、`block` 或其他命名 mutation。

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
