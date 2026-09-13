# Full Audit Prompt

Use the fuck-my-shit-mountain skill in **full mode**.

Shared setup, coverage, report template, HTML, and lint rules live in `references/report-format.md`; load that reference before producing the report.

Audit against the project's actual goals, maturity, and declared constraints. Do not assume a release-readiness requirement.

Your job is not to insult the codebase. Your job is to identify real engineering risks with evidence.

## Setup

Before writing findings, build a project map:

- Main components and their responsibilities
- Runtime entry points and initialization order
- Architecture boundaries — layers, modules, dependency direction
- Data flow — request/event lifecycle
- State ownership — what owns what state, how it is mutated
- Persistence layer — storage format, migration strategy, backup
- Privacy-sensitive data — collection, storage, deletion, exports
- External interfaces — APIs, WebSocket, CLI, file system, network
- AI/model surfaces — prompts, retrieval, tools, model calls, evals
- Security boundaries — authentication, authorization, input validation, secret management
- Testing structure — test organization, coverage patterns, CI integration
- Release process — versioning, build, packaging, deployment, rollback, supply chain
- Cost drivers — external APIs, model calls, storage, queues, background work

## Audit Dimensions

1. **Architecture and module boundaries** — check `prompts/architecture-audit.md` for cohesion, coupling, dependency direction, state ownership, and layered architecture
2. **Security** — authentication, authorization, injection, secret handling, dependency risks
3. **Stability and error handling** — panic paths, error propagation, retry, timeout, shutdown
4. **Performance and scalability** — hot paths, growth limits, resource leaks, contention
5. **Testing quality** — coverage, test types, flakiness, confidence
6. **Maintainability** — complexity, duplication, naming, documentation accuracy
7. **Design constraints** — use `prompts/design-audit.md`; consult `rubrics/principles.md` only when a concrete design concern warrants it, as required by the skill entrypoint
8. **Release and deployment process** — CI/CD, versioning, upgrade, rollback
9. **Documentation accuracy** — check `prompts/documentation-audit.md` for user/operator/developer docs, API contracts, setup, and decision records
10. **Configuration safety** — check `prompts/configuration-audit.md` for config schema validation, safe defaults, environment separation, secrets, feature flags, and config docs
11. **Observability** — check `prompts/observability-audit.md` for logging, metrics, tracing, health checks, alerting, runbooks, and debuggability
12. **Data integrity** — check `prompts/data-integrity-audit.md` for transaction boundaries, idempotency, concurrency consistency, migrations, invariants, and backup/restore
13. **Privacy / data governance** — check `prompts/privacy-audit.md` for PII, minimization, retention, deletion/export, access boundaries, and privacy in telemetry
14. **Accessibility / UX correctness** (if applicable) — check `prompts/accessibility-audit.md` for semantics, keyboard/focus, responsive correctness, and error/loading states
15. **Supply chain / reproducibility** — check `prompts/supply-chain-audit.md` for provenance, lockfiles, CI integrity, artifact signing, SBOM, and registry hygiene
16. **Cost / resource economics** — check `prompts/cost-audit.md` for unbounded work, storage, observability cost, external API/model spend, quotas, and budgets
17. **AI / LLM safety** (if applicable) — check `prompts/ai-safety-audit.md` for prompt injection, tool authorization, RAG leakage, model fallback, evals, and cost abuse
18. **Fallback / defensive code audit** — check `prompts/fallback-audit.md` for silent fallbacks, empty catches, compatibility branches, and defensive guessing that hides real errors
19. **Testing authenticity audit** — check `prompts/testing-authenticity-audit.md` for over-mocking, implementation detail tests, production code modified for tests, and false confidence
20. **Type safety audit** — check `prompts/type-safety-audit.md` for unsafe blocks, type assertions, boundary weakness, and error type quality
21. **Frontend state audit** (if applicable) — check `prompts/frontend-state-audit.md` for component size, state duplication, effect proliferation, and UI-business logic coupling
22. **Backend API audit** (if applicable) — check `prompts/backend-api-audit.md` for API consistency, request validation, data access patterns, and error response structure
23. **Dependency weight audit** — check `prompts/dependency-weight-audit.md` for overweight deps, unused deps, build toolchain complexity, and version strategy
24. **Code consistency audit** — check `prompts/code-consistency-audit.md` for naming conventions, import organization, error handling patterns, pattern uniformity, file structure, and boilerplate duplication
25. **Comment coverage audit** — check `prompts/comment-coverage-audit.md` for missing public API docs, stale/misleading comments, over-commenting, module documentation gaps, and inline comment quality

26. **Concurrency** — check `prompts/concurrency-audit.md` for races, atomicity, lock order, cancellation, and shared state where applicable.

## Findings and report

Use the shared evidence and coverage rules from `SKILL.md`. A size metric, missing test file, or general principle alone does not establish a finding. Review all applicable selected dimensions and state exclusions honestly.

`references/report-format.md` owns output requirements. Full coverage does not require scores, historical metadata, effort estimates, or the large report templates; include those only when requested.
