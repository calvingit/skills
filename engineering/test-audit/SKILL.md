---
name: test-audit
description: Audit test effectiveness and maintenance value when tests appear redundant, implementation-coupled, misleading, or costly to maintain.
---

# Test Audit

Audit the requested tests against confirmed behaviour and concrete regression risks. Work read-only by default; change tests only when the caller requests cleanup or repair. Do not turn this into a mandatory delivery gate or a whole-repository audit without scope.

## Establish scope

Read the requested paths or diff, applicable instructions, contracts, relevant production callers, tests, fixtures, mocks, snapshots and configuration. Distinguish existing tests from new changes. No SPEC or ticket is required when confirmed behaviour is available elsewhere. If intended behaviour cannot be established, report the uncertainty rather than recommending deletion on that basis.

## Assess value

For each material concern, establish the protected behaviour, how the test exercises it, and a plausible regression it would catch. Focus on:

- **Independent expectations.** Trace expected values to requirements, domain rules, worked examples or an independent reference. Copied implementation logic can duplicate a bug; a hard-coded literal is not automatically independent. Formulas, properties and snapshots need a justified basis, not a blanket ban.
- **Relevant execution.** Check whether the actual assertion observes the required result or side effect. Identify mocked-away boundaries, bypassed production paths, skipped checks and vacuous assertions. Call counts, database observations or internal checks may be justified by a concrete contract or risk; do not reject them by syntax alone.
- **Distinct protection.** Compare the failure modes, inputs, boundaries and feedback speed of apparently overlapping tests. Similar names, high test counts, coverage percentages or a large test diff are not deletion criteria. Before merging or removing a test, identify retained protection and any unique evidence that would be lost.
- **Maintenance cost.** Identify demonstrated brittleness, excessive setup, or production APIs and indirection added only for tests. Reuse existing boundaries and project conventions; do not demand new abstractions or replace fast unit tests with E2E by default.

Run targeted checks when they resolve a concrete uncertainty. A bounded mutation or negative control can test sensitivity when useful and permitted; use an isolated disposable copy and report the actual result. Do not add a mandatory mutation-testing tool or claim that a hypothetical failure was observed.

## Recommend or repair

Return concise Markdown with scope, evidence-backed findings, locations, protected behaviours or failure modes, and justified keep / merge / rewrite / remove recommendations. Report material retained protection without cataloguing every healthy test. Separate observed defects from uncertainty and state checks run and limitations. An empty findings list does not certify all acceptance criteria.

When cleanup is authorised, make only the scoped changes, preserve unique regression protection, run the smallest sufficient checks, and inspect the final diff. Do not update snapshots, relax assertions or alter product behaviour to hide failures. Return necessary production or harness changes to the caller unless separately authorised; do not expand a test cleanup into a redesign.

Stop when the requested test concerns are resolved or explicitly bounded. Acceptance evidence remains the responsibility of `verify`, which must still judge credibility for its own criteria; broader change risks belong to `code-review`. Return findings to the caller without scheduling other agents or changing ticket state.
