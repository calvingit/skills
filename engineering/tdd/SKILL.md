---
name: tdd
description: Test-driven development with a red-green loop. Use when building a feature or fixing a bug test-first, or when the work should move in vertical slices.
---

# Test-Driven Development

TDD is the red → green loop. The point is not more tests. It is independent, observable feedback that proves each slice moved the behaviour.

Every section applies on every cycle — consult them before and during the loop, not after.

## Preconditions

Do not start until all three exist:

1. Expected behaviour that can be judged from outside.
2. An independent source for the expected value — a confirmed literal, spec / acceptance criteria, public contract, authoritative docs, or a worked example.
3. A production Seam that can observe that behaviour stably.

If any is missing, do not invent a test. Unclear behaviour goes back to `grilling`. If the Seam or Interface itself is the wrong shape, consult `codebase-design`.

## What a good test is

Tests verify behaviour through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists — and survives refactors because it doesn't care about internal structure.

Prefer:

- Results a user or caller can actually observe.
- Real production construction and public entry points.
- The same Interface / Seam / Adapter the production path uses.
- An expected value computed independently of the code under test.

Avoid:

- Private methods, internal fields, or call order that are not the contract.
- Production APIs added for tests: `forTest`, noops, mutable callbacks, delay parameters, or leaked internals.
- Bypassing the interface via a database, internal logs, or "the source contains this string", unless that *is* the public contract.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking.

## Anti-patterns

- **Implementation-coupled** — mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behaviour hasn't changed.
- **Tautological** — the assertion recomputes the expected value the way the code does (`expect(add(a, b)).toBe(a + b)`, a snapshot derived by hand the same way, a constant asserted equal to itself), so it passes by construction and can never disagree with the code. Expected values must come from an independent source of truth — a known-good literal, a worked example, the spec.
- **Horizontal slicing** — writing all tests first, then all implementation. Bulk tests verify *imagined* behaviour: you test the *shape* of things rather than user-facing behaviour, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead — one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

```text
one behaviour → one red test → minimal green implementation → next behaviour
```

## Seams — where tests go

A **Seam** is a variation point where behaviour can be changed without editing the code at that point. Tests should normally enter through the production public Interface at that Seam, never through private internals.

**Test only at pre-agreed seams.** Before writing any test, write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam.

Write down:

- The public behaviour under observation.
- Which production Seam the test enters.
- Which external boundaries can stay real, and which need a stable stand-in.
- What this cycle will *not* test.

The Seam belongs on a real Module's Interface, satisfied by an Adapter when needed. If the only way to test is to add a production Interface, consult `codebase-design` before widening the Interface for testability.

A Seam already recorded in `SPEC.md` and confirmed with the user can be reused without asking again. Changing the public interface, acceptance coverage, trust boundary, or confirmed test contract requires stating the new Seam, coverage, and trade-off, then getting confirmation.

When the shape of that interface is itself in question — how deep the module is, where the seam belongs, what the interface should expose — consult `codebase-design`. It is a reference, not a session to run.

## Rules of the loop

Each slice, in this order:

1. **Pick one behaviour** — the smallest independently observable slice that still has user value.
2. **Red** — write the failing test. Confirm it fails because the target behaviour is missing or wrong, not because of fixtures, environment, or syntax.
3. **Green** — only enough production code to pass this test. Don't anticipate later slices.
4. **Verify** — re-run this test and the smallest existing set it can affect.
5. **Next slice** — choose from what this cycle taught you, not from a pre-written test inventory.

**Red before green.** Don't add speculative features.
**One slice at a time.** One seam, one test, one minimal implementation per cycle.
**Refactoring is not part of the loop.** After a coherent set of slices, hand structural contraction to `simplify` or the implementation flow's review / simplification gate, then re-run verification. Don't fold refactor into every red → green cycle.

## Test doubles

In this order:

1. Real, fast, deterministic dependencies.
2. Official fakes / emulators / in-memory Adapters the project already owns.
3. The smallest test double at a real external boundary.

Don't mock your own internal Modules to make a test more "unit". Mocks isolate real external uncertainty; they do not copy the implementation's call graph.

## Bug fixes

`debug` already owns the bug feedback loop, the minimised repro, and root-cause confirmation. In TDD, turn that minimised repro into a regression test: red first, then the smallest root-cause fix, then re-run the original repro. Do not re-run a separate diagnosis inside `tdd`.

## Done when

- Every new test names the external behaviour it checks and the independent expected source.
- Every new behaviour went through a confirmed red → green.
- Tests enter through a production public Seam and do not leak internals for testability.
- No obvious tautological, implementation-coupled, or horizontal-slicing tests.
- Related existing verification still passes; anything unverified is recorded.

## Boundaries

- No mandated test framework, directory, coverage percentage, or mocking library.
- Not every task is TDD. If a valuable tight loop cannot be built, use the target repo's existing verification instead.
- Passing tests are not the only evidence the requirement is done. Completeness still goes through `code-review` and the task's acceptance.
