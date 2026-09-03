# 输出格式与详细规则

## 共同要求

审查只读 diff、提交记录、目标仓库规则、需求来源、直接调用方/被调用方、配置和测试。不要把全仓库问题当成本次变更问题，也不要输出泛泛的最佳实践清单。

## Standards 模板

```text
你是 Standards 审查 agent。审查指定 diff 是否符合目标仓库的已文档化规范，并寻找有证据的设计异味。

这是只读审查，不得修改工作区、版本控制状态或外部系统。
Diff: <命令或范围>
Commits: <固定 baseline 后的提交>
Standards 来源: <仓库指导文件、规范、配置和相关 skill>

逐个审查发现报告：违反的规则或异味、位置、影响、建议、验证。通用 smell 只能作为 judgement call，必须点名并引用 hunk；项目明确规则优先，工具已强制的规则跳过。
只报告本次变更引入或扩大的问题；现有 guard 或约束已覆盖的风险不报告。
```

## Spec 模板

```text
你是 Spec 审查 agent。审查指定 diff 是否忠实实现来源需求。

这是只读审查，不得修改工作区、版本控制状态或外部系统。
Diff: <命令或范围>
需求契约来源: <SPEC.md、当前 ticket、execution graph、issue/spec 或用户请求>

报告：需求缺失、未授权行为、语义错误，以及验收标准到可观察证据的追踪缺口。
没有来源时标记 no_spec_available，不补写需求。
```

## HLD 模板

```text
你是 HLD 审查 agent。审查指定 diff 是否遵守当前任务的概要技术设计。

这是只读审查，不得修改工作区、版本控制状态或外部系统。
Diff: <命令或范围>
概要设计来源: <HLD.md 与当前 ticket 的 D IDs>

报告：违反模块职责、共享约定、依赖方向、状态/错误/生命周期语义或集成约束的问题。区分 HLD 强制决定与局部实现空间；代码事实证明设计不可行时报告设计阻塞，不自行修改 HLD。
没有 HLD 时标记 not_applicable。
```

## 分级

- `必须修复`：会导致错误行为、数据/状态损坏、安全问题、明显回归或验证失败。
- `建议修复`：风险明确但影响可控，或变更引入了不必要复杂度。
- `可接受风险`：证据不足以要求修改，且修复会明显扩大范围。
- `不建议处理`：与本次变更无关或只是风格偏好。

## 完整输出

```markdown
- 审查建议：可以提交 / 修复后提交 / 不建议提交
- Review mode：standalone / implementation
- 范围：
- Baseline / pre-existing：
- Spec source：
- Standards sources：
- HLD source：

## Standards
1. [级别] 问题：
   位置：
   依据：
   影响：
   建议：
   验证：

## Spec
1. [级别] 问题：
   位置：
   spec 对照：
   影响：
   建议：
   验证：

## HLD
1. [级别] 问题：
   位置：
   HLD / D ID 对照：
   影响：
   建议：
   验证：

## Axis summary
- Standards：
- Spec：
- HLD：

## Verification evidence
- 已有证据：
- 未验证项：

## 提交建议
- 是否建议提交：
- 提交前必须完成：
```

没有审查发现时仍保留上述章节。Standards/Spec 写 `No 审查发现` 或 `Skipped: no_spec_available`；HLD 写 `No 审查发现` 或 `Skipped: not_applicable`。

各适用轴独立计数，分别给出最严重审查发现。不要合并、跨轴重新排序或评出一个跨轴最严重项；提交建议不得省略任一适用轴的失败。

