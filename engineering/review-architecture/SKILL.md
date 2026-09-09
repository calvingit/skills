---
name: review-architecture
description: Read-only review of whether existing architecture matches project constraints and technical standards.
---

# Review Architecture

Read-only architecture review of an existing codebase or a named subsystem. Judge whether the current design is sound, whether it matches architecture constraints the project has already declared, and — when the stack has clear official guidance that still applies — whether a deviation actually matters.

This skill answers **WHETHER the current architecture is sound, where it isn't, why, and what that costs.** It does not design the target architecture, and it does not implement a refactor.

`codebase-design` answers **HOW** a confirmed Module / Interface / Seam should be shaped once a finding needs a change.

## Basis

Judge in this order. Do not dress personal taste as a standard:

1. The user's explicit request and the current task's constraints.
2. Repo-level agent instructions, architecture docs, ADRs, coding standards, and test / build rules.
3. Facts proven by current code, call chains, runtime paths, tests, and runnable checks.
4. Official architecture or best-practice guidance for this stack that is still current and directly relevant. Use `find-docs` when fresh external basis is needed, and distinguish project rules from external advice.
5. General design principles as an analysis lens only. They cannot prove non-compliance by themselves.

When talking about Module, Interface, Depth, Seam, Adapter, Leverage, or Locality, use `codebase-design`'s shared vocabulary. This skill still *reviews the current design*. It does not finish a redesign in advance.

## Boundaries

- Read-only by default. Do not edit source, tests, config, rules, baselines, or architecture docs.
- Do not form a concrete target architecture. Hand a needed Module / Interface / Seam design to `codebase-design`.
- Directory layout, naming taste, or "it looks inelegant" is not automatically an architecture problem.
- Ordinary bugs, local code quality, or performance stay out unless evidence shows the root is ownership, a boundary, dependency, state lifecycle, or architecture policy.
- Do not force Clean Architecture, DDD, or MVVM. Check conformance only when the project chose that constraint, or official stack rules are directly relevant to this question.
- Every finding needs current evidence, actual impact, and the architecture outcome expected. Candidate stage does not write file-level implementation recipes.
- Uncovered scope is listed as uncovered. Do not pretend a whole-repo audit finished.

## Workflow

Default: is the current architecture sound? Load `../improve-codebase-architecture/SKILL.md` only when the user explicitly wants refactor candidates. That mode does not add a new delivery stage.

### 1. Define scope and review question

Name what this round reviews and what "sound" means here.

- A named module, subsystem, feature, or pain point: that range plus its direct callers, dependencies, and composition boundary.
- A global architecture review: build a top-level runtime / module map first, then partition by responsibility. Do not sample by file count.
- When scope is too large, state this round's coverage and what is uncovered, and prefer high coupling, high churn, or a critical runtime path.

### 2. Discover current architecture and rules

If the applicable `AGENTS.md` `Engineering Skills Profile` names architecture authorities, treat them as the project's declared entry and keep verifying against current code. With no Profile, keep discovering dynamically. Do not run setup automatically.

Read what actually exists:

- README, CONTRIBUTING, agent instructions, architecture docs, ADRs / decision records.
- Entry points, composition / configuration, module / package bounds, dependency declarations, and test layout.
- Related lint, dependency checks, architecture guards, build / test commands.
- Official stack rules, only when they would actually change this judgement.

A document is not automatically fact. Check whether current code still matches it. History explains why a design exists. It does not replace current evidence.

### 3. Review through architecture lenses

Read `references/classification-guide.md` as needed. Look at:

- **Boundary / Ownership** — whether the right module owns duty, state, knowledge, and side effects.
- **Dependency direction** — whether dependencies cross a layer they shouldn't, cycle, or leak knowledge backwards.
- **Interface / Depth** — whether the interface hides complexity, or callers are forced to learn the implementation.
- **State / Lifecycle** — whether state owner, concurrency, init, cancel, dispose, and recovery match the use.
- **Data / Control Flow** — whether transforms, errors, events, and side effects are re-interpreted in several places.
- **Testability / Replaceability** — whether tests verify behaviour through the production interface, and whether seams are real variation points.
- **Standards conformance** — declared project constraints, or official stack rules that apply to this scene.
- **Evolution cost** — whether an ordinary requirement must cross too many owners, keep several facts in sync, or edit unrelated areas.

These are investigation lenses, not a scorecard that must be filled.

### 4. Deep-read and seek counter-evidence

Trace only the strongest candidates fully: the target module, representative callers, downstream dependencies, composition entry, related tests, and necessary data or control flow.

Label every conclusion:

- **Observed** — proven directly by current code, symbols, calls, tests, rules, or commands.
- **Inferred** — derived from several Observed facts; state the reasoning.
- **External guidance** — from official stack material; mark hard project constraint vs advice.
- **Unknown** — not enough information; do not assume.

Actively look for counter-evidence. If the current design really isolates a failure domain, protects compatibility, concentrates complexity, or satisfies a real replacement boundary, downgrade or reject the candidate.

### 5. Rank findings by impact

Do not rank by "how many principles it violates". Rank by evidence and actual cost:

- `Critical` — can cause data, safety, permission, persistence-compat, or system-level lifecycle failure.
- `High` — ongoing change fan-out, wrong ownership, runaway dependencies, or behaviour that cannot be verified reliably.
- `Medium` — stable architecture friction and maintenance cost, local and contained.
- `Low` — slight drift or an improvement that cannot drive an architecture change on its own.
- `Speculative` — a signal exists but a load-bearing fact is unknown. Not a confirmed finding.

When nothing holds, say **no findings**. Do not invent architecture debt to complete a report.

### 6. Report and stop

Write a Markdown architecture review from `references/report-template.md`. The report must make clear:

- scope / coverage / uncovered range
- current architecture and applicable authorities
- findings with evidence, impact, and rule / guidance basis
- counter-evidence that is *not* a problem
- recommendation direction and questions that still need confirmation

This skill stops at the review conclusion. If the user chooses to act on a finding:

- Need a target Module / Interface / Seam → `codebase-design`
- Requirements or trade-offs still open → `grilling`
- Need a formal task contract → `to-spec`
- Plan already clear → `to-spec`, then `high-level-design` when several implementations must share design, then `quick-implement` or `loop` by scope
- Goal is only to delete proven-unnecessary complexity → `simplify`

## Done when

- Review scope, judgement basis, and uncovered parts are stated.
- Current architecture facts come from code, relations, tests, or runnable checks — not from restating docs.
- Project rules, official external guidance, and general design judgement are distinguished.
- Every finding has evidence, impact, and an architecture concern.
- Important counter-evidence was sought and recorded. A reasonable trade-off is not mislabelled as a problem.
- The report concludes `Critical / High / Medium / Low / Speculative` or **no findings**.
- The review did not drift into redesign or implementation.
