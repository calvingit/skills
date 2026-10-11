---
name: quick-implement
description: Implement a single confirmed scope in the main agent, then delegate simplification, verification, and review. No execution graph.
---

# Quick Implement

Implement one confirmed, single-scope goal in the main agent. Obey `SPEC.md` and `HLD.md` when they exist in the same directory, and leave evidence that can be checked. The goal contract may live only in the current session.

Quick means no execution graph. It does not mean skipping high-level design checks, investigation, verification, simplification, or review. Task docs define the contract, not a code recipe. Re-investigate the current repo before implementing.

## Entry

Resolve the [Task Contract](../shared/task-contract.md): confirmed goal/scope/AC, decision limits and sufficient evidence, with applicable authority/recovery. Read and obey `SPEC.md`, a separate `ACCEPTANCE.md`, or `HLD.md` when they exist. Missing files do not block. Use the [workflow policy](../shared/workflow-policy.md) to assess uncertainty, blast radius and verification difficulty; confirm the whole scope can finish reliably in the current context.

- Unclear goal, scope, or result → `grilling` / `wayfinding`. Call `to-spec` only when the requirement needs to be persisted, shared, or versioned.
- No HLD, but shared types, Interfaces, state / error semantics, dependency direction, or integration choices span modules, callers, or implementation tasks → `high-level-design`.
- HLD conflicts, has gaps, or is disproven by code facts → stop. `high-level-design` amends it. Do not silently change a shared contract while implementing.
- Scope needs several execution units, dependencies, or more than one fresh context → `to-tickets`, then `loop`.
- A ticket graph already exists → do not use this skill; use `loop`.

## Investigate and plan

1. Record `HEAD`, staged / unstaged / untracked state, and a baseline. Protect existing edits.
2. Discover repo guidance, coding standards, domain vocabulary, long-lived decisions, related code, call chains, error paths, tests, and config. Read only relevant entries from the Profile linked by applicable `AGENTS.md` ([resolution](../project-setup/references/profile.md#resolve-and-load)); otherwise keep discovering what is already there.
3. Form the smallest implementation for this delivery. Shared contracts the HLD already locked must be obeyed. Apply `codebase-design` or local detailed design only to module internals, private helpers, file layout, and algorithms inside the local implementation space.
   Before implementing, relate each AC to a sufficient project method, prerequisites and coverage limits. Reuse existing guidance; route necessary method/test capability work within authority and keep uncovered criteria visible. No separate evidence-plan file is required.
4. New facts that would change behaviour, public contracts, permissions, acceptance, or scope → stop and hand back to `grilling` / `wayfinding` / `to-spec`. Technical design several implementations share → `high-level-design`.

## Implementation loop

- For each delivery slice, lock externally observable behaviour and a real production Seam, then write the smallest implementation.
- When the work fits test-first, expected behaviour is independently decidable, and a stable Seam exists, use `tdd`'s red → green → refactor behaviour cycles within implementation.
- When TDD does not fit, use the smallest sufficient feedback loop the target repo already has. Do not invent production interfaces for tests.
- Run this slice's targeted tests and related typechecks as you go. Do not leave all feedback until the end.

## Close-out

Close-out requires three separate independent judgements — simplification review, per-AC verification, and change review — each consumed from its own role's actual report. Worker creation, waiting and context assignment are Runtime mechanics; a dispatched worker existing is not proof its role judgement ran. Follow [close-out and receipt details](references/verification-and-review.md):

1. Use a dedicated `simplify` sub-agent in Review mode and consume its findings.
2. Use a separate native `verify` sub-agent for every applicable AC and project gate.
3. Use another native `code-review` sub-agent for the implemented scope; consume
   the actual report and rerun affected independent checks after required fixes.
4. Declare done only with sufficient AC evidence, passed required verification
   and review, and no unresolved high-risk issue. Commit only with explicit
   authorization, containing this task's changes; do not push on your own.

## Boundaries

- Do not edit SPEC / HLD to fit the implementation. Requirement or acceptance changes go to `to-spec`; high-level technical design changes go to `high-level-design`.
- Do not create tickets, maintain an execution graph, or schedule other work units.
- Do not re-delegate this whole job to another implementer. Reviewers and other specialised roles still run under their own skills.
- Do not overwrite existing edits. Do not swallow errors.
- Model self-report, a single passing test, or an implementation-detail check is not complete acceptance evidence.
- Do not stuff project rules back into a generic skill.

Output an implementation receipt listing applicable SPEC / ACCEPTANCE / HLD, baseline, pre-existing edits, actual changes, acceptance evidence, verification, simplification when it ran, review result, and unverified items.
