# Architecture Improvement Candidates

Use this reference only when the user explicitly asks where the architecture is
most worth improving or where to invest next. Candidate discovery is not a
claim that the current architecture is defective.

Inherit `SKILL.md`'s scope, evidence, counter-evidence, read-only, and stop
rules. Do not repeat them here.

## Search

Look for a small set of areas where architectural investment may provide
meaningful leverage:

- shallow Modules whose Interfaces expose implementation decisions;
- knowledge leakage across a Seam or dependency boundary;
- duplicated policy or coordination that belongs behind one owner;
- unstable dependencies or responsibilities that repeatedly change together;
- tests or callers that reach past an Interface;
- complexity that would spread back to callers if the current Module were
  deleted.

Do not treat a shallow Module, file layout, or architectural neatness alone as
enough reason to change code. Check change frequency, dependency spread,
knowledge leakage, ownership, and expected payoff. `shallow` does not mean
`bad`.

## Candidate report

For each consequential candidate, report:

- current structure and observed evidence;
- the actual friction or knowledge leakage;
- a possible improvement direction, without designing the final Interface;
- expected leverage, locality, and testability benefit;
- likely scope, migration cost, and important risks;
- recommendation strength: `Strong`, `Worth exploring`, or `Speculative`.

Prefer a few high-value candidates over exhaustive cleanup. If no candidate has
material payoff, say so instead of manufacturing a refactor list.

## Further analysis

When a candidate's dependency category changes the safe deepening approach, read
[`codebase-design/DEEPENING.md`](../../codebase-design/DEEPENING.md). When the
user asks for alternatives, or one direction is not enough to judge, read
[`codebase-design/DESIGN-IT-TWICE.md`](../../codebase-design/DESIGN-IT-TWICE.md).
Do not design the final Interface while producing the candidate report.

## Output and handoff

Use Markdown by default. Read [html-report.md](html-report.md) only when there
are several candidates, module relationships need a visual comparison, or the
user asks for an HTML report. The report belongs in the OS temporary directory,
not the repository.

Do not modify product code, generate HLD, split tickets, or start another
workflow.
Present the shortlist and wait for the user's selection. After a selection,
the caller can choose `grilling`, `codebase-design`, `high-level-design`, or
another appropriate next step.

An ordinary architecture review may mention a local improvement opportunity,
but it must not silently start this candidate search or scan the whole
repository for additional opportunities.
