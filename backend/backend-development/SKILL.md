---
name: backend-development
description: Apply backend engineering practices when changing server-side APIs, services, persistence, integrations, or background processing.
---

# Backend Development

Build backend changes that fit the existing system and preserve its behavioral,
data, and operational guarantees.

Use the repository as the primary source of truth. Prefer the architecture,
conventions, abstractions, and infrastructure already in use unless they prevent
the requirement from being implemented correctly.

## Understand the existing path

Before changing code, inspect the relevant execution path far enough to
understand:

- where requests or events enter the system;
- which layer owns the behavior;
- where data is read or written;
- which external systems are involved;
- how failures are represented;
- what tests or contracts protect the behavior.

Do not infer architecture from directory names alone. Follow actual call paths
and existing ownership.

Keep the change local when possible. Do not introduce a new architectural
pattern merely because it is common in backend systems.

## API and service boundaries

At external and service boundaries:

- validate untrusted input before it reaches deeper layers;
- preserve established request and response contracts;
- distinguish invalid input, missing resources, conflicts, authorization
  failures, and internal failures when the protocol exposes those distinctions;
- avoid leaking internal implementation details through errors;
- keep transport-specific concerns at the boundary when the existing
  architecture separates them from domain logic;
- preserve backward compatibility unless the requirement explicitly changes the
  contract.

For write operations, consider duplicate requests and retries when they can
cause repeated side effects. Add idempotency only where duplicate execution is
a realistic failure mode.

For collection APIs, follow the project's existing pagination, filtering,
ordering, and limit conventions. Do not invent a second convention.

## Business and domain logic

Place business rules in the layer that already owns similar rules.

Avoid:

- duplicating the same rule across controllers, handlers, jobs, or consumers;
- moving domain decisions into persistence or transport code for convenience;
- creating abstractions that exist only to wrap a single trivial operation;
- spreading a state transition across unrelated components without clear
  ownership.

When behavior depends on current state, make invalid transitions explicit rather
than relying on incidental database or framework failures.

## Data and persistence

Treat data integrity as part of application correctness.

When changing persistence behavior, determine:

- which writes must succeed or fail together;
- whether concurrent requests can modify the same state;
- whether reads require a particular consistency guarantee;
- whether the change affects existing queries, indexes, constraints, or data
  volume;
- whether existing data must remain readable after the change.

Use transactions around actual atomicity boundaries, not entire request flows by
default.

Prefer database constraints for invariants the database can enforce reliably,
while keeping user-facing validation and domain errors at the appropriate
application boundary.

Do not add locking, caching, denormalization, or new indexes without an observed
or structurally clear need.

For schema changes, consider both application versions and existing data during
deployment. Avoid changes that require all instances to switch versions at the
same instant unless the deployment model guarantees it.

## External systems

Treat network and external service calls as unreliable.

For each relevant integration, consider:

- timeout behavior;
- retry safety;
- partial failure;
- duplicate execution;
- rate or capacity limits;
- authentication and credential handling;
- behavior when the dependency is unavailable.

Do not retry failures blindly.

Retry only when the operation is safe to repeat or has an explicit idempotency
mechanism, and when the failure is plausibly transient.

Do not retry permanent failures such as invalid input, rejected authorization,
or known business errors.

Keep external provider details behind the project's existing integration
boundary when one exists.

## Asynchronous processing

For queues, events, schedulers, and background jobs, establish the delivery and
failure assumptions before relying on them.

Consider:

- whether processing may happen more than once;
- whether ordering matters;
- what happens after partial success;
- how failed work is retried or surfaced;
- whether consumers can safely resume after interruption.

Assume duplicate delivery is possible unless the infrastructure explicitly
guarantees otherwise.

Prefer idempotent consumers for operations that may be retried.

Do not introduce asynchronous processing when a synchronous path already meets
the requirement and operational constraints.

## Security

Treat authentication and authorization as separate concerns.

Verify authorization against the resource or operation being performed, not
only against the fact that a user is authenticated.

Keep secrets, credentials, tokens, and sensitive payloads out of logs and error
responses.

Preserve existing trust boundaries and least-privilege assumptions.

Do not bypass validation, authorization, tenancy, or ownership checks to reuse
an internal API.

## Failure handling

Handle failures at the layer that can make a meaningful decision about them.

Do not:

- swallow errors;
- convert every failure into a generic success or null result;
- expose raw infrastructure exceptions to callers;
- catch exceptions only to log and rethrow them repeatedly through every layer.

Preserve useful failure context for diagnostics while presenting stable errors
at public boundaries.

When an operation can partially succeed, make the resulting state explicit and
recoverable.

## Operational behavior

Follow the application's existing logging, metrics, and tracing infrastructure.

Add operational signals when the new behavior introduces a meaningful new
failure mode or operational dependency.

Prefer structured, contextual logs over free-form diagnostic output.

Avoid logging normal high-frequency execution paths unless the existing system
does so intentionally.

When relevant, preserve correlation or request context across downstream calls
and asynchronous work using the mechanisms already present in the project.

## Performance

Do not optimize speculatively.

Investigate performance when the change affects:

- high-volume paths;
- queries whose work grows with dataset size;
- repeated remote calls;
- large payloads;
- loops containing database or network operations;
- known latency-sensitive paths.

Prefer removing unnecessary work over adding caching.

Introduce caching only when ownership, invalidation, consistency, and failure
behavior are understood.

## Keep the design proportional

Prefer the smallest design that preserves correctness and existing architectural
boundaries.

Do not introduce microservices, CQRS, event sourcing, distributed transactions,
new message infrastructure, or additional architectural layers unless the
requirement or existing system actually needs them.

When a requirement conflicts with the current architecture, surface the conflict
instead of silently redesigning the system.