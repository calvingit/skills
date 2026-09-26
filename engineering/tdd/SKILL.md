---
name: tdd
description: Drive a feature or bug fix through small test-first behaviour cycles with red, green, and scoped refactoring.
---

# Test-Driven Development

Use TDD as an implementation method: choose one confirmed behaviour, observe a meaningful failing test, implement it, and improve the touched design while keeping tests green. Clear business rules and regression fixes can benefit as much as uncertain interface design. TDD does not replace the caller's delivery or acceptance responsibilities.

## Establish the behaviour and boundary

Read the confirmed requirements, relevant project vocabulary, applicable design decisions, and existing verification guidance. Identify:

- The behaviour and an independent basis for the expected result: a requirement, public contract, domain rule, or worked example.
- The production interface through which a caller observes it, and any external dependencies that need a test double.
- The smallest sufficient test level and what it cannot establish.

Reuse existing decisions and interfaces; do not ask the user to reconfirm routine test choices. For new behaviour, a proposed interface grounded in real caller needs is enough to start; it need not already be implemented. Resolve consequential requirement or shared-design conflicts through the caller before dependent work. Keep technical test boundaries in applicable design or test guidance, not in SPEC as implementation details.

Prefer public behaviour over private structure. Do not widen production APIs or add registries, setters, wrappers, or dependency layers solely to make a test convenient. Consult `codebase-design` when a real interface design problem needs its vocabulary; it is not a mandatory stage.

## Write useful tests

Protect a confirmed contract, domain rule, meaningful failure mode, or known regression. Choose checks that exercise the relevant production path and survive internal refactoring. Read [tests.md](tests.md) for examples and [mocking.md](mocking.md) when using test doubles.

Keep the expected result independent of the implementation under test. Copying its algorithm can reproduce the same mistake; replacing that algorithm with a literal does not establish independence. A formula, property, or reference implementation can be valid when independently justified. Ask what plausible contract violation the test would detect, not how many lines it covers.

Avoid bulk test-first work that commits to speculative interfaces before feedback. Choose one behaviour at a time; a TDD cycle need not be a complete delivery slice. When integration feasibility is the risk, first exercise the narrowest real end-to-end path rather than relying on isolated green tests.

## Red → Green → Refactor

1. **Pick one behaviour.** Define its observable expectation and check whether existing tests already protect it.
2. **Red.** Write the smallest useful failing test. Run it and confirm failure comes from the target behaviour being missing or wrong, not a broken fixture, environment, or unrelated syntax error. If it is already green, investigate before claiming a red step or adding redundant coverage.
3. **Green.** Implement the simplest correct behaviour needed for this cycle without speculative features.
4. **Refactor when useful.** Remove duplication or unnecessary complexity exposed in the touched code. Keep behaviour unchanged and rerun the test and the smallest affected regression set. No mandatory extraction, abstraction, or separate refactoring pass is required for each cycle.
5. **Continue.** Select the next confirmed behaviour using the feedback. Shared-design changes or unrelated cleanup exceed this cycle; return them to the caller.

For a bug fix, reuse an available minimised reproduction and diagnosis, turn it into a regression test, and rerun the original reproduction after the fix. If the cause is still unknown, investigate it (using `debug` when useful) before choosing a speculative fix.

## Stop and report

Report the behaviours covered, expected-result sources, actual red/green commands and observations, scoped refactoring, and remaining gaps. If a check could not run, say so; do not claim a completed TDD cycle. Never weaken expectations to obtain green.

When a useful, affordable test-first loop cannot be built, report the limitation and continue with the caller's appropriate verification method. Do not force TDD on every task, manufacture production hooks, or create a coverage target. Passing these tests supports only their exercised behaviours; required independent verification and review still apply.
