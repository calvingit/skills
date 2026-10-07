# Feedback-loop escalation

Phase 1 of `debug`, in more detail: how to construct a feedback loop, how to tighten it for diagnostic value, and what to do with non-deterministic bugs. Top to bottom: get a red signal cheaply, then escalate.

## Construction order

1. Failing test at the seam on the real call path.
2. Curl / HTTP script against a running service.
3. CLI plus fixture input, stdout diffed against a known-good snapshot.
4. Headless Playwright / Puppeteer script asserting on DOM / console / network.
5. Replay a captured trace (network request, payload, event log).
6. Throwaway harness (one service + mocked deps, one call that hits the bug path).
7. Property / fuzz loop: 1000 random inputs looking for the failure mode.
8. Bisection harness: automate "boot at state X, check, repeat" between two known states, for `git bisect run`.
9. Differential loop: same input through old vs new (or two configs), diff the outputs.
10. Human-in-the-loop capture when a person must act: use the host-native interactive mechanism or [`scripts/hitl-loop.template.sh`](../scripts/hitl-loop.template.sh), keeping the actions and observations re-runnable and recorded.

## Tighten the loop

Once you have *a* loop, improve it for diagnosis. Don't polish it into a general product:

- Sharper: assert the user's exact symptom, not "didn't crash".
- Repeatable: record whether it reproduces, under what conditions, and the known failure rate. Pin time, RNG, filesystem, or network when you can. Don't stall on tooling to chase unattainable determinism.
- Fast enough: cache setup, skip unrelated init, narrow the test. Iteration cost should match the current hypothesis. Count and duration are set by the failure. Slow integration, device paths, and rare races may stay slow if they still distinguish hypotheses.

A fast, deterministic, unattended loop is preferable. It is not the bar for starting investigation.

## Non-deterministic bugs

The goal is a reproduction rate high enough to distinguish hypotheses. Loop count, parallel stress, timing windows, and injected sleeps are set by the failure. Continue once the evidence can support or kill the current hypothesis. Don't mandate 100 runs, or 50% / 1% as hard thresholds. Record the rate you observed.

## Evidence before a fix

Name one command you have already run, or a set of observations that together distinguish the current hypothesis:

- It drives the real bug path and asserts the user's exact symptom, and should go green after the fix.
- Reproducibility is recorded, not a one-off impression.
- Performance problems have a baseline first, then measurement rather than generalised logs.

Do not execute a fix until the evidence distinguishes the cause from competing explanations and the change is authorized. Prefer a red-capable loop. When the available environment cannot reproduce, a recorded distinguishing observation set may support a repair decision; keep the unavailable reproduction and regression checks as verification limits. Continue useful read-only investigation and label unresolved hypotheses. Neither an observation set nor a loop alone proves the fix passed.
