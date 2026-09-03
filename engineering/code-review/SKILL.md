---
name: code-review
description: "只读审查已完成代码是否符合项目规范、需求 SPEC，以及存在时的概要设计 HLD，并分别报告三项审查的证据。"
---

# Code Review

对已完成的代码变更做只读审查，始终分开报告项目规范审查和需求实现审查；任务存在 `HLD.md` 时增加概要设计审查。三项审查分别计数和报告，不相互抵消，也不合并成单一严重程度。

## 审查模式

- **branch / commit**：用户提供对比基准。先用 `git rev-parse` 验证，再固定 `git diff <fixed-point>...HEAD` 和 `git log <fixed-point>..HEAD --oneline`；ref 无效或 diff 为空时立即停止。
- **working tree**：baseline 固定为 `HEAD`，分别审查 staged、unstaged，并记录未跟踪文件清单；不能把未读取的 untracked 文件算入覆盖范围。
- **explicit path**：仅在用户明确指定路径时使用，报告没有 branch 对比基准、无法证明完整提交范围的限制。
- **implementation**：由实现流程提供对比基准、既有改动、SPEC、存在时的 HLD、当前 ticket 或完整执行图、实际已实现范围、执行回执和验证证据；既可审查单个工作单元，也可审查整体交付集成结果。

`implementation` 模式使用调用方提供的范围，不重新猜测；无法从对比基准、执行回执和当前工作区实际状态证明完整覆盖时返回 `BLOCKER` 并说明未覆盖范围。

## 需求来源

按以下顺序寻找需求来源：

1. 用户明确提供的需求来源；
2. 当前 ticket 或执行图引用的 `SPEC.md`；
3. commit message 中可从已配置 issue tracker 获取的 issue；
4. 与 branch 或任务名匹配的本地 spec。

仍然没有来源时，标记 `no_spec_available`，跳过需求实现审查，不补写需求。

## HLD 来源

`implementation` 模式使用调用方提供的 `HLD.md`；ticket 引用 D IDs 时必须读取同一任务目录中的完整 HLD。其他模式只使用用户明确提供或与当前 SPEC 同目录的 HLD，不把仓库级架构文档误当成任务级概要设计。没有 HLD 时标记 `not_applicable`。

## Process

1. 固定审查模式、准确命令/路径、对比基准、既有改动和包含/排除范围。
2. 动态发现目标仓库自己的 Agent 指令、coding standards、架构/领域文档、配置、直接调用方、相关测试和外部边界。
3. 运行环境支持且当前授权允许时，按 `references/worker.md` 使用独立 reviewer 分别完成项目规范审查、需求实现审查，以及适用时的概要设计审查；否则由当前 Agent 前后分开执行各项审查。
4. 每条审查发现引用具体文件、行、逻辑分支、标准或需求条目，并标明当前审查项内的严重程度、影响、建议和验证方式。
5. 按 `references/output-and-rules.md` 聚合；不合并或跨审查项重新排序审查发现。

## 项目规范审查

首先检查目标仓库已文档化的约定；项目规则优先于通用工程启发式。没有项目规则时，不把个人风格偏好伪装成 violation。

通用检查包括错误处理、输入边界、安全、资源生命周期、并发、可读性、性能和明显过度设计。项目规则覆盖通用 heuristic，工具已经强制的规则不重复报告。

Fowler smell baseline 仅作为 judgement call；完整定义与建议见 [references/smell-baseline.md](references/smell-baseline.md)。报告时必须点名 smell、引用具体 hunk，并说明为什么它在当前 diff 中造成实际摩擦。

同时重点关注：

- 新增 Interface 是否有真实生产调用者与清晰 ownership；
- 测试是否通过生产公开 Seam，而不是测试专用入口；
- 是否把实现细节泄漏给调用方；
- 是否引入无调用者、纯转发或 speculative abstraction；
- 测试是否出现 implementation-coupled、tautological 或 horizontal-slicing 等问题。

涉及 Module / Interface / Seam 判断时参考 `codebase-design`；涉及测试质量时参考 `tdd`。这些是通用设计纪律，不覆盖项目自己的明确标准。

## 需求实现审查

检查需求是否完整实现、是否发生超出需求范围、状态/权限/错误/数据映射是否正确，以及每条验收标准是否有可观察证据。没有需求来源时标记 `no_spec_available`，不要猜测。

## 概要设计审查

仅当任务目录或调用方提供 `HLD.md` 时启用。检查变更是否遵守适用 D IDs、模块职责、共享约定、依赖方向、状态/错误语义与集成约束，并确认实现没有把 HLD 的局部实现空间错当成强制结构。对标记为 `Reuse` / `Extend` 的决定检查实现是否沿用所列参考实现；对 `New` / `Replace` 检查是否保持 HLD 声明的必要性、迁移边界和最小影响范围。没有 HLD 时标记 `not_applicable`，不能自行补写概要设计。

如果代码事实证明 HLD 不可行，报告设计阻塞并交回 `high-level-design`；不能把偏离 HLD 自动判成正确实现，也不能为了符合过期 HLD 建议错误修改。

## 边界

这是只读审查，不修改文件、版本控制状态或外部系统。运行时异常、测试失败和构建失败交给 `debug`；全仓架构诊断交给 `review-architecture`。最终可以给出提交建议，但必须保留每项适用审查各自的结论，不能用一个总评抵消任一项的失败。
