---
name: high-level-design
description: Search the current codebase against a confirmed SPEC and create or amend a task-level HLD.md. Prefer reusing or extending the architecture already there. Lock module duties, shared types, interfaces, and integration constraints that several implementations must share. Not for UI/UX, ticket splitting, or local detailed design.
---

# High-Level Design

Take a confirmed `SPEC.md` and current codebase facts, and form the high-level technical design for one delivery. Default to the smallest increment on the architecture, calling style, and naming already there. Do not treat the task as a greenfield architecture.

`HLD.md` is the final authority for the delivery's shared technical design. Local detailed design includes private methods, helpers, and a single caller's internal callbacks.

## Process

1. Investigate the confirmed SPEC and current codebase.
2. Create design candidates for the shared technical boundaries.
3. Review decision ownership and ask the user about choices that affect long-term direction.
4. Write the confirmed design into `HLD.md`.

## Authority and bounds

- `SPEC.md` owns requirements, external behaviour, acceptance, business bounds, and upstream-confirmed constraints, including technical constraints that define required behaviour.
- `HLD.md` derives module duties, shared types, internal Interfaces, dependency direction, data / control flow, state and error semantics, migration, and integration constraints from the SPEC and codebase facts.
- `tickets/*.json` only derive delivery split and blocking edges. Implementation owns local detailed design the HLD did not constrain.
- The HLD must not change the SPEC. On conflict, stop. `to-spec` fixes the spec, or this skill fixes the design. Do not pick one and keep implementing.
- This skill may apply `codebase-design` to a specific Module / Interface / Seam. It does not copy that skill's general rules.

SPEC technical constraints are inputs. Examples include API field semantics, protocol contracts, and backend-defined states. HLD decides how to satisfy them.

## Design from the codebase that exists

Choose design basis in this order:

1. The user's request and the confirmed SPEC.
2. Applicable `AGENTS.md`, architecture docs, ADRs, and project standards.
3. Stable implementations in the same domain or module.
4. Current production main path, real callers, and composition entry points.
5. Newer similar implementations.
6. General engineering principles.

Existing code is strong evidence, not absolute authority. When several patterns exist, do not vote by count. Pick the reference closest to current ownership, runtime path, and change scope, and record why. Obvious problems that do not block the SPEC are noted as found-and-not-this-task. Do not hijack the task into a refactor.

Investigate in two bounded stages:

- **Breadth**: precise search for related symbols, types, callers, tests, config, composition entry points, and similar behaviour.
- **Depth**: pick 1–3 of the most relevant references and follow the necessary call chains, data / control flow, and how they are verified.

Stop once the evidence is enough to lock design several implementations must share. Do not keep expanding to claim a whole-repo understanding.

## When an HLD is required

Read the full SPEC, applicable agent instructions, architecture / domain docs, ADRs, related code, and call chains first. An HLD is required if any of these hold:

- Several modules, callers, or implementation tasks must share types, enums, schemas, events, error models, or callback conventions.
- A public or cross-module Interface, ownership, dependency direction, or stable Seam must be added or changed.
- Several implementations must obey the same state machine, lifecycle, concurrency, cancel, or call order.
- Expand-then-contract, data migration, a compatibility window, or an explicit integration order is required.
- The user or project rules explicitly require a technical constraint several implementations share.

Ticket count is not the test. A single execution unit may still need an HLD; several independent tickets may not. If none of the conditions hold, report `hld_not_required` and why. Do not create `HLD.md`, and do not load the create template or amendment flow.

Ordinary technical choices are decided from repo evidence. Do not hand them to the user, and do not enter exploration just because an identical existing implementation is missing. Stop and hand back to `grilling` / `to-spec` only when code facts conflict irreconcilably with the SPEC, public behaviour, persisted format, or an explicit architecture constraint, *and* that conflict would change requirement meaning, compatibility policy, permissions, scope, or acceptance. Hand back to `wayfinding` only when a load-bearing technical feasibility is genuinely unknown, limited code investigation or a small check cannot settle it, and the exploration needs to cross sessions.

## Design Review Gate

After investigation and candidate creation, ask the user before selecting among options that affect long-term direction:

- a new public abstraction
- a new domain model
- an API or event contract change
- a data model change
- a permission model change
- a long-term architecture direction
- multiple reasonable long-term designs

For example: `Should reception mode become an extensible abstraction?`

Do not ask about local helper extraction, private methods, file layout, or other implementation details. When the gate is not triggered, choose from repository evidence.

## Modes

- **Create**: an HLD is required and the task directory has no `HLD.md`. Read [references/hld-template.md](references/hld-template.md) and follow its process and template.
- **Amendment**: an HLD exists, and the SPEC, codebase facts, or a confirmed design changed. Read [references/amendment.md](references/amendment.md). Amend the same file. Do not create a parallel version.

When SPEC meaning is unchanged, amend only the affected shared design decisions. Keep unrelated D IDs and design constraints intact; do not restart requirement planning. After the amendment, send only the affected execution impact to `to-tickets`.

## Decision traceability and verification

Every D ID must cite at least one SPEC requirement (R / AC) or an observed codebase fact with path / symbol. Record the decision, reason, and trade-offs. A module name alone is not evidence. Do not create a decision without a traceable basis.

Write confirmed decisions under `## Design Decisions` in `HLD.md` using the exact item shape in [references/hld-template.md](references/hld-template.md). The decision line must use `- **D1** — ...`; do not use `D1:` as the heading form.

Do not create a separate `design-decisions.md`.

HLD owns **Verification Seams**: where technical correctness can be checked, such as a repository integration test or event contract test. Relate each seam to D IDs, technical invariants, and relevant SPEC acceptance; state the check level and expected evidence. SPEC Acceptance Seams remain public observations. `verify` chooses and executes concrete checks against the implementation.

Keep integration order as technical prerequisites, not ticket IDs, assignments, or a task list. HLD defines shared design; tickets derive the execution graph.

## Handoff

Report the HLD path, D IDs, local implementation space, unverified items, and downstream impact:

- No execution graph needed → `quick-implement`.
- Several implementation tasks, blocking edges, or unified scheduling → `to-tickets`.
- An execution graph already exists and the HLD was amended → `to-tickets` syncs affected tickets.

Continue directly into the selected downstream planning skill when its entry conditions are satisfied. Do not stop only to ask the user to invoke the next skill.

Planning handoff does not expand implementation authority. Enter `quick-implement` or `loop` only when the user's current request authorises implementation.

This skill does not split tickets, implement code, or produce UI/UX, visual, or interaction drafts. It does not automatically gain authorisation to commit, push, create a branch, or rewrite history.
