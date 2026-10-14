---
name: to-spec
description: Write confirmed requirements and codebase facts into SPEC.md; maintain ACCEPTANCE.md only when a separate acceptance protocol is needed. Not for HLD, tickets, or implementation.
---

# To Spec

Write the settled consensus, requirement authority, and codebase facts into the task directory's `SPEC.md`. Create or update `ACCEPTANCE.md` only when the task explicitly needs a separate acceptance protocol, or that file already exists.

Create when there is no SPEC. Amend the same file when an existing SPEC's requirements are added, changed, removed, or clarified. Do not re-interview the whole requirement, split tickets, or implement code.

`SPEC.md` is the workflow's **engineering requirement snapshot**. It contains:

- problem
- goal
- scope
- behavioural requirements
- business constraints
- external technical constraints
- compatibility constraints
- observable acceptance

Technical constraints are allowed when they define required behaviour, including API contracts, field semantics, protocol limitations, and backend-defined states. `SPEC.md` does not contain classes, modules, internal interfaces, implementation approaches, file changes, derived high-level design, or an execution graph. An external PRD or user input can be upstream requirement authority. It cannot replace a confirmed SPEC as the driver of HLD, tickets, or implementation. Do not publish to an external tracker unless the user asks. Do not create a parallel authority such as `SPEC-v2.md`.

`HLD.md`, when it exists, is the high-level technical design derived from the SPEC and codebase facts. It must not change requirement meaning. Shared design across modules, callers, or implementation tasks belongs to `solution-design`.

## Entry

Resolve requirement sources in this order: what the user named this turn → `requirement_authority` via [Profile resolution](../project-setup/references/profile.md#resolve-and-load) → repo facts → this skill's defaults. `external-manual` may use only the current snapshot the user supplied, and must mark unverified original external content. Do not pretend to have reached Feishu, WeCom, or another system.

Unsettled requirements or technical fog: follow the [workflow policy](../shared/workflow-policy.md) (`grilling` / `wayfinding` as fits).

SPEC-specific stops:

- When the user supplies a finished `MAP.md`: confirm Frontier is empty, Not yet specified holds no fog still pointing at the destination, and blocking decisions are finally confirmed. Read the map's low-resolution view and the decision files that affect requirements, public contracts, bounds, tests, or acceptance. Purely technical high-level decisions wait for `solution-design`.
- Unsettled module duties, internal Interfaces, shared types, dependency direction, or integration strategy do not block the spec. Record them as design concerns and, after the SPEC is confirmed, Call the Skill tool with "solution-design".
- Do not invent missing fields, errors, public contracts, acceptance seams, Business Constraints, or expected results. Keep investigating what the codebase can prove. Stop and say so when the user must decide.

## Modes

- **Create**: no `SPEC.md` in the task directory. Follow the process below.
- **Amendment**: an existing SPEC has requirement changes. Before proceeding, read [references/amendment.md](references/amendment.md).
- Ticket granularity, dependencies, or execution facts with unchanged SPEC meaning → Call the Skill tool with "to-tickets" (or return to the execution owner). Do not touch the SPEC.

## Process

### 1. Gather confirmed context

Collect the conversation, user docs, finished decisions, and requirement authority. Grilling requirement decisions become requirements or constraints; design concerns go to HLD, glossary entries supply terminology, and ADRs supply historical context. Keep explicit facts, constraints, trade-offs and Out of scope without growing the task to fill a template.

Resolve the [Task Contract](../shared/task-contract.md) through these sources. Persist requirement-owned goal, scope, AC and confirmed task boundaries in the existing SPEC sections; link applicable authority and evidence rules instead of creating another contract file or copying project policy. Shared design and concrete verification methods keep their existing owners.

Task directory: what the user named this turn → the applicable linked Profile's `task_contract` → the repo's existing task-doc convention. Missing Profile does not block. Ask only when write location or requirement meaning is still undetermined.

### 2. Investigate the codebase

If this session has not already looked enough, before writing the SPEC find:

- Applicable `AGENTS.md`, domain glossary, architecture notes, and related ADRs.
- Current external behaviour, related modules and callers, existing public contracts.
- Which existing public surfaces expose similar behaviour and authoritative expected results.
- The user's existing workspace changes, so they are not overwritten or silently absorbed into the spec.

Use the project's domain language. Stop once scope, public contracts, and acceptance bounds are determined. Do not enter high-level design or implementation.

### 3. Decide the acceptance seams

An **Acceptance Seam** is where requirement completion can be observed: a user-visible interaction, an external contract response such as an API response, or an exported file. For each seam, cite the covered R / AC and expected-result source.

Prefer existing public surfaces. Internal services, repository mocks, database tables, test levels, test files, repository calls, and test implementation recipes belong to HLD / verification, not SPEC. An explicitly required public data artifact is a contract only when its upstream authority says so; do not expose internals merely to test them.

Choose ordinary observation points from confirmed requirements without another approval step. Return to requirement clarification only if a new public contract, acceptance meaning, or scope decision is needed.

### 4. Write SPEC.md, and ACCEPTANCE.md when needed

Once acceptance seams are decided, write from the templates. Read:

- [references/spec-template.md](references/spec-template.md)
- [references/acceptance-template.md](references/acceptance-template.md) only when separate acceptance is enabled.

Keep `R → AC` traceability and decidable expected results. AC are the sole behavioural acceptance authority; Scenarios / Examples only illustrate them and cannot add business rules. Evidence must support AC directly, with or without examples. A separate protocol records observation and evidence rules without redefining AC.

#### Select behaviour examples only when useful

- Keep an already unambiguous AC without examples. Prefer compact input → outcome Examples for meaningful branches or boundaries; use Given / When / Then Scenarios when state transitions, permissions, authentication or interacting conditions need context. Do not introduce a full BDD workflow.
- Retain an example only if it rules out a plausible misreading, expresses a business boundary or distinct outcome, or makes a key confirmed behaviour concrete. Omit equivalent inputs, test-category checklists and implementation details; do not expand every AC into Happy / Error / Edge cases.
- Stop when rules and key branches are clear and another example would not change an implementation decision. Nest an optional title under its AC, or cite that AC in a separate protocol; do not introduce Scenario IDs or a traceability matrix.
- If different answers would change business behaviour, Call the Skill tool with "grilling" for the unresolved choice before specifying dependent examples. For “delete account”, soft deletion, permanence and recovery are decisions, not details an example may assume. Settled behaviour that only needs concrete expression stays here.

### 5. Consistency

1. Problem, Goal, and Scope describe the same problem and goal.
2. `R` and `AC` IDs are unique and stable; every in-scope `R` is covered by at least one `AC`.
3. Each `AC` can be judged on its own and traces to a confirmed requirement or an authoritative expected source.
4. Every business or external technical constraint has an upstream basis. Explicit API, platform, protocol, backend-state, or compatibility requirements retain their source; derived architecture belongs to HLD.
5. Acceptance Seams identify observable user-visible or external-contract results and their expected source; test strategy and internal verification seams stay in HLD.
6. Bounds, defaults, Out of Scope, and acceptance do not conflict or silently expand.
7. No placeholders, untreated conflicts, invented facts, or silently skipped blockers.
8. Requirement Authority records source, snapshot bounds, and unverified items as they are.

Fix what confirmed context or the codebase can fix. Stop and Call the Skill tool with "grilling", or with "wayfinding", when a new decision is required.

### 6. Write and hand off

After consistency holds, write into the task directory. Report acceptance seams, business constraints, design concerns, HLD / graph routing, and unverified items.

Do not edit HLD, ticket contract, status, or evidence. Do not maintain tasks, frontier, status, retry, agent assignment, or any other execution graph inside the SPEC.

After confirming the SPEC, apply the [workflow policy](../shared/workflow-policy.md).
Use [HLD entry conditions](../solution-design/SKILL.md#when-an-hld-is-required)
to judge shared design independently of execution decomposition. A required HLD
must precede implementation; otherwise report `hld_not_required` with its basis.
Identify known observation methods or gaps without putting test recipes in SPEC.
This skill forecasts whether several execution units are likely, not their count
or split.

When the selected planning skill's entry conditions hold, Call the Skill tool
with that skill name. Call the Skill tool with "quick-implement", or with "graph-workflow",
only when implementation is authorized; otherwise finish with the required planning
artifacts. Missing authority, unsettled requirements or load-bearing feasibility
gaps return to their owner.

## Change rules

Amend here when behaviour, bounds, permissions, compatibility, public contracts
or acceptance change. Resolve unsettled requirement choices by calling the Skill
tool with "grilling" on the affected branch first. Unchanged requirement meaning does not warrant a
SPEC edit; use [contract change ownership](../shared/task-contract.md#handoff-inheritance-and-change)
for design, graph or execution changes and preserve unaffected work. Amendment
mode defines this skill's impact checks and handoff.
