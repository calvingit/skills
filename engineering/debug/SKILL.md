---
name: debug
description: Reproduce, locate, and fix confirmed runtime problems, including hard-to-reproduce, non-deterministic failures and performance regressions. Diagnosis-only requests stop at the root cause without changing code.
---

# Debug

Debug like an experiment: every changed line traces to runtime evidence. Belt-and-suspenders that "might help" is a hypothesis, not a fix. When evidence refutes a hypothesis, revert what it motivated. Do not divert bug work into SPEC or ticket splitting.

Discover domain docs, ADRs / decision records, and coding standards the way the project already lays them out. Check the working tree before editing.

## Before you start

- Write down expected behaviour, actual behaviour, and where the expectation comes from. If the expectation is unconfirmed, do not change code: name the gap and tell the user to run `grilling`.
- When the user asked only to diagnose, analyse, or investigate, stop at the root cause. Continue to a fix only when they asked for one.
- Do not commit, push, create a branch, or rewrite history on your own.
- Redact every secret in commands, outputs, and user-supplied material as `<REDACTED>`. Keep credentials in env vars.

## 1. Reproduce it yourself

- Drive every means you have before asking the user. Prefer, in order: a failing test on the real call path; curl / CLI / browser automation; replay of a captured request, trace, or log; a throwaway script last.
- The repro must assert the user's exact symptom — not "didn't crash", and not a nearby different failure.
- For non-deterministic bugs, record the observed reproduction rate and conditions. No hard run counts or thresholds; a rate that can distinguish hypotheses is enough.
- When you cannot reach a matching environment, ask the user for specific items: environment URL, test account (via env vars or a disposable account, never pasted in plain text), repro steps, logs / HAR / recording. Say why you need them and how far you got.
- Once it reproduces, minimise: cut inputs, config, and steps one at a time until every remaining element is load-bearing.
- If it still cannot be reproduced, continue read-only investigation. Label every hypothesis from logs or call chains as unverified, and record the non-reproducible scope as a verification limit. An unverified hypothesis is never written as the root cause.

## 2. Binary-search the cause

- List falsifiable hypotheses, each with a prediction: "If X is the cause, changing Y makes the bug disappear; changing Z makes it worse."
- Each round, take the split that cuts the most remaining possibilities, get runtime evidence, eliminate. Don't guess.
- When program state is unclear, instrument: debugger or REPL first, then targeted logs at distinguishing boundaries. Tag every debug log with a unique prefix such as `[DEBUG-a4f2]`. Never "log everything and grep".
- For performance regressions, measure a baseline first.
- If the subsystem is unfamiliar or a regression is suspected, trace code paths and history the way `how` / `why` would, or suggest the user run those skills. Do not call them from debug.
- Before fixing, the surviving mechanism must have runtime evidence that distinguishes it from rival explanations.

## 3. Fix

- Fix the root cause with the smallest change the evidence justifies. If the same pattern exists elsewhere, point it out.
- If no correct seam exists, do not expose `forTest`, mutable callbacks, delay parameters, or internals. Call the Skill tool with "codebase-design" when the Seam / Interface itself may need to move.

## 4. Regression test

- When a local test is cheap, turn the minimised repro into a test on the real production construction and call path. Watch it fail, fix, watch it pass (same cadence as `tdd`).
- When the test would be expensive, integration-heavy, or unclear, skip it and state why in the report.

## 5. Verify on the same surface

- Re-run the original, un-minimised repro from step 1. It must pass.
- "Inconclusive" or a different environment is not a pass. Unit tests show branch behaviour, not bug absence.
- Real-environment verification is optional. Without one, verify on the closest available environment and state "not verified in real environment" and what that gap leaves open.

## 6. Close out

- Remove all `[DEBUG-...]` instrumentation and throwaway scripts. Clean cross-session diagnosis notes per project convention, or state why they are kept.
- Call the Skill tool with "simplify" only when the diff has a clear complexity problem or the user asks.
- Suggest the commit order: failing test first, fix on top. The user decides whether to commit.
- If the problem needs an architecture change after the fix, tell the user to run `review-architecture`. Do not widen this debug.

## Report

What was broken / root cause / fix / how you verified. Paste redacted failing-then-passing repro output verbatim. End with unverified items and remaining risk.

## Across sessions

When the work cannot finish in this session, leave a minimal checkpoint in the project's existing convention: symptom, expectation source, repro command, ruled-out hypotheses, next step. Do not invent a fixed filename at repo root. After the problem is solved or abandoned, say whether the checkpoint was cleaned or kept.
