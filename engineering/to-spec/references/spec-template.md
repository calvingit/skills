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
- Acceptance Seams name public observations such as an API, UI interaction, or export file. Do not prescribe unit/integration tests, mocks, test paths, service classes, repository methods, or database tables as internal observation points.
- Explicit platform/public-contract constraints retain their authoritative source. Derived module ownership, internal interfaces, types, migration mechanisms, and test strategy belong to HLD.
- For existing SPECs, preserve requirement meaning and stable IDs. Replace `Solution` / `Destination` with Goal / Scope where appropriate, and classify legacy `Solution Constraints`, `Implementation Decisions`, and `Testing Decisions`: upstream requirements stay here; derived design / test strategy is handed to HLD. Do not silently discard confirmed requirements or maintain duplicate authority.
- SPEC contains no implementation plan, task list, execution state, or test implementation recipe.
