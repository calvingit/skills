---
name: loop
description: "执行并验证多工作单元的依赖图。"
---

# Loop

Loop 是一个 Runtime-neutral engineering execution protocol。它消费已经明确的多-ticket execution graph，负责计算 ready frontier、调度执行单元、聚合 evidence，并持续推进到 `done`、`blocked`、`no_progress` 或 `budget_exhausted`。

`SPEC.md` 提供规范性需求，`tickets/` 提供 execution graph。Loop 不定义需求、不拆 tickets，也不复制单个工作单元的实现纪律。

## 何时使用

已有多张 delivery tickets，需要持续推进依赖图、判断串并行、聚合交付证据并执行最终集成审查时使用 Loop。

以下情况不要使用：

- 需求或 expected behavior 尚未收敛；
- 重要技术路径仍处于 Fog of war；
- 只有一个明确的工作单元；
- 当前任务是调查未知 bug 根因；
- 只是重复执行因瞬态故障失败的命令。

## Contract and authority

首次 dispatch 前读取完整 `SPEC.md` 和所有 tickets，并记录 graph baseline、`HEAD` 与 pre-existing working-tree inventory。恢复执行时从最早可信的 implementation receipt 还原范围；无法还原时明确记录 review coverage blind spot。

Loop 只维护 execution graph，不改写 ticket 的 What to build、Constraints、Acceptance criteria 或 Blocked by。状态所有权如下：

Status 为 `ready`、`blocked`、`in_progress` 或 `done` 的 ticket 属于 active graph；`superseded` ticket 只保留历史 contract 和 evidence，不属于 active graph。

- `to-tickets` 创建 initial `ready` / `blocked`；
- SPEC amendment 后，`to-tickets` 保留仍有效的状态，或将不再适用的 ticket 标为 `superseded` 并创建 amendment/replacement ticket；
- `implement` 负责 `ready → in_progress → done/blocked`、验收勾选和 execution evidence；
- Loop 只在 evidence 证明阻塞解除后执行 `blocked → ready`，或在 SPEC 未变、whole-graph review 发现既有范围内缺陷时执行 `done → ready`。不得用 `done → ready` 表达需求变化。

调用 Loop 只授权按当前任务契约推进工程工作，不隐含 commit、push、建分支或改写历史授权。版本控制写操作必须来自用户明确授权或上层 workflow 已提供的授权。

## Execution loop

每轮按以下协议执行：

1. **Observe**：读取 graph、上一轮 receipts、landed changes、验证结果和未解决 findings，只加载决定下一步所需的上下文。
2. **Calculate frontier**：排除 `superseded` tickets，再根据 Status、Blocked by 和其他已记录阻塞计算 ready frontier；先处理状态冲突、重复领取、指向 superseded ticket 的依赖和 dependency cycle。
3. **Dispatch**：按调度规则选择一张或多张 ready ticket。为每个执行单元固定 parent SPEC、唯一当前 ticket、baseline、pre-existing changes、已落地依赖、必要项目上下文、workspace/isolation、版本控制授权和 receipt 契约。
4. **Verify landed state**：核对实际 diff、ticket receipt、验证命令、退出状态和关键 evidence；并行执行时同时检查跨 ticket 冲突、共享假设和集成结果。失败是下一轮 evaluate 的 evidence，除非证明确属瞬态故障，否则不自动 retry。
5. **Evaluate**：比较本轮前后的工程状态，检查 progress，重新计算 frontier，并决定继续或进入稳定结果。

所有 active tickets 都为 `done` 时进入 Whole-graph gate；`superseded` tickets 是保留 evidence 的非活动历史，不计入 frontier 或完成覆盖。没有 ready 或 `in_progress` active ticket 但仍有未完成 active ticket 时进入 `blocked`，并报告 blocker、状态冲突或 dependency cycle。

## Dispatch and isolation

默认串行选择一张 ready ticket。Runtime 支持 subagent 时，默认委托给独立 implementer subagent；不可用时由当前 Agent 执行。每个执行单元只处理当前 ticket，不得领取 sibling ticket。

Loop 拥有 implementer execution unit 的创建、scope、串并行、workspace/isolation、等待、恢复、中断和重新派发。接收任务的 Agent 必须调用 `implement` 执行当前 ticket；`implement` 定义内部调查、修改、验证、审查和 evidence 程序，不再递归创建 implementer。用户直接调用 `implement` 时，当前 Agent 就是 implementer。

多个 ready tickets 不代表应该并行。只有同时满足以下条件时才并行 dispatch：

- Runtime 支持多个独立执行单元；
- tickets 之间没有 dependency edge；
- 代码、生成物、测试资源、外部环境和可变状态具有足够 isolation；
- 一个 ticket 不太可能改变另一个 ticket 的契约或关键实现前提；
- landed changes 有明确、低风险的 integration 顺序和冲突处理方式；
- 并行收益足以覆盖协调和集成成本。

独立 worktree 只是可选 isolation mechanism。只有共享 working tree 无法提供所需隔离，且独立 worktree 能实质降低覆盖、竞争或集成风险时才使用；worktree 本身不能证明 tickets 相互独立。

并行执行后必须逐项核对 receipts、验证 landed state 并解决集成问题，再重新计算 frontier。不得仅依据 subagent 自报更新 graph。

## Progress and outcomes

有效 engineering iteration 必须产生至少一个可观察变化：

- ticket、acceptance criterion、blocker 或 ready frontier 改变；
- unknown 转化为 verified fact；
- failing verification 变为 passing；
- review finding 被解决或因新 evidence 被有效重新分类；
- whole-graph review 状态改变；
- 新 evidence 改变下一步选择。

本轮结束时工程状态与进入时实质相同，则进入 `no_progress`。不得把模型消息数、iteration 数、Token 消耗、代码行数或“再试一次”当作 progress。

Retry 只是同一 action 因网络错误、临时服务不可用、命令中断或 Runtime interruption 等瞬态失败而重试。Retry 不代表工程状态变化，也不计为新的 engineering iteration。

Loop 只有以下稳定结果：

- `done`：Whole-graph gate 通过；
- `blocked`：继续需要外部输入、权限、用户决策，或 graph 内部冲突导致没有可执行工作；
- `no_progress`：当前 evidence 下不存在能改变状态的合理动作；
- `budget_exhausted`：达到调用方明确提供的 safety budget，但尚未进入其他稳定结果。

`ready` 和 `in_progress` 是 ticket graph 状态，不是 Loop 的稳定结果。

## Whole-graph gate

所有 active tickets 都进入 `done` 后：

1. 从 graph baseline 到当前 landed state 构造完整审查范围，排除 pre-existing 和无关改动，并汇总 `SPEC.md`、全部 active 与 superseded tickets、implementation receipts、simplification receipts、verification evidence 和未验证项。superseded ticket 不提供当前验收覆盖，但它留下的代码仍属于 landed state，必须检查是否已被保留、修改或撤销。
2. 调用 `code-review` 的 `implementation` mode，对完整 graph 分别执行 Standards 与 Spec 审查。Loop 只负责提供范围、聚合结果和后续调度。
3. 必须修复的 finding 若属于既有 ticket contract，将最小责任 ticket 集合从 `done` 重新置为 `ready`，附上 finding evidence，再通过 `implement` 修复；不得改写 ticket 契约容纳 finding。
4. finding 没有既有 ticket 承担、暴露 graph 缺口时交回 `to-tickets`；需要改变需求、范围、接口 contract 或 acceptance criteria 时交回 `to-spec`。
5. 修复后重新运行受影响验证并再次执行 whole-graph review。

只有同时满足以下条件才能进入 `done`：

- 所有 active tickets 都是 `done`，且不存在仍被引用的 `superseded` blocker；
- 当前 SPEC 的每个 in-scope R/AC 都由至少一张 active `done` ticket 的 evidence 覆盖，不能使用 superseded ticket 充数；
- acceptance criteria 有可观察 verification evidence；
- 相关验证通过，或未验证项已明确且被任务契约允许；
- 每个 ticket 必要的 `simplify` / `code-review` 已完成；
- whole-graph Standards 与 Spec 审查均无未处理的必须修复 finding；
- 并行分支或 worktrees 的 landed state 已完成集成验证；
- 没有属于当前 Destination 的 blocker 或 unknown 被静默遗留。

不得根据各 ticket 分别通过审查推断完整 graph 已通过。跨 ticket 接口、共享状态、数据流、错误路径和集成行为必须在最终 landed state 上检查。

## Termination

出现以下情况时停止当前执行路径：

- 需求、契约、权限或验收必须重新收敛：转 `grilling` / `to-spec`；
- 重要路径重新进入 Fog of war：转 `wayfinding`；
- 当前问题变成根因未知的 bug investigation：转 `debug`；
- 一轮没有满足 progress invariant，或没有站得住脚的 next action：进入 `no_progress`；
- 达到调用方明确提供的 safety budget：记录当前 evidence 和剩余 frontier，进入 `budget_exhausted`。

Safety budget 是调用方提供的执行边界，不是任务规模估算。优先使用调用方或项目已有预算；没有既定预算时不设置固定 iteration 上限，持续执行到稳定结果。Retry 不消耗 engineering iteration budget，也不得为了“跑完”自动提高上限。

执行中收到已确认的 requirement amendment 时，停止新的受影响 dispatch，终止或收回相关 implementer，保留 partial landed state 与 receipt，并交给 `to-spec` / `to-tickets` 完成 graph reconciliation。只有更新后的 graph 不再存在 active writer、状态冲突或 superseded dependency 后才恢复调度。

## Boundaries

- 不创建与 `implement` 重复的固定 implementer prompt 或 Agent definition。
- 不复述或放宽 `implement`、`tdd`、`debug`、`simplify`、`code-review`、`codebase-design` 的内部规则。
- 不因为自主调度降低 HITL、安全、权限、测试、审查或项目规则门槛。
- 不要求所有项目采用相同 subagent 或 worktree 机制。
- 默认不 commit、不 push、不创建或切换分支、不改写历史；`done` 在逻辑上先于版本控制写操作，相关失败应单独报告。
