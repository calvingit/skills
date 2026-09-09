# When to Mock

Prefer real, fast, deterministic dependencies. Mock at **system boundaries** only — a third-party API, an uncontrolled network, time, or randomness. For databases and filesystems, prefer the project's existing test database, emulator, or in-memory Adapter.

Don't mock:

- Your own classes/modules
- Internal collaborators
- Anything you control

A test double should satisfy a confirmed Interface and return a result independent of the implementation under test. Don't use a mock to copy the current Implementation's call graph.

## Designing for Mockability

At system boundaries, inject a concrete, stable Interface. Prefer one entry per real operation. Don't expose a generic fetcher that needs conditional logic inside the mock.

**1. Use dependency injection**

Pass external dependencies in rather than creating them internally.

**2. Prefer SDK-style interfaces over generic fetchers**

Create specific functions for each external operation instead of one generic function with conditional logic. Each mock then returns one specific shape, with no conditional logic in test setup.
