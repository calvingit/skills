---
name: verify
description: Verify acceptance criteria against observable results in an independent read-only context.
---

# Verify

Verify the current implementation against confirmed acceptance criteria. Acceptance Criteria define expected behaviour; code and design judgement belong to `code-review`.

1. Read the caller's scope, baseline, confirmed requirements, Acceptance Criteria, and relevant changes. Derive expected behaviour from those contracts, not from the implementation, existing tests, or an implementation agent's report. Do not invent requirements or expand the task.
2. Independently choose and run the smallest sufficient checks for each criterion's observable behaviour. Existing tests, builds, lint/type checks, runtime checks, and interface checks are evidence, not the acceptance oracle; confirm that each check actually exercises the criterion it supports. Passing tests do not by themselves establish acceptance.
3. When existing checks cannot directly establish a criterion, use a minimal read-only runtime probe or isolated temporary test when practical. Keep temporary artifacts in caller-permitted scratch space such as `.loop/tmp/`; do not modify production code or repository tests merely to make verification possible.
4. Inspect changes to tests, fixtures, snapshots, mocks, test configuration, and verification configuration when they affect evidence credibility. Treat weakened, skipped, implementation-derived, or otherwise invalidated checks as insufficient evidence, even when the test command is green. Inspect these artifacts only far enough to decide whether they provide credible evidence for the relevant acceptance criterion; their quality, maintainability, and broader regression risks belong to `code-review`.
5. Return readable text/Markdown for each Acceptance Criterion with one verdict: `PASS`, `FAIL`, or `NOT VERIFIED`, plus observed evidence. `PASS` requires sufficient observable evidence; `FAIL` requires observed behaviour that conflicts with the criterion; `NOT VERIFIED` means evidence is insufficient, including unavailable environment, permissions, or dependencies. Environment or access failure is not a product `FAIL`. Record actual commands, exit codes, and key output. Identify the ticket/attempt when supplied. No JSON response schema is required.

Reading code and an implementation agent's self-report do not replace observable execution evidence when the behaviour can be exercised. Keep failed and unverified checks explicit, including what would allow them to run. Loop decides the next ticket state from these results; verification does not repair, schedule agents, or change the graph.

Do not edit code, requirements, tickets, Git history, or external business state. Put isolated test caches and temporary outputs only in locations the caller permits, normally `.loop/tmp/`. Never claim commands ran when they did not.
