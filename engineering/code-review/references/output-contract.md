# Output Contract

## Finding

每条 finding 至少包含以下字段，并补充位置、影响、建议和验证方式：

```json
{
  "category": "contract_violation",
  "severity": "P1",
  "evidence": "文件、行、分支或调用关系证据",
  "recommended_route": "retry"
}
```

`out_of_scope_risk` 必须使用 `recommended_route: new-ticket`。没有发现时保留空数组或空章节。

## Worker prompts

### Contract

```text
你是 Contract 审查 agent。审查指定 diff 是否满足当前 ticket 的 R/AC、SPEC.md、ACCEPTANCE.md 和失败状态矩阵。
这是只读审查，不得修改工作区、版本控制状态或外部系统。
逐条报告契约缺失、未授权行为、语义错误和证据缺口，并引用具体位置和验收章节。
```

### Change-surface

```text
你是 Change-surface 审查 agent。审查变更文件、直接调用方、直接被调用模块、公开类型、测试和配置。
这是只读审查，不得修改工作区、版本控制状态或外部系统。
只报告本次变更引入或扩大的直接调用链问题；高风险可达问题进入 blocking_findings。
```

### Exploratory

```text
你是 Exploratory 审查 agent。可以检查相邻模块和范围外风险，但不得改变当前完成门或验收协议。
范围外问题使用 category: out_of_scope_risk、severity、evidence 和 recommended_route: new-ticket。
```

## Markdown report

```markdown
- 审查建议：可以提交 / 修复后提交 / 不建议提交
- Review mode：standalone / implementation
- 范围：
- Baseline / pre-existing：
- Spec source：
- Acceptance source：
- HLD source：

## Contract
No 审查发现

## Change-surface
No 审查发现

## Exploratory
No 审查发现

## Findings
- blocking_findings：
- non_blocking_findings：
- acceptance_protocol_gaps：
- unverified_scope：
- protocol_health：not_triggered / pass / gap

## Verification evidence
- 已有证据：
- 未验证项：

## 提交建议
- 是否建议提交：
- 提交前必须完成：
```

各层独立计数，不跨层合并或重新排序。最终完成要求三层通过、没有 blocking findings、没有协议缺口、没有未验证范围，且所有适用验证命令成功。
