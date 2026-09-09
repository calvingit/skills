# Review Criteria

## Shared

Review is read-only: the diff, commits, target-repo rules, requirement source, direct callers and callees, config, and tests. Do not treat a whole-repo issue as this change's problem, and do not emit a generic best-practice list. Blocking findings are only issues this change introduced or enlarged. Pre-existing out-of-scope high risk is listed separately as `non_blocking_findings`. Do not re-report risk already covered by an existing guard or constraint.

## Contract

Review this ticket's `R` / `AC`, `SPEC.md`, `ACCEPTANCE.md` when it exists, and applicable failure-state constraints. Confirm every task statement has observable evidence, covering risk-related public interfaces, success, failure, cancel, timeout, permissions, scope, data safety, and resource cleanup. Contract violations, missing required evidence, or a contradictory existing protocol go in `blocking_findings`. An enabled protocol that cannot cover a real high-risk path goes in `acceptance_protocol_gaps`.

## Change-surface

Expand from changed files to direct callers, directly called modules, public types, serialization / deserialization, config, tests, artifact persistence, and resource lifecycle. Correctness, safety, permissions, data corruption, process leaks, or clear regressions on that direct chain go in `blocking_findings`.

When a task-level HLD exists, check applicable D IDs, module duties, dependency direction, shared types, and error semantics. Do not treat the HLD alone as a reason to widen scope.

## Exploratory

May inspect neighbouring modules and out-of-scope paths. Must not change this ticket's `R` / `AC`, `SPEC.md`, or `ACCEPTANCE.md`. Ordinary out-of-scope issues go in `non_blocking_findings`. When classified `out_of_scope_risk`, they must route to a new ticket:

```json
{
  "category": "out_of_scope_risk",
  "severity": "P2",
  "evidence": "concrete code or reachable-path evidence",
  "recommended_route": "new-ticket"
}
```

If an out-of-scope issue is proven to be introduced or enlarged by this change, reachable, and involves safety, data loss, permission bypass, resource leaks, or other high risk, it also goes in `blocking_findings`. That still does not rewrite the current acceptance protocol.

## Protocol health

Trigger only for a new public CLI, changed error or cancel semantics, changed permission or artifact rules, a production incident, or the same omission repeating across tickets. Check whether the implementation violates the protocol, whether the protocol covers real high-risk paths, and whether command fields and states contradict. Record independently as `protocol_health`. Gaps go in `acceptance_protocol_gaps` and back to `grilling` / `to-spec`. Review must not edit the protocol.

## Smell baseline

Fowler smells are judgement calls. A documented repo standard wins. Skip anything tooling already enforces. Report only when this diff causes real friction, and quote the hunk. Full list: [smell-baseline.md](smell-baseline.md).

## Severity

- `P0`: needs immediate stop-the-bleeding; widespread; no special input required; severe failure, data, or safety.
- `P1`: risk is clear and blocks current delivery.
- `P2`: risk is clear but contained, or should route as a new ticket.
- `P3`: clear benefit that does not affect current behaviour. Guesswork without evidence is not a finding.
