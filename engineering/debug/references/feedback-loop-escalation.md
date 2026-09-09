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
10. HITL bash script ([`scripts/hitl-loop.template.sh`](../scripts/hitl-loop.template.sh)): last resort when a human must click. The script still structures the loop and captures output.

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

Until a red-capable loop exists, do not proceed to repair decisions. You may inspect code, logs, and the environment as read-only inputs needed to *build* the loop. Do not change code when the evidence cannot support a fix conclusion.
