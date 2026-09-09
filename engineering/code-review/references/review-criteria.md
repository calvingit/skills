# Review Criteria

## 共同要求

审查只读 diff、提交记录、目标仓库规则、需求来源、直接调用方和被调用方、配置和测试。不要把全仓库问题当成本次变更问题，也不要输出泛泛的最佳实践清单。阻断发现只包含本次变更引入或扩大的问题；范围外既有高风险问题单列 non_blocking_findings，已有 guard 或约束已经覆盖的风险不重复报告。

## Contract

审查当前 ticket 的 `R`/`AC`、`SPEC.md`、存在时的 `ACCEPTANCE.md` 和适用失败状态约束，确认每条任务声明都有可观察证据，并覆盖与风险相关的公开接口、成功、失败、取消、超时、权限、scope、数据安全和资源清理。契约违反、缺少必需证据或已有协议矛盾进入 `blocking_findings`；已启用协议无法覆盖真实高风险路径时进入 `acceptance_protocol_gaps`。

## Change-surface

沿变更文件展开到直接调用方、直接被调用模块、公开类型、序列化 / 反序列化、配置、测试、artifact 保存和资源生命周期。直接链路上的正确性、安全、权限、数据损坏、进程泄漏或明显回归进入 `blocking_findings`。

存在任务级 HLD 时，检查适用 D IDs、模块职责、依赖方向、共享类型和错误语义，但不把 HLD 单独当作扩大 scope 的理由。

## Exploratory

允许检查相邻模块和范围外路径，但不改变当前 ticket 的 `R`/`AC`、`SPEC.md` 或 `ACCEPTANCE.md`。普通范围外问题进入 `non_blocking_findings`，分类为 `out_of_scope_risk` 时必须路由到新 ticket：

```json
{
  "category": "out_of_scope_risk",
  "severity": "P2",
  "evidence": "具体代码或可达路径证据",
  "recommended_route": "new-ticket"
}
```

如果范围外问题被证实由本次变更引入或扩大、可达且涉及安全、数据丢失、权限越界、资源泄漏或其他高风险，则进入 `blocking_findings`，但不因此修改当前验收协议。

## Protocol health

仅在新增公共 CLI、修改错误或取消语义、修改权限或 artifact 规则、线上事故，或多个 ticket 反复出现同类遗漏时触发。检查实现是否违反协议、协议是否覆盖真实高风险路径、命令字段和状态是否矛盾。结果独立记录为 `protocol_health`，缺口进入 `acceptance_protocol_gaps`，回流 `grilling` / `to-spec`，不得由 review agent 修改协议。

## Smell baseline

Fowler smell 只作为 judgement call，项目明确标准优先，工具已强制的项目跳过。只在当前 diff 造成实际摩擦时报告，并引用具体 hunk。完整清单见 [smell-baseline.md](smell-baseline.md)。

## Severity

- `P0`：需要立即止损、影响广泛且无需特殊输入即可触发的严重故障或数据、安全问题。
- `P1`：风险明确且会阻塞当前交付。
- `P2`：风险明确但影响可控，或应路由为新 ticket。
- `P3`：有明确收益但不影响当前行为的低优先级建议；证据不足的猜测不作为 finding。
