# Task context and delegation

Read when preparing context, resuming a task, or choosing to delegate. After initial targeted exploration, the main Agent maintains two concise derived notes under `<task-dir>/.loop/context/`:

- `context.md`: task-relevant architecture, existing patterns, constraints, risks, technical observations, and confirmed decision summaries with their SPEC/HLD or code sources.
- `repo-map.md`: relevant modules, call relationships, and useful starting points, not a complete repository index.

Reuse existing knowledge and inspect actual files where needed. Refresh the notes when discoveries or changes affect later work. On resume, compare summaries with current requirements, ticket state, and code before relying on them. Notes are navigation aids, not authority or acceptance evidence; contradictions are resolved against the actual sources. Do not copy complete upstream documents, logs, or repository contents. Keep changed-file accounting in existing attempts, baselines, and actual diffs rather than separate decisions/touched-files registries.

## Choosing an executor

Continue ordinary implementation serially in the main Agent. Use an Explorer for a bounded unknown area, or a Specialist when domain-specific reasoning benefits from isolation. An isolated task need not run concurrently. Final verification and review use separate independent Agents as described in [finalization](delivery-review.md).

Parallel delegation requires an explicit Loop decision supported by no dependency, expected write overlap, unresolved shared design decision, or conflict over mutable resources such as a test database or generated output. Independent tickets can still run serially. If newly discovered overlap invalidates the decision, stop overlapping writes through Runtime and re-plan ownership before continuing. Runtime worktrees isolate files, not unresolved contracts or shared external resources.

Give each delegated Agent its bounded question or ticket, current attempt when applicable, relevant context notes and authoritative requirements, baseline, existing edits, expected change areas, and required evidence. Read relevant notes first, then inspect current files. Return a concise report under the task's `.loop/` or through native results; exploratory conclusions do not silently amend requirements or shared design. Do not create a permanent Agent pool or dispatch one Agent for every ticket.

Record context tags, starting points, executor choice, parallel independence rationale, and native handle associations in existing `.loop/` execution notes. These are execution hints, not ticket JSON fields or another graph. Bind results to their original ticket/attempt or delivery snapshot even if an Agent context handles multiple tickets. Apply [waiting and recovery](wait-recovery.md) to each delegated execution.

## Observing cost

Record actual run start/end and total elapsed time, delegation count, and tickets completed per Agent context in existing execution notes. Record input tokens and dispatch-to-first-tool-call time only when Runtime exposes them; otherwise mark them unavailable. Preserve observations across resume without counting the same execution twice. Compare runs using the same task, baseline, model, and check scope. Fewer delegations alone do not prove faster execution or acceptable quality; no telemetry service, scheduling algorithm, or performance threshold is added.
