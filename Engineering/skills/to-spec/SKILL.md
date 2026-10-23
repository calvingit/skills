---
name: to-spec
description: Write confirmed requirements and codebase facts into SPEC.md; maintain ACCEPTANCE.md only when a separate acceptance protocol is needed. Delegate required shared design and recommend the next execution route; do not author SOLUTION, tickets, or implementation.
---

# To Spec

Write the settled consensus, requirement authority, and codebase facts into the task directory's `SPEC.md`. Create or update `ACCEPTANCE.md` only when the task explicitly needs a separate acceptance protocol, or that file already exists.

Create when there is no SPEC. Amend the same file when an existing SPEC's requirements are added, changed, removed, or clarified. Do not re-interview the whole requirement, split tickets, or implement code.

`SPEC.md` is the workflow's **engineering requirement snapshot**: problem, goal, scope, behavioural requirements, business / external technical / compatibility constraints, and observable acceptance.

Technical constraints are allowed when they define required behaviour, including API contracts, field semantics, protocol limitations, and backend-defined states. `SPEC.md` does not contain classes, modules, internal interfaces, implementation approaches, file changes, derived solution design, or an execution graph. An external PRD or user input can be upstream requirement authority. It cannot replace a confirmed SPEC as the driver of SOLUTION, tickets, or implementation. Do not publish to an external tracker unless the user asks. Do not create a parallel authority such as `SPEC-v2.md`.

`SOLUTION.md`, when it exists, is the technical solution design derived from the SPEC and codebase facts. It must not change requirement meaning. Shared design across modules, callers, or implementation tasks belongs to `solution-design`.

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

Collect the conversation, user docs, finished decisions, and requirement authority. Grilling requirement decisions become requirements or constraints; design concerns go to SOLUTION, glossary entries supply terminology, and ADRs supply historical context. Keep explicit facts, constraints, trade-offs and Out of scope without growing the task to fill a template.

Resolve the [Task Contract](../shared/task-contract.md) through these sources. Persist requirement-owned goal, scope, AC and confirmed task boundaries in the existing SPEC sections; link applicable authority and evidence rules instead of creating another contract file or copying project policy. Shared design and concrete verification methods keep their existing owners.

Task directory: what the user named this turn → the applicable linked Profile's `task_contract` → the repo's existing task-doc convention. Missing Profile does not block. Ask only when write location or requirement meaning is still undetermined.

### 2. Investigate the codebase

If this session has not already looked enough, before writing the SPEC find:

- Applicable `AGENTS.md`, domain glossary, architecture notes, and related ADRs.
- Current external behaviour, related modules and callers, existing public contracts.
- Which existing public surfaces expose similar behaviour and authoritative expected results.
- The user's existing workspace changes, so they are not overwritten or silently absorbed into the spec.

Use the project's domain language. Stop once scope, public contracts, and acceptance bounds are determined. Do not enter solution design or implementation.

### 3. Decide the acceptance seams

An **Acceptance Seam** is where requirement completion can be observed: a user-visible interaction, an external contract response such as an API response, or an exported file. For each seam, cite the covered R / AC and expected-result source.

Prefer existing public surfaces. Internal services, repository mocks, database tables, test levels, test files, repository calls, and test implementation recipes belong to SOLUTION / verification, not SPEC. An explicitly required public data artifact is a contract only when its upstream authority says so; do not expose internals merely to test them.

Choose ordinary observation points from confirmed requirements without another approval step. Return to requirement clarification only if a new public contract, acceptance meaning, or scope decision is needed.

### 4. Write SPEC.md, and ACCEPTANCE.md when needed

Once acceptance seams are decided, write from the templates. Read:

- [references/spec-template.md](references/spec-template.md)
- [references/acceptance-template.md](references/acceptance-template.md) only when separate acceptance is enabled.

Keep `R → AC` traceability and decidable expected results. AC are the sole behavioural acceptance authority; Scenarios / Examples only illustrate them and cannot add business rules. Evidence must support AC directly, with or without examples. A separate protocol records observation and evidence rules without redefining AC.

#### Select behaviour examples only when useful

Keep unambiguous AC without examples. When examples clarify a real branch or prevent a plausible misreading, apply [example selection](references/spec-template.md#behaviour-examples); do not invent behaviour or add Scenario IDs. Unsettled business choices go to `grilling` before writing dependent examples.

### 5. Consistency

1. Problem, Goal, Scope, bounds, defaults, exclusions and acceptance agree without expanding the confirmed task.
2. `R` / `AC` IDs are unique and stable; every in-scope R has AC coverage. Each AC is independently decidable and grounded in a confirmed requirement or authoritative expected source.
3. Constraints retain their upstream basis, and Acceptance Seams retain their public observations and expected sources. Derived architecture, test strategy and internal verification seams stay in SOLUTION.
4. Requirement Authority records source, snapshot bounds and unverified items accurately. Leave no placeholders, invented facts, untreated conflicts or silently skipped blockers.

Fix what confirmed context or the codebase can fix. Stop and Call the Skill tool with "grilling", or with "wayfinding", when a new decision is required.

### 6. Write and hand off

After consistency holds, write into the task directory. Report acceptance seams, business constraints, design concerns, SOLUTION / graph routing, and unverified items.

Do not edit SOLUTION, ticket contract, status, or evidence. Do not maintain tasks, frontier, status, retry, agent assignment, or any other execution graph inside the SPEC.

After confirming the SPEC, make two independent decisions:

1. **Shared design**: apply the [solution-design entry conditions](../solution-design/SKILL.md#when-a-solution-design-is-required), including shared Interface and lifecycle/cancellation changes even for a single delivery. When required, Call the Skill tool with "solution-design", passing the confirmed SPEC, relevant code facts, confirmed constraints and current authority. Let that skill own the design and its existing Design Review Gate; consume its returned result before recommending execution. Do not finalize a gated choice before user confirmation. Otherwise report `solution_not_required` with its basis. Identify observation methods or gaps without putting test recipes in SPEC.
2. **Execution recommendation**: read and apply the [workflow policy](../shared/workflow-policy.md#select-only-necessary-capabilities) to recommend `quick-implement` or `to-tickets` from delivery boundaries and dependencies. Do not split tickets here. This decision is independent of whether shared design was required; risk and verification difficulty alone do not require decomposition.

Respect a route the user has already selected; explain any relevant risks without requiring another route confirmation. An existing graph and active writers still follow the Task Contract's lifecycle and stop-write protections.

In the final reply, report a Handoff with:

- **Requirements**: SPEC path and confirmation status.
- **Technical Design**: `solution_required` / `solution_not_required`, SOLUTION path or None, reason, and Review Gate `confirmed` / `not_required` / `pending`.
- **Recommended Next Step**: `quick-implement` / `to-tickets`, reason from delivery boundaries and dependencies, and an alternative when useful.
- **Execution Authority**: whether continuing is authorized, and the next call or return action.

Keep this recommendation in the reply, not SPEC or a new handoff file. If only planning is authorized, stop after the requested SPEC and necessary design; do not create tickets unless separately authorized. When continuing is authorized, Call the Skill tool with "quick-implement" or "to-tickets" for the selected route under the [Invocation Contract](../shared/ownership-and-invocation.md); implementation through Graph Workflow still requires implementation authority. A pending design gate blocks dependent execution, not a reason to invent approval or expand authority. Missing authority, unsettled requirements or load-bearing feasibility gaps return to their owner.

## Change rules

Amend here when behaviour, bounds, permissions, compatibility, public contracts
or acceptance change. Resolve unsettled requirement choices by calling the Skill
tool with "grilling" on the affected branch first. Unchanged requirement meaning does not warrant a
SPEC edit; use [contract change ownership](../shared/task-contract.md#handoff-inheritance-and-change)
for design, graph or execution changes and preserve unaffected work. Amendment
mode defines this skill's impact checks and handoff.
