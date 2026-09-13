# Incremental Audit

Review risks introduced or worsened by the selected change. Use `code-review` when available for change review standards; this prompt contributes baseline selection and the dimensions requested for the project audit. Shared report requirements live in `references/report-format.md`.

## Establish the baseline

Record the actual commit IDs and comparison meaning before inspecting the patch:

- Branch / PR review: resolve the merge base of the target branch and HEAD, then compare that commit with HEAD. `git diff <target>...HEAD` expresses this comparison. Target-branch-only changes must not be attributed to the reviewed branch.
- Explicit endpoint comparison, such as two releases: `git diff <old> <new>` (equivalently `<old>..<new>`). Two-dot diff compares endpoints, not the branch point.
- One commit: inspect that commit's patch relative to its parent. A merge commit requires an explicit parent/comparison meaning.
- Working tree: inspect staged and unstaged changes and relevant untracked files, keeping existing user edits distinct.

Use the user's requested comparison. Resolve an ambiguous or invalid baseline before drawing conclusions; do not silently reinterpret an explicit endpoint range as a branch review. Use the same baseline for file lists and line-level diffs.

## Inspect the change

Trace changed behaviour through unchanged callers, dependencies, tests, configuration, and deleted or renamed paths. Compare against confirmed requirements. Existing unrelated defects do not become regressions because they appear in a changed file.

Evaluate missing tests only when a concrete changed behaviour lacks meaningful verification; report the scenario and consequence. A widely used module increases the area to inspect, not severity automatically. Rank findings by actual impact and scale report detail to the change.
