# Code Review Worker

Read-only review of the named scope. Do not edit files, commit, push, create a branch, or spawn subagents. By default do not run integration verification; only check evidence that already exists.

## Inputs

Required: `review_mode`, `review_scope`, `user_request`, and this task's declared `R` / `AC`. Read `SPEC.md` and `ACCEPTANCE.md` when they exist. Optional `review_target` defaults to `diff`.

`implementation` also needs baseline, pre-existing edits, SPEC, HLD when present, the current ticket or full execution graph if any, actual scope, implementation receipt, simplification receipt, and verification evidence. Missing required inputs → `BLOCKER`.

## Execution

1. Pin the diff, task docs, and pre-existing-edit range.
2. Read the target repo's guidance, standards, config, and change-related context.
3. The worker runs Contract, Change-surface, and Exploratory. Without an independent reviewer, the current agent still runs the three layers separately, one after another.
4. Classify findings with [SKILL.md's Blocking rules](../SKILL.md#blocking-rules), including contract and evidence gaps. Do not define a separate worker completion gate.
5. The Contract worker receives acceptance from the user request, ticket, or `SPEC.md`, plus `ACCEPTANCE.md` and the failure-state matrix when they exist. The Change-surface worker receives the direct call chain, public types, tests, and config. The Exploratory worker may widen observation, but must tag out-of-scope issues as `out_of_scope_risk`. Check against [review-criteria.md](review-criteria.md) and return the receipt in [output-contract.md](output-contract.md).

Root-cause work goes to `debug`. Whole-repo architecture analysis goes to `review-architecture`. Model self-report, test output, or a receipt cannot replace judging the actual diff.

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
