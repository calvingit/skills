---
name: tdd
description: "用于以 test-first / red-green 方式实现功能或修复 bug，通过公开 Seam 的 vertical slice 验证行为。"
---

# Test-Driven Development

TDD 在这里指 **red → green 的 vertical-slice 反馈循环**。目标不是最大化测试数量，而是用独立、可观察的反馈约束实现，让每一步都能证明行为是否向目标移动。

## Preconditions

开始前必须有：

1. 可外部判定的 expected behavior；
2. expected value 的独立来源，例如用户确认、spec/acceptance criteria、公开 contract、权威文档或 worked example；
3. 可以稳定观察该行为的生产 Seam。

任一项不存在时，不伪造测试：行为不清楚转 `grilling`；Seam / Interface 本身不合理时调用或参考 `codebase-design`。

## What a good test is

好的测试验证 **behavior through public interfaces**，而不是实现结构。实现可以被重写，只要外部行为不变，测试就应尽量保持有效。

优先：

- 用户或调用方真正可观察的结果；
- 真实生产构造和公开入口；
- 与生产路径一致的 Adapter / boundary；
- 独立于被测实现计算方式的 expected value。

避免：

- 测 private method、内部字段或调用顺序，而这些不是 contract；
- 为测试新增 `forTest`、noop、mutable callback、delay 参数或公开内部状态；
- 用数据库旁路、内部日志或源码字符串存在性代替真实行为，除非这些本身就是公开 contract。

## Anti-patterns

### Implementation-coupled

测试绑定内部 collaborator、private API 或当前文件结构。重构不改变行为却导致大量测试失败，是最常见信号。

### Tautological

测试的 expected value 与实现来自同一逻辑或同一假设，因此“按构造必然通过”。例如：

- 实现用公式 X 计算，测试再用同一个公式 X 计算 expected；
- 刚向源码写入字符串 X，测试只检查源码包含 X，而真实需求是运行时行为；
- mock 按实现当前调用方式返回值，再断言实现按同一调用方式工作。

expected value 必须尽量来自独立 source of truth：已确认 literal、spec 示例、协议文档、golden fixture、外部系统可验证结果等。

### Horizontal slicing

先批量写所有测试，再批量实现。这样测试通常锁定想象中的结构，而不是根据每个反馈循环学到的事实演化。

使用 vertical slice：

```text
one behavior → one red test → minimal green implementation → next behavior
```

## Choose the Seam first

写测试前明确：

- 被观察的 public behavior 是什么；
- 测试从哪个生产 Seam 进入；
- 哪些外部边界可以使用真实依赖，哪些需要稳定替身；
- 本轮不测试什么。

Seam 应优先来自真实 Module / Interface / Adapter 边界。如果测试只能通过新增生产 API 才能建立，先用 `codebase-design` 判断边界是否真的应该改变，而不是直接为可测性扩 API。

## The loop

每个 slice 严格按以下顺序：

1. **Pick one behavior**：选择一个最小但有用户价值、可独立观察的行为。
2. **Red**：写一个失败测试，确认失败原因正是缺失/错误的目标行为，而不是 fixture、环境或语法问题。
3. **Green**：只写足够让这个测试通过的最小生产代码；不要提前实现后续 slice。
4. **Verify**：重跑该测试和受影响的最小现有测试集，确认没有把其他行为破坏。
5. **Next slice**：根据刚得到的新事实选择下一个行为，而不是按预先写死的测试清单机械推进。

Refactor / simplify 不应掺进每个 red-green cycle 造成反馈失焦。完成一组连贯 slice 后，再交给 `simplify` 或实现流程的 review/simplification gate 处理结构收缩，并重跑验证。

## Test doubles

优先级：

1. 真实、快速、确定性的依赖；
2. 目标项目已经提供的官方 fake / emulator / in-memory Adapter；
3. 在真实外部边界使用最小 test double。

不要 mock 自己的内部 Module 只是为了让测试更“单元化”。mock 应隔离真实外部不确定性，而不是复制实现结构。

## Bug fixes

`debug` 已负责建立 bug feedback loop、最小复现和根因确认。进入 TDD 时，把已确认的最小复现转成回归测试：先 red，再做最小 root-cause fix，最后重跑原始复现。不要让 `tdd` 重新执行一套独立 bug diagnosis。

## Done when

- 每个新增测试都能说明它验证的外部行为和独立 expected 来源；
- 所有新增行为都经历过可确认的 red → green；
- 测试通过生产公开 Seam，没有为测试泄漏不必要实现细节；
- 没有明显 tautological、implementation-coupled 或 horizontal-slicing 测试；
- 相关现有验证仍通过；未验证部分明确记录。

## Boundaries

- 不强制具体 test framework、目录、coverage 百分比或 mocking library。
- 不要求所有任务都 TDD；无法建立有价值的快速反馈循环时，应选择目标仓库已有的更合适验证方式。
- 不把“测试通过”当作需求完整实现的唯一证据；最终仍由 `code-review` 的 Spec 轴和任务验收判断完整性。
