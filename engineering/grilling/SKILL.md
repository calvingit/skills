---
name: grilling
description: Interview the user about a plan, decision, or idea until consequential open choices are settled.
---

# Grilling

Interview the user until you reach a shared understanding. Map the discussion as a **design tree**: every decision branches into the decisions that depend on it. Keep the tree within the agreed goal and scope.

## Interview

Work the tree in **rounds**. The **frontier** contains unresolved decisions whose prerequisites are settled: questions you can ask now without guessing at answers you have not heard yet. Ask the whole frontier in one round, then wait for the user's answers.

Each answered round reshapes the tree: settled decisions unblock dependent questions. Recompute the frontier and ask the next round. A question that depends on an unanswered question belongs to a later round. Reopen only branches affected by new evidence or requirement changes.

Finding facts is your job. Investigate available code, documents, and tools before asking the user. Use native subagents when available and useful. An ongoing investigation blocks only dependent questions; ask the rest of the frontier now. Decisions belong to the user: explain the relevant choices and wait. Do not invent inaccessible source content or silently assume unresolved choices.

## Question format

Number questions and keep each focused on the decision, necessary context, and key consequences. Give a recommendation and its reason when supported. Use meaningful options or ask directly; do not force A/B/C. Accept free-form answers and alternatives.

```markdown
❓ **Q1** — **<decision>**: <essential context and question>

A. <option and key consequence>
B. <option and key consequence>

➡️ <recommendation and main reason>

---

❓ **Q2** — **<decision>**: <direct question>

➡️ <assessment, when useful>

---
**Reply:** `1A; 2: <answer or alternative>`
```

Show the reply shortcut once per round. Keep numbering unique across rounds.

## Session documents

Read `domain-modeling` on entry and apply it throughout the interview. Its domain questions join the same frontier; grilling owns the tree, rounds, and question cadence.

Resolve the session directory from the user's location or the applicable Profile's `task_contract`; otherwise use a task-specific directory under `.grilling/` in the project. Resume existing session records when continuing the same task.

After each round, automatically update `decisions.md` with confirmed decisions, important reasons, observable acceptance, and unresolved questions. As terms or lasting decisions settle, use `domain-modeling` to update the glossary and write ADRs that pass its gate. Reuse established project locations; otherwise use the session directory. Follow its formats without duplicating records or requiring another approval to record confirmed conclusions.

Create `acceptance-draft.md` only when a separate acceptance draft is needed for handoff or reuse; keep it to observable requirements, scenarios, expected results, and evidence sources.

## Finish

The session is done when the frontier is empty: relevant branches have been explored and no consequential choice is silently assumed. Summarize the settled outcome and document locations, and obtain the user's confirmation of shared understanding before handing back to the caller.

If interrupted, preserve unresolved questions alongside confirmed conclusions. This skill records the interview; it does not implement code or automatically rewrite downstream artifacts.
