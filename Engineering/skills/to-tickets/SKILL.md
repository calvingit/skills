---
name: to-tickets
description: Break a confirmed SPEC and optional SOLUTION into tracer-bullet tickets with real dependencies, or sync the graph after an upstream amendment. Not for rewriting requirements, SOLUTION, or implementing code.
---

# To Tickets

Break the confirmed `SPEC.md` and, when present, the task directory's `SOLUTION.md` into claimable **delivery tickets** under sibling `tickets/`. Each ticket is an independently verifiable end-to-end delivery, and each declares the other tickets that actually block it from starting.

Wayfinding Map decisions that affect requirements must go through `to-spec` first. Purely technical decisions are absorbed by `solution-design` after the SPEC is confirmed. Stop and Call the Skill tool with "to-spec" when there is no SPEC.

Every ticket derives delivery acceptance from SPEC / AC through `covers.requirements` and `covers.spec_acceptance`; do not invent new acceptance semantics. Graph checks must report `R` / `AC` / `D` coverage and ticket coverage. Check scenario coverage only when the task enabled independent acceptance scenarios, and Call the Skill tool with "to-spec" only when a scenario is missing an expected result.

## Modes

- **Create**: follow the inputs, split, validation, and write steps below.
- **Upstream amendment**: before changing an existing graph, read [references/amendment.md](references/amendment.md). Keep the authority and coverage rules here; use reconciliation instead of the initial-create steps.

## Inputs

1. Read the full `SPEC.md`: Goal, requirements, bounds, acceptance, Out of scope, and decision basis. Do not guess scope from headings.
2. If `SOLUTION.md` exists in the same task directory, read the full SOLUTION, D IDs, local implementation space, and migration / integration constraints. If it does not, check [solution-design entry conditions](../solution-design/SKILL.md#when-a-solution-design-is-required); Call the Skill tool with "solution-design" when they hold.
3. Investigate the target repo, applicable `AGENTS.md`, domain vocabulary, ADRs, related call chains, and existing task conventions only when those facts would change a ticket's outcome, grain, or dependencies. Do not explore just to split tickets.
4. Ticket titles and delivery descriptions use the project's domain language. Unresolved requirements, public contracts, bounds, or acceptance → Call the Skill tool with "grilling", or with "to-spec". High-level technical gaps → Call the Skill tool with "solution-design". Do not write assumptions as tickets.

Tickets derive scope and acceptance from SPEC and shared design constraints from SOLUTION. On conflict, return to the source owner; do not change upstream meaning.

Follow [Task Contract inheritance](../shared/task-contract.md#handoff-inheritance-and-change) using the existing ticket fields. A slice may narrow scope/constraints, never grant extra authority or replace an upstream AC. Do not copy a full contract into each ticket or add another state/configuration format. Confirm each slice has an identifiable observation method or a visible capability gap before execution; method details remain in project guidance or the handoff.

`to-tickets` does not read or interpret the Profile's `requirement_authority`, an external PRD, or new requirements from chat. Those inputs must already be written and confirmed into the SPEC by `to-spec`. Do not write chat-level technical preferences onto tickets. Design decisions that affect several implementations must enter the SOLUTION first.

## Split rules

Prefer independently verifiable end-to-end delivery:

- Each ticket cuts a narrow but **complete** path through every layer the delivery needs — data, interface, UI, tests, docs when they are load-bearing. A completed slice is demoable or verifiable on its own from the user, caller, or acceptance view, and is small enough to implement and verify as one coherent unit. Ticket size does not prescribe an Agent lifetime.
- Tests, verification, and necessary local tidy-up belong on the slice. Do not create a "add all the tests" or "final cleanup" ticket with no independent delivery. A blocking edge exists only when a missing prior result would make this ticket start incorrectly. Tickets with no blockers are the first executable set. Do not invent a linear chain for narrative order, and do not keep cycles.

A shared contract lands on the first end-to-end ticket that actually uses it. Later tickets depend on it only when that contract's absence would make them start incorrectly. Do not default to a horizontal "build all the interfaces / enums first" architecture ticket. Preparatory technical-work tickets exist only for real blockers: schema generation, expand-then-contract, compatibility layers.

When a mechanical change cannot land green as independent vertical slices, read [references/wide-refactors.md](references/wide-refactors.md) for the expand–contract exception.

Tickets describe outcomes, not stale file paths, snippets, or step-by-step recipes. When a SOLUTION exists, each ticket cites only the applicable D IDs and derives those decisions as Constraints. Do not copy the full SOLUTION. The only exception is a state machine, schema, or shared type shape the SOLUTION explicitly requires to land — keep only what is necessary and cite the D ID.

## Validate the split

Before writing, form a candidate split and check it against the confirmed SPEC, optional SOLUTION, and real blocking edges:

1. **Title** — short, outcome-oriented name.
2. **Blocked by** — real prior tickets, or "None — can start immediately".
3. **What it delivers** — the end-to-end behaviour this ticket alone makes verifiable.
4. **Design** — applicable SOLUTION D IDs, or `None`.

Choose ordinary ticket grain and blocking edges from the confirmed upstream contracts. Do not require user confirmation for ordinary execution decomposition.

Stop and Call the Skill tool with the owning upstream skill only when decomposition exposes a product, scope, priority, rollout, compatibility, acceptance, or shared-design choice that the SPEC / SOLUTION does not settle. Do not encode that choice as a ticket assumption.

## Write local tickets

`tickets/*.md` holds **stable delivery contracts**; execution never rewrites them. Lifecycle, attempts, evidence and blockers belong to `graph-workflow` in Git-ignored `.loop/state.json`. Do not hand-write tickets, allocate IDs, or maintain runtime progress here.

After validating the split, read the applicable operation in [script inputs](references/script-inputs.md): `create-batch` for initial creation, `reconcile-batch` for a confirmed amendment after writers stop. Build its JSON request and use the installed skill's command. For initial creation:

```bash
python3 <to-tickets-skill>/scripts/create-graph create-batch <task-dir> --input <request.json>
```

Ticket-local AC IDs must be unique and remain distinct from SPEC AC IDs; evidence identifies both the ticket and its local AC. An ordinary delivery ticket must cover at least one current R or SPEC AC; a design-only correction / migration must cite at least one D ID. Use `constraints: []` when no specific inherited constraint applies.

After the first graph create, report the CLI-computed frontier, blocked reasons, ID / path mapping, applicable D IDs, and unverified items. Once an execution graph exists, continue directly with `graph-workflow` whether one ticket or several are active, but only when the user's current request authorises implementation. For planning-only requests, stop after the required planning artifacts are ready. `quick-implement` is only for a single SPEC / SOLUTION with no graph.

For an upstream amendment, reconcile only tickets affected by the confirmed delta. Preserve unaffected contracts, runtime progress, and still-valid evidence. Do not rebuild the graph from scratch merely because `SPEC.md` or `SOLUTION.md` changed. Reconciliation that changes contracts and runtime entries commits them in one transaction, so a failed reconciliation leaves neither half applied.

## Script boundary

Scripts own schema, IDs, readiness and transactional storage; they do not infer requirements or design. Supply the confirmed split, preserve sibling `shared/`, and resolve commands from the installed skill rather than the target repository. Runtime requirements, read-only validation and legacy conversion are documented in [script inputs](references/script-inputs.md); use migration only for an existing v3 task. Do not maintain a parallel ticket template or state format.

## Handoff

`to-tickets` stops at graph creation or reconciliation; Graph Workflow owns claiming and execution. Planning inherits the caller's authority under the Task Contract.
