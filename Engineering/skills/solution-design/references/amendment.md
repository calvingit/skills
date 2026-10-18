# Solution Amendment

Read this file when `SOLUTION.md` already exists and the SPEC, codebase facts, or a confirmed design changed. Do not load it when deciding whether a SOLUTION is needed, or on first create. Amend the same file. Do not create a parallel version.

Shared stop-write → confirm → write → reconcile order: [Amendment stop-write protocol](../../shared/task-contract.md#amendment-stop-write-protocol).

Compare old / new SPEC, the current SOLUTION, codebase facts, and existing tickets. Classify design change as `added`, `changed`, `removed`, or `no design effect`:

- Keep unaffected D IDs. Append new IDs for new decisions. Do not renumber.
- Requirement or external-behaviour change is amended in the SPEC by calling the Skill tool with "to-spec" first, then the SOLUTION.
- Design change with unchanged requirements updates only the SOLUTION. Do not rewrite the SPEC backwards.
- When a graph exists, read-only check which tickets cite affected Ds, which implemented behaviour still holds, and what needs amendment, correction, migration, or replacement. Do not edit tickets.
- Before writing a shared SOLUTION while a graph exists, follow the shared stop-write protocol (Call the Skill tool with "graph-workflow" so it can stop writers). The current shared-workspace runtime pauses the entire task, including tickets outside the selection.
- Show the user the design delta and ticket impact, then apply the Design Review Gate in [SKILL.md](../SKILL.md#design-review-gate). If the gate is triggered and the affected design choice is not already confirmed, wait for the user's decision before updating the SOLUTION or handing off dependent execution. When the gate is not triggered or the choice is already confirmed, update the same SOLUTION from confirmed requirements and repo evidence, then follow [Handoff](../SKILL.md#handoff): return to `to-spec` when it is the caller; otherwise coordinate an affected graph through `to-tickets` within current authority. New requirement choices or unresolved feasibility follow the upstream routing rules in SKILL.md.

If implementation finds the SOLUTION cannot hold, the worker must report blocked. It must not quietly change a shared design constraint and continue. After the SOLUTION is amended, resume execution according to actual impact.

Treat repeated, structurally similar implementation friction as evidence that a shared design decision may be invalid rather than as a reason to keep adding local exceptions. Signals include repeated workarounds across callers or implementations, callers depending on hidden implementation protocol, recurring type escape hatches, multiple deviations from the same D decision, or a small Interface that keeps expanding to cover ordinary cases.

One local edge case or one implementation friction is not enough. Confirm the pattern and its shared-design cause before amending the SOLUTION. Isolated caller-specific edges remain local implementation.

Section structure, writing rules, and done-when: [solution-template.md](solution-template.md).
