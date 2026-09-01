---
name: loop
description: "执行多-ticket dependency graph：计算 ready frontier，默认通过独立 subagent 串行调度 implement，在可证明隔离且有收益时并行，聚合 landed evidence，并在完成前执行 whole-graph review。用于已有 SPEC 和 tickets/ 的多工作单元实现；不用于单一 scoped task 或需求澄清。"
---

# Loop

Loop 是一个 **Runtime-neutral engineering execution protocol**。它消费已经明确的多-ticket execution graph，负责计算当前可执行工作、选择调度策略、收集 evidence、执行最终 whole-graph review、判断 progress，并持续推进到 `done`、`blocked`、`no_progress`，或调用方明确预算耗尽。

Loop 不定义需求、不拆 tickets，也不复制具体实现纪律。`SPEC.md` 提供规范性需求，`tickets/` 提供 execution graph，每个工作单元由 `implement` 执行。

## 何时使用

使用 Loop：

- 已有多张 delivery tickets，需要持续计算 ready frontier 和推进依赖图；
- 多个 ready tickets 可能安全并行，需要显式判断 isolation 与 integration 风险；
- 需要统一 progress、evidence、iteration / retry、whole-graph review 和 no-progress 语义。

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
单一 scoped task             → implement
多-ticket execution graph    → loop
根因不清楚                  → debug
```

## 输入与授权

Loop 使用目标仓库中已确认的 `SPEC.md` 与包含多张 delivery tickets 的 `tickets/`。`SPEC.md` 提供规范性需求，`tickets/` 提供 execution graph。单一 scoped task 或只有一个工作单元的 SPEC 直接交给 `implement`。

Loop 的调用只授权按当前任务契约推进工程工作，**不隐含 commit、push、建分支或改写历史授权**。版本控制写操作必须来自用户明确授权或上层 workflow 已提供的授权。

## Ticket graph execution

执行多-ticket graph 时：

1. 首次 dispatch 前在 Loop execution evidence 中记录 graph baseline 与 pre-existing working-tree inventory；恢复执行时从最早可信的 implementation receipt 还原，不能还原时记录 review coverage blind spot，不得假装拥有完整范围；
2. 读取 `SPEC.md`、所有 tickets 的 Status 与 Blocked by，计算 ready frontier；
3. 从 frontier 选择当前可执行 tickets，并为每张 ticket 调用独立的 `implement` 执行单元；
4. 收集每个执行单元的 landed state、verification evidence、阻塞和未验证项；
5. 完成的 ticket 由其 `implement` 更新验收、evidence 和 Status；
6. 重新读取 graph 并计算 frontier：Loop 只在 evidence 表明声明的依赖和 implement 记录的其他阻塞都已解除时，将 ticket 从 `blocked` 更新为 `ready`；
7. 所有 tickets 都 `done` 时执行 Whole-graph review；通过后才进入 `done`；没有 ready 或 `in_progress` ticket 但仍有未完成 ticket 时进入 `blocked`，并报告未完成 blocker、状态冲突或 dependency cycle。

Loop 读取 ticket contract 并调度执行，不改写 What to build、Constraints、Acceptance criteria 或 Blocked by。Loop 拥有经 evidence 证明阻塞解除后的 `blocked → ready`，以及 whole-graph review 发现既有 ticket 范围内缺陷时的 `done → ready`；`implement` 拥有 `ready → in_progress → done/blocked`、验收勾选和 execution evidence。

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

## Implementer ownership

Loop 拥有 implementer execution unit 的调度，不拥有其内部实现规则：

- Loop 决定当前 ticket 是在当前 Agent 内执行，还是创建独立 subagent；Runtime 支持 subagent 时默认创建独立 implementer subagent。
- Loop 为每个 execution unit 固定 parent SPEC、唯一当前 ticket、graph baseline、pre-existing changes、已落地依赖、必要项目上下文、workspace/isolation、版本控制授权和 receipt 返回契约。
- Loop 决定执行单元的串行/并行、subagent identity，以及 Runtime 支持时的等待、恢复、中断或重新派发；这些属于 graph scheduling。
- 接收任务的 Agent 必须调用 `implement` 执行当前 ticket。`implement` 定义调查、修改、验证、审查和 evidence 规则，但不再递归创建另一个 implementer，也不选择 sibling ticket。
- 用户直接调用 `implement` 时，当前 Agent 就是 implementer；不为了保持形式再包装一层 subagent。

不创建与 `implement` 重复的固定 implementer prompt 或 Agent definition。Runtime-specific 的 subagent 工具调用可以不同，但 dispatch contract 与 implementation procedure 的 owner 不变。

## Execution state

每轮结束必须归一到以下状态之一：

- `ready`：存在明确、未阻塞且有证据支撑的下一步；
- `in_progress`：一个或多个已领取工作单元仍在执行；
- `done`：任务完成条件、验收和质量 gate 已满足；
- `blocked`：继续需要用户决策、外部输入、权限或新的项目事实；
- `no_progress`：当前 evidence 下不存在能改变状态的合理动作；
- `budget_exhausted`：达到调用方明确提供的 safety budget，但任务尚未进入其他稳定终态。

这些状态只描述 execution graph 的工程交付进度。

## Progress invariant

每个有效 engineering iteration 必须产生至少一个可观察的状态变化：

- 一个 ticket / acceptance criterion 从未完成变为有 evidence 的完成；
- 一个 blocker 被解除；
- 一个 unknown 被转化为 verified fact；
- 一个 failing verification 变为 passing；
- 一个 review finding 被解决，或因新 evidence 被有效重新分类；
- whole-graph review 从存在必须修复 finding 变为通过；
- ready frontier 发生有效变化；
- 新 evidence 改变了下一步选择。

如果 iteration 结束时工程状态与进入时实质相同，则判定为 `no_progress`。不得仅凭“再试一次”“换个写法”或模型自报继续循环。

## Iteration vs retry

**Engineering iteration** 基于上一轮产生的新 evidence 改变状态、实现或下一步。

**Retry** 只是同一 action 因瞬态执行失败而重试，例如网络错误、临时服务不可用、命令被中断或 Agent Runtime interruption。Retry 不代表工程状态发生变化，不应自动计为新的 engineering iteration。

## 每轮协议

### 1. Observe

读取 `SPEC.md`、ticket graph、上一轮 receipts、landed changes、验证结果和未解决 findings，只加载决定当前 next action 所需的上下文。

### 2. Calculate frontier

根据 Status 与 Blocked by 计算所有可执行工作。先处理状态冲突、重复领取和 dependency cycle，再选择调度策略。

### 3. Dispatch

默认串行 dispatch 一张 ready ticket；只有满足 Scheduling 的全部并行条件时才 dispatch 多张。每个执行单元使用 `implement`，并获得 parent SPEC、当前 ticket、已落地依赖和必要项目上下文。

适合 test-first 时由 `implement` 调用 `tdd`；发现 bug 根因未知时转 `debug`；涉及 Interface / Seam 重新设计时参考 `codebase-design`。Loop 不复制这些 Skills 的内部规则。

### 4. Verify landed state

核对实际 diff、ticket receipt、验证命令、退出状态和关键 evidence。并行执行时还要检查跨 ticket 冲突、共享假设和集成结果。失败是下一轮 evaluate 的输入，不自动等于 retry。

### 5. Evaluate and repeat

比较 iteration 前后的工程状态，检查 Progress invariant，重新计算 frontier，并得出：继续、完成、阻塞、无进展或预算耗尽。

## Whole-graph review

所有 tickets 都进入 `done` 后、Loop 最终进入 `done` 前：

1. 从 graph baseline 到当前 landed state 构造完整审查范围，排除 pre-existing 和无关改动；同时汇总 `SPEC.md`、全部 tickets、implementation receipts、simplification receipts、verification evidence 和未验证项。
2. 调用 `code-review` 的 `implementation` mode，对完整 graph 分别执行 Standards 与 Spec 审查。`code-review` 拥有 reviewer dispatch、审查规则和 finding 判断；Loop 只负责提供范围、聚合结果和执行后续调度。
3. 对必须修复的 finding，若修复仍属于一个或多个既有 ticket contract，将最小责任 ticket 集合从 `done` 重新置为 `ready`，附上 finding evidence，并继续通过 `implement` 串行修复；不得改写 ticket 契约来容纳 finding。
4. finding 没有既有 ticket 承担、暴露 execution graph 缺口时，停止并交回 `to-tickets`；需要改变需求、范围、接口 contract 或 acceptance criteria 时，交回 `to-spec`。
5. 修复后重新执行受影响验证，并再次进行 whole-graph review。只有两轴均无未处理的必须修复 finding，且 integration verification 完整时，才通过本 gate。

不得仅根据各 ticket 已分别通过 review 推断完整 graph 已通过；跨 ticket 的接口、共享状态、数据流、错误路径和集成行为必须在最终 landed state 上检查。

## Done gate

`done` 不能由模型或 subagent 自报决定。至少满足：

- 当前 execution graph 的所有 tickets 都是 `done`；
- acceptance criteria 有可观察 verification evidence；
- 相关验证通过，或未验证项已明确且被任务契约允许；
- 每个 ticket 必要的 `simplify` / `code-review` 已完成，且 Whole-graph review 已通过；
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
- 达到调用方明确提供的 safety budget → 停止并报告当前 evidence。

## Safety budget

Safety budget 是调用方可以提供的执行边界，不是任务规模估算。

- 优先使用调用方或项目已有的执行预算；
- 没有既定预算时，不设置固定 iteration 上限，持续执行到 `done`、`blocked` 或 `no_progress`；
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
- Loop 只根据可复核 evidence 维护 readiness、触发 whole-graph review 并聚合 review outcome；`implement` 负责单个 ticket 的领取、调查、代码修改、验证、审查、完成状态和 execution evidence。
- Loop 拥有 implementer subagent 的 dispatch lifecycle；`implement` 拥有 implementer 的单工作单元执行程序。不得让两者同时创建或调度 implementer。
- 不复述或放宽 `implement`、`tdd`、`debug`、`simplify`、`code-review`、`codebase-design` 的内部规则。
- 不因为自主调度就降低 HITL、安全、权限、测试、审查或项目规则门槛。
- 不把 iteration 数量、模型消息数量、Token 消耗或代码行数当作 progress。
- 不要求所有项目采用相同 subagent 或 worktree 机制。
