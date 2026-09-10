# Review Criteria

## Shared

Apply [SKILL.md's Blocking rules](../SKILL.md#blocking-rules) to every layer; this file defines what to inspect, not a second completion gate. Do not emit a generic best-practice list or re-report risk already covered by an existing guard or constraint.

## Contract

Review this ticket's `R` / `AC`, `SPEC.md`, `ACCEPTANCE.md` when it exists, and applicable failure-state constraints. Confirm every task statement has observable evidence, covering risk-related public interfaces, success, failure, cancel, timeout, permissions, scope, data safety, and resource cleanup. When ACCEPTANCE.md exists, inspect Public Interface, Observable Behavior, Acceptance Criteria / Scenarios, Failure and Environment Notes, and Evidence Rules. Check that no unauthorised public behaviour or behaviour beyond the ticket was introduced. Do not infer unstated acceptance conditions. Report a current-task contract that cannot be judged; protocol gaps go back to `grilling` / `to-spec`.

## Change-surface

Expand from changed files to direct callers, directly called modules, public types, serialization / deserialization, config, tests, artifact persistence, and resource lifecycle. Inspect correctness, safety, permissions, data corruption, process leaks, and clear regressions on that chain.

When a task-level HLD exists, check applicable D IDs, module duties, dependency direction, shared types, and error semantics. Do not treat the HLD alone as a reason to widen scope.

## Exploratory

Inspect neighbouring modules and out-of-scope paths without changing this ticket's R / AC, SPEC, or ACCEPTANCE. Distinguish pre-existing risk from reachable high-risk issues this change introduced or enlarged, using the canonical Blocking rules. Use the finding format in [output-contract.md](output-contract.md).

For a triggered protocol-health check, follow [SKILL.md](../SKILL.md#protocol-health). Do not edit the protocol.

## Smell baseline

Fowler smells are judgement calls. A documented repo standard wins. Skip anything tooling already enforces. Report only when this diff causes real friction, and quote the hunk. Full list: [smell-baseline.md](smell-baseline.md).

## Severity

- `P0`: needs immediate stop-the-bleeding; widespread; no special input required; severe failure, data, or safety.
- `P1`: risk is clear and blocks current delivery.
- `P2`: risk is clear but contained, or should route as a new ticket.
- `P3`: clear benefit that does not affect current behaviour. Guesswork without evidence is not a finding.
