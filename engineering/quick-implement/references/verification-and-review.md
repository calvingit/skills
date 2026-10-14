# Verification and Review

Follow the shared [close-out roles](../../shared/closeout-roles.md) for dedicated `simplify` → `verify` → `code-review` judgements, independence, and panel rules. This file adds the quick-implement receipt only.

During implementation, the main agent runs this slice's targeted tests and related typechecks. At close-out, prepare the final candidate after any authorized simplification edits, then run the three roles in that order.

## Receipt

```markdown
## Implementation receipt

- Result: completed | blocked | failed | no_change
- SPEC: <path>
- ACCEPTANCE: <path | None>
- HLD: <path | None>
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
