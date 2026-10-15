---
name: quick-implement
description: Implement the caller-selected confirmed scope in the main agent, then delegate simplification, verification, and review. No execution graph.
---

# Quick Implement

Implement the confirmed scope selected by the caller in the main agent. Obey `SPEC.md` and `SOLUTION.md` when they exist in the same directory, and leave evidence that can be checked. The goal contract may live only in the current session.

quick-implement is an implementation entry point, not a workflow coordinator. Respect the caller's selected route even when the confirmed scope contains several independent fixes.

Quick means no execution graph. It does not mean skipping solution-design checks, investigation, verification, simplification, or review. Task docs define the contract, not a code recipe. Re-investigate the current repo before implementing.

## Entry

Resolve the [Task Contract](../shared/task-contract.md): confirmed goal/scope/AC, decision limits and sufficient evidence, with applicable authority/recovery. Read and obey `SPEC.md`, a separate `ACCEPTANCE.md`, or `SOLUTION.md` when they exist. Missing optional files do not block; required shared design still does. Assess context and verification risks, report them when relevant, and implement authorized slices. If the whole scope cannot reliably finish, report remaining work accurately. The caller owns route selection under the [workflow policy](../shared/workflow-policy.md); a route preference or unit count alone is not a hard stop.

Hard stops (do not bypass):

- A ticket graph already exists or active writers may overlap → pause affected writes and report to the caller. Do not bypass graph lifecycle, Runtime writer controls or the Task Contract's stop-write protocol. The caller resolves execution ownership before work resumes; do not launch another execution route yourself.
- Unclear goal/scope/result, missing shared solution design across modules, or a conflict/gap in the recorded design decisions (`SOLUTION.md`) → pause affected operations; follow workflow-policy to `grilling` / `wayfinding` / `to-spec` / `solution-design` as fits. Do not silently change a shared contract while implementing.

Return missing or conflicting contracts to their owner, pausing affected operations; confirmed or unneeded steps are not redone:

- Missing requirement decisions → Call the Skill tool with "grilling" (load-bearing technical fog → "wayfinding").
- Missing or outdated spec → Call the Skill tool with "to-spec".
- Missing shared solution design → Call the Skill tool with "solution-design".

A Graph Workflow recommendation may explain delivery dependencies or context risks, but cannot switch the selected route. Do not call `to-tickets` or `graph-workflow` to take over execution, create tickets, or create a graph. Continue unaffected authorized work and keep incomplete scope visible.

## Investigate and plan

1. Record `HEAD`, staged / unstaged / untracked state, and a baseline. Protect existing edits.
2. Discover repo guidance, coding standards, domain vocabulary, long-lived decisions, related code, call chains, error paths, tests, and config. Read only relevant Profile entries via [Profile resolution](../project-setup/references/profile.md#resolve-and-load); otherwise keep discovering what is already there.
3. Form the smallest implementation for this delivery. Shared contracts the solution design already locked must be obeyed. Call the Skill tool with "codebase-design" (or use local detailed design) only for module internals, private helpers, file layout, and algorithms inside the local implementation space.
   Before implementing, relate each AC to a sufficient project method, prerequisites and coverage limits. Reuse existing guidance; route necessary method/test capability work within authority and keep uncovered criteria visible. No separate evidence-plan file is required.
4. New facts that would change behaviour, public contracts, permissions, acceptance, or scope → stop and Call the Skill tool once for the fitting owner among "grilling", "wayfinding", and "to-spec". Technical design several implementations share → Call the Skill tool with "solution-design".

## Implementation loop

- For each delivery slice, lock externally observable behaviour and a real production Seam, then write the smallest implementation.
- When the work fits test-first, expected behaviour is independently decidable, and a stable Seam exists, Call the Skill tool with "tdd" and follow its red → green → refactor behaviour cycles within implementation.
- When TDD does not fit, use the smallest sufficient feedback loop the target repo already has. Do not invent production interfaces for tests.
- Run this slice's targeted tests and related typechecks as you go. Do not leave all feedback until the end.

## Close-out

Close-out requires three separate independent judgements — simplification review, per-AC verification, and change review — each consumed from its own role's actual report. Worker creation, waiting and context assignment are Runtime mechanics; a dispatched worker existing is not proof its role judgement ran. Follow [close-out and receipt details](references/verification-and-review.md):

1. Dispatch a dedicated native sub-agent that loads `simplify` (Call the Skill tool with "simplify", or pass its resolved `SKILL.md`) in Review mode and consume its findings.
2. Dispatch a separate native `verify` sub-agent the same way (Call the Skill tool with "verify", or pass its resolved `SKILL.md`) for every applicable AC and project gate.
3. Dispatch another native `code-review` sub-agent the same way (Call the Skill tool with "code-review", or pass its resolved `SKILL.md`) for the implemented scope; consume
   the actual report and rerun affected independent checks after required fixes.
4. Declare done only with sufficient AC evidence, passed required verification
   and review, and no unresolved high-risk issue. Commit only with explicit
   authorization, containing this task's changes; do not push on your own.

## Boundaries

- Do not edit SPEC or the solution design (`SOLUTION.md`) to fit the implementation. Requirement or acceptance changes → Call the Skill tool with "to-spec"; solution design changes → Call the Skill tool with "solution-design".
- Do not create tickets, maintain an execution graph, or schedule other work units.
- Do not re-delegate this whole job to another implementer. Reviewers and other specialised roles still run under their own skills.
- Do not overwrite existing edits. Do not swallow errors.
- Model self-report, a single passing test, or an implementation-detail check is not complete acceptance evidence.
- Do not stuff project rules back into a generic skill.

Output an implementation receipt listing applicable SPEC / ACCEPTANCE / SOLUTION, baseline, pre-existing edits, actual changes, acceptance evidence, verification, simplification when it ran, review result, and unverified items.
