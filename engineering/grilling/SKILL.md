---
name: grilling
description: Resolve branching requirements or design decisions through structured questioning before specification or implementation.
---

## Grilling

Interview the user until you reach a shared understanding.

Map the discussion as a **Design Tree**: every decision branches into the decisions that depend on it.

`grilling` investigates facts, maintains the Design Tree, computes the frontier, and runs rounds. The user confirms decisions.

The goal is not to discover every possible requirement. The goal is to resolve the decisions that would otherwise force later stages to invent behavior, scope, constraints, or acceptance criteria.

On start:

1. Read `domain-modeling` and follow it to discover the applicable `AGENTS.md`, Profile, domain docs, and code facts.
2. Name the **Destination** — the target state and its bounds.
3. When another workflow such as `wayfinding` is orchestrating, follow that workflow's write convention instead.

---

## Design Tree

A Design Tree represents decisions and their dependencies.

Each node should represent a decision that changes one or more of:

- behavior
- scope
- ownership
- permissions
- lifecycle
- state transitions
- external contracts
- compatibility
- acceptance criteria

A child decision should not be explored before its parent decision is settled.

Do not expand branches whose assumptions may still be invalidated.

### Decision types

A Design Tree usually contains several kinds of decisions:

#### Model decisions

Change the meaning or boundary of the system.

Examples:

- entity identity
- ownership
- lifecycle
- state semantics
- responsibility boundaries

Resolve these first.

#### Behavior decisions

Change user-visible workflows.

Examples:

- user actions
- navigation behavior
- available operations
- default behavior

#### Constraint decisions

Define boundaries that implementation must respect.

Examples:

- permissions
- compatibility
- external contracts
- platform limitations

#### Acceptance decisions

Define observable completion criteria.

Examples:

- expected result
- failure behavior
- state after action

Higher-level decisions should be resolved before lower-level details.

---

## Session docs

- `decisions.md` is the Design Tree snapshot:
  - confirmed decisions
  - major rejected options
  - default assumptions
  - still-open questions

  Update it at the end of each round.

- `glossary.md` and `adr/NNNN-*.md` record confirmed terms and long-lived decisions that pass the ADR gate. Format and numbering follow `domain-modeling`.

- Create files lazily, and write immediately after the user confirms.

- Domain issues discovered through `domain-modeling` become Design Tree decisions when they require user confirmation.

- By default, read `task_contract` from `AGENTS.md` to determine `DOC_DIR`.

- If it is unset, lazily create the project-local temporary `.grilling/` directory and use it for session documents. Remind the user once that `project-setup` can configure it.

- When the Profile configures `domain_glossary` or `adr_root`, use those entries for the corresponding long-lived artifacts.

---

## Interview

Work the tree in **rounds**.

The **frontier** is every decision whose prerequisites are already settled:

the questions you can ask now without guessing at answers you have not heard yet.

Ask the whole frontier in one round, then wait for the user's answers before opening the next round.

A question whose answer depends on another unresolved question belongs to a later round.

Independent questions merge into the current round.

---

### Frontier priority

When multiple frontier questions exist, prioritize decisions by impact.

Ask first:

1. decisions that change the behavior model or ownership boundary
2. decisions that affect multiple downstream branches
3. decisions that change permissions or external contracts
4. decisions that change user-visible behavior
5. acceptance details

Do not start with low-impact details when a higher-level decision remains open.

---

### Investigation

Before asking a question:

- resolve available facts yourself using workspace, tools, docs, call chains, or tests
- do not ask the user for information that can be verified
- identify the decision boundary, not just the missing detail

Finding facts is the agent's responsibility.

The user should only decide choices that cannot be determined from available evidence.

An unresolved fact only blocks questions that depend on it.

Ask the remaining frontier questions without unnecessary waiting.

---

### Assumption challenge

Before exploring detailed choices, identify whether the requirement contains a hidden assumption that may no longer hold.

Look for changes to:

- ownership
- permission boundaries
- lifecycle
- state meaning
- source of truth
- responsibility boundaries
- existing invariants

Ask the highest-impact hidden assumption first.

A useful challenge question usually has these properties:

- the requirement appears simple but changes a deeper behavior model
- different answers affect multiple downstream decisions
- the user may not have explicitly considered the consequence

Example:

Instead of asking:

> Can another user send this message?

Challenge the assumption:

> Does this requirement mean that ownership no longer determines message permission?

Do not manufacture challenges.

Only surface assumptions that can materially affect implementation.

---

### Question rules

For each frontier question:

- explain what decision is being made
- explain why it matters
- show the main mutually exclusive directions
- provide the current recommendation or assessment
- wait for the user's decision

Do not present implementation details as user decisions unless they affect:

- external behavior
- contracts
- scope
- permissions
- acceptance

---

### Question format

Use this format for every question.

Adapt the structure to the type of decision.
Do not force every question into A/B/C options.

```markdown
❓ **Q1** - **<decision title>**

<One or two sentences explaining the decision boundary, conflict, or
assumption being challenged.>

**Options** *(when there are genuinely different choices)*

A. <option>
   - <key consequence>

B. <option>
   - <key consequence>

C. <option, only when genuinely different>

**Need confirmation** *(when this is not a choice question)*

<The rule, meaning, or constraint that needs to be confirmed.>

➡️ **Recommend:**
<Optional assessment based on current facts, constraints, and risk.>

---
**Answer format:**

- Choices: `1A 2B`
- Constraints: `3: <constraint>`
- Explanation: provide additional context when needed

```

---

## Avoid premature expansion

Do not explore downstream details before parent decisions are settled.

Example:

Do not ask:

* refund retry count
* refund failure message
* refund timeout behavior

before confirming:

* whether refund is an order state transition
* or an independent refund transaction

Do not expand hypothetical edge cases that do not affect current decisions.

---

## Acceptance frontier

For every decision that changes external behavior, confirm:

* behavior
* state transitions
* inputs / outputs
* success and failure semantics
* permissions
* compatibility policy
* observable result
* evidence source

Anything unconfirmed stays on the frontier.

When the frontier is empty:

1. Summarize the confirmed acceptance conclusions, observable expected results, and evidence sources.

2. Write `${DOC_DIR}/acceptance-draft.md` only when those conclusions need:

   * persistence
   * cross-session continuation
   * handoff

   When written, keep only:

   * requirements
   * acceptance criteria
   * scenarios
   * expected results
   * evidence source

   Exclude:

   * implementation advice
   * mocks
   * file paths
   * internal call order

3. Summarize:

   * decisions
   * session-doc locations
   * terms or ADRs not yet in the project

4. After the user's final confirmation, continue directly with `to-spec` when the contract needs to be persisted, shared, or versioned.

Otherwise continue within the user's authorized scope.

---

## Amendments

When invoked because a later requirement change reopens an earlier decision:

1. Reopen only affected Design Tree branches.
2. Keep unrelated confirmed decisions closed.
3. Re-run acceptance-frontier checks only for behavior and bounds affected by the change.
4. Continue to `to-spec` amendment after the user confirms changed decisions.

Do not restart the entire Design Tree.

---

## Boundaries

* Do not write product code.
* Do not create `SPEC.md`, `HLD.md`, delivery tickets, or implementation docs.
* Follow the applicable Profile's `requirement_authority` for requirement facts.
* In `external-manual` mode, treat user-supplied snapshots as unconfirmed input.
* Do not invent contents of inaccessible requirement sources.
* If a missing fact changes behavior, bounds, or acceptance, return it to the user.
* If a load-bearing path is larger than this session can see, explain why and suggest `wayfinding`.
* If actual behavior violates an existing authority, stop and suggest `debug`.
* Talk in the user's language.
