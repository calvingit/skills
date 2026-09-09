# ACCEPTANCE.md template

Create this only when a separately versioned protocol, cross-ticket reusable scenarios, or a complex protocol matrix is needed. Create and Amendment keep the sections this task needs. If a section does not apply, say why. No placeholders.

````markdown
---
protocol_version: 1
status: draft | confirmed | superseded
owner: to-spec
---

# Acceptance Protocol

## Public Interface

- <CLI / HTTP / JSON / schema / exit codes / permission or artifact bounds; else None and why>

## Observable Behavior

- <External behaviour observable without looking at the implementation>

## Acceptance Criteria / Scenarios

- <Acceptance criteria or scenarios; fill only when a separate protocol is needed>

## Failure and Environment Notes

- <Failure, cancel, timeout, permission, and environment constraints; else None>

## Evidence Rules

- <What counts as pass, what must be kept, and what must not be replaced by model self-report>

## Unverified Coverage

- <Unverified paths and why, or None>

## Change History

- v1: <this create or amendment summary>
````

## Writing rules

- `protocol_version` is this task's acceptance revision, starting at 1. Bump when public behaviour, error or cancel semantics, CLI / JSON / schema / exit codes, permissions, or artifact bounds change. Internal refactors and new tests do not bump.
- Before writing, run the bidirectional check `R → AC → scenario → expected result → executable evidence`. Protocol gaps go back to `grilling`. Do not disguise them as implementation tasks.
- Every scenario cites at least one current `R` and `AC`, and names expected result and evidence kind. Machine-readable mapping is required only when an independent scenario protocol is enabled.
- Success, failure, cancel, timeout, permission, and environment paths must be written explicitly.
- HLD owns shared technical constraints. Tickets own execution. This file does not invent acceptance meaning.
