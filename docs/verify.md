# Verify

`verify` 是交付流程中的独立验收角色。它针对一个明确的候选快照（candidate snapshot），逐条核对已确认的 Specification / Acceptance Criteria，判断每条是否有足够、可信、可复核的可观察证据（observable evidence）。

## 为什么需要独立 Verify

AI 可以同时修改产品代码、测试、fixture、mock、snapshot 和测试配置，也可以把失败的测试修到绿色。因此：

```text
tests passed != acceptance satisfied
```

单元测试仍然有价值，但在 AI Coding 里，它更准确的定位是快速反馈信号和回归约束，而不是正确性的自动证明。本仓库 TDD 的 red → green 纵向切片循环是实现方法，不是 verify 的验收标准，是否 test-first 也不改变最终的独立验收要求。

真正需要隔离的是“成功标准”而不只是 Agent 进程：

```text
SPEC / confirmed AC
        ↓
预期行为
        ↓
候选可观察行为
        ↓
独立证据比对
        ↓
PASS / FAIL / NOT VERIFIED
```

Acceptance Criteria 定义预期行为（expected behaviour），不能从实现、现有测试或实现者自报（implementor self-report）反向推导需求。独立子 Agent 只有在依据和证据都独立时，才有验收价值。

## 验收依据与证据

`ACCEPTANCE.md` 是按需建立的独立验收协议，不是 `verify` 的前置条件。日常任务没有这个文件时，`verify` 直接以 `SPEC.md` 中已确认、可单独判定的 AC 和验收边界（Acceptance Seam）为权威。

验证者可以组合使用：

- 现有回归测试、单元测试和集成测试；
- 构建、lint、类型检查、接口或运行时检查；
- 面向 AC 的最小只读探针（read-only probe）或 `.loop/tmp/` 中的临时测试；
- 候选改动差异（candidate diff）和验证产物（verification artifacts）的可信度检查；
- 必要时根据风险选择其他合理的外部参照（external oracle）或边界检查。

这些都是 evidence，不是 oracle。验证者必须确认每项 evidence 确实覆盖对应 AC，不能只看命令退出码为 0。测试、fixture、mock、snapshot、golden、CI/测试配置的修改本身不违规，但必须检查是否削弱、跳过、放宽了验证条件，或按实现重写了验证逻辑。这个检查只判断 evidence 是否仍可信，不评价架构、命名、可维护性或实现风格；后者属于 `code-review`。

如果现有检查无法直接证明某条 AC，验证者应优先寻找最小的独立可观察检查（observable check），而不是修改仓库测试或新增生产 API 来制造通过结果。没有安全、合理的验证方式时，返回 `NOT VERIFIED`。

## 三种结论

- `PASS`：有足够的可观察证据（observable evidence）证明该 AC 满足。
- `FAIL`：已经实际执行能够验证该 AC 的检查，并观察到结果与已确认需求（confirmed requirement）/ AC 冲突。
- `NOT VERIFIED`：证据不足，或环境、权限、依赖、运行时等条件不可用；这不是产品行为失败，也不是通过。

## Loop 如何处理结果

`verify` 只报告 verdict 和 evidence，后续状态由 `loop` 决定，不能把三种结论压成简单的成功/失败二值。

- `FAIL` 是当前已确认约定（confirmed contract）的已验证缺陷。Loop 保留原始发现和执行证据（execution evidence），交给 implement 走修正尝试（correction attempt），修复后重跑受影响的本地检查（local checks）和独立 verify。其他测试全绿不能覆盖它，相关代码、需求、执行图或环境变化后也不能复用旧报告。
- `NOT VERIFIED` 是验证缺口（verification gap）。Loop 先区分环境/权限/依赖阻塞、验证方法不足和需求/规范问题：环境类问题记录阻塞解除条件（release condition），方法不足就换其他只读证据，契约问题交回需求负责方（requirement owner）。不能直接把它丢给 implementor 修代码，也不能完成交付。
- 如果 verifier 的预期行为与已确认需求不一致，应解决验证依据（verification basis）/ 约定冲突，而不是修改实现去迎合错误期望。

因此，以下情况都不能视为通过：

- implementor 自报完成，但必需的 verifier 报告缺失；
- 本地检查或其他测试全绿，但某条必需的 AC 仍是 `FAIL` 或 `NOT VERIFIED`；
- 一部分 AC 是 `PASS`，其余必需的 AC 仍未验证。

只有所有必需的 AC 都是 `PASS`，并且必需的独立报告齐全，才满足验证层面的完成条件。

## 职责边界

```text
implement
  实现产品、编写开发测试、修复实现
        ↓
verify
  只读地独立判断 AC 与可观察证据
        ↓
code-review
  判断实现质量、设计、正确性风险和可维护性
        ↓
loop
  根据证据决定重试、阻塞、约定路由或完成
```

`verify` 不修复代码，不改需求、ticket、Git 历史或外部业务状态（external business state），也不修改仓库测试，不调度 Agent，不改变执行图。执行规则见 [`engineering/verify/SKILL.md`](../engineering/verify/SKILL.md)。
