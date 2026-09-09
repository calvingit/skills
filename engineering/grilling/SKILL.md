---
name: grilling
description: Question the user about a plan, decision, or idea until the open choices are settled. Use before implementation, when requirements or design still branch.
---

# Grilling

Interview the user until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that depend on it.

`grilling` investigates facts, maintains the Design Tree, computes the frontier, and runs rounds. The user confirms decisions.

On start, read `domain-modeling` and follow it to discover the applicable `AGENTS.md`, Profile, domain docs, and code facts. Name the **Destination** — the target state and its bounds. Set `DOC_DIR` to `${TMPDIR:-/tmp}/grilling-<UTC timestamp>/` and create it. When another workflow such as `wayfinding` is orchestrating, follow that workflow's write convention instead.

## Session docs

- `decisions.md` is the Design Tree snapshot: confirmed decisions, major rejected options, default assumptions, and still-open questions. Update it at the end of each round.
- `glossary.md` and `adr/NNNN-*.md` record confirmed terms and long-lived decisions that pass the ADR gate. Format and numbering follow `domain-modeling`.
- Create files lazily, and write immediately after the user confirms. Term conflicts, ambiguity, and new concepts that collide with code or a public contract are Design Tree decisions.
- With no project doc directory specified, write everything into the created `DOC_DIR`, not the target repo.
- When the user asks to write into the project, use the path they named or a path already proven in the project. If the Profile configures `domain_glossary` or `adr_root`, use that entry. If unset or `auto`, discover dynamically via `domain-modeling`. Do not require `project-setup` first. Ask only when the write location still cannot be determined.

## Interview

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait for the user's answers before the next round.

A question whose answer depends on another question still open in this round belongs to a later round. Independent questions merge into this round.

Each question states the contract or scope it affects, the main mutually exclusive options, the recommended answer, and why. Finding *facts* is your job, never the user's. When a frontier question needs a fact from the workspace, tools, docs, call chains, or tests, look it up. An unresolved fact only blocks questions that depend on it; ask the rest of the frontier now. The *decisions* are the user's: put each to them and wait.

Format every question like this — keep the numbers, recommendation, and separators:

```markdown
❓ **Q1** - **<question title>**: <body and options>

➡️ <recommended answer and why>

---
**Answer format:** `1A 2B`. To keep a bound, write it in, e.g. `3B (keep: …)`.
```

## Acceptance frontier

For every decision that changes external behaviour, confirm: behaviour, inputs / outputs, success and failure semantics (including cancel, timeout, permissions, and environment), compatibility policy, observable result, and evidence source. Anything unconfirmed stays on the frontier.

When the frontier is empty:

1. Summarise the confirmed acceptance conclusions, observable expected results, and evidence sources in the current conversation. Write `${DOC_DIR}/acceptance-draft.md` only when those conclusions need persistence, cross-session continuation, or handoff. When written, keep only `R`, `AC`, scenarios, expected result, and evidence source; exclude implementation advice, mocks, file paths, and internal call order. Simple discussions that proceed directly within this session do not require the draft.
2. Summarise conclusions, session-doc locations, and any terms or ADRs not yet in the project. After the user's final confirmation, hand to `to-spec` only when the contract needs to be persisted, shared, or versioned. Otherwise go direct or to `quick-implement`.

## Boundaries

- Do not write product code. Do not create `SPEC.md`, `HLD.md`, delivery tickets, or implementation docs — those are other skills.
- Follow the applicable Profile's `requirement_authority` for requirement facts. In `external-manual` mode, treat user-supplied snapshots as unconfirmed input. Do not invent contents of a requirement source the user cited but you cannot reach; hand gaps that change behaviour, bounds, or acceptance back to the user.
- If a load-bearing path is larger than this session can see, say why and suggest `wayfinding`. If actual behaviour violates expected behaviour defined by an existing authority, stop and suggest `debug`. Talk in the user's language.
