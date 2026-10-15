# Delegation inputs

Read when invoking a worker or handing work across contexts. Pass the bounded ticket/question, current attempt or delivery candidate, authoritative source links, baseline, existing edits, expected change areas, resolved verification entry, permitted test resources, and evidence location. Include prior findings for corrections; do not copy all repository docs or prescribe verify's conclusions.

Explicitly name the role Skill. Prefer `Call the Skill tool with "<role>"` when the harness exposes it; otherwise provide the resolved `SKILL.md` path/instructions to the native worker. Dispatch is an explicit assignment within the authorised workflow, not model implicit selection. Confirm the Runtime can load the assigned Skill; a role name alone is not proof of loading. See [Engineering Invocation](../../shared/engineering-invocation.md#三种写法).

Carry relevant decision, authority, evidence and recovery bounds from the [Task Contract](../../shared/task-contract.md#handoff-inheritance-and-change). Keep upstream references and narrower role restrictions distinguishable. A summary or ticket cannot grant operations the caller lacks; missing optional documents do not require a new contract artifact.

Reuse available task knowledge and source links. Write a brief derived note under the task's `.loop/` only when needed for handoff; compare it with current sources on resume. Notes are navigation, not requirements or acceptance evidence. Runtime owns context continuation and compaction; no fixed context-file pair or telemetry ledger is required.

Invoke native implementation workers serially by default: one implementation worker at a time, and preferably the same worker across tickets, with its context refreshed for the new assignment. New contexts are useful for independence or isolation, not automatically for every ticket. Final roles remain separate as specified in [finalization](delivery-review.md).

## Reusing a worker across serial tickets

A reused context still inherits the state of the previous ticket's edits, so restate the assignment before continuing: the current ticket ID and attempt, the contract it must satisfy (delivery text, constraints, delivery AC), its expected change areas, the requirement/design sources, and which changes already exist on disk from earlier tickets. Reload the project's verification entry rather than assuming the previous command still applies.

Reuse changes only how much context the worker carries, never what it owns: each ticket keeps its own scope, attempt number and evidence, and a worker that cannot separate a new ticket's work from the previous one's is a reason to start a new context. If the Runtime cannot continue a worker, dispatch a new one — serial means one worker at a time, not the same session. Do not build a session-continuation mechanism, Agent pool or handoff file to force reuse.

## Parallel safety under an explicit swarm request

Swarm is only used when the user asked for it (see [SKILL.md](../SKILL.md#execution-strategy)). Before dispatching in parallel, establish for each pair from the current ready frontier: no direct delivery dependency, no expected write overlap, no shared mutable resource (build cache, test process, emulator, external service, generated artifacts), and no unresolved shared technical contract or interface. The shared-resource and contract checks are judgement calls a script cannot make; the dependency and write-scope checks are also enforced by `start`.

Confirm the shared-resource position from project facts rather than assuming isolation. Runtime worktrees isolate files, not shared services, caches or ports. If a ticket cannot be shown safe, leave it waiting for another round instead of dispatching everything that is ready. If overlap appears mid-flight, stop the conflicting writes through Runtime and settle ownership before continuing. Record the decision with the existing execution notes.

Bind returned evidence to its ticket/attempt or delivery candidate and original executor. Native results or preserved Markdown suffice; do not create a result parser, permanent Agent pool, lifecycle tracker, or session recovery layer.
