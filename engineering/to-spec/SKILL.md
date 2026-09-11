---
name: to-spec
description: Turn confirmed requirements, the settled conversation, and codebase facts into a normative SPEC.md. Maintain ACCEPTANCE.md only when the task needs a separate acceptance protocol. Distinguish requirement constraints from high-level technical design, and decide whether downstream work needs an HLD or an execution graph.
---

# To Spec

Write the settled consensus, requirement authority, and codebase facts into the task directory's `SPEC.md`. Create or update `ACCEPTANCE.md` only when the task explicitly needs a separate acceptance protocol, or that file already exists.

Create when there is no SPEC. Amend the same file when an existing SPEC's requirements are added, changed, removed, or clarified. Do not re-interview the whole requirement, split tickets, or implement code.

`SPEC.md` is the workflow's only local requirement snapshot: problem, goal, scope, requirements, business constraints, observable acceptance, and open questions. It does not contain derived high-level design, an execution graph, or an implementation recipe. An external PRD or user input can be upstream requirement authority. It cannot replace a confirmed SPEC as the driver of HLD, tickets, or implementation. Do not publish to an external tracker unless the user asks. Do not create a parallel authority such as `SPEC-v2.md`.

`HLD.md`, when it exists, is the high-level technical design derived from the SPEC and codebase facts. It must not change requirement meaning. Shared design across modules, callers, or implementation tasks belongs to `high-level-design`.

## Entry

Resolve requirement sources in this order: what the user named this turn → the applicable Profile's `requirement_authority` → repo facts → this skill's defaults. `external-manual` may use only the current snapshot the user supplied, and must mark unverified original external content. Do not pretend to have reached Feishu, WeCom, or another system.

Stop and hand back to `grilling` when requirements, external behaviour, business bounds, permissions, public contracts, or acceptance still have open choices that would change the plan.

Stop and hand back to `wayfinding` when the destination can be named but a load-bearing path is still in technical fog and needs investigation across sessions.

When the user supplies a finished `MAP.md`: confirm Frontier is empty, Not yet specified holds no fog still pointing at the destination, and blocking decisions are finally confirmed. Read the map's low-resolution view and the decision files that affect requirements, public contracts, bounds, tests, or acceptance. Purely technical high-level decisions wait for `high-level-design`.

Unsettled module duties, internal Interfaces, shared types, dependency direction, or integration strategy do not block the spec. Record them as design concerns and route to `high-level-design` after the SPEC is confirmed.

Do not invent missing fields, errors, public contracts, acceptance seams, Business Constraints, or expected results. Keep investigating what the codebase can prove. Stop and say so when the user must decide.

## Modes

- **Create**: no `SPEC.md` in the task directory. Follow the process below.
- **Amendment**: an existing SPEC has requirement changes. Before proceeding, read [references/amendment.md](references/amendment.md).
- Ticket granularity, dependencies, or execution facts with unchanged SPEC meaning go to `to-tickets` or the execution owner. Do not touch the SPEC.

## Process

### 1. Gather confirmed context

Collect the conversation, user docs, finished decisions, and requirement authority. Keep only explicit facts, constraints, terms, trade-offs, and Out of scope. Do not grow scope to fill a template.

Task directory: what the user named this turn → the applicable `AGENTS.md` `Engineering Skills Profile` → the repo's existing task-doc convention. Missing Profile does not block. Ask only when write location or requirement meaning is still undetermined.

### 2. Investigate the codebase

If this session has not already looked enough, before writing the SPEC find:

- Applicable `AGENTS.md`, domain glossary, architecture notes, and related ADRs.
- Current external behaviour, related modules and callers, existing public contracts.
- Which existing public surfaces expose similar behaviour and authoritative expected results.
- The user's existing workspace changes, so they are not overwritten or silently absorbed into the spec.

Use the project's domain language. Stop once scope, public contracts, and acceptance bounds are determined. Do not enter high-level design or implementation.

### 3. Decide the acceptance seams

An **Acceptance Seam** is where requirement completion can be observed: a Conversation API response, user UI interaction, or exported file. For each seam, cite the covered R / AC and expected-result source.

Prefer existing public surfaces. Internal services, repository mocks, database tables, test levels, test files, and test implementation recipes belong to HLD / verification, not SPEC. An explicitly required public data artifact is a contract only when its upstream authority says so; do not expose internals merely to test them.

Choose ordinary observation points from confirmed requirements without another approval step. Return to requirement clarification only if a new public contract, acceptance meaning, or scope decision is needed.

### 4. Write SPEC.md, and ACCEPTANCE.md when needed

Once acceptance seams are decided, write from the templates. Read:

- [references/spec-template.md](references/spec-template.md)
- [references/acceptance-template.md](references/acceptance-template.md) only when separate acceptance is enabled.

Without a separate acceptance protocol, check `R → AC` and decidable results before writing. When creating or amending `ACCEPTANCE.md`, run the bidirectional check `R → AC → scenario → expected result → executable evidence`. Protocol gaps go back to `grilling`. Do not disguise them as implementation tasks.

### 5. Consistency

1. Problem, Goal, and Scope describe the same problem and goal.
2. `R` and `AC` IDs are unique and stable; every in-scope `R` is covered by at least one `AC`.
3. Each `AC` can be judged on its own and traces to a confirmed requirement or an authoritative expected source.
4. Every Business Constraint has an upstream basis. Explicit platform or compatibility requirements retain their source; derived architecture belongs to HLD.
5. Acceptance Seams identify observable results and their expected source; test strategy and internal verification seams stay in HLD.
6. Bounds, defaults, Out of Scope, and acceptance do not conflict or silently expand.
7. No placeholders, untreated conflicts, invented facts, or silently skipped blockers.
8. Requirement Authority records source, snapshot bounds, and unverified items as they are.

Fix what confirmed context or the codebase can fix. Stop and hand back to `grilling` or `wayfinding` when a new decision is required.

### 6. Write and hand off

After consistency holds, write into the task directory. Report acceptance seams, business constraints, design concerns, HLD / graph routing, and unverified items.

Do not edit HLD, ticket contract, status, or evidence. Do not maintain tasks, frontier, status, retry, agent assignment, or any other execution graph inside the SPEC.

After the SPEC is confirmed, judge two paths separately. Ticket count is not a substitute for the design judgement:

1. **High-level design**: call `high-level-design` first when shared types, Interfaces, state or error semantics, dependency direction, migration, or integration constraints span modules, callers, or implementation tasks. Otherwise record `hld_not_required` and why.
2. **Execution**: `quick-implement` when the scope is single and needs no execution graph; `to-tickets` then `loop` when several implementation tasks, dependencies, or unified scheduling are needed.

Continue directly into the selected downstream planning skill when its entry conditions are satisfied. Do not stop merely to ask the user to invoke `high-level-design` or `to-tickets`.

Planning handoff does not expand implementation authority. Enter `quick-implement` or `loop` only when the user's current request authorises implementation; otherwise stop after the required planning artifacts are ready.

Stop for a new user decision, missing requirement authority, unresolved load-bearing technical fog, or another action that requires explicit authorisation.

When an HLD is required, it must exist before either execution path. This skill only forecasts whether several implementation tasks are likely. It does not choose ticket count or the split.

No automatic authorisation to publish externally, commit, push, create a branch, or rewrite history.

## Change rules

When new information arrives after downstream work has started, classify the change by authority before editing anything downstream. Resume from the owning artifact instead of restarting the full workflow.

- **Unsettled product / requirement choice** → `grilling` on the affected branch, then Amendment mode.
- **Normative change** to behaviour, bounds, permissions, compatibility, public contracts, or acceptance → Amendment mode here.
- **High-level design change with unchanged SPEC meaning** → do not edit the SPEC. `high-level-design` amends the HLD, then `to-tickets` coordinates the affected graph.
- **Execution split / dependency change with unchanged SPEC / HLD meaning** → `to-tickets` only.
- **Execution-only change** → update ticket execution state/evidence only.

Do not restart unaffected upstream stages or regenerate unaffected artifacts.
