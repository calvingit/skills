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

## AC References and Optional Examples

- <Current SPEC R / AC reference, observable expected result and evidence kind; add a titled Example / Scenario only when it clarifies that AC>

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
- Check `R → AC` and whether planned evidence can establish each referenced AC. Apply [behaviour example selection](../SKILL.md#select-behaviour-examples-only-when-useful); a separate protocol does not make Scenarios mandatory. Unconfirmed behavioural choices → Call the Skill tool with "grilling".
- Every Example / Scenario cites at least one current SPEC `R` and `AC`, and names expected result and evidence kind. Keep AC definitions in SPEC; this protocol owns scenario detail and evidence rules, not another editable copy of the same AC. Do not add Scenario IDs or a traceability matrix.
- Include success, failure, cancel, timeout, permission or environment distinctions only when they express confirmed contract behaviour or applicable evidence constraints. Do not invent semantics or expand these categories mechanically.
- Add machine-readable fields and verification commands only when the task explicitly enables an executable protocol; ordinary acceptance does not require them.
- HLD owns shared technical constraints. Tickets own execution. This file does not invent acceptance meaning.
