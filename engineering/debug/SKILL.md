---
name: debug
description: Diagnosis loop for hard bugs, non-deterministic failures, and performance regressions. Fixing requires explicit authorisation.
---

# Debug

A discipline for confirmed runtime problems. Do not divert bug work into SPEC or ticket splitting.

When exploring the codebase, discover domain docs, ADRs / decision records, and coding standards the way the project already lays them out. Check the working tree before editing. Do not assume these files live at a fixed path.

## Authorisation

Write down expected behaviour, actual behaviour, and where the expectation comes from. If the expectation is unconfirmed, do not change code. Name the evidence gap and suggest `grilling`.

When the user asked for a fix, continue to the smallest fix after the bug is confirmed. When they asked only to diagnose, analyse, or investigate, stop at diagnosis.

- Confirmed bug: fix the root cause, not the symptom.
- Insufficient evidence, or not a bug: do not change code. Name the gap.
- Do not commit, push, create a branch, or rewrite history on your own.
- Skip a diagnosis phase only when the repro already isolates the root cause and the evidence can support a minimal fix — and say why.
- Cross-layer, intermittent, environment, or performance problems run the full loop.

## Redact

This skill has you show commands, outputs, and captured artifacts. **Redact every secret first** — write `<REDACTED>` in its place. Keep credentials in env vars, not in the command or the output. Quote only the lines that carry the signal.

## Phase 1 — Build a feedback loop

**This is the skill.** Everything else is mechanical. If you have a **tight** pass/fail signal for the bug — one that goes red on *this* bug — you will find the cause. If you don't, later phases just guess.

Prefer one command that can go red on *this* bug and that you can re-run:

1. A failing test at the seam on the real call path.
2. curl, CLI, browser automation, or a captured-trace replay.
3. A throwaway harness or script last.

If cheap options cannot produce a red signal, escalate using `references/feedback-loop-escalation.md` — construction order, tightening for diagnostic value, and non-deterministic strategy.

The loop must assert the user's exact symptom, not "didn't crash".

Phase 1 is done when you can name **one command** you have **already run at least once** (show the invocation and its redacted output) that is:

- **Red-capable** — it drives the actual bug path and asserts the user's exact symptom, so it can go red on this bug and green once fixed.
- **Repeatable** — same verdict every run, or, for flaky bugs, a recorded reproduction rate high enough to debug against.
- **Agent-runnable** — you can run it unattended; a human in the loop only via `scripts/hitl-loop.template.sh`.

While building the loop, you may inspect code, logs, and the environment as read-only inputs. Do not move to repair decisions or execution until a red-capable command exists.

When you genuinely cannot build a loop: stop and say so. List what you tried. Ask for access to the reproducing environment, a redacted captured artifact (HAR, log dump, recording), or permission to add temporary instrumentation. Do **not** proceed to hypothesise without a loop.

## Phase 2 — Reproduce + minimise

Run the loop. Confirm it produces the failure the **user** described — not a nearby different failure. Record how reproducible it is.

Cut inputs, callers, config, and steps one at a time until every remaining element is load-bearing. Capture the exact symptom: error, wrong output, or wrong timing.

Do not proceed until you have reproduced **and** minimised.

## Phase 3 — Hypothesise

List falsifiable hypotheses ranked by current evidence. If the evidence supports one strong hypothesis, do not invent extras to pad the list.

Each hypothesis must state a prediction:

> If <X> is the cause, then <changing Y> will make the bug disappear / <changing Z> will make it worse.

Show the ranked list to the user. Don't block on a reply. Change one variable at a time.

## Phase 4 — Instrument

Each probe maps to a Phase 3 prediction.

1. Debugger / REPL if the env supports it.
2. Targeted logs at the boundaries that distinguish hypotheses.
3. Never "log everything and grep".

Tag every debug log with a unique prefix, e.g. `[DEBUG-a4f2]`. Cleanup becomes one grep.

For performance regressions: measure a baseline first, then locate the regression and change the code. Do not substitute generalized logs for measurement.

## Phase 5 — Fix + regression test

Diagnosis-only mode stops here. Report root cause, ruled-out hypotheses, impact bounds, and behaviour the fix must preserve.

Default fix mode:

1. Turn the minimised repro into a regression test on the real production construction, public entry, and same call path.
2. Watch it fail.
3. Apply the smallest root-cause fix.
4. Watch it pass.
5. Re-run the original, un-minimised Phase 1 loop.

If no correct seam exists, do not expose `forTest`, mutable callbacks, delay parameters, noops, or internals. Consult `codebase-design` when the Seam / Interface itself may need to move. Do not widen a production API for tests unless that production change is justified.

## Phase 6 — Simplify only when needed

After the fix and regression pass, call `simplify` only when the current diff has a clear complexity problem or the user asks. Do not make simplify a required Debug stage.

- `completed` with edits: re-run related tests and the applicable targeted static, format, and diff-whitespace checks.
- `no_change`: keep the receipt; reuse verification that is still valid.
- `blocked` or `failed`: stop and report. Do not pretend done.

Simplification must not change error handling, lifecycle, concurrency, cancel, protocol, or user-observable behaviour.

## Phase 7 — Cleanup

Before declaring done:

- Original repro no longer reproduces (re-run the Phase 1 loop).
- Regression test passes, or the missing seam is recorded.
- All `[DEBUG-...]` instrumentation and throwaway scripts are gone.
- Cross-session diagnosis docs are cleaned up per project convention, or their keep-reason is stated.
- `simplify`, if run, returned `completed` or `no_change`.
- The report names root cause, change, validation, unverified items, and remaining risk.

If the problem needs an architecture change, hand to `review-architecture` *after* the fix. Do not widen this debug.

## Across sessions

Create a minimal diagnosis checkpoint only when the work cannot finish in this session. Prefer the target repo's existing task / debug convention. With no convention, ask or keep state in the current session — do not invent a fixed filename at repo root.

The checkpoint records symptom, expectation source, feedback command, observations, tested hypotheses, root-cause status, and next step. A new session reads it and continues from verified state. After the problem is solved, confirmed not a bug, or abandoned, state whether that checkpoint was cleaned or kept. Do not leave stale diagnosis as fact.
