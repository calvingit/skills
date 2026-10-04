---
name: backend-development
description: Apply backend engineering practices when changing server-side APIs, services, persistence, integrations, or background processing.
---

# Backend Development

Build the smallest backend change that preserves the system's behavioural, data,
and operational guarantees. Use the existing architecture, conventions and
infrastructure unless they prevent the requirement from being met. Every added
reliability or scalability mechanism needs a concrete failure mode, invariant or
operational constraint.

## Understand the affected path

Follow the relevant production entry through its callers, business rules, reads,
writes, external dependencies and failure handling. Identify the owner of each
rule and state transition, and the contracts and tests protecting them. Directory
names alone do not establish architecture.

These checks complement the caller's implementation or review workflow; they do
not create another planning, scheduling or acceptance process. Apply only the
checks the change touches. Read-only queries usually need authorization, cost
and result-limit checks; writes also need invariants, concurrency and atomicity.
Expand investigation when the affected path or unexplained evidence requires it.

## Choose relevant checks

| Affected boundary | Check |
| --- | --- |
| API or service | Validate untrusted input; preserve required request, response and error contracts, including invalid input, missing resources, conflicts, authorization and internal failures when exposed by the protocol. Keep transport concerns and internal details behind the existing boundary. Follow established pagination, filtering, ordering and limits. |
| Business rules | Keep rules with their current owner, without duplicating them in handlers, jobs or consumers. Make invalid state transitions explicit. Avoid trivial wrappers and state changes spread across unrelated owners. |
| Persistence | Identify atomic writes, concurrent updates, read consistency, query/index impact and data compatibility. Read [persistence and migrations](references/persistence-and-migrations.md) for schema changes, backfills or repairs. |
| External writes | Distinguish confirmed success, confirmed failure and unknown outcome. Read [operation outcomes and retries](references/operation-outcomes-and-retries.md) when retries or partial completion can repeat effects. Keep provider details behind the existing integration boundary. |
| External dependencies | Check relevant timeouts, partial failure, duplicates, rate/capacity limits, credentials and unavailability. Retry only safe-to-repeat operations on plausibly transient failures, not invalid input, rejected authorization or known business errors. |
| Async processing | Establish actual delivery, ordering, retry and interruption semantics from infrastructure and configuration; preserve duplicate safety where effects matter. Read [lifecycle and resource limits](references/lifecycle-and-resource-limits.md) for workers, cancellation, shutdown or capacity changes. |
| Security | Check resource/operation authorization separately from authentication. Preserve tenancy, ownership, trust boundaries and least privilege; keep secrets and sensitive payloads out of logs and responses. Do not bypass these checks to reuse an internal API. |
| Failure handling | Handle errors where a meaningful decision is possible. Preserve diagnostic context and stable public errors; do not swallow failures, turn them into success/null, or repeatedly log and rethrow through every layer. Make partial success explicit and recoverable. |
| Operations | Use existing logging, metrics and tracing. Add signals for meaningful new failure modes or operational dependencies; keep logs structured and avoid unnecessary high-frequency output. Preserve correlation context across downstream and async work when relevant. |
| Performance | Investigate affected high-volume or latency-sensitive paths, work growing with data size, large payloads, repeated remote calls, and I/O inside loops. Remove unnecessary work first. Cache only with understood ownership, invalidation, consistency and failure behaviour. |

For explicit API compatibility or schema work, use `api-contracts` when available;
for delivery, acknowledgement, replay or asynchronous side-effect design, use
`event-driven-backend`. In a standalone installation, inspect the actual project
contracts and infrastructure for those same questions; missing sibling skills do
not remove the checks or block other investigation.

## Keep the design proportional

Do not add compatibility for obsolete internal behaviour without a required
contract. Idempotency is warranted when duplicates can repeat meaningful effects;
async processing is warranted when the synchronous path cannot meet the need.
Do not add locks, caching, denormalization, indexes, microservices, CQRS, event
sourcing, distributed transactions, message infrastructure or architectural
layers without an observed or structurally clear need.

Validate the affected business result and failure boundaries using the caller's
project methods. If requirements conflict with the existing architecture,
surface the conflict rather than silently redesigning the system.
