---
name: implement
description: "实现、验证并审查一项已明确的工作。"
---

# Implement

实现已确认的任务契约并交付可复核 evidence。普通小任务可以直接以 `SPEC.md` 为输入；跨多个 fresh context 的工作必须先由 `to-tickets` 拆分，并且一次只实现一张 ready delivery ticket。实现前必须重新调查当前仓库；任务文档定义需求和验收，不是代码配方。

## 入口与范围

接受以下两种输入：

1. **单次 SPEC mode**：一份 `SPEC.md` 的范围能够在一个 fresh context 内可靠完成，且不需要 execution graph；
2. **ticket mode**：用户指定 `tickets/<NN>-<slug>.md`。这是多 session 工作的常规入口；对应 `SPEC.md` 是规范性需求来源，ticket 是当前交付范围。

ticket mode 开始前：

- 读取完整 ticket 与它引用的 `SPEC.md`；
- 确认 ticket 含有 What to build、Constraints、Acceptance criteria、Blocked by 与 Status；
- 只领取 `Status: ready` 的 ticket，并确认每个 Blocked by ticket 都是 `done`；
- 将当前 ticket 更新为 `in-progress` 后才开始工作，避免并发 session 重复领取。

两种模式都必须：

1. 记录 `HEAD`、staged/unstaged/untracked 状态和 baseline，保护既有改动；
2. 动态发现仓库指导文件、coding standards、领域词汇、长期决策、相关代码、调用链、错误路径、测试和配置；适用 `AGENTS.md` 存在 `Engineering Skills Profile` 时把它作为项目入口索引，没有时继续发现现有结构；
3. 形成当前交付的最小实现方案；若关键 Module / Interface / Seam 本身仍未确定，调用或参考 `codebase-design`，不要在实现中临时发明边界；
4. 发现会改变行为、协议、权限、验收或范围的新事实时停止。单个未决选择转回 `grilling`；重要路径重新进入 Fog 转回 `wayfinding`，再经 `to-spec` 更新契约与受影响 tickets。

## 实现循环

- 每次调用只实现当前 SPEC 的单一范围，或一张 ticket；不得在同一 session 顺带开始另一个 ready ticket。
- 每个 delivery slice 先确定外部可观察行为和真实生产 seam，再写最小实现。
- 当任务适合 test-first、需求已有可独立判定的 expected behavior、且存在稳定 seam 时，调用 `tdd` skill 驱动 red → green vertical-slice 循环；不要在本 skill 复制 TDD 规则。
- 目标仓库已有其他验证方式且 TDD 不适用时，使用最小但足够的现有反馈循环；不要为了满足流程而制造测试专用生产接口。
- 实现过程中持续运行当前 slice 的定向测试和相关 typecheck，不要把反馈全部留到收尾。

## 收尾

1. 基于当前交付的完整 diff 串行执行 `simplify`；没有本任务代码改动则记录 `no_change`。
2. 按 [references/verification-and-review.md](references/verification-and-review.md) 运行定向验证，并在收尾默认运行项目完整测试集。只有项目契约明确允许更窄 gate、完整测试不可用或成本明显不成比例时才能跳过，同时记录原因、替代证据和未验证范围。
3. 按 [references/verification-and-review.md](references/verification-and-review.md) 使用 `code-review` 做 Standards 与需求契约两轴审查；修复 findings 后重新运行受影响验证。
4. ticket mode 下，只有当全部 Acceptance criteria 都有可观察 evidence 时，勾选对应条目、写入 evidence，并将 Status 更新为 `done`。无法继续时改为 `blocked`，写明精确原因；不得将未完成工作标为 done。
5. 只有用户明确授权时才 commit；不自动 push。提交范围只含本任务改动。

## 边界

- 不修改 SPEC、ticket 的 What to build、Constraints、Acceptance criteria 或 Blocked by 以迎合实现；只允许更新 ticket 的 Status、验收勾选和 execution evidence。
- 不覆盖既有改动。
- 不静默吞错。
- 不把模型自报、单次测试通过或实现细节检查当作完整验收证据。
- 不把项目规则塞回通用 Skill；项目自己的 coding standards、架构规则和技术栈约定由目标仓库提供。

输出实现 receipt，列明当前 SPEC 或 ticket、改动、验收/evidence、验证、审查和未验证项。
