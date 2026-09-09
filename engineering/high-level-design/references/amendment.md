# HLD Amendment

Read this file when `HLD.md` already exists and the SPEC, codebase facts, or a confirmed design changed. Do not load it when deciding whether an HLD is needed, or on first create. Amend the same file. Do not create a parallel version.

Compare old / new SPEC, the current HLD, codebase facts, and existing tickets. Classify design change as `added`, `changed`, `removed`, or `no design effect`:

- Keep unaffected D IDs. Append new IDs for new decisions. Do not renumber.
- Requirement or external-behaviour change is amended in the SPEC by `to-spec` first, then the HLD.
- Design change with unchanged requirements updates only the HLD. Do not rewrite the SPEC backwards.
- When a graph exists, read-only check which tickets cite affected Ds, which implemented behaviour still holds, and what needs amendment, correction, migration, or replacement. Do not edit tickets.
- If an affected worker is still writing, ask `loop` to stop new dispatch, reclaim partial receipts, and confirm it is no longer writing.
- Show the user the design delta and ticket impact. After confirmation, update the same HLD, then hand to `to-tickets` to coordinate the graph.

If implementation finds the HLD cannot hold, the worker must report blocked. It must not quietly change a shared design constraint and continue. After the HLD is amended, resume execution according to actual impact.

Section structure, writing rules, and done-when: [hld-template.md](hld-template.md).
