# 为什么需要独立 Verify

AI 可以同时修改产品代码、测试、fixture、mock、snapshot 和测试配置，也可以把失败的测试修到绿色。因此：

```text
tests passed != acceptance satisfied
```

单元测试仍然有价值，但在 AI Coding 里，它更准确的定位是快速反馈信号和回归约束，而不是正确性的自动证明。本仓库 TDD 的 red → green → refactor 小步循环是实现方法，不是 verify 的验收标准，是否 test-first 也不改变最终的独立验收要求。

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

Acceptance Criteria 定义预期行为（expected behaviour），不能从实现、现有测试或实现者自报（implementor self-report）反向推导需求，验收要依据独立来源和可观察证据。

## 方法、证据与结论

项目本地方法说明如何启动、驱动、观察、隔离和清理，验证方法的冒烟运行只支持实际执行的路径和环境。SPEC 或已确认的会话 AC 定义预期，独立验证判断当前候选是否满足它。项目必需门禁的结果应单独记录，不能自动映射成所有 AC 通过。

测试、fixture、mock、snapshot、golden 和配置都是需要核对来源、执行路径和覆盖范围的证据。测试绿色不能自行保证独立预期正确，行为 E2E、视觉参考、交互时序和真实第三方集成也需要各自充分的观察。

[Verify](../SKILL.md) 维护执行步骤、PASS / FAIL / NOT VERIFIED 的定义和只读边界，[verification-setup](../../verification-setup/SKILL.md) 维护项目方法，专项测试价值审计由 [test-audit](../../test-audit/SKILL.md) 负责。Loop 如何接受证据和改变状态，见 [Loop 的证据决策](../../loop/SKILL.md#decide-from-evidence)，这些角色的判断不能相互替代。
