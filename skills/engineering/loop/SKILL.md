---
name: loop
description: "Used when 目标、边界和验收已经明确，但任务需要多轮自主推进时（触发词：loop、自动跑完、持续推进、run loop）。每轮必须产生新的可验证证据或有效状态变化，并在完成、阻塞、无进展或安全预算耗尽时停止。"
---

# Loop

对目标和任务边界已明确的工程任务进行多轮自主推进。Loop 不负责发明需求，也不把“再试一次”当作工程进展；它负责在已有任务契约上重复执行 **observe → act → verify → evaluate → persist**，直到任务达到稳定终态。

Loop 的核心不是重复 `implement`，而是确保每个有效 round 都消耗当前状态、产生新 evidence，并让系统状态可验证地向 Destination 靠近。

## 何时使用

使用 Loop 的前提是：

- Destination 已明确；
- 需求边界和验收标准已经收敛；
- 当前存在可执行、未阻塞的下一步；
- 任务规模或反馈链条决定了它通常无法靠一次实现动作可靠完成；
- 用户希望 Agent 在多个 engineering iterations 中自主推进，而不是每一步都等待人工确认。

典型场景：

- 已有 SPEC/PLAN 或等价任务契约，需要连续完成多个 task / acceptance criteria；
- 实现后必然还要经过验证、修复、简化、审查，并可能根据新 evidence 再推进一轮；
- 大型但路径已经清楚的重构、迁移、接口改造或多阶段 feature；
- 任务可能跨会话，需要持久化 checkpoint 后继续。

不要使用 Loop：

- 需求或 expected behavior 还没收敛：先用 `grilling`；
- 重要路径仍处于 Fog of war：先用 `wayfinding`；
- 只是一个小而明确、单次实现即可完成的任务：直接用 `implement` 或当前 Agent 实现；
- 主要问题是未知 bug 根因：先用 `debug`；
- 只是希望重复执行一个瞬态失败命令：那是 retry，不是 engineering iteration。

简化判断：

```text
需求不清楚        → grilling
路径不清楚        → wayfinding
路径清楚且任务较小 → implement
路径清楚且需要多轮 → loop
根因不清楚        → debug
```

## 输入与授权

Loop 使用目标仓库已有的任务契约。优先使用 `SPEC.md` / `PLAN.md`；如果项目采用 issue、ticket、goal 或其他等价格式，只要能明确 Destination、范围、acceptance criteria、依赖和完成条件，也可以使用，不因本 Skill 强制改成固定文件格式。

Loop 的调用只授权持续推进到工程上的稳定终态，**不隐含 commit、push、建分支或改写历史授权**。版本控制写操作必须来自用户明确授权或上层 workflow 已提供的授权。

进入前：

1. 固定任务契约、baseline、当前工作区状态和 pre-existing changes；
2. 确认当前 ready frontier；
3. 记录本轮 safety budget；
4. 如果没有可执行 next action，则不要进入 loop。

## Loop state

每轮结束必须归一到以下状态之一：

- `ready`：存在明确、未阻塞且有证据支撑的下一步；
- `done`：任务完成条件、验收和质量 gate 已满足；
- `blocked`：继续需要用户决策、外部输入、权限或新的项目事实；
- `no_progress`：当前 evidence 下不存在能改变状态的合理动作；
- `budget_exhausted`：达到 safety round budget，但任务尚未进入其他稳定终态。

只有 `ready` 可以进入新的 engineering round。

## Progress invariant

每个有效 round 必须产生至少一个可观察的状态变化：

- 一个 task / acceptance criterion 从未完成变为有 evidence 的完成；
- 一个 blocker 被解除；
- 一个 unknown 被转化为 verified fact；
- 一个 failing verification 变为 passing；
- 一个 review finding 被解决，或因新 evidence 被有效重新分类；
- ready frontier 发生有效变化；
- 新 evidence 改变了下一步选择。

如果 round 结束时任务状态与进入时实质相同，则判定为 `no_progress`。不得仅凭“再试一次”“换个写法”“模型觉得应该再试”继续循环。

## Iteration vs retry

**Engineering iteration** 基于上一轮产生的新 evidence 改变状态、实现或下一步，计入 round budget。

**Retry** 只是同一 action 因瞬态执行失败而重试，例如网络错误、临时服务不可用、命令被中断或 Agent Runtime interruption。Retry 不代表工程状态发生变化，不应自动计为新的 round。

Retry 只能在失败具有明确瞬态特征、重试不会重复产生副作用、且当前环境允许安全重试时执行。否则把失败作为 evidence 进入 evaluate，而不是盲目 retry。

## 每轮协议

每个 round 都遵循同一个高层协议：

### 1. Observe

读取当前任务契约、checkpoint、working tree、上一轮 receipts、验证结果和未解决 findings，只加载决定当前 next action 所需的上下文。

### 2. Select next action

从 ready frontier 里选择最能减少剩余不确定性或推进验收的最小工作单元。优先完成 vertical slice，而不是制造大量并行半成品。

需要实现时使用 `implement` 的规则；适合 test-first 时使用 `tdd`；发现 bug 根因未知时切到 `debug`；涉及 Interface / Seam 重新设计时参考 `codebase-design`。Loop 只负责编排，不复制这些 Skill 的内部纪律。

### 3. Act

执行当前工作单元。不得为了维持 loop 而扩大 scope、修改任务契约、降低验收或跳过项目自己的规则。

### 4. Verify

按当前变更风险执行目标仓库适用的验证，记录命令、退出状态和关键 evidence。验证失败不是自动失败，也不是自动 retry；它是下一步 evaluate 的输入。

### 5. Evaluate

比较 round 前后的状态，检查 Progress invariant，并归一到 `ready | done | blocked | no_progress | budget_exhausted`。

### 6. Persist

在任务已有的状态记录机制中保存最小 checkpoint；若项目没有既有机制且任务确实需要跨会话，才创建最小本地 checkpoint。不要为本 Skill 强制目标仓库采用固定目录或文件名。

Checkpoint 至少记录：

- Destination / task contract 引用；
- baseline 与 pre-existing changes；
- 已完成项及 evidence；
- 当前 frontier；
- blockers / unknowns；
- 已用 engineering rounds；
- 下一步及其依据。

## Done gate

`done` 不能由模型自报决定。至少满足：

- 所选任务范围全部完成；
- acceptance criteria 有可观察 verification evidence；
- 相关验证通过，或未验证项已明确且被任务契约允许；
- 必要的 `simplify` / `code-review` 等质量 gate 已完成；
- 没有未处理的必须修复 finding；
- 没有属于当前 Destination 的 blocker 或 unknown 被静默遗留。

如果任务契约或项目流程没有要求某个 gate，不因 Loop 自行增加无关流程。

## Stop conditions

出现以下任一情况立即停止，不原地打转：

- 新事实表明需求、契约、权限或验收必须重新收敛 → `blocked`，转 `grilling` / `to-spec`；
- 重要路径重新进入 Fog of war → `blocked`，转 `wayfinding`；
- 当前问题变成根因未知的 bug investigation → `blocked`，转 `debug`；
- 一轮没有满足 Progress invariant → `no_progress`；
- 没有站得住脚的 next action → `no_progress`；
- 达到 safety round budget → `budget_exhausted`。

停止时汇报已尝试路径、已获得 evidence、当前状态和继续所需条件。输入和 evidence 都没有变化时不得自动继续。

## Safety round budget

Round budget 是防止无界自主执行的 **safety fuse**，不是任务规模估算，也不是正常完成机制。

- 默认 budget：3 个 engineering rounds；
- 用户或上层 orchestrator 可以根据任务规模覆盖；
- retry 不消耗 engineering round budget；
- 达到 budget 时先持久化 checkpoint，再以 `budget_exhausted` 停止；不得为了“跑完”自动提高上限。

## Resume

恢复 Loop 时：

1. 重读任务契约和最新 checkpoint；
2. 重新检查 baseline、working tree 和外部状态是否仍成立；
3. 验证上一轮 evidence 是否仍有效；
4. 重新计算 ready frontier；
5. 从新的 state 继续，而不是重复上一轮 action。

如果 baseline 失效、外部改动混入或 checkpoint 与当前事实冲突，停止并说明，不静默吞并。

## Version control

Loop completion 与版本控制写操作解耦。

- 默认不 commit、不 push、不创建或切换分支、不改写历史；
- 用户明确授权 commit 时，只提交本任务拥有的改动，并遵循目标仓库已有 commit 规则；
- 没有仓库级 commit 规则时，不因本 Skill 创建新的规则文件；
- `done` 在逻辑上先于 commit，commit failure 不应反向把工程任务伪装成未完成，应单独报告 VCS failure。

## Boundaries

- Loop 只用于“路径已知但需要多轮推进”的工程执行，不负责未知问题空间的探索。
- 不复述或放宽 `implement`、`tdd`、`debug`、`simplify`、`code-review`、`codebase-design` 的内部规则。
- 不因为处于 autonomous loop 就降低 HITL、安全、权限、测试、审查或项目规则门槛。
- 不把 round 数量、模型消息数量、Token 消耗或代码行数当作 progress。
- 不要求所有项目采用相同 task artifact、checkpoint 文件名或 Agent Runtime。
