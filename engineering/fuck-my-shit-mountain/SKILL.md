---
name: fuck-my-shit-mountain
description: Run an evidence-driven project audit; explicit invocation only.
---

# Project Audit

Audit the selected project surfaces and deliver evidence, coverage limits, prioritised risks, and proportionate fixes. Preserve the existing skill name and explicit invocation policy.

## Scope and defaults

Use the user's audit question, scope, language, and requested output. Default to the conversation language and a concise Markdown response in the conversation. Do not require a format or language questionnaire. For an explicit full-project audit, use `full`; for a named concern, select the matching modes. Ask only when missing scope or a Git baseline would materially change the audit.

When a project inventory would help choose applicable dimensions, run `python3 <skill-dir>/scripts/project_inventory.py <project-root> --format json`. Inventory recommendations are evidence for scope selection, not additional required user choices.

- Path and semantic scopes include directly relevant callers and dependencies.
- Incremental audits establish the baseline using [the incremental guide](prompts/incremental-audit.md); an invalid ref is a limitation, never a clean review.
- A full audit checks applicability of all focused dimensions, records inapplicable ones as Not assessed, and does not assume a production release is the user's goal.
- Read-only by default. Create report files only when requested, at the requested or project-conventional path. Do not modify audited code, tests, configuration, dependencies, Git state, or project rules without explicit implementation authorisation.
- Historical tracking is optional. Save metadata only when requested, using a user-selected or established audit location; do not create `.claude/audits/` by default.

## Responsibilities and resource loading

This skill owns project coverage and the combined report. When available, use the existing engineering review standards for overlapping dimensions: `code-review` for changes, `review-architecture` for architecture soundness, and the review mode of `simplify` for unnecessary complexity. Read their guidance without automatically starting another workflow or modifying code. Local target design belongs to `codebase-design` only when requested.

For standalone installations, the local evidence, severity, confidence, and coverage rubrics remain sufficient. Missing sibling skills do not block auditing. Focused prompts add investigation surfaces, not a second set of evidence thresholds or mandatory output fields.

1. Read only selected prompts from the table below; `full` identifies the focused dimensions to examine.
2. Read `rubrics/evidence.md`, `rubrics/severity.md`, `rubrics/confidence.md`, and `rubrics/coverage.md` for findings and coverage. Project requirements and actual impact take precedence over generic principles or metric thresholds.
3. Read [report rules](references/report-format.md) before reporting. Prompt-local finding formats are investigation aids; this shared reference owns output requirements.
4. Read `rubrics/principles.md` only for a concrete design concern, `rubrics/scoring.md` only when scores are requested, and `references/tooling.md` when local tools would improve evidence. Examples are optional calibration, never sources of project findings.

## Audit method

Map entry points, responsibilities, state ownership, external interfaces, tests, and relevant operational surfaces. Follow in-scope behaviour through callers and dependencies. Prioritise realistic risks while recording important areas left uninspected.

Exclude Git internals, dependency directories, generated/minified files, build outputs, and binary assets unless the selected question requires them. Inspect lockfiles when dependency or release evidence requires them. Use configured local checks; report unavailable tools and unexecuted verification honestly.

Every finding needs a location, reachable scenario, material consequence, and the smallest supported correction. Check for guards and counterevidence before reporting. Missing tests, large files, or a preferred design pattern are investigation cues, not findings on their own. Suggest verification suited to the issue; do not require new tests for every documentation or configuration correction. Estimate effort only when planning is requested and the scope supports an estimate.

Merge duplicate symptoms and distinguish confirmed issues, hypotheses, and optional improvements. A clean result is valid; do not manufacture findings. Do not expose secrets or private data: identify affected paths and key names with redacted values.

## Modes

| Mode | Prompt | Focus |
|------|--------|-------|
| `full` | `prompts/full-audit.md` | All dimensions; principles when relevant to a concrete concern |
| `incremental` | `prompts/incremental-audit.md` | Diff-based audit of changed files since git reference |
| `architecture` | `prompts/architecture-audit.md` | Module boundaries, dependency direction, state ownership |
| `security` | `prompts/security-audit.md` | Security risks |
| `stability` | `prompts/stability-audit.md` | Reliability & errors |
| `performance` | `prompts/performance-audit.md` | Realistic bottlenecks |
| `testing` | `prompts/testing-audit.md` | Test quality & gaps |
| `maintainability` | `prompts/maintainability-audit.md` | Complexity, coupling, principles |
| `design` | `prompts/design-audit.md` | Engineering principles and design risk |
| `release` | `prompts/release-audit.md` | Release readiness |
| `documentation` | `prompts/documentation-audit.md` | Docs accuracy, setup, operator/developer guidance |
| `observability` | `prompts/observability-audit.md` | Logging, metrics, tracing, health checks, alerting |
| `configuration` | `prompts/configuration-audit.md` | Config validation, defaults, feature flags, env separation |
| `data-integrity` | `prompts/data-integrity-audit.md` | Transactions, idempotency, migrations, invariants |
| `privacy` | `prompts/privacy-audit.md` | PII, minimization, retention, deletion, data governance |
| `accessibility` | `prompts/accessibility-audit.md` | Keyboard, focus, semantics, responsive and UX states |
| `supply-chain` | `prompts/supply-chain-audit.md` | Provenance, reproducibility, CI integrity, signing |
| `cost` | `prompts/cost-audit.md` | Resource economics, budgets, external API and LLM costs |
| `ai-safety` | `prompts/ai-safety-audit.md` | Prompt injection, tool auth, RAG leakage, evals, cost abuse |
| `fallback` | `prompts/fallback-audit.md` | Silent fallback, catch, defensive guessing |
| `testing-authenticity` | `prompts/testing-authenticity-audit.md` | Real confidence vs green checkmarks |
| `type-safety` | `prompts/type-safety-audit.md` | Unsafe blocks, assertions, boundary types |
| `frontend-state` | `prompts/frontend-state-audit.md` | Component size, state, effects, coupling |
| `backend-api` | `prompts/backend-api-audit.md` | API design, validation, data access patterns |
| `dependency-weight` | `prompts/dependency-weight-audit.md` | Overweight deps, build toolchain |
| `code-consistency` | `prompts/code-consistency-audit.md` | Naming, imports, patterns, style uniformity |
| `comment-coverage` | `prompts/comment-coverage-audit.md` | Doc quality, stale comments, missing docs |
| `concurrency` | `prompts/concurrency-audit.md` | Race conditions, deadlocks, atomicity, shared state, locking |

## Delivery

Lead with the conclusion, then scope and baseline, prioritised findings, coverage and verification limits. Scores, large templates, fix-planning tables, and historical tracking are optional deliverables; selecting `full` expands coverage, not mandatory presentation overhead. Use [report rules](references/report-format.md) for file output and its validation.
