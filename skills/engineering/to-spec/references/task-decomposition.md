# Task Decomposition

用于把已经确认的 `SPEC.md` 派生为静态、声明式的 `PLAN.md` Task Graph。只在存在多个真实工作单元、真实 blocking edge，或任务预计跨多个 fresh context 时需要显式拆分。

## 原则

- 每个 task unit 交付一个可观察或可验证的完整结果，使用稳定 `T` ID。
- 优先 vertical slice：一个 task 尽量完成从输入到可观察结果的一条完整行为，而不是只完成某一技术层。
- 只记录真实依赖；无 blocker 的 task 都可以进入 initial ready frontier，不为形成线性顺序制造依赖。
- 每个 task 至少覆盖一个 `AC`，全部 `AC` 必须被覆盖；task 不得超出 SPEC scope。
- task 只能细化已确认决策。发现新的产品、协议、架构、边界或验收选择时，停止拆分并回到 `grilling` / `to-spec`。
- 测试、静态检查、文档收尾和清理默认属于对应 slice，不单独制造 task；只有它们本身交付独立 acceptance criterion 时才成为 task。
- PLAN 只保存静态 Task Graph，不保存 `todo / doing / done`、retry、round、Agent 分配或其他 runtime state。

## 每个 Task 的最小结构

每个 task 使用以下五类信息：

```markdown
### T1 — <Outcome-oriented title>

**Outcome**
<完成后可观察或可验证的状态>

**Blocked by**
- none

**Covers**
- AC1

**Constraints**
- <必须保持的 contract / boundary>

**Verification**
- <需要获得的 evidence target>
```

- `Outcome` 写结果，不写实现步骤。
- `Blocked by` 只写真正阻止正确开始的 task ID。
- `Covers` 建立 `T → AC` 可追踪关系。
- `Constraints` 只写这个 task 特有且已确认的边界。
- `Verification` 描述需要证明的行为或结果，不指定测试框架、测试文件、shell command 或具体实现方式。

禁止写文件清单、代码片段、命令、逐步 recipe、内部类设计或为了可测试性预设的生产接口。

## Task Graph

有多个 task 或依赖时，在 PLAN 中提供摘要：

```markdown
| Task | Blocked by | Covers |
| --- | --- | --- |
| T1 | — | AC1, AC2 |
| T2 | T1 | AC3 |
| T3 | T1 | AC4 |
```

frontier 由依赖关系自然产生：所有 `Blocked by` 已满足的未完成 task 都是 ready。PLAN 不需要也不应该保存当前 frontier 的动态状态。

## 拆分判断

一个候选 task 应同时满足：

1. 完成后能说明一个完整的外部可观察结果或明确的可验证状态；
2. 至少覆盖一个 AC；
3. 不需要在 task 内重新决定 SPEC 尚未确认的问题；
4. 不依赖未来 task 的实现细节才能定义自身 outcome；
5. Verification 可以描述为独立 evidence target，而不是“代码写完了”；
6. 实现 Agent 仍需要根据当前仓库重新调查具体文件、接口和实现方案。

如果一个 task 只是“新增 model”“修改 service”“补测试”这类技术层动作，优先尝试把它并回交付完整行为的 vertical slice。

## Dependency rules

只有以下情况才应建立 `Blocked by`：

- 后续 task 的 contract 或输入必须由前一 task 先产生；
- 前一 task 建立的 migration / compatibility state 是后续正确执行的必要条件；
- 真实环境或数据状态要求顺序执行；
- 并行执行会破坏已确认的不变量或产生不可接受冲突。

不要因为“通常先做 A 再做 B”、文件修改顺序或作者偏好建立依赖。

自检：完成后是否能说明每个 task 的外部结果、依赖确实阻塞、`R → AC → T` 映射完整、无 dependency cycle、无 runtime state，且实现 Agent 仍需基于当前仓库重新调查。