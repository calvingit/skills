# Ticket format (schema v4)

Each ticket is `tickets/<ID>-<slug>.md`. Scripts write it; people read it and may edit wording in the body. Edits that change the contract make existing evidence stale until `reconcile-batch` (see [amendment](amendment.md)).

A ticket document states the **stable delivery contract** and nothing else. Lifecycle, attempts, evidence, blockers and authority are runtime progress and live in the task's `.loop/state.json` ([runtime state schema](../../shared/runtime-state-schema.json)); no command that advances execution rewrites the ticket.

```markdown
---
schema_version: 4
id: T001
covers:
  requirements:
    - R1
  spec_acceptance:
    - AC1
referenced_design_decisions:
  - D1
dependencies: []
---

# Send and observe a message

## Delivery

The caller can send a message and observe its confirmed result.

## Constraints

- Use the persistence boundary established by D1.

## Delivery Acceptance

- **AC1** — The returned result satisfies SPEC AC1.
```

`supersession` is optional and appears only when the ticket was replaced:

```yaml
supersession:
  reason: "The original delivery boundary was replaced."
  replacement_ticket_id: T004
```

| Schema field | Location |
| --- | --- |
| `schema_version`, `id`, `covers`, `referenced_design_decisions`, `dependencies`, `supersession` | frontmatter |
| `title` | `# ` heading |
| `what_to_build` | `## Delivery` text |
| `constraints` | `## Constraints` list (`- ` items; continuation lines indented two spaces) |
| `delivery_acceptance` | `## Delivery Acceptance` list, `- **AC1** — description` |

No field appears in both places; a body field in frontmatter is rejected as `duplicated_authority`. The three sections are required, in this order, and no other sections are allowed. `ready` / `blocked` are computed, never stored, and `lifecycle` / `execution` are not ticket fields at all — a document carrying them is rejected rather than migrated silently.

Frontmatter is a restricted YAML subset parsed without third-party packages: block mappings and sequences, `[]`, `{}`, `null`, `true`/`false`, integers, double- or single-quoted strings and simple unquoted words. Comments, anchors, tags, block scalars, inline collections with items, tabs and duplicate keys are rejected. Contract updates rewrite only the frontmatter and keep the body bytes unchanged; execution updates rewrite neither.

## Version boundary

v4 is a breaking storage format: a v3 ticket is never read as a v4 contract, and `inspect` reports `unsupported_schema_version` for it. Convert an existing v3 task once, locally:

```bash
python3 <to-tickets-skill>/scripts/create-graph migrate-v3 <task-dir>
```

The conversion keeps ticket IDs, contracts, dependencies and confirmed execution records (phase, attempt, evidence with its recorded attempt, blocker, authority, review) and moves them into `.loop/state.json`. It reports what it cannot confirm instead of inventing progress, refuses to overwrite existing runtime state, and leaves the ticket bodies byte-identical. Finish and archive v2 JSON tasks with the v2 tooling first: v4 stores Markdown tickets only, with no JSON ticket storage, mixed-format graph or legacy entry point. JSON remains the CLI request/response format.
