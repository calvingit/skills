---
name: implement
description: "Used when 用户明确要求按已落盘 SPEC/PLAN 实现任务时（触发词：implement、实现 spec、按 PLAN 实现、执行任务文档、实现任务）。"
---

# Implement

实现由 `to-spec` 生成或兼容的 `SPEC.md` 与 `PLAN.md`。文档定义需求和验收，不是代码配方；实现前必须重新调查当前仓库。

## 入口与范围

1. 要求任务目录；缺少 `SPEC.md` 或 `PLAN.md` 时停止并转回 `to-spec`。
2. 校验 `R`、`AC`、`T` ID 唯一且覆盖完整；阻塞性未决问题转回 `grilling`。
3. 记录 `HEAD`、staged/unstaged/untracked 状态和 baseline，保护既有改动。
4. 读取仓库指导文件、相关代码、调用链、错误路径、测试和配置，形成当前任务的最小实现方案。

## 实现循环

- 单 task 直接实现；多 task 只处理无 blocker 的 ready task。
- 每个 vertical slice 先确定公开行为和真实外部边界，再写最小实现；测试使用仓库适用的工具，不为可测性扩大生产接口。
- 发现会改变行为、协议、权限、验收或依赖关系的新事实时停止，回到 `grilling` / `to-spec`。
- 多 task 需要并行时，遵守 `references/multi-task-orchestration.md`；无法证明写入隔离则串行。

## 收尾

1. 所有 task 完成后，基于完整 diff 串行执行 `simplify`，没有本任务代码改动则记录 `no_change`。
2. 按变更风险选择仓库适用的最小测试、静态检查或构建验证，保存命令、退出码和关键结果。
3. 使用 `code-review` 做 Standards + Spec 两轴审查；修复后重新验证。
4. 只有用户明确授权时才 commit；不自动 push。提交范围只含本任务改动。

## 边界

不修改 SPEC/PLAN 以迎合实现，不覆盖既有改动，不静默吞错，不把模型自报或测试通过当作完整验收证据。输出实现 receipt，列明 task/AC、改动、验证、审查和未验证项。
