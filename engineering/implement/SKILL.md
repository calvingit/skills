---
name: implement
description: "用于按已确认任务契约实现、验证并审查代码改动。"
---

# Implement

实现由 `to-spec` 生成或兼容的 `SPEC.md` 与 `PLAN.md`。文档定义需求和验收，不是代码配方；实现前必须重新调查当前仓库。

## 入口与范围

1. 要求任务目录；缺少 `SPEC.md` 或 `PLAN.md` 时停止并转回 `to-spec`。
2. 校验 `R`、`AC`、`T` ID 唯一且覆盖完整；阻塞性未决问题转回 `grilling`。
3. 记录 `HEAD`、staged/unstaged/untracked 状态和 baseline，保护既有改动。
4. 动态发现仓库指导文件、coding standards、领域词汇、长期决策、相关代码、调用链、错误路径、测试和配置；适用 `AGENTS.md` 存在 `Engineering Skills Profile` 时把它作为项目入口索引，没有时继续发现现有结构，不假定固定文档路径或技术栈。
5. 形成当前 task 的最小实现方案；若关键 Module / Interface / Seam 本身仍未确定，调用或参考 `codebase-design`，不要在实现中临时发明边界。

## 实现循环

- 单 task 直接实现；多 task 只处理无 blocker 的 ready task。
- 每个 vertical slice 先确定外部可观察行为和真实生产 seam，再写最小实现。
- 当任务适合 test-first、需求已有可独立判定的 expected behavior、且存在稳定 seam 时，调用 `tdd` skill 驱动 red → green vertical-slice 循环；不要在本 skill 复制 TDD 规则。
- 目标仓库已有其他验证方式且 TDD 不适用时，使用最小但足够的现有反馈循环；不要为了满足流程而制造测试专用生产接口。
- 发现会改变行为、协议、权限、验收或依赖关系的新事实时停止，回到 `grilling` / `to-spec`。
- 多 task 需要并行时，遵守 `references/multi-task-orchestration.md`；无法证明写入隔离则串行。

## 收尾

1. 所有 task 完成后，基于完整 diff 串行执行 `simplify`；没有本任务代码改动则记录 `no_change`。
2. 按变更风险和目标仓库已有能力选择最小测试、静态检查、构建或端到端验证，保存命令、退出码和关键结果。
3. 使用 `code-review` 做 Standards + Spec 两轴审查；修复 findings 后重新运行受影响验证。
4. 只有用户明确授权时才 commit；不自动 push。提交范围只含本任务改动。

## 边界

- 不修改 SPEC/PLAN 以迎合实现。
- 不覆盖既有改动。
- 不静默吞错。
- 不把模型自报、单次测试通过或实现细节检查当作完整验收证据。
- 不把项目规则塞回通用 Skill；项目自己的 coding standards、架构规则和技术栈约定由目标仓库提供。

输出实现 receipt，列明 task/AC、改动、验证、审查和未验证项。
