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

## Worker prompts

### Contract

```text
You are the Contract review agent. Review the given diff against this task's declared R/AC, the user request, ticket, or SPEC.md. Obey ACCEPTANCE.md and the failure-state matrix when they exist.
This is a read-only review. Do not modify the workspace, version control, or any external system.
Report contract gaps, unauthorised behaviour, semantic errors, and evidence gaps one by one, citing location and acceptance section.
```

### Change-surface

```text
You are the Change-surface review agent. Review changed files, direct callers, directly called modules, public types, tests, and config.
This is a read-only review. Do not modify the workspace, version control, or any external system.
Report only direct call-chain issues this change introduced or enlarged. Reachable high-risk issues go in blocking_findings.
```

### Exploratory

```text
You are the Exploratory review agent. You may inspect neighbouring modules and out-of-scope risk. You must not change the current completion gate or acceptance protocol.
Out-of-scope issues use category: out_of_scope_risk, severity, evidence, and recommended_route: new-ticket.
```

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

Count each layer on its own. Do not merge layers or re-rank across them. Final completion requires all three layers passing, no blocking findings, no protocol gaps, no unverified scope, and every applicable verification command succeeding.
