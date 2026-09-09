---
name: codebase-design
description: Shared vocabulary for designing deep modules. Use when designing or judging a module's interface, seam, dependency direction, or test surface.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this language and these principles wherever a *specific* Module / Interface / Seam is being designed or restructured.

This skill answers **HOW** a known design point should be shaped. It does not judge whether the whole architecture is sound, and it does not scan the repo for architecture problems — that is `review-architecture`.

The aim is leverage for callers, locality for maintainers, and testability for everyone.

## Glossary

Use these terms exactly — don't substitute "component," "service," "API," or "boundary." Consistent language is the whole point. The target project need not use the same file or type names; every skill must share this meaning.

**Module** — anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice. _Avoid_: unit, component, service.

**Interface** — everything a caller must know to use the module correctly: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics. _Avoid_: API, signature (too narrow — they refer only to the type-level surface).

**Implementation** — what's inside a module, its body of code. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Depth** — leverage at the interface: the amount of behaviour a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation.

**Seam** _(Michael Feathers)_ — a place where you can alter behaviour without editing in that place; the *location* at which a module's interface lives. Where to put the seam is its own design decision, distinct from what goes behind it. _Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter** — a concrete thing that satisfies an interface at a seam. Describes *role* (what slot it fills), not substance (what's inside).

**Leverage** — what callers get from depth: more capability per unit of interface they learn. One implementation pays back across N call sites and M tests.

**Locality** — what maintainers get from depth: change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers. Fix once, fixed everywhere.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- Callers and tests cross the same **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.

## Principles

- **Hide complexity behind the right owner.** Necessary complexity belongs in the module that understands it, not spread across callers. Callers should say what they want, not re-learn how the inside works. Watch for repeated wiring, validation, or protocol steps; callers that must know an internal state-machine order; simple behaviour assembled from low-level details across files; and production APIs that exist to expose test switches, noops, delays, callbacks, or mutable state.
- **Design the Interface from observable behaviour.** Name the capability, inputs, outputs, failure semantics, lifecycle, and cancel / concurrency constraints first. Do not reverse-engineer a public interface from existing classes, tables, or a vendor SDK. Keep the interface small and complete, in the language of the domain or task, without leaking unrelated internals, and usable by real production callers.
- **Put Seams at real variation points.** Good seams already exist: a public Interface, I/O Adapter, process boundary, clock or random source, external system, storage, or UI. Do not add a seam because tests are awkward. Ask whether production also benefits from that boundary, whether it is a real ownership or variation reason, and whether existing public Interfaces already let tests observe the behaviour. If only tests need it, do not widen the production Interface. One adapter means a hypothetical seam. Two adapters with a real reason means a real one — commonly a production adapter and a test adapter. Don't introduce a forwarding port for a single implementation.
- **Keep adapters at the edge.** Vendor SDKs, HTTP, databases, filesystems, and platform APIs stay on the adapter side. Core modules should not spread vendor-specific types, errors, or config without cause. Don't wrap every dependency. An adapter earns its keep by occupying a stable seam, isolating change, or offering a better internal contract.
- **Prefer locality over speculative reuse.** Rules that change together should live together. Abstract only when several real callers or variation points already exist, or when a real boundary must hide complexity. Names like factory, strategy, repository, manager, or service do not make an abstraction real.
- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, mockable, swappable parts — they just aren't part of the interface. A module can have **internal seams** (private to its implementation, used by its own tests) as well as the **external seam** at its interface.
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
7. Stop at the local design judgement. Confirmed SPEC that needs several design points gathered into a task-level technical contract goes to `high-level-design`. Requirement contracts go to `grilling` / `to-spec`. Implementation goes to `quick-implement` or `loop`.

When dependency category changes how a cluster should deepen, read [DEEPENING.md](DEEPENING.md). Read [DESIGN-IT-TWICE.md](DESIGN-IT-TWICE.md) only when the user asks to compare interfaces, or one design is not enough to judge.

## Boundaries

- Whether the current architecture is sound, matches project constraints, or has architecture debt: `review-architecture`.
- A known Module / Interface / Seam that needs a local target design: `codebase-design`.
- Confirmed SPEC that needs shared design across modules, callers, or implementation tasks, written to `HLD.md`: `high-level-design`.
- Requirements or behaviour still open: `grilling`.
- Bug root cause: `debug`.
- Shrinking a behaviour-preserving diff: `simplify`.
- Do not mandate Clean Architecture, DDD, Hexagonal, MVC, or MVVM. Judge ownership, Interface, and Seam from current evidence.
