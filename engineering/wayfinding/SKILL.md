---
name: wayfinding
description: Map cross-session decisions when the destination is known but dependent fog blocks one-session convergence. Not for unclear requirements, standalone research, settled design, or ticketable work.
---

# Wayfinding

A destination can be named, but the way from here to it is still in **fog**, and the decision work will not fit in one session. Wayfinding maps that path. It does not deliver the destination.

By default this skill produces decisions, not deliverables. The destination might be a SPEC, a locked decision, or — when Notes explicitly allow it — a change made in place.

Use wayfinding only when the destination is known, multiple unresolved decisions depend on one another, and ordinary exploration cannot converge in one session. A large task by itself is not enough.

## Relationship with other flows

These labels help choose a flow; they are not Skill tool calls by themselves. Full routing: [workflow policy](../shared/workflow-policy.md).

- Destination known, user decisions still open → `grilling`
- Destination known, dependent decisions will not converge in one session → this skill
- Requirements settled, remaining uncertainty is technical structure → `solution-design`
- Unknown facts need investigation rather than decisions → research
- Decisions resolved, a build contract is needed → `to-spec`

When the user names this flow and the destination is clear, enter directly. When *this* skill suggests switching from other work, state the reason and get confirmation first.

## First entry, resume, destination change

- **First entry**: no `MAP.md` for the current destination → Chart (below).
- **Resume across sessions**: read the map's low-resolution view, the current frontier tickets, and necessary dependencies. Do not re-run aimless breadth search, re-ask for entry, or overwrite settled ticket answers. Then Work (below).
- **Destination change or conflicting user request**: redraw the destination with the user. Mark no-longer-applicable tickets superseded or move them to Out of scope. Keep the rationale. Do not silently reuse old answers.

## Storage and claim

Default to local working docs. Prefer the task directory the user named this turn, then the project's existing task-doc convention.

Read `requirement_authority` via [Profile resolution](../project-setup/references/profile.md#resolve-and-load) only to classify the question. An unreachable external requirement, a missing requirement increment, or an unconfirmed product bound is a **requirement gap** — hand it to the user, or Call the Skill tool with "grilling" when continuing an authorised interview. Technical fog is only when the destination already stands and the technical path is still unclear. Wayfinding does not sync an external PRD, and it does not write unverified requirements as decision answers.

If the location would change project structure and is still unclear, ask. This flow creates only:

```text
MAP.md
decisions/
  01-<decision>.md
  02-<decision>.md
```

`MAP.md` is a low-resolution **index**, not a store. It contains navigation information only: the destination, scope, current state, and links to decisions. Do not store detailed reasoning or evidence in `MAP.md`; decision files own the reasoning and answers. Each decision lives in exactly one place — its `decisions/` file. Decision tickets are logical work units; the Markdown files are the local storage form.

## The map

Keep these headings. Section bodies follow the project's language.

1. **Destination** — what the end of this map looks like. This also fixes scope.
2. **Notes** — project constraints, skills every session should consult, standing preferences for this effort.
3. **Decisions so far** — each resolved ticket's name, relative link, and one-line gist of the answer.
4. **Frontier** — decision tickets whose blockers are resolved and that can be worked now.
5. **Not yet specified** — fog that is still toward the destination but not yet sharp enough to ticket.
6. **Out of scope** — work consciously ruled beyond this destination.

Fog is the dim view of questions you can tell are coming. **Not yet specified** is where that view is written. They are not synonyms.

**Fog or ticket?** Ticket when the question is already sharp, even if still blocked. Not yet specified when you cannot yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces.

Out of scope never graduates as the frontier advances, unless the user redraws the destination.

In everything the human reads, refer to a map or ticket by its **name**, never by a bare ID. Include the ID in the name when useful.

## Decision tickets

Each local ticket resolves one decision, or gathers the facts that decision needs. Its Markdown file contains:

1. Question
2. Type
3. Blocked by
4. Status: `open | in-progress | resolved | superseded`
5. Claimed by: `unclaimed | <actor>`
6. Evidence
7. Answer

The local frontier is open, unclaimed tickets whose blockers are all resolved.

### Claim and re-read (every Chart write and every Work step)

Claim before any work, then re-read the ticket and the workspace diff. If another session has claimed or modified the decision, stop and preserve both sides; do not overwrite another session.

### Ticket types

Every ticket is either **HITL** — worked *with* a human who speaks for themselves — or **AFK**, driven by the agent alone. Never stand in for the human on a HITL ticket.

- **Grilling (HITL)**: needs the user's judgement. Call the Skill tool twice, for "grilling" and "domain-modeling". Grilling owns Design Tree / frontier / round; domain-modeling keeps terms and necessary ADRs in sync.
- **Research (AFK)**: gathers facts from the project, docs, or read-only external investigation to answer the decision.
- **Exploration (HITL or AFK)**: a prototype, spike, benchmark, or technical experiment is needed to produce evidence for the decision.
- **Task (HITL or AFK)**: nothing to decide, explore, or research, but some external prep or human action must happen before a *decision* can be made. A task unblocks a decision. It does not deliver the destination.

Do not disguise an implementation ticket as a decision. The answer resolves the question; it does not include final implementation steps.

## Chart the map

1. Name the destination and fix the scope.
2. Investigate breadth-first: tickets that can be stated now, their blocking edges, and remaining fog.
3. If the user named this flow and the destination is clear, chart immediately. If *this* skill suggested entering, explain why this session cannot converge and get confirmation.
4. Create `MAP.md` and the tickets that can be stated now (`open` / `unclaimed`). Apply claim and re-read before writing.
5. Wire blocking edges and compute the frontier. Stop charting — resolve tickets only in Work.

If there is no technical fog after investigation, do not create a map. When decisions can converge directly, tell the user to run `grilling` (or Call the Skill tool with "grilling" only if this session already authorised that handoff). If the requirement is already clear, go to the work the user actually wants.

## Work through the map

Resolve one decision at a time by default. Continue to the next only when it is a direct consequence of the current answer and introduces no additional uncertainty.

1. Load the map's low-resolution view, then the chosen frontier ticket and necessary dependencies. Do not load the full history. Zoom related or closed tickets on demand.
2. Claim and re-read (above). Stop on concurrent claim, edits, or conflict; keep both sides and hand back to the user.
3. Resolve by type. A Grilling ticket asks the current local frontier in one round. After the user answers, do not ask whether to continue — record the round, recompute the local frontier, and if questions remain, recommend and ask the next round.
4. Pause only to wait for answers already asked, when the ticket is done, when blocked, or for a closing handoff. "Should I continue?" is not a pause point.
5. When done: write evidence and answer; set `resolved` (or `superseded` if past the destination). Append a relative link and one-line gist to Decisions so far; drop from Frontier.
6. Create newly well-defined tickets; clear matching Not yet specified entries. Recompute the frontier; move anything past the destination to Out of scope. Continue only when the next decision is a direct consequence with no added uncertainty; otherwise recommend the next ready ticket in the handoff.

`MAP.md` and `decisions/` may update incrementally before the map is done. Do not create or edit downstream `SPEC.md`, `HLD.md`, or delivery tickets.

## Exit

Leave when the current frontier is empty; every decision ticket is resolved or superseded with no active claim; Not yet specified holds no fog still pointing at the destination; and every blocking decision has a traceable answer.

Then summarise, get the user's final confirmation, and choose the exit from the destination: Call the Skill tool with "to-spec" when a build contract is needed; a decision handoff when the destination *is* the decision; the matching execution flow when Notes explicitly allow an in-place change. Keep `MAP.md` and `decisions/` as the decision record. They are not implementation notes.
