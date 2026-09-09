---
name: simplify
description: "Review or remove complexity in existing code or the current diff that has no current responsibility."
---

# Simplify

Reduce the concepts, state, contracts, and implementation paths the codebase must keep consistent over time. Deleting lines is a result, not the goal; finding nothing safe to delete is a valid result.

Look for complexity without a current production responsibility, especially maintenance created by legacy leftovers, AI coding, test convenience, expired migrations, and speculative extensibility. This skill investigates complexity that already exists. It does not clean up old paths that `implement` should have removed as part of the current change.

## Modes

- **Review**: inspect and report evidence-backed simplification candidates without modifying code.
- **Modify**: remove, merge, or replace unnecessary complexity within the authorized scope and validate the result. Modification requires explicit authorization.

Default to the current diff or an explicitly requested responsibility. Use broader repository investigation only when requested or when dynamic consumers cannot be resolved locally.

## Rules

- Prefer removing an unnecessary responsibility completely over making its implementation smaller.
- Do not preserve abstractions, compatibility paths, fallbacks, extension points, or production interfaces without a current responsibility or a confirmed contract.
- Tests, fixtures, examples, documentation, or historical usage alone do not justify keeping a production contract.
- Production architecture that exists primarily to support tests is a strong simplification candidate when no real production variability or boundary requires it.
- Static search and code smells identify candidates, not proof. Check real callers, external boundaries, persisted data, and dynamic consumers before deletion.
- Do not move complexity elsewhere merely to reduce local code.
- Do not change confirmed requirements or public contracts as part of simplification; if that change is required, stop and report the upstream decision needed.
- After modification, check for leftovers and run the smallest validation capable of detecting incorrect removal.

Read `references/candidates.md` when generating candidates. Read `references/investigation.md` only when consumer ownership or dynamic behavior is unclear.

## Output

For review, report meaningful candidates with evidence and expected maintenance reduction.

For modification, report what was removed or merged, validation performed, and anything intentionally kept because evidence was insufficient.
