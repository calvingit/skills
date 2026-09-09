---
name: code-review
description: Read-only review of completed changes along three layers — Contract, Change-surface, and Exploratory — covering acceptance, direct call chains, and out-of-scope risk, then emit a verifiable completion-gate result.
---

# Code Review

Review completed code changes. Decide whether they satisfy the current task's public contract, and keep enough direct call-chain context to catch regressions a line-level diff will miss.

Review is read-only. It does not modify code, Git state, `SPEC.md`, `ACCEPTANCE.md`, HLD, or any other external system.

The three layers are not interchangeable:

```text
Review
├── Contract review       # decides whether the current task can complete
├── Change-surface review # covers the change and its direct call chain
└── Exploratory review    # reports out-of-scope high risk; does not widen the completion gate
```

Contract review pins requirements and acceptance. Change-surface and Exploratory look for reachable regressions this change introduced or enlarged. Classify findings using the Blocking rules below; review must not invent missing acceptance protocol.

## Inputs and scope

Lock these before starting:

- `review_mode`, `review_target`, comparison baseline, and pre-existing edits.
- Current-task `R` / `AC`, `SPEC.md`, and `ACCEPTANCE.md` when it exists. With no separate protocol, use acceptance stated in the user request, ticket, or SPEC. Missing protocol is not itself a blocker.
- Target-repo `AGENTS.md`, project standards, config, related tests, and external bounds.
- Changed files, direct callers, directly called modules, related public types, tests, and config.
- Task-level `HLD.md` when present, applicable D IDs, implementation receipt, simplification receipt, and verification evidence.

Resolve requirement sources in this order: a source the user named, `SPEC.md` cited by the current ticket or execution graph, an issue on the configured tracker, a local spec matching the branch or task name. With no requirement source, mark `no_spec_available`, skip contract-implementation judgement, and do not guess requirements.

Use a task-level HLD only when the user or caller supplied it, or it sits next to the current SPEC. Do not treat repo-level architecture docs as task-level design. With no HLD, mark `not_applicable`.

## Review modes

- **branch / commit**: `git rev-parse` the fixed point, then pin `git diff <fixed-point>...HEAD` and `git log <fixed-point>..HEAD --oneline`. Stop on a bad ref or empty diff.
- **working tree**: baseline is `HEAD`. Review staged and unstaged separately, and record untracked files. Unread untracked files are not coverage.
- **explicit path**: only the paths the user named, and state the limit of not having a full commit range.
- **implementation**: use the implementation flow's baseline, actual scope, execution receipt, and verification evidence. Do not second-guess the caller's declared scope. Return `BLOCKER` when full-scope coverage cannot be proven.

## Order

1. Lock mode, baseline, scope, pre-existing edits, and requirement source.
2. Read target-repo rules, `SPEC.md` / `ACCEPTANCE.md`, HLD, config, tests, and the direct call chain.
3. Run Contract, Change-surface, and Exploratory in that order. If the environment cannot spawn independent reviewers, the current agent still runs them separately.
4. Every finding cites a file, line, branch, `R` / `AC`, acceptance section, or call relation, plus impact, suggestion, and how to verify.
5. Aggregate per [output-contract.md](references/output-contract.md). Do not merge layers or re-rank severity across them. Read [worker.md](references/worker.md) when assigning or acting as a delegated reviewer; it contains worker inputs and prompts.

## Layer checks

Read [references/review-criteria.md](references/review-criteria.md) for the checks in each layer. Keep Contract, Change-surface, and Exploratory results separate. HLD decisions inform Change-surface review without widening scope.

## Blocking rules

| Issue | Current completion gate |
| --- | --- |
| Violates current SPEC, AC, or acceptance protocol | Blocks |
| This change introduced or enlarged a reachable high-risk issue (safety, data loss, permission bypass, process / resource leak) | Blocks |
| Pre-existing out-of-scope high risk | Report separately; recommend a new ticket |
| Correctness issue on the change's direct call chain | Blocks |
| Neighbouring risk that does not affect this behaviour | Report; recommend a new ticket |
| Pure style, refactor suggestions, speculative risk | Does not block |
| Enabled acceptance protocol contradicts itself or cannot cover a high-risk path | `acceptance_protocol_gaps`; hand back to `grilling` / `to-spec` |

Record contradictory existing protocol, inability to cover a real high-risk path, or missing evidence the task declared in `acceptance_protocol_gaps` and hand back to `grilling` / `to-spec`. Without a separate protocol, report only the current-task contract that cannot be judged.

Final completion requires all three layers passing, empty `blocking_findings`, empty `acceptance_protocol_gaps`, empty `unverified_scope`, and every applicable verification command succeeding.

## Protocol health

Protocol health is not a default re-review of every ticket. Trigger it only for a new public CLI, changed error or cancel semantics, changed permission or artifact rules, a production incident, or the same omission repeating across tickets.

When triggered, emit `protocol_health` separately and check:

1. Whether the current implementation violates the protocol.
2. Whether the protocol covers real high-risk paths.
3. Whether commands, fields, states, and failure semantics contradict each other.

Protocol-health issues go only into `acceptance_protocol_gaps` and back to `grilling` / `to-spec`. Review must not edit the protocol.

## Output and bounds

Final output always includes:

- `blocking_findings`
- `non_blocking_findings`
- `acceptance_protocol_gaps`
- `unverified_scope`

Finding fields and Markdown format are defined in [output-contract.md](references/output-contract.md).

Root-cause work goes to `debug`. Whole-repo architecture diagnosis goes to `review-architecture`. Test or build failures go to `verify` / `debug`. Review may suggest a commit. It must not commit, push, edit branches, edit the acceptance protocol, or widen this ticket's completion gate.

When Loop calls this skill, return JSON per the [Runtime capability output contract](../../docs/loop-runtime.md#capability-result). Standalone review keeps a Markdown receipt.
