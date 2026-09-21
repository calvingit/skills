# Verification and Review

## Verification

During implementation, keep running this slice's targeted tests and related typechecks. At close-out, collect verification that directly proves Acceptance Criteria, plus the project's existing checks for the affected range. If the repo defines a standard PR, CI, or full gate, run that gate. Gates the project explicitly requires stay.

Reuse results that are still valid on the current code. Do not re-run a check already covered by the standard gate. Re-run only after a later edit, a failure, or a new risk. When a full test, build, or end-to-end check is unavailable or clearly out of proportion, record why, substitute evidence, unverified scope, and risk.

Run verification for the current scope through the project's existing entries. Record exit code and key output for every command actually run. A tool succeeding proves only that gate. It does not automatically prove the requirement is complete.

## Review

After verification, spawn a dedicated `code-review` sub-agent, separate from the `simplify` Review sub-agent, against the implemented scope. Consume its actual Markdown report; a main-agent self-check does not satisfy this gate. Pass baseline, pre-existing edits, SPEC, HLD when present, the scope actually implemented, the simplification receipt, and the actual command records. Pass a separate `ACCEPTANCE.md` when it exists. Review returns its normal readable Markdown report. After review findings are fixed, re-run affected verification and spawn a sub-agent for review again.

The review receipt follows code-review's [report guidance](../../code-review/references/output-contract.md). Do not keep a second review taxonomy.

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

- `<command>` — exit <code> — <key result>

### Simplification

- Mode: Review (dedicated sub-agent)
- Result: completed | no_change | blocked
- Findings and any explicitly authorized changes: <report or None>

### Review

<Paste the conclusion, findings, requirement gaps, unverified scope, and evidence from the canonical Markdown review report>

### Unverified

- None | <scope, reason, and risk>
```
