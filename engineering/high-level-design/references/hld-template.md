# HLD create

Read this file when an HLD is required and the task directory has no `HLD.md`. Do not load it when deciding *whether* an HLD is needed.

## Process

1. Pin the current SPEC, codebase comparison baseline, pre-existing edits, and applicable project constraints.
2. Breadth first, then deep-check 1–3 of the most relevant reference implementations. Record path, symbol, and why they were chosen.
3. Describe the current call chain, ownership, existing Interfaces, shared data shapes, external bounds, and invariants that must hold. Mark Observed / Inferred / Unknown.
4. Find design points that would diverge if downstream implementers decided them separately. Form the target design only for those points. Local implementation stays free.
5. For each design point prefer `Reuse`, then `Extend`. `New` or `Replace` only when the existing structure cannot satisfy the SPEC. Those two must say why Reuse / Extend fails, the migration impact, and the control range.
6. Apply `codebase-design` to load-bearing Module / Interface / Seam points. Compare at most 2–3 real candidates only when evidence cannot lock a single design. Ordinary engineering trade-offs are recommended and decided by this skill.
7. Assign stable `D1`, `D2`… IDs to each normative high-level decision. Mark change kind, the reference implementation, and which SPEC `R` / `AC`, callers, or modules it constrains.
8. Check the HLD against the SPEC, project ADRs, current architecture facts, and its own sections. Create the HLD only after a multi-implementer consistency check, with no untreated conflict or unknown that would change the plan.

## HLD.md

Keep only sections that apply. Do not invent content to fill the template:

```markdown
# <Change title> — High-Level Design

## Authority

- Specification: [SPEC.md](SPEC.md)
- Baseline: <commit or equivalent fixed point>
- Scope: <covered R/AC>
- Unverified: <items or None>

## Current Structure

<Call chains, ownership, Interfaces, and constraints relevant to this design. List 1–3 primary reference implementations with path / symbol.>

## Design Decisions

- **D1** — <design decision several implementations must share>
  - Change: <Reuse | Extend | New | Replace>
  - Reference: <existing path / symbol or None>
  - Covers: <R/AC, Module, or callers>
  - Rationale: <why>
  - Consequences: <what downstream must obey>

## Modules and Ownership

- <Module>: <state, rules, external interaction, or stable bound it owns>

## Shared Contracts

- <shared types, enums, schemas, events, callbacks, Interfaces, error or lifecycle semantics>

## Data and Control Flow

<Only load-bearing cross-module flow.>

## Dependency Direction

- <allowed and forbidden dependency direction>

## Integration and Migration

- <which end-to-end delivery ticket lands the shared design, migration order, compatibility window, and deletion conditions>

## Verification Seams

- <how to verify the high-level design and cross-module behaviour, without copying SPEC Acceptance Criteria>

## Local implementation space

- <local classes, functions, file layout, and algorithms left to implementers>

## Open Questions

- None
```

Do not enumerate every class, file, or method by default. Write a name or signature only when several callers will share it, it carries a real interface contract, or the user / project explicitly constrained it. Do not pre-build an Interface that has no real caller yet.

`New` / `Replace` must explain why the existing reference cannot satisfy the SPEC. Do not introduce a new architecture school, a parallel abstraction system, infrastructure rebuild, or cleanup unrelated to this delivery just for theoretical consistency.

## Done when

- Every design decision that several implementations share has codebase evidence, a change kind, and a stable D ID.
- The plan prefers reuse or extension of what exists. Every `New` / `Replace` has necessity and a migration bound.
- Two implementers who do not share an implementation context would still make the same choice on shared types, Interface semantics, ownership, dependency direction, and integration order from SPEC, HLD, and their own tickets alone.
- Private helpers, local classes, algorithms, and file layout remain in local implementation space.
- Existing architecture problems were not silently expanded into this task's refactor.
- There is no untreated SPEC conflict the user must decide.
