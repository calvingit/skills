# Amend an existing SPEC

Use the shared process in [SKILL.md](../SKILL.md), with these amendment rules.

## Scope and identity

`SPEC.md` already exists. Read the full current SPEC and this delta, then update in place. Read or update `ACCEPTANCE.md` only if it already exists or this turn explicitly enables separate acceptance. Keep unaffected `R` / `AC` IDs. Bump an existing protocol version when public behaviour, error or cancel semantics, CLI / JSON / schema / exit codes, permissions, or artifact bounds change. Internal refactors and new tests do not bump.

For an amendment, split the delta into `added` / `changed` / `removed` / `no normative effect`. List affected `R`, `AC`, bounds, Solution Constraints, and testing decisions. When an HLD or tickets already exist, read related Ds, ticket contracts, status, and evidence — report which design and delivery may still hold, need appending, replacement, or reversal. Do not edit downstream artifacts. Keep existing `R` / `AC` IDs; append new IDs for new requirements; keep a traceable note for removals and do not renumber. Unsettled product choices go back to `grilling` on the affected branches only. Directed `wayfinding` only when the requirement is settled but a new technical path is still in fog.

## Acceptance and consistency

An amendment re-evaluates only affected seams. Keep testing decisions that still cover the changed behaviour, and say so in the impact summary. Do not force re-confirmation when testing seams are unaffected. Recheck the applicable full SPEC and ACCEPTANCE, not only the delta.

## Confirm and hand off

Show the requirement delta, spec impact, and possibly affected HLD decisions / tickets first. Update in place after confirmation, then report kept, added, or removed R / AC IDs.

When an HLD exists, `high-level-design` syncs affected Ds first, then `to-tickets` coordinates the graph. If affected tickets are running, ask `loop` to stop related dispatch, stop the affected workers, reclaim their partial receipts, and keep evidence. Do not edit downstream artifacts.
