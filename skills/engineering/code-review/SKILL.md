---
name: code-review
description: "Used when 审查代码改动或 SPEC/PLAN 任务文档时（触发词：code review、审查改动、审查 SPEC、审查 PLAN、review diff、提交前审查）。"
---

# Code Review

对代码变更或任务文档做只读审查，始终分开报告 Standards 轴和 Spec 轴。当前 Agent 可以直接审查；只有确实需要独立视角且运行环境支持时，才委派 reviewer。不要把委派当作审查前提。

## 流程

1. 记录 `review_mode`（`standalone` 或 `implementation`）、`review_target`（`diff`、`task-docs` 或 `both`）和准确范围。
2. 固定 baseline、既有改动、包含/排除范围，以及 SPEC/PLAN 或用户请求等需求来源。
3. 读取目标仓库自己的指导文件、规范、配置、直接调用方、相关测试和外部边界；只读与变更相关的上下文。
4. 分别完成 Standards 和 Spec 审查，主动寻找现有 guard、调用约束和反证。
5. 每条 finding 引用具体文件、行、逻辑分支或需求条目，并标明严重程度、影响、建议和验证方式。

## Standards 轴

检查仓库已文档化的约定、错误处理、输入边界、安全、资源生命周期、并发、可读性、性能和明显的过度设计。重点关注新增接口是否真实、测试是否走生产入口、是否把实现细节泄漏给调用方，以及是否引入无调用者的抽象。

## Spec 轴

检查需求是否完整实现、是否发生 scope creep、状态/权限/错误/数据映射是否正确，以及每条验收标准是否有可观察证据。没有需求来源时标记 `no_spec_available`，不要猜测。

## 边界

这是只读审查，不修改文件、版本控制状态或外部系统。运行时异常、测试失败和构建失败交给 `debug`；全仓架构诊断交给 `examine-architecture`。详细模板见 `references/output-and-rules.md`，reviewer 输入契约见 `references/worker.md`。
