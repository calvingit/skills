# Ticket format (schema v3)

Each ticket is `tickets/<ID>-<slug>.md`. Scripts write it; people read it and may edit wording in the body. Edits that change the contract make existing evidence stale until `reconcile-batch` (see [amendment](amendment.md)).

```markdown
---
schema_version: 3
id: T001
covers:
  requirements:
    - R1
  spec_acceptance:
    - AC1
referenced_design_decisions:
  - D1
dependencies: []
lifecycle:
  phase: open
execution:
  attempt_sequence: 0
  evidence: {}
  blocker: null
  current_attempt: null
  reopen_context: null
  authority:
    fingerprint: "<sha256>"
    reason: "Confirmed initial delivery split."
supersession: null
---

# Send and observe a message

## Delivery

The caller can send a message and observe its confirmed result.

## Constraints

- Use the persistence boundary established by D1.

## Delivery Acceptance

- **AC1** — The returned result satisfies SPEC AC1.
```

| Schema field | Location |
| --- | --- |
| `schema_version`, `id`, `covers`, `referenced_design_decisions`, `dependencies`, `lifecycle`, `execution`, `supersession` | frontmatter |
| `title` | `# ` heading |
| `what_to_build` | `## Delivery` text |
| `constraints` | `## Constraints` list (`- ` items; continuation lines indented two spaces) |
| `delivery_acceptance` | `## Delivery Acceptance` list, `- **AC1** — description` |

No field appears in both places; a body field in frontmatter is rejected as `duplicated_authority`. The three sections are required, in this order, and no other sections are allowed. `ready` / `blocked` are computed, never stored.

Frontmatter is a restricted YAML subset parsed without third-party packages: block mappings and sequences, `[]`, `{}`, `null`, `true`/`false`, integers, double- or single-quoted strings and simple unquoted words. Comments, anchors, tags, block scalars, inline collections with items, tabs and duplicate keys are rejected. Lifecycle commands rewrite only the frontmatter and keep the body bytes unchanged.

## Version boundary

v3 is a breaking storage format. New tasks use Markdown tickets only. Finish
and archive existing v2 JSON tasks with the v2 tooling before adopting v3.
There is no JSON migration, mixed-format graph, or legacy CLI entry point.
JSON remains the CLI request/response format, not ticket storage.
