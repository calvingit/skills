# Verification and Review

## Simplification

Before verification, dispatch a dedicated `simplify` sub-agent in Review mode on
the implemented scope and consume its report. Record `no_change` when it finds no
supported candidate. Apply candidates only when the user explicitly authorized
simplification; otherwise report them. This role is separate from verification
and review. Prepare the final candidate after any authorized edits.

## Verification

During implementation, the main agent runs this slice's targeted tests and related typechecks. At close-out, dispatch a dedicated native `verify` sub-agent, separate from `simplify` and `code-review`, to check every applicable confirmed Acceptance Criterion and the project's existing delivery gates for the affected range, including any required standard PR, CI, or full gate. Pass the baseline, pre-existing edits, confirmed requirements and AC, implemented scope, and local check records. The main agent reads its per-criterion `PASS`, `FAIL`, or `NOT VERIFIED` report before deciding completion.

Reuse results that are still valid on the current code. Do not re-run a check already covered by the standard gate. Re-run only after a later edit, a failure, or a new risk. When a full test, build, or end-to-end check is unavailable or clearly out of proportion, record why, substitute evidence, unverified scope, and risk.

The `verify` sub-agent follows the task's project verification entry, `verification_instructions` when configured, or existing local verification skills/docs/scripts. Setup is not a prerequisite; use existing checks and report any capability gap. Follow documented isolation, evidence and cleanup rules. Record exit code and key output for every command actually run. A tool succeeding proves only that gate. It does not automatically prove the requirement is complete.

## Review

After verification, spawn a dedicated native `code-review` sub-agent, separate from the `simplify` and `verify` sub-agents, against the implemented scope. Consume its actual Markdown report; a main-agent self-check does not satisfy this gate. Pass baseline, pre-existing edits, SPEC, HLD when present, the scope actually implemented, the simplification and verification reports, and the actual command records. Pass a separate `ACCEPTANCE.md` when it exists. Review returns its normal readable Markdown report. After required fixes, re-run affected verification and review in separate sub-agents.

Use one reviewer by default. Only for high-impact changes with unresolved, under-evidenced judgements, or an explicit user request for a panel, may the caller dispatch 2–3 independent reviewers on the same scope and synthesize their findings against the evidence.

Use code-review's [report guidance](../../code-review/references/output-contract.md) and reference or retain its original report; the receipt does not define another review taxonomy.

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
