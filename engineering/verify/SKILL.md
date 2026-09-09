---
name: verify
description: Verify a ticket's Acceptance Criteria in an independent read-only context.
---

# Verify

Against the implementation snapshot Loop supplies, verify ticket-local Acceptance Criteria. The question is whether it works as required, and what the evidence is. Do not judge code or design quality.

## Boundary with `code-review`

Verify observable results and completion conditions only. Coding standards, design quality, smells, whether an abstraction earns its keep, and implementation style belong to `code-review`.

## Process

1. Extract verifiable completion conditions from the user request, SPEC, ticket, and handoff bundle. With no explicit conditions, verify only what can be confirmed objectively. Do not expand the requirement.
2. Choose the smallest verification that matches change scope and risk: targeted tests, lint, typecheck, build, runtime checks, interface calls, static search, diff checks, or verification entries the project already has. Prefer existing scripts, Make targets, CI commands, and test entries. Do not add production code or test-only interfaces just to verify.
3. Record the commands actually run, key output, and failures. Mark checks that could not run as unverified. Reading code is not a substitute for run evidence. Return `passed` or `not_verified` per completion condition with evidence that can be rechecked. On a clear failure, set the capability outcome to `failed` and list findings. Do not disguise a failure as passing AC evidence.

Record each evidence item with these fields, as-is:

```json
{"acceptance_id":"AC1","result":"passed","summary":"..."}
```

`verify` records the actual `command`, `exit_code`, and a summary. Do not fabricate command exit codes. Add scenario mapping only when the task explicitly enabled structured acceptance.

CLI capability JSON envelope, fields, and examples: [Runtime output contract](../../docs/loop-runtime.md#capability-result).

## Boundaries

Read-only by default. Do not edit code, SPEC, HLD, tickets / graph, or external business state. Loop by default allows isolated temp test artifacts and caches only under `.loop/tmp/`. Other paths require an explicit Loop allocation. On failure, return evidence. Cause-finding goes to `debug`. Implementation-quality judgement goes to `code-review`.

When done, return a capability receipt with at least ticket / attempt identity, AC evidence, verification, unverified scope, and outcome. Do not schedule sibling tickets, edit the graph, or commit version-control changes.
