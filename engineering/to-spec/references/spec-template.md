# SPEC.md template

Create and Amendment use the same structure. Sections must be concrete. If a section does not apply, say why. No placeholders.

```markdown
# <Spec title>

## Problem Statement

<From the user or caller view: what is missing or wrong, and why it is worth solving.>

## Requirement Authority

- Mode: <repository | integrated | external-manual | auto>
- Source: <in-repo entry, configured integration, or a user-confirmed snapshot. Do not invent links.>
- Snapshot boundary: <requirement version, date, or this-turn input bound this SPEC covers>
- Unverified: <not verified from the original source, or None>

## Solution

<Overall direction of the solution from the user or caller view. Not a step-by-step implementation recipe.>

## Destination

<Observable target state and bounds once every in-scope behaviour is done.>

## User Stories

1. **R1** — As a <domain actor>, I want <behavior>, so that <benefit>.
2. **R2** — ...

## Boundaries and Defaults

- <Input sources, defaults, failure/cancel behaviour, permissions, or compatibility bounds.>

## Solution Constraints

- <Technical and public-contract constraints already fixed by requirement authority, the user, or project rules, which high-level design must not change. None if empty.>

## Testing Decisions

- <Confirmed test seams, covered behaviour, test level, expected-result source, and related prior art.>

## Acceptance Criteria

- **AC1** — Covers: R1. <A result that can be judged without looking at implementation details.> Expected source: <user confirmation, decision, public contract, protocol, worked example, or other authority>.

## Out of Scope

- <Explicitly not part of this delivery.>

## Further Notes

- <Decision basis, relative links, or facts that do not fit above but downstream must keep.>
```

## Writing rules

- User Stories use stable `R1`, `R2`…. This is an exhaustive, independently checkable behaviour list covering every confirmed case of the feature. Each line names actor, behaviour, and value. With no traditional end user, use a real domain role or caller. Do not invent a persona.
- Solution Constraints record only upstream-confirmed technical or public-contract constraints that HLD must not change. They do not record Agent-derived module splits, internal Interfaces, shared types, or dependency direction. A prototype's public state machine, schema, or type shape may be inlined when it is more precise than prose, with the source noted.
- When an old SPEC already has `Implementation Decisions`, split upstream-fixed constraints from derived design first: the former move into Solution Constraints; the latter move into the HLD via `high-level-design` after user confirmation. Until that migration finishes, do not maintain the same decision in both places.
- Testing Decisions must record the confirmed seam, why it was chosen, which external behaviour is observed from it, the independent expected-result source, and existing tests to look at.
- Acceptance Criteria use stable `AC1`, `AC2`… and name the covered `R`. Every in-scope `R` is covered by at least one `AC`. An `AC` verifies external behaviour. It does not lock class names, file layout, internal call order, or an implementation approach unless those *are* the explicit contract.
- When compressing from a Map, decisions that affect requirements or public contracts land in Solution Constraints or Further Notes. Purely technical decisions go to the HLD. Keep relative links or names later sessions can follow.
