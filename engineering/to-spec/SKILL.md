---
name: to-spec
description: "用于将已收敛需求写成可执行的 SPEC.md 与 PLAN.md；不自动实现。"
---

# To-Spec

把已经收敛的需求编译为同一任务目录中的 `SPEC.md` 与 `PLAN.md`，不自动实现。

`SPEC.md` 是规范性需求契约；`PLAN.md` 是从 SPEC 派生出的静态 declarative task graph，供 `implement`、Runtime-native Goal/Task 或 `loop` 消费。两者共同构成一个原子任务契约，但职责不同：

```text
confirmed decisions
        ↓
     to-spec
      /   \
SPEC.md   PLAN.md
contract  execution graph
      \   /
    R → AC → T
```

运行时进度、retry 次数、当前 round、临时 finding、实际验证命令和 resume 状态不属于 PLAN；这些由 Agent Runtime 的 Goal/Task 状态或执行 checkpoint 保存。

## 入口

- 需求仍有会改变行为、边界、接口或验收的未决选择时，先用 `grilling` 收敛。
- 目标和关键路径仍不清楚且需要跨会话调查时，先用 `wayfinding`。
- 用户确认前不创建正式文档；不编造字段、错误、接口、实现选择或任务依赖。
- `to-spec` 只把已确认事实结构化；如果生成 PLAN 时发现新的产品、协议、架构、边界或验收选择，停止并回到 `grilling`，不要在 PLAN 中偷偷完成设计。

任务目录优先采用用户本次指定，其次采用适用 `AGENTS.md` 的 `Engineering Skills Profile`，再沿用仓库已有任务文档约定；仍无约定且落盘位置会影响项目结构时询问用户。没有 Profile 不阻塞本 Skill，也不自动调用 setup。

## SPEC.md — normative contract

至少包含：背景、变更摘要、目标生效需求、边界与默认行为、验收标准。

- 需求使用稳定 `R1`、`R2`…；
- 验收使用稳定 `AC1`、`AC2`…，并明确覆盖的需求；
- 每条需求描述角色/触发、输入来源、状态变化、输出以及失败/取消行为；
- 每条验收必须能在不查看实现细节的情况下独立判定；
- 每条验收说明独立 expected source，例如用户确认、公开 contract、协议文档、worked example 或其他权威依据；
- 不把文件结构、类名、内部调用顺序或某种实现方案写成 acceptance criterion，除非它们本身就是明确 contract。

SPEC 是需求 authority。PLAN、Goal 或实现过程不得静默改变 SPEC 语义。

## PLAN.md — declarative task graph

PLAN 引用同目录 `SPEC.md`，把 `R / AC` 派生为可执行的 Task Graph。它描述 **需要达到什么结果、依赖什么、如何证明完成**，不描述实现 Agent 应该逐步怎么写代码。

PLAN 至少包含以下部分。

### Destination

用一小段话描述 PLAN 全部完成后的目标状态。Destination 必须与 SPEC 一致，不增加新的 scope。

### Constraints

仅记录会约束所有或多个 task 的已确认事实，例如必须保持的 contract、明确 non-goals、兼容性要求或不能突破的边界。项目已有规则只引用，不复制整套规则。

### Task Graph

有多个 task 或存在依赖时，提供稳定、可直接计算 frontier 的摘要表：

```markdown
| Task | Blocked by | Covers |
| --- | --- | --- |
| T1 | — | AC1, AC2 |
| T2 | T1 | AC3 |
| T3 | T1 | AC4 |
```

只记录真实 blocking edge；不为制造线性流程添加伪依赖。无 blocker 的 task 都属于 initial ready frontier。

### Tasks

任务使用稳定 `T1`、`T2`…，标题面向 outcome。每个 task 固定表达五类信息：

```markdown
### T1 — <Outcome-oriented title>

**Outcome**
<完成后可观察或可验证的状态>

**Blocked by**
- none

**Covers**
- AC1
- AC2

**Constraints**
- <本 task 必须保持的 contract / boundary>

**Verification**
- <完成时需要获得的 evidence target>
```

字段语义：

- **Outcome**：这个 task 应造成的完整状态变化，不写操作清单；
- **Blocked by**：只有真实前置结果缺失会使本 task 无法正确开始时才记录依赖；
- **Covers**：至少一个 `AC`；全部 `AC` 必须被某个 task 覆盖；
- **Constraints**：只写该 task 特有且已确认的边界，不重复 SPEC；
- **Verification**：描述需要证明的行为或结果，而不是提前指定测试框架、文件或 shell command。

例如 Verification 应写“未授权调用无法改变状态”“取消后不留下部分持久化结果”，而不是写 `npm test ...`、`flutter test ...` 或某个测试文件路径。实际命令和结果属于执行 evidence，由 `implement` / Runtime Goal / `loop` 在执行时记录。

PLAN 不写：

- 文件清单、类名清单或代码片段；
- 具体 shell 命令和逐步 implementation recipe；
- `todo / doing / done` 等运行时状态；
- retry 次数、round 次数、模型/Agent 分配、Token 预算；
- 为了“看起来完整”而创建的测试、文档、清理等独立 task；这些默认属于对应 vertical slice，除非它们自身交付独立 AC。

### Completion

PLAN 末尾定义与技术栈无关的完成门槛：

- 所有 in-scope task 已完成；
- 每个 `AC` 都有可观察 verification evidence；
- 没有未解决的真实 blocker；
- 目标仓库或任务契约要求的 quality gates 已满足；
- 未验证项如果存在，必须是 SPEC/任务契约明确允许的例外，而不是静默遗漏。

不要在 PLAN 中永久硬编码 `simplify`、`code-review`、某个 CI 命令或特定框架测试作为所有项目的强制 gate；是否需要这些由目标仓库和实际任务决定。

## PLAN 与 Runtime state 的边界

PLAN 是相对稳定的执行图，不是运行日志。

```text
SPEC.md   → normative contract
PLAN.md   → static declarative task graph
Goal/Loop → runtime progress + evidence + checkpoint
```

执行过程中通常不因 `T1` 已完成就改写 PLAN。Runtime-native Goal/Task 优先拥有暂停、恢复、session recovery 和动态状态；只有运行环境缺少这些能力且任务确实跨会话时，执行层才创建最小 checkpoint。

如果执行 evidence 证明原 Task Graph 的 dependency、scope 或 acceptance contract 错了，不能只改 runtime state：先判断是 PLAN 派生错误还是 SPEC 需要重新收敛，再回到 `to-spec` 或 `grilling` 更新正式契约。

Runtime 可以为了执行方便把一个 task 临时拆成更小 action，但不得借 re-plan 静默改变 `AC`、Destination 或 scope。

## Task decomposition

多个 task、存在真实 blocking edge 或预计跨多个 fresh context 时，按 `references/task-decomposition.md` 拆分。

优先 vertical slice：每个 task 交付一个对调用方有意义、可独立验证的结果。不要按“先建所有数据层、再建所有服务层、最后统一接 UI/API”的 horizontal layer 拆分，除非目标系统的真实依赖迫使这样做。

需要人工交接材料时再生成 `IMPLEMENT_PROMPT.md`；它不是 SPEC/PLAN 的一部分，也不是 Goal/Loop 的状态文件。

## Consistency validation

生成后必须做一次静态一致性检查：

1. `R`、`AC`、`T` ID 唯一且稳定；
2. 每个 in-scope `R` 至少被一个 `AC` 覆盖；
3. 每个 `AC` 至少被一个 `T` 覆盖；
4. 每个 `T` 至少服务于一个 `AC`；
5. 不存在 orphan AC、orphan task 或超出 SPEC 的 task；
6. `Blocked by` 引用存在，且依赖代表真实 blocking edge；
7. Task Graph 不存在明显 dependency cycle；
8. Verification 是 evidence target，不是 implementation recipe；
9. PLAN 未包含运行时 status；
10. Destination、Constraints 与 Completion 没有扩张 SPEC；
11. 文档中不存在占位符、未处理冲突或被静默跳过的 blocker。

发现一致性问题时先修正文档；如果问题来自尚未收敛的需求或设计决策，停止并回到 `grilling`。

## 变更规则

SPEC/PLAN 是一个原子任务契约：

- **规范性变化**：需求、范围、接口 contract、acceptance criterion 或明确约束变化时，同时检查并更新 SPEC 与 PLAN，再重新确认；
- **派生变化**：SPEC 语义不变，但原 Task Graph 的 decomposition / dependency 经新事实证明不合理时，可以只调整 PLAN，但必须保持 `R → AC → T` 完整追踪并说明依据；
- **运行时变化**：task 已完成、验证失败、发生 retry、round 前进等，只更新 Runtime state/checkpoint，不改 PLAN。

除非用户另行要求，不运行实现测试、不修改业务代码、不 commit/push。
