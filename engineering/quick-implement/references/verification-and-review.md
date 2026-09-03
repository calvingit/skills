# Verification and Review

## Verification

实现过程中持续运行当前 slice 的定向测试和相关 typecheck。收尾时先运行能直接证明 Acceptance Criteria 的验证，再运行受影响范围的项目既有检查；仓库定义了标准 PR、CI 或 full gate 时默认运行该 gate。完整测试、构建或端到端验证不可用或成本明显不成比例时，记录原因、替代证据、未验证范围和风险。

每条实际命令记录退出码和关键输出。工具运行成功只能证明对应 gate，不自动证明需求完整。

## Review

验证完成后使用 `code-review` 的 `implementation` mode，传入 baseline、既有改动、SPEC、存在时的 HLD、实际已实现范围、简化检查回执和验证证据。审查必须分别输出 Standards、SPEC，以及 HLD 存在时的 HLD 符合性；修复审查发现后重新执行受影响验证和审查。

## Receipt

```markdown
## Implementation receipt

- Result: completed | blocked | failed | no_change
- SPEC: <path>
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

- Standards: pass | 审查发现
- SPEC: pass | 审查发现
- HLD: pass | 审查发现 | not_applicable

### Unverified

- None | <scope, reason, and risk>
```

