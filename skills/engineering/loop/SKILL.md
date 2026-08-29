---
name: loop
description: "仅当 Runtime 缺少可靠任务生命周期能力时，定义可移植的 evidence、progress 与 retry 规则；否则优先使用 Runtime 原生 goal/task 管理。"
---

# Loop

Loop 是一个 **Runtime-neutral Loop Engineering protocol**。它不试图替代 Codex、Claude Code 或其他 Coding Agent Runtime 已有的 goal / long-running task / resume 能力，而是定义一套跨 Runtime 可复用的工程执行语义：每轮如何产生 evidence、什么算 progress、何时继续、何时停止，以及如何避免无效原地重试。

如果当前 Runtime 已经可靠地拥有任务生命周期、暂停/恢复、持久化状态和 continue/stop 决策，优先让 Runtime 管这些能力；不要再套一层具有相同职责的 Loop orchestrator。此时可把本 Skill 作为 Goal 内部的 execution protocol 使用。

## Runtime-native orchestration

优先级：

1. **Runtime 已有可靠 Goal / Task 能力**：优先使用 Runtime 原生机制负责生命周期、持久化、暂停、恢复和 session recovery；本 Skill 只提供 progress / evidence / no-progress 等工程执行规则。
2. **Runtime 没有可靠的 long-running mechanism**：本 Skill 可以承担最小的多轮执行控制与 checkpoint 语义。
3. **需要跨 Runtime 一致行为**：即使不同工具各有实现，也可以用本 Skill 统一 engineering iteration 的判定标准。

不要建立重复控制：

```text
Runtime Goal
   ↓
Loop orchestrator
   ↓
另一个 continue/stop/checkpoint loop
```

当外层 Runtime 已经拥有相同职责时，Loop 不再决定任务生命周期，只约束每一轮怎样才算有效推进。

推荐关系：

```text
Runtime Goal / Task
    │ owns lifecycle, persistence, pause/resume
    ▼
Loop Engineering protocol
    │ owns progress invariant, evidence, iteration semantics
    ▼
Engineering Skills
    ├── implement
    ├── tdd
    ├── debug
    ├── simplify
    └── code-review
```

## 何时使用

使用 Loop 的典型情况：

- 当前 Runtime 没有可靠的 goal / long-running task 能力，但任务需要多轮自主推进；
- 需要在 Codex、Claude Code、Pi、Kimi 或其他 Runtime 之间保持一致的 progress / stop 语义；
- 已经处于 Runtime-managed goal 内，希望给每个 engineering iteration 增加明确的 evidence 与 no-progress 约束；
- 任务目标和路径已经明确，但实现、验证、修复、简化或审查需要多轮反馈。

不要使用 Loop：

- Runtime 已经拥有成熟 Goal，并且你只是想再包一层相同的 lifecycle loop；
- 需求或 expected behavior 还没收敛：先用 `grilling`；
- 重要路径仍处于 Fog of war：先用 `wayfinding`；
- 只是一个小而明确、单次实现即可完成的任务：直接用 `implement` 或当前 Agent 实现；
- 主要问题是未知 bug 根因：先用 `debug`；
- 只是希望重复执行一个瞬态失败命令：那是 retry，不是 engineering iteration。

简化判断：

```text
需求不清楚                  → grilling
路径不清楚                  → wayfinding
路径清楚且单次可完成         → implement
需要多轮，Runtime 有 Goal    → 优先 Runtime Goal + Loop protocol
需要多轮，Runtime 无 Goal    → loop
根因不清楚                  → debug
```

## 输入与授权

Loop 使用目标仓库已有的任务契约。优先使用 `SPEC.md` / `PLAN.md`；如果项目采用 issue、ticket、goal 或其他等价格式，只要能明确 Destination、范围、acceptance criteria、依赖和完成条件，也可以使用，不因本 Skill 强制改成固定文件格式。

Loop 的调用只授权按当前任务契约推进工程工作，**不隐含 commit、push、建分支或改写历史授权**。版本控制写操作必须来自用户明确授权或上层 workflow 已提供的授权。

如果外层 Runtime Goal 已提供 baseline、checkpoint 或任务状态，本 Skill 复用外层状态，不再创建重复 artifact。

## Loop state

当本 Skill 自己承担执行控制时，每轮结束必须归一到以下状态之一：

- `ready`：存在明确、未阻塞且有证据支撑的下一步；
- `done`：任务完成条件、验收和质量 gate 已满足；
- `blocked`：继续需要用户决策、外部输入、权限或新的项目事实；
- `no_progress`：当前 evidence 下不存在能改变状态的合理动作；
- `budget_exhausted`：达到 safety round budget，但任务尚未进入其他稳定终态。

如果外层 Runtime Goal 已拥有自己的状态机，不要求它改用这些状态名；只需把本 Skill 的判断映射到 Runtime 的等价 continue / done / blocked / stop 语义。

## Progress invariant

每个有效 engineering iteration 必须产生至少一个可观察的状态变化：

- 一个 task / acceptance criterion 从未完成变为有 evidence 的完成；
- 一个 blocker 被解除；
- 一个 unknown 被转化为 verified fact；
- 一个 failing verification 变为 passing；
- 一个 review finding 被解决，或因新 evidence 被有效重新分类；
- ready frontier 发生有效变化；
- 新 evidence 改变了下一步选择。

如果 iteration 结束时任务状态与进入时实质相同，则判定为 `no_progress`。不得仅凭“再试一次”“换个写法”“模型觉得应该再试”继续循环。

## Iteration vs retry

**Engineering iteration** 基于上一轮产生的新 evidence 改变状态、实现或下一步。

**Retry** 只是同一 action 因瞬态执行失败而重试，例如网络错误、临时服务不可用、命令被中断或 Agent Runtime interruption。Retry 不代表工程状态发生变化，不应自动计为新的 engineering iteration。

Runtime 如果已经有 interruption recovery / retry 机制，优先交给 Runtime 处理，不在本 Skill 再实现一套重试器。

## 每轮协议

每个 engineering iteration 遵循同一个高层协议：

### 1. Observe

读取当前任务契约、已有 Runtime/项目状态、上一轮 receipts、验证结果和未解决 findings，只加载决定当前 next action 所需的上下文。

### 2. Select next action

从当前可执行 frontier 里选择最能减少剩余不确定性或推进验收的最小工作单元。优先完成 vertical slice，而不是制造大量并行半成品。

需要实现时使用 `implement` 的规则；适合 test-first 时使用 `tdd`；发现 bug 根因未知时切到 `debug`；涉及 Interface / Seam 重新设计时参考 `codebase-design`。Loop 只提供执行协议，不复制这些 Skill 的内部纪律。

### 3. Act

执行当前工作单元。不得为了维持 loop 而扩大 scope、修改任务契约、降低验收或跳过项目自己的规则。

### 4. Verify

按当前变更风险执行目标仓库适用的验证，记录命令、退出状态和关键 evidence。验证失败不是自动失败，也不是自动 retry；它是下一步 evaluate 的输入。

### 5. Evaluate

比较 iteration 前后的状态，检查 Progress invariant，并得出：继续、完成、阻塞、无进展或预算耗尽。

如果 Runtime 已拥有 goal state machine，把结果交还给 Runtime；不要在 Skill 内创建第二套 lifecycle 决策。

### 6. Persist

优先使用 Runtime 或目标项目已有的持久化/goal/checkpoint 机制。只有两者都不存在、且任务确实需要跨会话时，才创建最小本地 checkpoint。

不要为本 Skill 强制目标仓库采用固定目录或文件名。

## Done gate

`done` 不能由模型自报决定。至少满足：

- 所选任务范围全部完成；
- acceptance criteria 有可观察 verification evidence；
- 相关验证通过，或未验证项已明确且被任务契约允许；
- 必要的 `simplify` / `code-review` 等质量 gate 已完成；
- 没有未处理的必须修复 finding；
- 没有属于当前 Destination 的 blocker 或 unknown 被静默遗留。

如果外层 Runtime Goal 有自己的 completion contract，本 Skill 提供 evidence，由外层 Runtime 做最终生命周期收口。

## Stop conditions

出现以下任一情况，不继续原地循环：

- 新事实表明需求、契约、权限或验收必须重新收敛 → 转 `grilling` / `to-spec`；
- 重要路径重新进入 Fog of war → 转 `wayfinding`；
- 当前问题变成根因未知的 bug investigation → 转 `debug`；
- 一轮没有满足 Progress invariant → `no_progress`；
- 没有站得住脚的 next action → `no_progress`；
- 达到外层 Runtime 或本 Skill 的 safety budget → 停止并持久化当前 evidence。

如果由 Runtime Goal 管生命周期，把 stop reason 返回给外层 Runtime，不自行开启新的 nested loop。

## Safety budget

Safety budget 是防止无界自主执行的 fuse，不是任务规模估算。

- 外层 Runtime 已设置 goal/task budget 时，优先使用外层 budget；
- 只有本 Skill 自己承担执行控制时，默认最多 3 个 engineering iterations；
- retry 不消耗 engineering iteration budget；
- 达到 budget 时先持久化 evidence，再停止；不得为了“跑完”自动提高上限。

## Resume

优先使用 Runtime 原生 resume / goal continuation。如果 Runtime 已经持久化目标状态，本 Skill 不再建立独立 resume 协议。

只有缺少 Runtime-native resume 时，恢复前才需要：

1. 重读任务契约和最新 checkpoint；
2. 重新检查 baseline、working tree 和外部状态是否仍成立；
3. 验证上一轮 evidence 是否仍有效；
4. 重新计算 ready frontier；
5. 从新的 state 继续，而不是重复上一轮 action。

## Version control

Loop completion 与版本控制写操作解耦。

- 默认不 commit、不 push、不创建或切换分支、不改写历史；
- 用户明确授权 commit 时，只提交本任务拥有的改动，并遵循目标仓库已有 commit 规则；
- `done` 在逻辑上先于 commit，commit failure 不应反向把工程任务伪装成未完成，应单独报告 VCS failure。

## Boundaries

- Runtime 原生 Goal 优先负责 lifecycle、持久化、pause/resume 和 session recovery。
- Loop 主要负责可移植的 progress invariant、evidence、iteration / retry 区分和 no-progress gate。
- 不建立与外层 Runtime 重复的 nested orchestrator。
- 不复述或放宽 `implement`、`tdd`、`debug`、`simplify`、`code-review`、`codebase-design` 的内部规则。
- 不因为处于 autonomous loop 就降低 HITL、安全、权限、测试、审查或项目规则门槛。
- 不把 round 数量、模型消息数量、Token 消耗或代码行数当作 progress。
- 不要求所有项目采用相同 task artifact、checkpoint 文件名或 Agent Runtime。
