---
name: loop
description: "调度带状态的工程工作，并通过证据持续推进直到完成或稳定停止。"
---

# Loop

Loop 是一个 **Runtime-neutral engineering execution protocol**。它消费已经明确的任务契约或 ticket graph，负责计算当前可执行工作、选择调度策略、收集 evidence、判断 progress，并持续推进到 `done`、`blocked`、`no_progress` 或预算耗尽。

Loop 不定义需求、不拆 tickets，也不复制具体实现纪律。`SPEC.md` 提供规范性需求，`tickets/` 提供 execution graph，每个工作单元由 `implement` 执行。

## 何时使用

使用 Loop：

- 已有明确任务契约，但实现、验证、修复、简化或审查需要多轮反馈；
- 已有多张 delivery tickets，需要持续计算 ready frontier 和推进依赖图；
- 多个 ready tickets 可能安全并行，需要显式判断 isolation 与 integration 风险；
- 需要统一 progress、evidence、iteration / retry 和 no-progress 语义。

不要使用 Loop：

- 需求或 expected behavior 还没收敛：先用 `grilling`；
- 重要路径仍处于 Fog of war：先用 `wayfinding`；
- 只是一个小而明确、单次实现即可完成的任务：直接用 `implement`；
- 主要问题是未知 bug 根因：先用 `debug`；
- 只是希望重复执行一个瞬态失败命令：那是 retry，不是 engineering iteration。

简化判断：

```text
需求不清楚                  → grilling
路径不清楚                  → wayfinding
路径清楚且单次可完成         → implement
需要持续推进或调度 tickets   → loop
根因不清楚                  → debug
```

## 输入与授权

Loop 使用目标仓库已有的任务契约。当前 workflow 中，`SPEC.md` 提供规范性需求，`tickets/` 提供 execution graph；其他等价格式只要能明确 Destination、范围、acceptance criteria、依赖和完成条件，也可以使用，不因本 Skill 强制改成固定文件格式。

Loop 的调用只授权按当前任务契约推进工程工作，**不隐含 commit、push、建分支或改写历史授权**。版本控制写操作必须来自用户明确授权或上层 workflow 已提供的授权。

## Ticket graph execution

当任务目录存在由 `to-tickets` 生成的 `tickets/` 时：

1. 读取 `SPEC.md`、所有 tickets 的 Status 与 Blocked by，计算 ready frontier；
2. 从 frontier 选择当前可执行 tickets，并为每张 ticket 调用独立的 `implement` 执行单元；
3. 收集每个执行单元的 landed state、verification evidence、阻塞和未验证项；
4. 完成的 ticket 由其 `implement` 更新验收、evidence 和 Status；
5. 重新读取 graph 并计算 frontier：Loop 将全部 blocker 都 `done`、且没有其他阻塞原因的后继 ticket 从 `blocked` 更新为 `ready`；
6. 所有 tickets 都 `done` 时进入 `done`；没有 ready 或 in-progress ticket 但仍有未完成 ticket 时进入 `blocked`，并报告未完成 blocker、状态冲突或 dependency cycle。

Loop 只读取 ticket contract 并调度执行，不改写 What to build、Constraints、Acceptance criteria 或 Blocked by。Loop 只拥有依赖解除产生的 `blocked → ready` 转换；`implement` 拥有 `ready → in-progress → done/blocked`、验收勾选和 execution evidence。

## Scheduling

默认调度策略：

- 串行选择一张 ready ticket；
- Runtime 支持 subagent 时，默认把该 ticket 委托给独立 subagent，并要求其使用 `implement`；
- subagent 不可用时，在当前 Agent 中调用 `implement`；
- 一个执行单元只能实现当前 ticket，不得顺带领取 sibling ticket。

多个 ready tickets **不等于** 应该并行。只有同时满足以下条件时，Loop 才主动并行 dispatch：

- Runtime 支持多个独立执行单元；
- tickets 之间没有 dependency edge；
- 能证明代码、生成物、测试资源、外部环境和可变状态具有足够 isolation；
- 一个 ticket 的实现不太可能改变另一个 ticket 的契约或关键实现前提；
- landed changes 有明确、低风险的 integration 顺序和冲突处理方式；
- 并行收益足以覆盖协调和集成成本。

独立 worktree 只是可选 isolation mechanism。默认不创建；只有共享 working tree 无法提供所需隔离，且独立 worktree 能实质降低覆盖、竞争或集成风险时才使用。worktree 本身不能证明 tickets 相互独立。

并行执行后，先逐项核对 receipts、验证 landed state 和解决集成问题，再重新计算 frontier。不得仅依据 subagent 自报更新 graph。

## Execution state

每轮结束必须归一到以下状态之一：

- `ready`：存在明确、未阻塞且有证据支撑的下一步；
- `in_progress`：一个或多个已领取工作单元仍在执行；
- `done`：任务完成条件、验收和质量 gate 已满足；
- `blocked`：继续需要用户决策、外部输入、权限或新的项目事实；
- `no_progress`：当前 evidence 下不存在能改变状态的合理动作；
- `budget_exhausted`：达到 safety round budget，但任务尚未进入其他稳定终态。

这些状态描述工程交付进度，不承担 conversation、session、context recovery 或 interruption persistence。

## Progress invariant

每个有效 engineering iteration 必须产生至少一个可观察的状态变化：

- 一个 ticket / acceptance criterion 从未完成变为有 evidence 的完成；
- 一个 blocker 被解除；
- 一个 unknown 被转化为 verified fact；
- 一个 failing verification 变为 passing；
- 一个 review finding 被解决，或因新 evidence 被有效重新分类；
- ready frontier 发生有效变化；
- 新 evidence 改变了下一步选择。

如果 iteration 结束时工程状态与进入时实质相同，则判定为 `no_progress`。不得仅凭“再试一次”“换个写法”或模型自报继续循环。

## Iteration vs retry

**Engineering iteration** 基于上一轮产生的新 evidence 改变状态、实现或下一步。

**Retry** 只是同一 action 因瞬态执行失败而重试，例如网络错误、临时服务不可用、命令被中断或 Agent Runtime interruption。Retry 不代表工程状态发生变化，不应自动计为新的 engineering iteration。

## 每轮协议

### 1. Observe

读取当前任务契约、ticket graph、上一轮 receipts、landed changes、验证结果和未解决 findings，只加载决定当前 next action 所需的上下文。

### 2. Calculate frontier

根据 Status 与 Blocked by 计算所有可执行工作。先处理状态冲突、重复领取和 dependency cycle，再选择调度策略。

### 3. Dispatch

默认串行 dispatch 一张 ready ticket；只有满足 Scheduling 的全部并行条件时才 dispatch 多张。每个执行单元使用 `implement`，并获得 parent SPEC、当前 ticket、已落地依赖和必要项目上下文。

适合 test-first 时由 `implement` 调用 `tdd`；发现 bug 根因未知时转 `debug`；涉及 Interface / Seam 重新设计时参考 `codebase-design`。Loop 不复制这些 Skills 的内部规则。

### 4. Verify landed state

核对实际 diff、ticket receipt、验证命令、退出状态和关键 evidence。并行执行时还要检查跨 ticket 冲突、共享假设和集成结果。失败是下一轮 evaluate 的输入，不自动等于 retry。

### 5. Evaluate and repeat

比较 iteration 前后的工程状态，检查 Progress invariant，重新计算 frontier，并得出：继续、完成、阻塞、无进展或预算耗尽。

## Done gate

`done` 不能由模型或 subagent 自报决定。至少满足：

- ticket graph mode 下，所选任务范围内所有 tickets 都是 `done`；没有 tickets 时，当前任务契约的范围全部完成；
- acceptance criteria 有可观察 verification evidence；
- 相关验证通过，或未验证项已明确且被任务契约允许；
- 必要的 `simplify` / `code-review` 等质量 gate 已完成；
- 并行分支或 worktrees 的 landed state 已完成集成验证；
- 没有未处理的必须修复 finding；
- 没有属于当前 Destination 的 blocker 或 unknown 被静默遗留。

## Stop conditions

出现以下任一情况，不继续原地循环：

- 新事实表明需求、契约、权限或验收必须重新收敛 → 转 `grilling` / `to-spec`；
- 重要路径重新进入 Fog of war → 转 `wayfinding`；
- 当前问题变成根因未知的 bug investigation → 转 `debug`；
- 一轮没有满足 Progress invariant → `no_progress`；
- 没有站得住脚的 next action → `no_progress`；
- 达到 safety budget → 停止并报告当前 evidence。

## Safety budget

Safety budget 是防止无界自主执行的 fuse，不是任务规模估算。

- 优先使用调用方或项目已有的执行预算；
- 没有既定预算时，默认最多 3 个 engineering iterations；
- retry 不消耗 engineering iteration budget；
- 达到 budget 时先记录 evidence 和剩余 frontier，再停止；不得为了“跑完”自动提高上限。

## Version control

Loop completion 与版本控制写操作解耦。

- 默认不 commit、不 push、不创建或切换分支、不改写历史；
- 用户明确授权 commit 时，只提交本任务拥有的改动，并遵循目标仓库已有 commit 规则；
- `done` 在逻辑上先于 commit，commit failure 应单独报告为 VCS failure。

## Boundaries

- `to-spec` 定义规范性需求，`to-tickets` 定义 execution graph，Loop 不改写二者的契约。
- Loop 负责 ready frontier、调度、progress、evidence 聚合、重新计算和稳定停止。
- Loop 只维护 dependency-derived readiness；`implement` 负责单个 ticket 的领取、调查、代码修改、验证、审查、完成状态和 execution evidence。
- Runtime 负责 conversation、session、context recovery 和 interruption persistence；它们不属于 ticket delivery state。
- 不复述或放宽 `implement`、`tdd`、`debug`、`simplify`、`code-review`、`codebase-design` 的内部规则。
- 不因为自主调度就降低 HITL、安全、权限、测试、审查或项目规则门槛。
- 不把 round 数量、模型消息数量、Token 消耗或代码行数当作 progress。
- 不要求所有项目采用相同 task artifact、文件名、subagent 或 worktree 机制。
