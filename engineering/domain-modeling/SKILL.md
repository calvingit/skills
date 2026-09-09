---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when terminology needs to change, or when recording a long-lived architecture decision.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. Merely *reading* existing domain docs for vocabulary is not this skill. This skill is for when you're changing the model, not just consuming it.

## Discover authorities

Do not assume a fixed path or filename. Discover in this order:

1. Glossary, architecture decisions, or project docs the user named.
2. Locations declared by repo-level agent instructions, README, CONTRIBUTING, or architecture docs.
3. An existing glossary, CONTEXT, domain model, or ADR / decision-record layout.
4. Facts proven by current code, public contracts, call chains, and tests.

If the applicable `AGENTS.md` `Engineering Skills Profile` names a glossary or ADR entry, use it first. `auto` or no Profile means keep discovering in the order above. Do not run setup automatically.

If the project has no glossary or ADR convention, do not invent a fixed `docs/**` layout. Prefer the repo's existing structure when a long-lived document is actually needed. If there is still no convention and the location will matter later, ask once where to write. Default shapes live in [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md) and [ADR-FORMAT.md](ADR-FORMAT.md); a project format always wins.

## When to update the glossary

Check code and existing docs first, then update the project's domain vocabulary source when:

- The user or spec uses a word that conflicts with existing terms.
- One word carries several meanings across the session, code, or docs.
- A new concept will enter code names, interface names, task docs, or long-lived specs.
- `grilling`, `to-spec`, `review-architecture`, or `code-review` need a stable domain word for a Module, Seam, or requirement.

Keep implementation out of the glossary. File paths, class names, API paths, field mappings, cache policy, and release steps belong in a task spec, API docs, rules, or an ADR.

Generic programming ideas — timeout, retry, error types, factory — are usually not domain language. Ask: is this unique to this business context, or a generic engineering idea? Only the former enters the model.

## Term format

Each entry says what the thing *is*, not what the code does. Keep it to one or two sentences. When several words name the same concept, pick one canonical term and record the rest as avoided or compatible aliases. Prefer the project's existing format; otherwise:

```markdown
**Visitor** - the other party in a session that the service is helping.
_Avoid_: Customer, Buyer, User
```

## During the session

1. Discover and read current domain docs, related code, task docs, and historical decisions.
2. If the user's language conflicts with existing terms, call it out immediately and offer candidate readings grounded in current facts.
3. Stress-test boundaries with concrete scenarios: roles, states, lifecycle, permissions, failure paths, and cross-module interaction.
4. Update the adopted vocabulary source as soon as a term settles in this round. Don't wait for the session to end. Don't guess a path when the write location is unclear.
5. If code, docs, and the user disagree, list the conflict and the evidence. Do not silently pick a side.

## ADR gate

Offer an ADR only when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful.
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons.

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](ADR-FORMAT.md).

Task-local choices belong in the task / spec. Interface protocols belong in API / contract docs. Coding rules belong in project coding standards.

## ADR content

Follow the project's ADR / decision-record format. With no existing format, keep it small:

```markdown
# <Decision>

<Background, decision, and reason. Usually 1–3 paragraphs.>
```

Add status, considered options, or consequences only when they add lasting value. The value is the decision and why, not the template.

When composed with `grilling`, this skill does not own the Design Tree, frontier, rounds, or question cadence. It finds domain issues that need clarifying or recording, hands them to `grilling` on the same frontier, and writes after the user confirms. Default write location is `grilling`'s session doc directory. When the user asks to write into the project, follow `grilling`'s Profile rules for location.

## Verify

Run only lightweight checks the target repo already has for this doc change — Markdown / lint / link check, or `git diff --check`. Do not invent a stack-specific check that isn't there.
