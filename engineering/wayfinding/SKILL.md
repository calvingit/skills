---
name: wayfinding
description: Plan a chunk of work too large for one agent session as a shared map of decision tickets, and resolve them one at a time until the way to the destination is clear. Do not treat an unreachable requirement source as technical fog.
---

# Wayfinding

A destination can be named, but the way from here to it is still in **fog**, and the decision work will not fit in one session. Wayfinding maps that path. It does not deliver the destination.

By default this skill produces decisions, not deliverables. The destination might be a SPEC, a locked decision, or — when Notes explicitly allow it — a change made in place.

When the user names this flow and the destination is clear, enter directly. When *this* skill suggests switching from other work, state the reason and get confirmation first.

## First entry, resume, destination change

- **First entry**: no `MAP.md` for the current destination. Chart the map: create `MAP.md` and the decision tickets that can already be stated.
- **Resume across sessions**: read the map's low-resolution view, the current frontier tickets, and necessary dependencies. Do not re-run aimless breadth search, re-ask for entry, or overwrite settled ticket answers.
- **Destination change or conflicting user request**: redraw the destination with the user. Mark no-longer-applicable tickets superseded or move them to Out of scope. Keep the rationale. Do not silently reuse old answers.

## Storage and claim

Default to local working docs. If the applicable `Engineering Skills Profile` configures an external issue tracker, read its instructions and use the tracker's native child issues, blocking, and assignment. Missing that config does not block; stay in local mode.

Read the Profile's `requirement_authority` only to classify the question. An unreachable external requirement, a missing requirement increment, or an unconfirmed product bound is a **requirement gap** — hand it to the user or `grilling`. Technical fog is only when the destination already stands and the technical path is still unclear. Wayfinding does not sync an external PRD, and it does not write unverified requirements as decision answers.

Prefer the task directory the user named this turn, then the project's existing task-doc convention. If the location would change project structure and is still unclear, ask. This flow creates only:

```text
MAP.md
decisions/
  01-<decision>.md
  02-<decision>.md
```

`MAP.md` is a low-resolution **index**, not a store. Each decision lives in exactly one place — its `decisions/` file. Decision tickets are logical work units; the Markdown files are the local storage form.

## The map

Keep these headings. Section bodies follow the project's language.

1. **Destination** — what the end of this map looks like. This also fixes scope.
2. **Notes** — project constraints, skills every session should consult, standing preferences for this effort.
3. **Decisions so far** — each resolved ticket's name, relative link, and one-line gist of the answer.
4. **Frontier** — decision tickets whose blockers are resolved and that can be worked now.
5. **Not yet specified** — fog that is still toward the destination but not yet sharp enough to ticket.
6. **Out of scope** — work consciously ruled beyond this destination.

Fog is the dim view of questions you can tell are coming. **Not yet specified** is where that view is written. They are not synonyms.

**Fog or ticket?** The test is whether you can state the question precisely *now* — not whether you can answer it now.

- Ticket when the question is already sharp, even if it is still blocked.
- Not yet specified when you cannot yet phrase it that sharply. Don't pre-slice the fog into ticket-sized pieces.

Out of scope never graduates as the frontier advances, unless the user redraws the destination.

In everything the human reads, refer to a map or ticket by its **name**, never by a bare ID. Include the ID in the name when useful.

## Decision tickets

Each local ticket resolves one decision, or gathers the facts that decision needs. Its Markdown file contains:

1. Question
2. Type
3. Blocked by
4. Status: `open | in-progress | resolved | superseded`
5. Claimed by: `unclaimed | <runtime-id>`; if the runtime has no stable id, `local-session-<UTC timestamp>`
6. Evidence
7. Answer

The local frontier is open, unclaimed tickets whose blockers are all resolved. Claim before any work, then re-read the ticket and the workspace diff. Stop on a concurrent claim, content change, or conflict — do not overwrite another session. On an external tracker, assignment is the claim.

Every ticket is either **HITL** — worked *with* a human who speaks for themselves — or **AFK**, driven by the agent alone. Never stand in for the human on a HITL ticket.

- **Grilling (HITL)**: needs the user's judgement. Use `grilling`'s Design Tree / frontier / round. Domain terms and necessary ADRs stay in sync through the domain-modeling discipline `grilling` orchestrates.
- **Research (AFK)**: can be answered from the project, docs, or read-only external investigation. Parallelise only when the runtime supports it and current authorisation allows; otherwise treat it as an ordinary frontier ticket.
- **Prototype (HITL)**: discussion is not enough; a cheap, authorised analysis prototype is needed so the user can react.
- **Task (HITL or AFK)**: nothing to decide, prototype, or research, but some external prep or human action must happen before a *decision* can be made. A task unblocks a decision. It does not deliver the destination.

Do not disguise an implementation ticket as a decision. The answer resolves the question; it does not include final implementation steps.

## Chart the map

1. Name the destination and fix the scope.
2. Investigate breadth-first: the decision tickets that can be stated now, their blocking edges, and the remaining fog.
3. If the user named this flow and the destination is clear, chart immediately. If *this* skill suggested entering, explain why this session cannot converge and get confirmation.
4. Create `MAP.md` and the tickets that can be stated now. Initial status `open`, claimed by `unclaimed`.
5. Wire blocking edges and compute the frontier.
6. Stop charting. Do not resolve several decision tickets in the same session.

If there is no technical fog after investigation, do not create a map. Suggest `grilling` when decisions can converge directly. If the requirement is already clear, go to the work the user actually wants.

## Work through the map

Never resolve more than one decision ticket per session.

1. Load the map's low-resolution view, then the chosen frontier ticket and necessary dependencies. Do not load the full history. Zoom related or closed tickets on demand.
2. Claim first, then re-read files and the workspace diff. Stop on concurrent claim, edits, or conflict; keep both sides and hand back to the user.
3. Resolve by type. A Grilling ticket asks the current local frontier in one round.
4. Inside one Grilling ticket, after the user answers a round, do not ask whether to continue. Record the round, recompute the local frontier, and if questions remain, recommend and ask the next round.
5. Pause only to wait for answers already asked, when the ticket is done, when blocked, or for a closing handoff. "Should I continue?" is not a pause point.
6. When the ticket is done, write evidence and the answer, set status `resolved`. If it sits past the destination, set `superseded`.
7. Append a relative link and one-line gist to Decisions so far, and drop the ticket from Frontier.
8. Create newly well-defined tickets and clear the matching entries from Not yet specified.
9. Recompute the frontier. Move anything past the destination to Out of scope. If the frontier is not empty, recommend the next ticket that is ready to claim in the report — do not start it in this session.

`MAP.md` and `decisions/` may update incrementally before the map is done. Do not create or edit downstream `SPEC.md`, `HLD.md`, or delivery tickets.

## Exit

Leave when:

- The current frontier is empty.
- Every decision ticket is resolved or superseded, with no active claim.
- Not yet specified holds no fog still pointing at the destination.
- Every blocking decision has a traceable answer.

Then summarise, get the user's final confirmation, and choose the exit from the destination: `to-spec` when a build contract is needed; a decision handoff when the destination *is* the decision; the matching execution flow when Notes explicitly allow an in-place change. Keep `MAP.md` and `decisions/` as the decision record. They are not implementation notes.
