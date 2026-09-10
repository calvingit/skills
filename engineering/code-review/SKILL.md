---
name: code-review
description: Review code changes for actionable defects, regressions, and unnecessary complexity, with an evidence-based report.
---

# Code Review

Review whether the change solves the intended problem without breaking existing behaviour or adding unjustified complexity. Work read-only; report findings rather than fixing code or changing requirements, Git state, or external systems.

## Establish scope

Use the user's requested commit, branch, working tree, or paths. Pin the baseline and distinguish pre-existing edits. For a branch comparison use its merge base; for a single commit inspect that commit's patch, not a three-dot comparison against HEAD. Include staged, unstaged, and relevant untracked files in a working-tree review. An invalid ref, unreadable scope, or empty diff is a limitation, not a successful review.

Read the request and applicable repository rules, then follow the changed behaviour through callers, dependencies, public types, configuration, and tests. Use supplied requirements, acceptance criteria, and task-level design when available. No ticket, SPEC, HLD, receipt, or separate acceptance document is required for standalone use. Without a requirement source, review demonstrable defects and state that requirement completeness was not assessed; do not invent intent.

## What to review

Prioritise the questions that require judgement:

- **Intent and behaviour:** Does the implementation satisfy confirmed requirements, including relevant failure paths? Did it add unauthorised behaviour or change a public contract?
- **Correctness and regression:** Trace reachable inputs, state transitions, error propagation, concurrency, and resource lifetime. Check interactions beyond the diff where the change can affect them.
- **Safety and cost:** Look for concrete permission bypass, data loss, sensitive-data exposure, and performance or resource problems on plausible workloads. Explain the trigger and impact.
- **Design and complexity:** Does the change fit existing boundaries and conventions? Report unnecessary compatibility paths, speculative abstractions, or test-only indirection only when their concrete maintenance cost is evident. Prefer the smallest correction; do not prescribe patterns or broad refactors.
- **Evidence:** Do tests assert the intended observable behaviour and cover the risky changed paths? Passing commands do not prove the requirements are right or the tests meaningful. Separate evidence actually inspected from claims and unverified scope.

Do not repeat formatter, linter, or type-checker output as manual findings. Do not demand more tests, abstractions, compatibility, or defensive code without a specific failure or maintenance problem. Follow neighbouring code only to resolve a concrete concern; no mandatory whole-repository exploration.

## Decide what matters

Before reporting a finding, check the relevant guards, callers, and tests for evidence that disproves it. A finding needs a reachable scenario, a location, and a material consequence. Separate confirmed defects from unanswered questions; omit speculative risks and style preferences.

Current-scope requirement violations and defects introduced or worsened by this change require fixes. Existing unrelated problems and optional improvements belong in follow-up and do not block this change. Merge duplicate symptoms of the same cause and rank findings by impact, not by review category.

Use P0 for immediate severe widespread harm, P1 for serious impact requiring prompt correction, P2 for a contained actionable defect, and P3 for a useful optional improvement. Severity and whether a finding blocks this change are separate decisions; a P2 correctness defect can require a fix.

Contradictory requirements need clarification by their owner. Missing access or evidence needs an explicit limitation, not a fabricated defect or a pass. Required verification failures must remain visible. Review does not replace execution of required tests or grant permission to commit or deploy.

## Report

Always return readable Markdown in the user's language, including when invoked by another workflow. Use [the report format](references/output-contract.md): conclusion, scope, prioritised findings, follow-up, requirement gaps, unverified scope, and evidence. Keep explanations concise but sufficient for a human to act. Do not return JSON or require the reader to understand an orchestrator's schema.
