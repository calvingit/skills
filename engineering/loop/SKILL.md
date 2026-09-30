---
name: loop
description: Advance a confirmed ticket graph through implementation, evidence inspection, and state transitions using native workers.
---

# Loop

Select work, invoke the responsible skill, inspect its result, and record the resulting task state. The Manager owns these decisions; Runtime owns worker creation, waiting, cancellation, and session continuation. State scripts record graph and delivery facts, never launch agents or interpret reports.

Loop's existing execution contract uses Runtime-native workers for implementation and corrections; the Manager does not edit product code. Final simplification, verification, and review use dedicated workers. If the required native capability is unavailable, report the blocker and leave delivery incomplete. Do not substitute an external Agent CLI.

## Execute

1. Read `python3 <loop-skill>/scripts/frontier <task-dir>`, the current SPEC, applicable ACCEPTANCE/HLD, relevant tickets, and existing execution records. Confirm requirements are current and check any recorded native execution before dispatching replacement work. Missing optional documents add no prerequisites.
2. Resume an in-progress ticket before choosing a ready one. Establish its baseline, pre-existing edits, current attempt, expected change areas, and delivery AC. Use `scripts/record-attempt start` for a new attempt or `retry` for a scoped correction. Read [script inputs](references/script-inputs.md) when writing state.
3. Invoke `implement` through a native worker with the ticket, authoritative inputs, baseline/scope, verification entry, permitted resources, and previous findings. Preserve useful continuity; read [delegation inputs](references/context-and-delegation.md) when needed. Run workers serially unless an explicit parallel decision establishes independent contracts, writes, and mutable resources.
4. Inspect actual changes and the worker's local acceptance evidence for every ticket AC and applicable project gate. `implement` owns development checks; request missing checks or corrections rather than duplicating its test strategy. Per-ticket independent verify/review is optional unless required by the user or project. Record the executor so local checks are not labelled independent verification.
5. Read text/Markdown reports directly and decide whether to complete, correct, block, or route a contract change. Preserve original reports and command evidence under the task's `.loop/`. Do not infer success from silence or a completion claim; scripts cannot judge prose or report independence.
6. Record the decision through `scripts/update-status`. A successful mutation returns the updated graph; continue from it and query again only when it is unclear or stale. Ticket `done` releases dependencies; it does not pass final delivery. Continue until final delivery passes, the user stops work, or progress requires unavailable external input/capability.

## Decide from evidence

Use `verify`'s [verdict definitions](../verify/SKILL.md#verdicts). Preserve findings and their evidence source; other green checks do not override a required failure or evidence gap.

| Result / conflict | Next action |
| --- | --- |
| Observed defect against an unchanged contract | Send the finding to `implement`, record a correction attempt, and recheck affected evidence. Use `reopen` for a completed ticket only when graph rules permit it; otherwise request a corrective ticket. |
| Environment, permission, dependency, or external gap | Record a blocker with its release condition; resume only after confirming release evidence. Do not repeatedly retry an unresolved blocker. |
| Inadequate verification method | Try a sufficient existing read-only method; route required harness work to `verification-setup` or missing repository-test work to `implement`, within caller authority. A gap alone does not prove a product defect. |
| Requirement or shared-design conflict | Return it to the owning upstream skill; do not modify product code to satisfy an unconfirmed or incorrect expectation. |
| Missing or unclear required report | Retrieve or clarify the original result; keep the required stage incomplete. |

Complete a ticket only when every current delivery AC has sufficient local evidence and no required gap or unresolved blocker remains. Final delivery requires `PASS` for every current SPEC AC, independent verification and review for the current candidate, and no required unresolved scope. An explicitly authorised substitution must record authority, executor, and coverage; local checks alone do not satisfy independent gates.

Changes to code, requirements, tests, fixtures, snapshots, verification configuration, graph, or relevant environment require reassessing affected evidence. Do not reuse a report for a candidate it did not establish.

## State and execution boundaries

Resolve `<loop-skill>` to this installed skill directory; scripts use Python 3.10+ and sibling `engineering/shared/`. Query with `scripts/frontier` or `scripts/graph-query`; record attempts with `scripts/record-attempt`; record state/delivery with `scripts/update-status`. `recover` repairs a graph transaction, not an Agent session.

Keep `.loop/` in the task directory next to SPEC and tickets. It contains attempts, reports, command logs, and delivery inputs; it is not project configuration or a place for product code/tests. Use existing source links and brief handoff notes when needed, without mandatory context files, timing ledgers, Agent pools, heartbeat services, or another execution state machine.

A ticket's `allowed_write_scope` records expected change areas, not sandbox permission. Related changes needed to complete the ticket may extend those areas within caller authority; report them for review. Unrelated changes remain outside scope.

Use Runtime's native lifecycle and configured limits. A wait returning without a result does not prove failure or stopped execution. On interruption, preserve partial work and bind reports to their original attempt/candidate. Confirm prior writers and relevant commands have stopped before starting overlapping work; if this cannot be established, report the blocker. Do not invent inactivity thresholds or reconstruct Runtime sessions.

## Requirement changes and final delivery

Before changing shared requirements/design or reconciling tickets, pause dispatch, stop active writers through Runtime, confirm they stopped, preserve partial results, and block affected attempts. Changing graph state alone does not stop a worker.

Route unsettled choices to `grilling`, normative requirements to `to-spec`, shared design to `high-level-design`, and graph-only changes to `to-tickets`. Keep unaffected contracts/evidence and historical done records; changed behaviour needs amendment/correction tickets rather than reopening an old contract.

When `delivery_ready` is true, continue with [finalization](references/delivery-review.md) in the same run. Report completion only when `frontier` shows `delivery_review.state: passed`. Runtime ending does not promise background continuation. Commit or push only when explicitly authorised.
