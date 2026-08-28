# Task Decomposition

仅当实现预计包含多个 fresh context window，或存在需要显式表达的 blocking edges 时读取本规则。任务分解写入 `PLAN.md`，不生成 `TASKS.md` 或单独 implementation ticket 文件。

fresh context window 指不依赖上一个任务未落盘推理的全新实现会话。

## 目标

把已确认方案拆成少量 tracer-bullet vertical slices，让实现 Agent 能选择一个 task unit 后在 fresh context window 中重新调查并独立实施。task unit 只定义完整结果、验收映射、blocking edges、必须保持的边界和验证目标，不提供实现配方。

## 拆分规则

- 每个 task unit 使用稳定 ID `T1`、`T2`……，默认交付一个可观察或可验证的完整结果，不按技术层、目录、代码类型或测试类型拆成 horizontal slice。
- 每个 vertical slice 应能由一个 fresh context window 合理完成；无法做到时继续按交付结果拆分。
- 只记录真实 blocking edges。`Blocked by` 为空的 task 可以开始；不要为了形成线性顺序制造依赖。
- 每个 task 必须映射至少一个 SPEC `AC`，所有 `AC` 必须由至少一个 task 覆盖；不得用「全部验收」替代可检查的 ID 映射。
- task 只能细化已确认决策。发现新的产品、协议、边界或验收决策时返回分析阶段，不在 PLAN 中擅自决定。
- 不默认增加 prefactoring。只有已确认决策要求，或不做就无法形成独立可验证的 vertical slice 时，才保留高层前置 task。
- wide refactor 是 vertical slicing 的例外。只有大范围机械变更使任何独立 slice 都无法保持可验证状态时，才能用 expand-contract 表达高层迁移阶段；不得擅自引入 SPEC 未要求的兼容、双写或灰度策略。
- 测试、静态分析、文档收尾和代码清理默认属于相关 slice 的完成责任，不单独建 task。只有独立设备、外部环境或人工验收无法随 slice 完成时，才建立单独验证 task。

## PLAN.md 中的 task unit

每个 task unit 只写：

1. `T` ID 与名称
2. What it delivers
3. Blocked by
4. Covers：明确的 `AC` ID
5. Must preserve
6. Verification target：需要取得的证据类型或可观察结果

禁止写：

- 文件、目录、类、函数、变量或代码位置清单
- 代码片段、伪代码或接口调用方式
- 具体命令、测试路径或逐步修改步骤
- 未经确认的实现选择
- 与 `implement` skill 通用纪律重复的预算、重试或停止模板

如果整个实现可在一个 fresh context window 内完成，保留一个 `T1` 即可，不为拆分而拆分。

## 自检

完成任务分解后逐项确认：

- 能否清楚回答「该 task 完成后，外部可观察到什么结果」
- blocking edges 是否确实阻止该 task 开始
- 每个 `AC` 是否有 task 覆盖，每个 task 是否有明确 `AC` 来源
- 验证目标是否随 slice 交付，而不是被推迟为通用 test-after task
- 实现 Agent 是否仍需要重新调查项目并选择具体实现方式

最后一项必须为「是」。如果 PLAN 已经可以直接复制成代码修改清单，说明分析过度，应删去实现细节。
