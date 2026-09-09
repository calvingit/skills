---
name: to-tickets
description: Break a confirmed SPEC and optional HLD into tracer-bullet delivery tickets with real blocking edges, or sync the affected graph after an upstream amendment. Do not redo requirements or high-level design, and do not implement code.
---

# To Tickets

Break the confirmed `SPEC.md` and, when present, the task directory's `HLD.md` into claimable **delivery tickets** under sibling `tickets/`. Each ticket is an independently verifiable end-to-end delivery, and each declares the other tickets that actually block it from starting.

SPEC owns the requirement. HLD, when it exists, owns the high-level design several implementations must share.

`to-tickets` sits downstream of `to-spec` and, when applicable, `high-level-design`. It only decomposes delivery. It does not redo decisions, the requirement spec, or high-level design. Wayfinding Map decisions that affect requirements must go through `to-spec` first. Purely technical decisions are absorbed by `high-level-design` after the SPEC is confirmed. Stop and hand back to `to-spec` when there is no SPEC.

Every ticket must cite existing protocol meaning through `covers.requirements` and `covers.spec_acceptance`, for example:

```json
{"covers":{"requirements":["R1"],"spec_acceptance":["AC1"]},"acceptance_criteria":[{"id":"AC1","description":"..."}]}
```

Cite existing acceptance meaning. Derive ticket-specific acceptance criteria from the cited SPEC / AC; do not invent new acceptance semantics. Graph checks must report `R` / `AC` / `D` coverage and ticket coverage. Check scenario coverage only when the task enabled independent acceptance scenarios, and hand back to `to-spec` only when a scenario is missing an expected result.

## Inputs

1. Read the full `SPEC.md`: Destination, requirements, bounds, acceptance, Out of scope, and decision basis. Do not guess scope from headings.
2. If `HLD.md` exists in the same task directory, read the full HLD, D IDs, local implementation space, and migration / integration constraints. If it does not, check whether shared types, Interfaces, state or error semantics, dependency direction, or integration choices still span modules, callers, or implementation tasks. If they do, stop and hand back to `high-level-design`.
3. Investigate the target repo, applicable `AGENTS.md`, domain vocabulary, ADRs, related call chains, and existing task conventions only when those facts would change a ticket's outcome, grain, or dependencies. Do not explore just to split tickets.
4. Ticket titles and delivery descriptions use the project's domain language. Unresolved requirements, public contracts, bounds, or acceptance go back to `grilling` / `to-spec`. High-level technical gaps go back to `high-level-design`. Do not write assumptions as tickets.

SPEC is the final authority for scope, acceptance, and Solution Constraints. HLD, when present, is the final authority for design constraints several implementations share. Tickets are the derived execution graph for claiming and collaboration. On conflict, hand back to the owner of that artifact. Tickets must not silently change upstream meaning.

`to-tickets` does not read or interpret the Profile's `requirement_authority`, an external PRD, or new requirements from chat. Those inputs must already be written and confirmed into the SPEC by `to-spec`. Do not write chat-level technical preferences onto tickets. Design decisions that affect several implementations must enter the HLD first.

## Split rules

Prefer independently verifiable end-to-end delivery:

- Each ticket cuts a narrow but **complete** path through every layer the delivery needs — data, interface, UI, tests, docs when they are load-bearing. A completed slice is demoable or verifiable on its own from the user, caller, or acceptance view, and fits in one fresh context.
- Tests, verification, and necessary local tidy-up belong on the slice. Do not create a "add all the tests" or "final cleanup" ticket with no independent delivery. A blocking edge exists only when a missing prior result would make this ticket start incorrectly. Tickets with no blockers are the first executable set. Do not invent a linear chain for narrative order, and do not keep cycles.

A shared contract lands on the first end-to-end ticket that actually uses it. Later tickets depend on it only when that contract's absence would make them start incorrectly. Do not default to a horizontal "build all the interfaces / enums first" architecture ticket. Preparatory technical-work tickets exist only for real blockers: schema generation, expand-then-contract, compatibility layers.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change — rename a column, retype a shared symbol — whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius, each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains. When even the batches cannot stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket — green is promised only there.

Tickets describe outcomes, not stale file paths, snippets, or step-by-step recipes. When an HLD exists, each ticket cites only the applicable D IDs and derives those decisions as Constraints. Do not copy the full HLD. The only exception is a state machine, schema, or shared type shape the HLD explicitly requires to land — keep only what is necessary and cite the D ID.

## Confirm the split

Before writing, show the user a numbered list of candidate tickets:

1. **Title** — short, outcome-oriented name.
2. **Blocked by** — real prior tickets, or "None — can start immediately".
3. **What it delivers** — the end-to-end behaviour this ticket alone makes verifiable.
4. **Design** — applicable HLD D IDs, or `None`.

Ask whether the grain is right, whether blocking edges only express real gates, and whether any tickets should merge or split. Do not create tickets without that confirmation.

## Sync a SPEC / HLD amendment

When tickets already exist and a SPEC or HLD amendment is confirmed, first confirm `loop` has stopped affected new dispatch and has stopped the affected workers and reclaimed their partial receipts. `to-tickets` does not manage subagents itself. Then compare old / new upstream contracts and the current graph:

- Unaffected tickets keep immutable ID, contract, and current evidence.
- An HLD design-only amendment does not change historical acceptance that still satisfies the SPEC. If done behaviour still matches the requirement but not the new design, keep its requirement evidence and create an explicit correction / migration ticket covering the affected Ds. Supersede only when the original delivery contract is replaced as a whole.
- SPEC amendments follow requirement-contract change. The HLD must not be used to quietly change `R` / `AC`.
- An unstarted `open` ticket may be updated in place by reconciliation when the delivery bound is unchanged. When the bound has changed, mark the old ticket `superseded` and create a replacement. `ready` / `blocked` are dynamic projections, not a writable lifecycle.
- An affected `in_progress` ticket must first be stopped by `loop`, with its partial receipt reclaimed. If implemented changes exist, keep the original ticket and evidence, mark it `superseded`, then create a replacement / correction ticket. In-place update is allowed only when nothing has been implemented and the delivery bound is unchanged.
- A `done` ticket stays `done` when its existing contract and implemented behaviour still fully satisfy the current SPEC. Additional behaviour keeps the original ticket and adds an amendment ticket. When original behaviour must change, replace, or reverse, mark the old ticket `superseded` and create a replacement / correction ticket.
- New end-to-end delivery creates a new ticket. Removed requirements that already have implemented behaviour get an explicit removal / correction ticket. Do not merely delete the old ticket or its evidence.

Upstream contract change must not `reopen` a `done` ticket. `done → open` means SPEC and HLD are unchanged and overall delivery review found the original ticket did not satisfy its original contract. A SPEC or HLD amendment must keep still-valid evidence and express the change with amendment / correction / migration / replacement tickets or necessary `superseded`.

Show the user an impact plan and confirm before `reconcile-batch`. The CLI validates all dependencies, lineage, coverage, and current lifecycle, then recomputes readiness. Any dependency pointing at a `superseded` ticket must be deleted, replaced, or rewired so there is no dangling reference or cycle. If an active worker is still writing the same ticket, stop the sync and hand the lifecycle back to `loop`.

`superseded` is terminal and non-active. It is not on the frontier, does not cover current SPEC acceptance, and is not failure. It keeps the original evidence and records the supersession reason plus nullable replacement lineage.

## Write local tickets

`tickets/*.json` is the only execution graph. `to-tickets` does not write JSON files directly, scan max IDs, or maintain readiness, checkboxes, or evidence. After the user confirms candidates, build a `create-batch` JSON request. Each item supplies a temporary key, title, covers, applicable D IDs, what to build, constraints, ticket-specific acceptance criteria, and real dependencies expressed as temporary keys.

Request shape and amendment examples: `loopx graph create-batch --help`, `loopx graph reconcile-batch --help`. Command input describes the current graph contract. It does not copy the acceptance protocol.

After confirmation:

```bash
loopx graph create-batch <task-dir> --input <request.json>
```

The CLI assigns immutable `T001`-style IDs, resolves in-batch dependencies, writes initial `open` lifecycle / empty execution facts, and returns key / ID / path mapping plus the full graph projection. Ticket-document schema, filename slug, evidence, blockers, current attempt, supersession lineage, and dynamic readiness belong to the graph tool. This skill must not keep a second JSON template.

AC IDs must be unique inside a ticket. Full evidence identity is ticket ID plus local AC ID. Tickets cite the upstream contract through `covers.requirements`, `covers.spec_acceptance`, and `design_decisions` without copying SPEC / HLD prose. An ordinary delivery ticket must cover at least one current `R` or SPEC `AC`. A design-only correction / migration must cite at least one D ID.

After the first graph create, report the CLI-computed frontier, blocked reasons, ID / path mapping, applicable D IDs, and unverified items. Once an execution graph exists, call `loop` whether one ticket or several are active. `quick-implement` is only for a single SPEC / HLD with no graph.

## Handoff

`to-tickets` does not claim a ticket, implement code, or automatically gain authorisation to commit, push, create a branch, or rewrite history.
