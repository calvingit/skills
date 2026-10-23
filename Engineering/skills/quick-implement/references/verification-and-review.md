# Verification and Review

This receipt records the results of [quick-implement closeout](../SKILL.md#close-out). Role execution and independence are defined by [close-out roles](../../shared/closeout-roles.md); the receipt adds no separate gate.

## Receipt

```markdown
## Implementation receipt

- Result: completed | blocked | failed | no_change
- SPEC: <path>
- ACCEPTANCE: <path | None>
- SOLUTION: <path | None>
- Baseline: <commit or equivalent fixed point>
- Pre-existing changes: <included and excluded paths>

### Landed changes

- <path>: <observable change>

### Acceptance evidence

- <AC>: passed | not_verified — <command, artifact, or observation>

### Verification

- <AC>: PASS | FAIL | NOT VERIFIED — <independent observation and coverage limit>
- `<command>` — exit <code> — <key result>

### Simplification

- Mode: Review (dedicated sub-agent)
- Result: completed | no_change | blocked
- Findings and any explicitly authorized changes: <report or None>

### Review

<Original Markdown review report or its retained path, with conclusion and unresolved findings>

### Unverified

- None | <scope, reason, and risk>
```
