---
name: code-review
description: "审查已完成的代码变动是否符合标准和需求。"
---

# Code Review

对已完成的代码变更做只读审查，始终分开报告 Standards 轴和 Spec 轴。两轴独立计数，不跨轴重排，也不把两轴合并后评出一个“最严重问题”，以免一轴掩盖另一轴。

## Review modes

- **branch / commit**：用户提供 fixed point。先用 `git rev-parse` 验证，再固定 `git diff <fixed-point>...HEAD` 和 `git log <fixed-point>..HEAD --oneline`；ref 无效或 diff 为空时立即停止。
- **working tree**：baseline 固定为 `HEAD`，分别审查 staged、unstaged，并记录 untracked inventory；不能把未读取的 untracked 文件算入覆盖范围。
- **explicit path**：仅在用户明确指定路径时使用，报告没有 branch fixed point、无法证明完整提交范围的限制。

实现流程传入的 baseline、pre-existing changes 和当前 ticket 作为 working-tree review 的固定范围，不重新猜测。

## Spec source

按以下顺序寻找需求来源：

1. 用户明确提供的 source；
2. 当前 ticket 引用的 `SPEC.md`；
3. commit message 中可从已配置 issue tracker 获取的 issue；
4. 与 branch 或任务名匹配的本地 spec。

仍然没有来源时，标记 `no_spec_available`，跳过 Spec 轴，不补写需求。

## Process

1. 固定 review mode、准确命令/路径、baseline、既有改动和包含/排除范围。
2. 动态发现目标仓库自己的 Agent 指令、coding standards、架构/领域文档、配置、直接调用方、相关测试和外部边界。
3. 运行环境支持且当前授权允许时，按 `references/worker.md` 使用两个独立 reviewer，并行完成 Standards 与 Spec；否则由当前 Agent 前后分开执行两次审查。
4. 每条 finding 引用具体文件、行、逻辑分支、标准或需求条目，并标明轴内严重程度、影响、建议和验证方式。
5. 按 `references/output-and-rules.md` 聚合；不合并或跨轴重新排序 findings。

## Standards 轴

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

## Spec 轴

检查需求是否完整实现、是否发生 scope creep、状态/权限/错误/数据映射是否正确，以及每条验收标准是否有可观察证据。没有需求来源时标记 `no_spec_available`，不要猜测。

## 边界

这是只读审查，不修改文件、版本控制状态或外部系统。运行时异常、测试失败和构建失败交给 `debug`；全仓架构诊断交给 `review-architecture`。最终可以给出提交建议，但必须同时保留两个轴各自的结论，不能用一个总评抵消某一轴的失败。
