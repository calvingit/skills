---
name: codebase-design
description: Shared vocabulary for designing deep modules. Use when designing or judging a module's interface, seam, dependency direction, or test surface.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this language and these principles wherever a *specific* Module / Interface / Seam is being designed or restructured.

This skill answers **HOW** a known design point should be shaped. It does not judge whether the whole architecture is sound, and it does not scan the repo for architecture problems — that is `review-architecture`.

## Glossary

Use these meanings within Module / Interface / Seam design discussions. Preserve the project's established domain terms and external contract names; clarify mappings when needed rather than renaming components, services, or APIs to match this glossary. These are analysis terms, not a replacement for the project's domain model.

**Module** — anything with one caller-visible Interface and an Implementation, from a function to a tier-spanning slice. _Avoid_: unit, component, service.

**Interface** — everything a caller must know: signatures, invariants, ordering, errors, configuration and performance. Do not reduce this meaning to an API signature.

**Implementation** — the module's internal code. **Adapter** describes its role at a Seam, not its implementation size.

**Depth** — behaviour available per unit of Interface a caller or test must learn. A deep module hides substantial behaviour behind a small interface; a shallow one exposes nearly its implementation's complexity.

**Seam** _(Michael Feathers)_ — a variation point where behaviour can change without editing code at that point: public or internal Interface, I/O, process or external system. Placement is a separate decision from Implementation. _Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter** — a concrete implementation of an Interface at a Seam.

**Leverage** — caller capability per unit of Interface learned.

**Locality** — change, bugs, knowledge and verification concentrated with their owner rather than spread across callers.

## Principles

- **Hide complexity behind the right owner.** Callers express intent rather than repeat wiring, validation, protocols or internal state-machine steps. Production APIs should not exist to expose test controls.
- **Design the Interface from observable behaviour.** Name the capability, inputs, outputs, failure semantics, lifecycle, and cancel / concurrency constraints first. Do not reverse-engineer a public interface from existing classes, tables, or a vendor SDK. Keep the interface small and complete, in the language of the domain or task, without leaking unrelated internals, and usable by real production callers.
- **Put Seams at real variation points.** Use existing public Interfaces, I/O, process, clock/random, storage or UI boundaries when sufficient. Require a production ownership or variation benefit; awkward tests alone do not justify widening the Interface. Judge by isolated complexity and change, not adapter count: one adapter can still isolate vendor protocol, lifecycle or errors. Reject forwarding ports that add no such value.
- **Keep adapters at the edge.** Isolate vendor SDKs, HTTP, databases, filesystems and platform APIs when doing so hides change or improves the internal contract. Do not spread vendor types, errors or configuration without cause, or wrap every dependency.
- **Prefer locality over speculative reuse.** Keep rules that change together with one owner. Abstract for several real callers or existing variation points, or for a real boundary that hides complexity, not a pattern name.
- **Depth is relative to the Interface.** Internal parts may be small, mockable and swappable. Keep private test seams internal rather than exposing them through the caller-facing Interface.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test *past* the interface, the module is probably the wrong shape.

## The deletion test

Imagine deleting the module and letting callers use its downstream dependency directly. If almost no abstraction, constraint, stability, or understanding cost is lost, it was a pass-through. If complexity reappears across N callers — protocol, state, invariants, error semantics, cache / transaction boundaries — it was earning its keep.

The deletion test judges value and depth. It does not prove the seam or the dependency direction is right.

## Workflow

1. Name the design question, the intended callers, and the Module / Interface / Seam under decision. Do not expand into a repo-wide architecture review.
2. Read the target module, representative production callers, composition / configuration entry points, downstream dependencies, and related tests.
3. Write down current observable behaviour, ownership, invariants that must hold, and real external boundaries.
4. Judge the current Interface, Depth, Seam, Adapter, dependency direction, and Locality. Mark each claim Observed / Inferred / Unknown.
5. Offer at most two or three real candidate designs, with benefit, cost, migration impact, and test seam. Do not pad with fake options.
6. Recommend the simplest design that puts necessary complexity with the right owner without widening the public surface.
7. Stop at the local design judgement; route further work using the boundaries below.

When dependency category changes how a cluster should deepen, read [DEEPENING.md](DEEPENING.md). Read [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) only when the user asks to compare interfaces, or one design is not enough to judge.

## Boundaries

- Whether the current architecture is sound, matches project constraints, or has architecture debt: `review-architecture`.
- Confirmed SPEC that needs shared design across modules, callers, or implementation tasks, written to `SOLUTION.md`: `solution-design`.
- Requirements or behaviour still open: `grilling`.
- Bug root cause: `debug`.
- Shrinking a behaviour-preserving diff: `simplify`.
- Do not mandate Clean Architecture, DDD, Hexagonal, MVC, or MVVM. Judge ownership, Interface, and Seam from current evidence.
