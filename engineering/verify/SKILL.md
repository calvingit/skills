---
name: verify
description: Verify confirmed acceptance criteria in an independent read-only context using project verification guidance and observable evidence.
---

# Verify

Judge the current implementation against confirmed Acceptance Criteria (AC). Requirements define expected behaviour; the project verification harness supplies execution knowledge; `code-review` judges implementation quality and design.

1. Read the caller's scope, baseline, confirmed requirements, AC and relevant changes. Derive expectations from those contracts, never from implementation, existing tests or an implementer's report. Do not invent requirements or expand scope.
2. Locate project guidance from the current task, then `verification_instructions` in the applicable Engineering Skills Profile, then existing local verification skills, docs, scripts and CI. Missing or `auto` means discover dynamically. For multiple surfaces, follow the relevant entries and cross-surface paths. If guidance is stale or absent, inspect actual commands and use a safe existing method; report any gap for `verification-setup` without creating or repairing the harness in this read-only role.
3. Independently select and run the least costly sufficient checks for every AC and the project's applicable mandatory gates. Confirm that each check actually exercises the behaviour it supports; a harness command or smoke pass is evidence, not an acceptance oracle. When needed, use a minimal runtime probe or isolated temporary test in caller-permitted scratch space (normally `<task-dir>/.loop/tmp/`). Do not edit product code or repository tests to enable verification.
4. Inspect the tests, fixtures, snapshots, mocks and verification configuration supporting the current AC, including relevant changes, only as far as evidence credibility requires. Weakened, skipped, implementation-derived or otherwise invalidated checks are insufficient even when green. State mocked boundaries, bypassed paths, platform limits and visual/UX gaps; behavioural success does not establish visual or interaction quality. Do not defer this credibility judgement to a separate audit. A broader test-value audit may be requested through the caller using `test-audit`; broader maintainability and regression review belong to `code-review`.
5. Return readable text/Markdown per AC with `PASS`, `FAIL` or `NOT VERIFIED`, linked observations and coverage limits. Record the candidate revision and relevant working-tree changes, environment, actual commands/tool actions, working directories, exit codes where available, key results and retained artifact paths. Identify ticket/attempt when supplied; no JSON response schema is required.

`PASS` requires sufficient observable evidence. `FAIL` requires observed behaviour conflicting with the confirmed criterion. `NOT VERIFIED` means evidence is insufficient, including unavailable environment, permissions or dependencies; environment failure is not product failure. Report mandatory gate outcomes separately when they do not establish an AC. Keep unresolved gaps and what would enable verification explicit. Never claim an unexecuted check passed or infer all mapped features work from one smoke run.

Remain read-only with respect to code, repository tests, requirements, tickets, Git history and live business state. Execution may create isolated test state, caches and evidence only in caller-permitted resources. Follow the harness's isolation and cleanup instructions, remove only run-owned resources, and preserve evidence after cleanup, including failed runs. Report cleanup failures. A project recipe does not expand the caller's permissions.

Reading code or an implementation report does not replace observable execution when behaviour can be exercised. Loop decides ticket state; verify does not repair, schedule agents or change the graph. Return missing capabilities to the caller for setup/implementation work, then verify the updated candidate afresh.
