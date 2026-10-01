---
name: verify
description: Verify confirmed acceptance criteria using project verification guidance and observable evidence.
---

# Verify

Independently judge the current candidate against confirmed Acceptance Criteria (AC). Requirements define expectations; project guidance supplies execution methods; `code-review` judges change risks and implementation quality.

For the rationale behind independent evidence, see [evidence.md](references/evidence.md).

## Verify the candidate

1. Read the caller's scope, baseline, candidate revision and relevant working-tree changes, requirements, and every applicable AC. Derive expectations from confirmed contracts, not implementation, existing tests, or an implementer's report. Missing or conflicting expectations are a contract gap, not permission to invent them.
2. Locate methods from the task, then the Profile linked by applicable `AGENTS.md` ([resolution](../project-setup/references/profile.md#resolve-and-load)), then existing local skills, guides, scripts, and CI. Missing / `auto` permits discovery; a broken explicit entry is a reported configuration gap. Follow relevant surfaces and actual cross-surface journeys; do not create or repair the harness here.
3. Select and independently run the least costly sufficient checks for every AC and applicable mandatory gate. Confirm each check exercises the behaviour it supports. Reuse still-valid observations only with their candidate, environment, executor, and coverage established; implementation self-checks are not independent verification. A minimal probe or isolated temporary test may be created in caller-permitted scratch space, but do not edit product code or repository tests.
4. Inspect supporting tests, fixtures, snapshots, mocks, and verification configuration only far enough to judge evidence credibility. Weakened, skipped, implementation-derived, or otherwise invalidated checks are insufficient even when green. State mocked/bypassed boundaries, platform limits, and visual/interaction gaps. Judge this credibility here; a separate `test-audit` is not a prerequisite or substitute.
5. Report a verdict for every AC, with its requirement source, actual observation, and coverage limit. Record applicable gate outcomes separately when they do not establish an AC. Keep failures and gaps visible in the conclusion.

## Verdicts

- `PASS`: sufficient observable evidence establishes the criterion.
- `FAIL`: observed behaviour conflicts with the confirmed criterion.
- `NOT VERIFIED`: evidence is insufficient, including unavailable environment, permissions, dependencies, or a missing contract basis. Environment failure is not product failure.

A smoke pass supports only the exercised path. Behavioural E2E does not establish visual conformance or interaction quality; screenshots do not establish interaction timing; mocked responses do not establish real provider integration. Never claim an unexecuted check passed.

## Report and boundaries

Return readable Markdown with the verified scope/candidate, per-AC verdicts, mandatory gates, actual commands or tool actions, working directories, environment, exit codes where available, key results, and retained evidence paths. Identify ticket/attempt when supplied. For each gap, state what would enable verification; a JSON response schema is unnecessary.

Remain read-only toward product code, repository tests, requirements, tickets, Git history, and live business state. Execution may create isolated test state, caches, and evidence only in caller-permitted resources. Follow project isolation/cleanup instructions, clean up only run-owned resources even after failure, preserve evidence, and report cleanup failures. Project recipes do not expand permissions.

Stop at the evidence judgement. Return contract conflicts, capability gaps, and defects to the caller; do not repair, schedule agents, or change task state. Recheck affected evidence after the candidate or relevant verification conditions change.
