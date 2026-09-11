# HLD Amendment

Read this file when `HLD.md` already exists and the SPEC, codebase facts, or a confirmed design changed. Do not load it when deciding whether an HLD is needed, or on first create. Amend the same file. Do not create a parallel version.

Compare old / new SPEC, the current HLD, codebase facts, and existing tickets. Classify design change as `added`, `changed`, `removed`, or `no design effect`:

- Keep unaffected D IDs. Append new IDs for new decisions. Do not renumber.
- Requirement or external-behaviour change is amended in the SPEC by `to-spec` first, then the HLD.
- Design change with unchanged requirements updates only the HLD. Do not rewrite the SPEC backwards.
- When a graph exists, read-only check which tickets cite affected Ds, which implemented behaviour still holds, and what needs amendment, correction, migration, or replacement. Do not edit tickets.
- Before writing a shared HLD while a graph exists, ask `loop` to stop task dispatch, interrupt workers, preserve partial receipts, and block all active attempts. The current shared-workspace runtime pauses the task, not just the selected tickets.
- Show the user the design delta and ticket impact. When the design follows confirmed requirements and repo evidence, update the same HLD and continue to `to-tickets` to coordinate the graph. New requirement choices or unresolved feasibility follow the upstream routing rules in SKILL.md.

If implementation finds the HLD cannot hold, the worker must report blocked. It must not quietly change a shared design constraint and continue. After the HLD is amended, resume execution according to actual impact.

Section structure, writing rules, and done-when: [hld-template.md](hld-template.md).
