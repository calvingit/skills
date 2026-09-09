---
name: quick-implement
description: Implement, verify, and review a single confirmed scope in one fresh context, under SPEC/HLD constraints when those files exist. No execution graph.
---

# Quick Implement

Finish one confirmed, single-scope goal inside one fresh context. Obey `SPEC.md` and `HLD.md` when they exist in the same directory, and leave evidence that can be checked. The goal contract may live only in the current session.

Quick means no execution graph. It does not mean skipping high-level design checks, investigation, verification, simplification, or review. Task docs define the contract, not a code recipe. Re-investigate the current repo before implementing.

## Entry

Confirm goal, scope, and a decidable result. Read and obey `SPEC.md`, a separate `ACCEPTANCE.md`, or `HLD.md` when they exist. Missing files do not block. Confirm the whole scope can finish reliably in the current context.

- Unclear goal, scope, or result → `grilling` / `wayfinding`. Call `to-spec` only when the requirement needs to be persisted, shared, or versioned.
- No HLD, but shared types, Interfaces, state / error semantics, dependency direction, or integration choices span modules, callers, or implementation tasks → `high-level-design`.
- HLD conflicts, has gaps, or is disproven by code facts → stop. `high-level-design` amends it. Do not silently change a shared contract while implementing.
- Scope needs several execution units, dependencies, or more than one fresh context → `to-tickets`, then `loop`.
- A ticket graph already exists → do not use this skill; use `loop`.

## Investigate and plan

1. Record `HEAD`, staged / unstaged / untracked state, and a baseline. Protect existing edits.
2. Discover repo guidance, coding standards, domain vocabulary, long-lived decisions, related code, call chains, error paths, tests, and config. If applicable `AGENTS.md` has an `Engineering Skills Profile`, treat it as the project entry index; otherwise keep discovering what is already there.
3. Form the smallest implementation for this delivery. Shared contracts the HLD already locked must be obeyed. Apply `codebase-design` or local detailed design only to module internals, private helpers, file layout, and algorithms inside the local implementation space.
4. New facts that would change behaviour, public contracts, permissions, acceptance, or scope → stop and hand back to `grilling` / `wayfinding` / `to-spec`. Technical design several implementations share → `high-level-design`.

## Implementation loop

- For each delivery slice, lock externally observable behaviour and a real production Seam, then write the smallest implementation.
- When the work fits test-first, expected behaviour is independently decidable, and a stable Seam exists, use `tdd`'s red → green vertical-slice loop.
- When TDD does not fit, use the smallest sufficient feedback loop the target repo already has. Do not invent production interfaces for tests.
- Run this slice's targeted tests and related typechecks as you go. Do not leave all feedback until the end.

## Close-out

1. Run `simplify` when the current diff has a clear complexity problem or the user asks; otherwise skip and say so.
2. Run targeted verification and the project's applicable delivery gates per [references/verification-and-review.md](references/verification-and-review.md).
3. Using the same reference, run `code-review` in implementation mode through Contract, Change-surface, and Exploratory, with project standards, SPEC, and applicable HLD as the basis. After review findings are fixed, re-run affected verification and review.
4. Declare done only when every applicable Acceptance Criterion has observable evidence, required verification and review passed, and no unresolved high-risk issue remains.
5. Commit only with explicit user authorisation. Do not push on your own. The commit contains only this task's changes.

## Boundaries

- Do not edit SPEC / HLD to fit the implementation. Requirement or acceptance changes go to `to-spec`; high-level technical design changes go to `high-level-design`.
- Do not create tickets, maintain an execution graph, or schedule other work units.
- Do not re-delegate this whole job to another implementer. Reviewers and other specialised roles still run under their own skills.
- Do not overwrite existing edits. Do not swallow errors.
- Model self-report, a single passing test, or an implementation-detail check is not complete acceptance evidence.
- Do not stuff project rules back into a generic skill.

Output an implementation receipt listing applicable SPEC / ACCEPTANCE / HLD, baseline, pre-existing edits, actual changes, acceptance evidence, verification, simplification when it ran, review result, and unverified items.
