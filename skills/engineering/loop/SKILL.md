---
name: loop
description: "Used when 用户明确要求把已落盘 SPEC/PLAN 自动循环跑到收尾并提交时（触发词：loop、自动跑完、循环实现、run loop）。"
---

# Loop

把已落盘 `SPEC.md` / `PLAN.md` 的实现自动推进到收尾：按轮驱动 `implement` 的实现、验证、简化与审查循环，满足退出条件后按一次性授权 commit。循环顺序、退出条件、轮数上限、断点续跑和 commit 授权归本 skill 所有；各阶段的规则、门槛和降级矩阵以对应 skill 为唯一 owner，不复述、不放宽。

## 1. 调用即授权

- 调用本 skill 等于一次性授权收尾 commit：提交范围只含本任务文件，message 遵循 `docs/rules/git-commit.rules.md`，不 push、不改分支、不重写历史。
- 输入与 `implement` 相同：task 目录，可选 task unit 名称或编号。缺少 SPEC/PLAN 时停止，先走 `to-spec`。
- 入口校验、baseline 记录和 pre-existing 改动保护全部继承 `implement`，不因循环放宽。

## 2. 每轮动作

一轮 = 从当前 ready frontier 进入 `implement`，推进到它的集成验证与两轴审查完成，含内部强制 simplify 和审查修复循环。每轮结束先落断点（`STATUS.md`、receipts 摘要、已用轮数），再做退出判定。单 task 当轮完成时同样走退出判定，不制造多余轮次；no-op 轮不计入轮数上限。

## 3. 退出与停止

全部退出条件满足时 commit，并汇报 task/AC 状态、实际改动、验证与审查结果、剩余风险：

- 所选 task unit 全部 `completed`，每条 `AC` 有 verification evidence；
- 两轴审查没有未处理的 `必须修复`；
- 简化 gate 已执行（存在 simplification receipt）。

出现以下任一情况立即停止：保留断点，汇报已尝试路径、证据、阻塞点和继续所需输入，不 commit。

- 出现必须先收敛需求的新事实（契约冲突、方案失效、scope 变化）→ 转回 `grilling` / `to-spec`；
- 同一 finding 无新证据重复出现，按 `implement` 第 6 节规则判定为无进展；
- 达到轮数上限：默认 3 轮，用户指定时以指定值为准；
- 没有站得住脚的下一步。

停止后用户解决问题，可从断点续跑；输入不变时不得原地重试。

## 4. 断点与续跑

- 断点 = `STATUS.md`（沿用 `implement` 的表格，仍只由主 agent 更新）+ 已用轮数 + baseline 与 pre-existing patch snapshot 的引用。
- 跨 Agent Runtime 交接时结合 `to-spec` 的 `IMPLEMENT_PROMPT.md`，把退出条件、剩余轮数和 commit 授权状态写进 envelope；目标 Runtime 按本 skill 恢复，SPEC/PLAN 仍是唯一需求来源。
- 恢复时先重读 SPEC/PLAN 与断点，重新核对工作区状态；baseline 失效或他人改动混入时停止并说明，不吞并。

## 5. 边界

- 不为满足退出条件弱化任何 gate：不把 `必须修复` 降级、不跳过 simplification pass、不用主 agent 自审代替独立审查；退出判定只引用已存在的证据。
- 与 `implement` 的规则冲突时以 `implement` 为准，停止并说明。
- 轻路径任务不进本 skill；需求未落盘先走 `grilling` / `to-spec`。
