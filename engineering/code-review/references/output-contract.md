# Output Contract

## Finding

Every finding has at least these fields, plus location, impact, suggestion, and how to verify:

```json
{
  "category": "contract_violation",
  "severity": "P1",
  "evidence": "file, line, branch, or call-relation evidence",
  "recommended_route": "retry"
}
```

`out_of_scope_risk` must use `recommended_route: new-ticket`. Keep empty arrays or empty sections when there is nothing to report.

## Markdown report

```markdown
- Review advice: may commit / commit after fixes / do not commit
- Review mode: standalone / implementation
- Scope:
- Baseline / pre-existing:
- Spec source:
- Acceptance source:
- HLD source:

## Contract
No findings

## Change-surface
No findings

## Exploratory
No findings

## Findings
- blocking_findings:
- non_blocking_findings:
- acceptance_protocol_gaps:
- unverified_scope:
- protocol_health: not_triggered / pass / gap

## Verification evidence
- Existing evidence:
- Unverified:

## Commit advice
- Recommend commit:
- Must finish before commit:
```

Count each layer on its own; do not merge layers or re-rank across them. Apply the completion conditions in [SKILL.md](../SKILL.md#blocking-rules).
