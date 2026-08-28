---
name: loop
description: "Used when 用户明确要求把已落盘 SPEC/PLAN 自动循环跑到收尾并提交时（触发词：loop、自动跑完、循环实现、run loop）。调用即授权在退出条件满足后提交本任务改动，但不 push。"
---

# Loop

把已落盘 `SPEC.md` / `PLAN.md` 的实现自动推进到收尾：按轮驱动 `implement` 的实现、验证、简化与审查循环，满足退出条件后按一次性授权 commit。循环顺序、退出条件、轮数上限、断点续跑和 commit 授权归本 skill 所有；各阶段的规则、门槛和降级矩阵以对应 skill 为唯一 owner，不复述、不放宽。

## 1. 调用即授权

- 调用本 skill 等于一次性授权收尾 commit：提交范围只含本任务文件，不 push、不改分支、不重写历史。
- commit message 遵循用户明确要求，其次遵循目标仓库已有 Git/commit 约定；不存在项目约定时使用简洁、准确、描述实际改动的 message，不假定固定规则文件路径。
- 输入与 `implement` 相同：task 目录，可选 task unit 名称或编号。缺少 SPEC/PLAN 时停止，先走 `to-spec`。
- 入口校验、baseline 记录和 pre-existing 改动保护全部继承 `implement`，不因循环放宽。

## 2. 每轮动作

一轮 = 从当前 ready frontier 进入 `implement`，推进到它的集成验证与两轴审查完成，含内部强制 simplify 和审查修复循环。每轮结束先落断点，再做退出判定。断点位置和格式优先遵循目标仓库已有任务状态约定；不存在约定时使用当前 task 目录内的最小状态文件，不引入仓库级固定目录规范。

单 task 当轮完成时同样走退出判定，不制造多余轮次；no-op 轮不计入轮数上限。

## 3. 退出与停止

全部退出条件满足时 commit，并汇报 task/AC 状态、实际改动、验证与审查结果、剩余风险：

- 所选 task unit 全部 `completed`，每条 `AC` 有 verification evidence；
- 两轴审查没有未处理的必须修复项；
- 简化 gate 已执行，并有 `completed` 或 `no_change` receipt。

出现以下任一情况立即停止：保留断点，汇报已尝试路径、证据、阻塞点和继续所需输入，不 commit。

- 出现必须先收敛需求的新事实（契约冲突、方案失效、scope 变化）→ 转回 `grilling` / `to-spec`；
- 同一 finding 无新证据重复出现，判定为无进展；
- 达到轮数上限：默认 3 轮，用户指定时以指定值为准；
- 没有站得住脚的下一步。

停止后用户解决问题，可从断点续跑；输入和证据不变时不得原地重试。

## 4. 断点与续跑

断点至少保存：task/AC 状态、已用轮数、baseline、pre-existing 改动保护信息、最近一次验证/审查结果和下一步。具体文件名与位置沿用目标仓库或 task 流程现有约定，不假定固定 `STATUS.md`、`docs/**` 或 Agent Runtime 路径。

跨 Agent Runtime 交接时，可结合 `to-spec` 生成的实现交接材料或其他已有 handoff 机制，把退出条件、剩余轮数和 commit 授权状态写入交接上下文；SPEC/PLAN 仍是唯一需求来源。

恢复时先重读 SPEC/PLAN 与断点，重新核对工作区状态；baseline 失效或他人改动混入时停止并说明，不吞并。

## 5. 边界

- 不为满足退出条件弱化任何 gate：不把必须修复项降级、不跳过 simplification pass、不把未经独立证据支持的主 Agent 自报当作审查通过。
- 运行环境不支持独立 reviewer 时，遵循 `code-review` 的降级规则，而不是把某个特定 sub-agent 机制作为本 skill 的硬依赖。
- 与 `implement` 的实现规则冲突时以 `implement` 为准，停止并说明。
- 轻路径任务不进本 skill；需求未落盘先走 `grilling` / `to-spec`。
