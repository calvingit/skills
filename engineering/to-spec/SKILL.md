---
name: to-spec
description: Turn confirmed requirements, the settled conversation, and codebase facts into a normative SPEC.md. Maintain ACCEPTANCE.md only when the task needs a separate acceptance protocol. Distinguish requirement constraints from high-level technical design, and decide whether downstream work needs an HLD or an execution graph.
---

# To Spec

Write the settled consensus, requirement authority, and codebase facts into the task directory's `SPEC.md`. Create or update `ACCEPTANCE.md` only when the task explicitly needs a separate acceptance protocol, or that file already exists.

Create when there is no SPEC. Amend the same file when an existing SPEC's requirements are added, changed, removed, or clarified. Do not re-interview the whole requirement, split tickets, or implement code.

`SPEC.md` is the workflow's only local requirement snapshot: problem, solution, behaviour, Solution Constraints, testing decisions, bounds, and acceptance. It does not contain derived high-level design, an execution graph, or an implementation recipe. An external PRD or user input can be upstream requirement authority. It cannot replace a confirmed SPEC as the driver of HLD, tickets, or implementation. Do not publish to an external tracker unless the user asks. Do not create a parallel authority such as `SPEC-v2.md`.

`HLD.md`, when it exists, is the high-level technical design derived from the SPEC and codebase facts. It must not change requirement meaning. Shared design across modules, callers, or implementation tasks belongs to `high-level-design`. A single, clearly bounded task goes to `quick-implement`. Several execution units are derived by `to-tickets` and run by `loop`.

## Entry

Resolve requirement sources in this order: what the user named this turn → the applicable Profile's `requirement_authority` → repo facts → this skill's defaults. `external-manual` may use only the current snapshot the user supplied, and must mark unverified original external content. Do not pretend to have reached Feishu, WeCom, or another system.

Stop and hand back to `grilling` when requirements, external behaviour, business bounds, permissions, public contracts, or acceptance still have open choices that would change the plan.

Stop and hand back to `wayfinding` when the destination can be named but a load-bearing path is still in technical fog and needs investigation across sessions.

When the user supplies a finished `MAP.md`: confirm Frontier is empty, Not yet specified holds no fog still pointing at the destination, and blocking decisions are finally confirmed. Read the map's low-resolution view and the decision files that affect requirements, public contracts, bounds, tests, or acceptance. Purely technical high-level decisions wait for `high-level-design`.

Unsettled module duties, internal Interfaces, shared types, dependency direction, or integration strategy do not block the spec. Record them as design concerns and route to `high-level-design` after the SPEC is confirmed.

Do not invent missing fields, errors, public contracts, test seams, Solution Constraints, or expected results. Keep investigating what the codebase can prove. Stop and say so when the user must decide.

## Modes

- **Create**: no `SPEC.md` in the task directory. Write `SPEC.md` from settled inputs. Create `ACCEPTANCE.md` only when a separate acceptance protocol has a clear use.
- **Amendment**: `SPEC.md` already exists. Read the full current SPEC and this delta, then update in place. Read or update `ACCEPTANCE.md` only if it already exists or this turn explicitly enables separate acceptance. Keep unaffected `R` / `AC` IDs. Bump an existing protocol version when public behaviour, error or cancel semantics, CLI / JSON / schema / exit codes, permissions, or artifact bounds change. Internal refactors and new tests do not bump.
- Ticket granularity, dependencies, or execution facts with unchanged SPEC meaning go to `to-tickets` or the execution owner. Do not touch the SPEC.

## Process

### 1. Gather confirmed context

Collect the conversation, user docs, finished decisions, and requirement authority. Keep only explicit facts, constraints, terms, trade-offs, and Out of scope. Do not grow scope to fill a template.

Task directory: what the user named this turn → the applicable `AGENTS.md` `Engineering Skills Profile` → the repo's existing task-doc convention. Missing Profile does not block. Ask only when write location or requirement meaning is still undetermined.

For an amendment, split the delta into `added` / `changed` / `removed` / `no normative effect`. List affected `R`, `AC`, bounds, Solution Constraints, and testing decisions. When an HLD or tickets already exist, read related Ds, ticket contracts, status, and evidence — report which design and delivery may still hold, need appending, replacement, or reversal. Do not edit downstream artifacts. Keep existing `R` / `AC` IDs; append new IDs for new requirements; keep a traceable note for removals and do not renumber. Unsettled product choices go back to `grilling` on the affected branches only. Directed `wayfinding` only when the requirement is settled but a new technical path is still in fog.

### 2. Investigate the codebase

If this session has not already looked enough, before writing the SPEC find:

- Applicable `AGENTS.md`, domain glossary, architecture notes, and related ADRs.
- Current external behaviour, related modules and callers, existing public contracts.
- Which seams existing tests use for similar behaviour, and prior art worth reusing.
- The user's existing workspace changes, so they are not overwritten or silently absorbed into the spec.

Use the project's domain language. Stop once scope, public contracts, and acceptance bounds are determined. Do not enter high-level design or implementation.

### 3. Decide the acceptance seams

Before the formal docs, sketch which *external* seams this change should be accepted through: observable behaviour, test level, and expected-result source. Do not design internal Modules, shared types, or dependency direction — those are the HLD's Verification Seams.

An amendment re-evaluates only affected seams. Keep testing decisions that still cover the changed behaviour, and say so in the impact summary. Inside a confirmed public interface, acceptance coverage, trust boundary, and test contract, choosing an existing test entry can be decided and recorded. Changing those requires user confirmation.

- Prefer existing external seams. A new public contract must be part of the requirement, not an internal structure exposed for tests.
- Use one stable seam when it covers the whole change.
- For each seam, say which behaviour it covers, where the expected result comes from, and similar tests already in the repo.
- Do not presuppose internal Interfaces for tests, and do not treat file paths, internal call order, or mock structure as the contract.

Tell the user the proposed seams, why, and the trade-off. New product, protocol, architecture, scope, or acceptance choices go back to `grilling` or `wayfinding` first.

### 4. Write SPEC.md, and ACCEPTANCE.md when needed

Once acceptance seams are decided, write from the templates. Read:

- [references/spec-template.md](references/spec-template.md)
- [references/acceptance-template.md](references/acceptance-template.md) only when separate acceptance is enabled.

Without a separate acceptance protocol, check `R → AC` and decidable results before writing. When creating or amending `ACCEPTANCE.md`, run the bidirectional check `R → AC → scenario → expected result → executable evidence`. Protocol gaps go back to `grilling`. Do not disguise them as implementation tasks.

### 5. Consistency

1. Problem, Solution, and Destination describe the same problem and goal.
2. `R` and `AC` IDs are unique and stable; every in-scope `R` is covered by at least one `AC`.
3. Each `AC` can be judged on its own and traces to a confirmed requirement or an authoritative expected source.
4. Every Solution Constraint has an upstream basis and does not smuggle in derived technical design that HLD owns.
5. Testing Decisions record the decided seams and why, and verify external behaviour from the highest seam that can.
6. Bounds, defaults, Out of Scope, and acceptance do not conflict or silently expand.
7. No placeholders, untreated conflicts, invented facts, or silently skipped blockers.
8. Requirement Authority records source, snapshot bounds, and unverified items as they are.
9. Every current `R` / `AC` is covered by the SPEC's Acceptance Criteria; check ACCEPTANCE scenarios only when separate acceptance is enabled.
10. An amendment keeps unaffected `R` / `AC` IDs and rechecks the applicable SPEC and ACCEPTANCE, not only the delta.

Fix what confirmed context or the codebase can fix. Stop and hand back to `grilling` or `wayfinding` when a new decision is required.

### 6. Write and hand off

After consistency holds, write into the task directory. Create reports path, acceptance seams, Solution Constraints, design concerns, HLD / graph routing, and unverified items. Amendment shows the requirement delta, spec impact, and possibly affected HLD decisions / tickets first, updates in place after confirmation, and reports kept, added, or removed `R` / `AC`.

Do not edit HLD, ticket contract, status, or evidence. Do not maintain tasks, frontier, status, retry, agent assignment, or any other execution graph inside the SPEC.

After the SPEC is confirmed, judge two paths separately. Ticket count is not a substitute for the design judgement:

1. **High-level design**: call `high-level-design` first when shared types, Interfaces, state or error semantics, dependency direction, migration, or integration constraints span modules, callers, or implementation tasks. Otherwise record `hld_not_required` and why.
2. **Execution**: `quick-implement` when the scope is single and needs no execution graph; `to-tickets` then `loop` when several implementation tasks, dependencies, or unified scheduling are needed.

When an HLD is required, it must exist before either execution path. This skill only forecasts whether several implementation tasks are likely. It does not choose ticket count or the split.

No automatic authorisation to publish externally, commit, push, create a branch, or rewrite history.

## Change rules

- **Normative change** → Amendment. Update `SPEC.md`; sync `ACCEPTANCE.md` only when separate acceptance is already enabled. Do not force re-confirmation when testing seams are unaffected. When an HLD exists, `high-level-design` syncs affected Ds first, then `to-tickets` coordinates the graph. If affected tickets are running, ask `loop` to stop related dispatch, reclaim workers, and keep evidence.
- **High-level design change** → do not edit the SPEC. `high-level-design` amends the HLD, then `to-tickets` coordinates the affected graph.
- **Execution split change** → `to-tickets` only. Do not rewrite upstream.
- **Execution change** → update the ticket or execution evidence only. Do not edit SPEC / HLD.
