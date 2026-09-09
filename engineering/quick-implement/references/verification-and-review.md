# Verification and Review

## Verification

实现过程中持续运行当前 slice 的定向测试和相关 typecheck。收尾时收集能直接证明 Acceptance Criteria 的验证，并覆盖受影响范围的项目既有检查。仓库定义了标准 PR、CI 或 full gate 时运行该 gate。项目明确要求的 gate 必须保留。

复用当前代码状态下仍有效的结果。标准 gate 已覆盖的检查不再单独重复。只有后续修改、失败或新风险才重跑对应检查。完整测试、构建或端到端验证不可用或成本明显不成比例时，记录原因、替代证据、未验证范围和风险。

按项目已有入口执行当前范围的验证。每条实际命令记录退出码和关键输出；工具运行成功只能证明对应 gate，不自动证明需求完整。

## Review

验证完成后使用 `code-review` 的 `implementation` mode，传入 baseline、既有改动、SPEC、存在时的 HLD、实际已实现范围、简化检查回执和实际命令执行记录；存在独立 `ACCEPTANCE.md` 时一并传入。审查必须输出 Contract、Change-surface、Exploratory；修复审查发现后重新执行受影响验证与审查。

审查回执沿用 code-review 的 [权威模板](../../code-review/references/output-contract.md)，不维护第二份审查分类。

## Receipt

```markdown
## Implementation receipt

- Result: completed | blocked | failed | no_change
- SPEC: <path>
- ACCEPTANCE: <path | None>
- HLD: <path | None>
- Baseline: <commit or equivalent fixed point>
- Pre-existing changes: <included and excluded paths>

### 已实现改动

- <path>: <observable change>

### Acceptance evidence

- <AC>: passed | not_verified — <command, artifact, or observation>

### Verification

- `<command>` — exit <code> — <key result>

### Simplification

- completed | no_change | blocked

### Review

<填入 code-review 权威回执中的三层结果、阻断发现、协议缺口和未验证范围>

### Unverified

- None | <scope, reason, and risk>
```
