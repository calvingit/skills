# SPEC.md template

Create and Amendment use the same requirement structure. Preserve existing R / AC IDs. Keep only applicable sections; do not invent content to fill them.

```markdown
# <Spec title>

## Problem

<What is missing or wrong from the user or caller view, and why it matters.>

## Requirement Authority

- Mode: <repository | integrated | external-manual | auto>
- Source: <confirmed source or supplied snapshot>
- Snapshot boundary: <version, date, or confirmed input boundary>
- Unverified: <items or None>

## Goal

<Observable target state.>

## Scope

<Included behaviours and boundaries.>

## Requirements

1. **R1** — <Actor/caller, required behaviour, and value.>

## Business Constraints

- <Confirmed permissions, defaults, compatibility, business rules or externally mandated constraints, with source.>

## Acceptance Seams

- <Public observation surface, covered R / AC, and expected-result source.>

## Acceptance Criteria

- **AC1** — Covers: R1. <Independently decidable observable result.> Expected source: <authority>.

## Out of Scope

- <Explicit exclusions.>

## Open Questions

- <Unresolved non-blocking question, or None. Blocking requirement choices must be settled before downstream work.>
```

## Writing rules

- Every in-scope R has at least one AC. Preserve the numbered R and bulleted AC syntax above for graph extraction.
- Examples are optional and subordinate to their AC; use [the selection rules below](#behaviour-examples) only when they clarify confirmed behaviour.
- Acceptance Seams name public observations such as an API, UI interaction, or export file. Do not prescribe unit/integration tests, mocks, test paths, service classes, repository methods, or database tables as internal observation points.
- Explicit platform/public-contract constraints retain their authoritative source. Derived module ownership, internal interfaces, types, migration mechanisms, and test strategy belong to SOLUTION.
- For existing SPECs, preserve requirement meaning and stable IDs. Replace `Solution` / `Destination` with Goal / Scope where appropriate, and classify legacy `Solution Constraints`, `Implementation Decisions`, and `Testing Decisions`: upstream requirements stay here; derived design / test strategy is handed to SOLUTION. Do not silently discard confirmed requirements or maintain duplicate authority.
- SPEC contains no implementation plan, task list, execution state, or test implementation recipe.
- Use the existing Goal, Scope, AC and applicable constraint sections for the [Task Contract](../../shared/task-contract.md). Add Decision Boundary, Authority, Recovery or Evidence Rules only for confirmed task-specific restrictions not already covered by a source link. Do not fill them with invented policies, Runtime configuration or duplicate project instructions; omit inapplicable sections.

## Behaviour examples

- Use compact input → outcome Examples for meaningful branches or boundaries; use Given / When / Then Scenarios when state transitions, permissions, authentication or interacting conditions need context. Do not introduce a full BDD workflow.
- Retain only examples that rule out a plausible misreading, express a business boundary or distinct outcome, or make key confirmed behaviour concrete. Omit equivalent inputs, test-category checklists and implementation details; do not expand every AC into Happy / Error / Edge cases.
- Stop when another example would not change an implementation decision. Nest an optional title under its AC, or cite that AC in a separate protocol. Do not introduce Scenario IDs or a traceability matrix.
- If an example requires an unsettled business choice, Call the Skill tool with "grilling" before specifying it. For “delete account”, soft deletion, permanence and recovery are decisions, not details to assume.

For a confirmed rule accepting a coupon iff the eligible amount is at least 100 yuan (two decimal places):

```markdown
- **AC1** — Covers: R1. Accept the coupon when the eligible amount is at least 100 yuan; reject it below 100 yuan. Expected source: <confirmed rule>.
  - Example — Threshold: 99.99 → rejected; 100.00 → accepted.
```
