---
name: to-tickets
description: Break a confirmed SPEC and optional HLD into tracer-bullet delivery tickets with real blocking edges, or sync the affected graph after an upstream amendment. Do not redo requirements or high-level design, and do not implement code.
---

# To Tickets

Break the confirmed `SPEC.md` and, when present, the task directory's `HLD.md` into claimable **delivery tickets** under sibling `tickets/`. Each ticket is an independently verifiable end-to-end delivery, and each declares the other tickets that actually block it from starting.

Wayfinding Map decisions that affect requirements must go through `to-spec` first. Purely technical decisions are absorbed by `high-level-design` after the SPEC is confirmed. Stop and hand back to `to-spec` when there is no SPEC.

Every ticket must cite existing protocol meaning through `covers.requirements` and `covers.spec_acceptance`, for example:

```json
{"covers":{"requirements":["R1"],"spec_acceptance":["AC1"]},"delivery_acceptance":[{"id":"AC1","description":"..."}]}
```

Cite existing acceptance meaning. Derive delivery acceptance targets from the cited SPEC / AC; do not invent new acceptance semantics. Graph checks must report `R` / `AC` / `D` coverage and ticket coverage. Check scenario coverage only when the task enabled independent acceptance scenarios, and hand back to `to-spec` only when a scenario is missing an expected result.

## Modes

- **Create**: follow the inputs, split, validation, and write steps below.
- **Upstream amendment**: before changing an existing graph, read [references/amendment.md](references/amendment.md). Keep the authority and coverage rules here; use reconciliation instead of the initial-create steps.

## Inputs

1. Read the full `SPEC.md`: Goal, requirements, bounds, acceptance, Out of scope, and decision basis. Do not guess scope from headings.
2. If `HLD.md` exists in the same task directory, read the full HLD, D IDs, local implementation space, and migration / integration constraints. If it does not, check [HLD entry conditions](../high-level-design/SKILL.md#when-an-hld-is-required); hand back to `high-level-design` when they hold.
3. Investigate the target repo, applicable `AGENTS.md`, domain vocabulary, ADRs, related call chains, and existing task conventions only when those facts would change a ticket's outcome, grain, or dependencies. Do not explore just to split tickets.
4. Ticket titles and delivery descriptions use the project's domain language. Unresolved requirements, public contracts, bounds, or acceptance go back to `grilling` / `to-spec`. High-level technical gaps go back to `high-level-design`. Do not write assumptions as tickets.

Tickets derive scope and acceptance from SPEC and shared design constraints from HLD. On conflict, return to the source owner; do not change upstream meaning.

Follow [Task Contract inheritance](../shared/task-contract.md#handoff-inheritance-and-change) using the existing ticket fields. A slice may narrow scope/constraints, never grant extra authority or replace an upstream AC. Do not copy a full contract into each ticket or add another state/configuration format. Confirm each slice has an identifiable observation method or a visible capability gap before execution; method details remain in project guidance or the handoff.

`to-tickets` does not read or interpret the Profile's `requirement_authority`, an external PRD, or new requirements from chat. Those inputs must already be written and confirmed into the SPEC by `to-spec`. Do not write chat-level technical preferences onto tickets. Design decisions that affect several implementations must enter the HLD first.

## Split rules

Prefer independently verifiable end-to-end delivery:

- Each ticket cuts a narrow but **complete** path through every layer the delivery needs — data, interface, UI, tests, docs when they are load-bearing. A completed slice is demoable or verifiable on its own from the user, caller, or acceptance view, and is small enough to implement and verify as one coherent unit. Ticket size does not prescribe an Agent lifetime.
- Tests, verification, and necessary local tidy-up belong on the slice. Do not create a "add all the tests" or "final cleanup" ticket with no independent delivery. A blocking edge exists only when a missing prior result would make this ticket start incorrectly. Tickets with no blockers are the first executable set. Do not invent a linear chain for narrative order, and do not keep cycles.

A shared contract lands on the first end-to-end ticket that actually uses it. Later tickets depend on it only when that contract's absence would make them start incorrectly. Do not default to a horizontal "build all the interfaces / enums first" architecture ticket. Preparatory technical-work tickets exist only for real blockers: schema generation, expand-then-contract, compatibility layers.

When a mechanical change cannot land green as independent vertical slices, read [references/wide-refactors.md](references/wide-refactors.md) for the expand–contract exception.

Tickets describe outcomes, not stale file paths, snippets, or step-by-step recipes. When an HLD exists, each ticket cites only the applicable D IDs and derives those decisions as Constraints. Do not copy the full HLD. The only exception is a state machine, schema, or shared type shape the HLD explicitly requires to land — keep only what is necessary and cite the D ID.

## Validate the split

Before writing, form a candidate split and check it against the confirmed SPEC, optional HLD, and real blocking edges:

1. **Title** — short, outcome-oriented name.
2. **Blocked by** — real prior tickets, or "None — can start immediately".
3. **What it delivers** — the end-to-end behaviour this ticket alone makes verifiable.
4. **Design** — applicable HLD D IDs, or `None`.

Choose ordinary ticket grain and blocking edges from the confirmed upstream contracts. Do not require user confirmation for ordinary execution decomposition.

Stop and hand back to the owning upstream skill only when decomposition exposes a product, scope, priority, rollout, compatibility, acceptance, or shared-design choice that the SPEC / HLD does not settle. Do not encode that choice as a ticket assumption.

## Write local tickets

`tickets/*.json` is the only execution graph. `to-tickets` does not write JSON files directly, scan max IDs, or maintain readiness, checkboxes, or evidence. After the split passes the checks above, build a `create-batch` JSON request. Each item supplies a temporary key, title, covers, applicable D IDs, what to build, constraints, delivery acceptance targets, and real dependencies expressed as temporary keys.

Read [script inputs](references/script-inputs.md) for JSON request shapes. Use `python3 <to-tickets-skill>/scripts/create-graph create-batch --help` for the current command input.

Then:

```bash
python3 <to-tickets-skill>/scripts/create-graph create-batch <task-dir> --input <request.json>
```

The CLI assigns immutable `T001`-style IDs, resolves dependencies, initializes `open` lifecycle and empty execution facts, and returns the mapping and full graph. Schema, identity, execution facts and readiness belong to the graph tool; do not keep another JSON template here.

AC IDs must be unique inside a ticket. Full evidence identity is ticket ID plus local AC ID. Tickets cite the upstream contract through `covers.requirements`, `covers.spec_acceptance`, and `referenced_design_decisions` without copying SPEC / HLD prose. An ordinary delivery ticket must cover at least one current `R` or SPEC `AC`. A design-only correction / migration must cite at least one D ID.

After the first graph create, report the CLI-computed frontier, blocked reasons, ID / path mapping, applicable D IDs, and unverified items. Once an execution graph exists, continue directly with `loop` whether one ticket or several are active, but only when the user's current request authorises implementation. For planning-only requests, stop after the required planning artifacts are ready. `quick-implement` is only for a single SPEC / HLD with no graph.

For an upstream amendment, reconcile only tickets affected by the confirmed delta. Preserve unaffected contracts, lifecycle, and still-valid evidence. Do not rebuild the graph from scratch merely because `SPEC.md` or `HLD.md` changed.

## Script boundary

Resolve `<to-tickets-skill>` to this installed skill directory, never to the target project's working directory. Run with Python 3.10+ on macOS/Linux; no global CLI installation is needed. Keep sibling `engineering/shared/` with this skill: it owns [the ticket schema](../shared/ticket-schema.json), graph validation and transactional storage. Scripts do not infer requirements or design from documents; this skill supplies the confirmed candidate split.

- `scripts/create-graph create-batch`: allocate IDs and resolve dependencies; initialize empty execution facts.
- `scripts/create-graph reconcile-batch`: apply an upstream amendment after Loop stops writers.
- `scripts/validate-graph`: read-only schema, dependency, authority and coverage checks.

Use `constraints: []` when a ticket has no specific inherited constraint, rather than adding filler. Keep implementation recipes out of tickets.

## Handoff

`to-tickets` stops at graph creation or reconciliation; Loop owns claiming and execution. Planning inherits the caller's authority under the Task Contract.
