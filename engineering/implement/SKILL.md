---
name: implement
description: "Implement one ticket's delivery behavior within Loop's allowed write scope."
---

# Implement

Implement the current ticket, including necessary simplification of complexity this change creates or makes obsolete. Modify only Loop's allowed write scope and return the implementation result. Do not modify SPEC, ACCEPTANCE, HLD, tickets, or the graph; do not schedule sibling tickets; do not commit version-control changes.

Implement the ticket using the simplest correct final design. Before returning, remove code made obsolete by the change and any unnecessary compatibility, fallback, indirection, duplication, or temporary scaffolding introduced by the implementation. Do not preserve old behavior without a confirmed requirement.

Do not broaden the task into unrelated cleanup; pre-existing complexity beyond this ticket remains the responsibility of `simplify`.

After implementation, return `landed_changes`, `simplification` status, and the capability receipt. Issues found by verify or review are re-injected by Loop as a new attempt.

`implement` does not run or fill in verify's command exit codes, and must not fabricate evidence; verification belongs to `verify`.

CLI capability output follows the [Runtime output contract](../../docs/loop-runtime.md#capability-result). Runtime injects the current role schema with the prompt.
