---
name: kimi-worker
description: Use when the user explicitly asks to use Kimi/kimi CLI for a focused code implementation, bug fix, refactor, or test change in the current repository.
---

# Kimi Worker

Delegate a concrete coding task to Kimi CLI through a thin script while keeping the caller as the coordinator. Provide only goal, acceptance criteria, constraints, starting points, and verification commands, not a full code analysis.

## Workflow

1. Do not pre-read implementation files just to prepare Kimi input.
2. Summarize the task as a short request with:
   - `task_goal`
   - `acceptance_criteria`
   - `known_constraints`
   - `starting_points`
   - `forbidden_changes`
   - `verification_commands`
3. Run the bundled script from the repo root:

```bash
bash "$SKILL_PATH/scripts/kimi-worker" '<task summary>'
```

For multiline input, pipe stdin:

```bash
bash "$SKILL_PATH/scripts/kimi-worker" <<'TASK'
task_goal:
- ...

acceptance_criteria:
- ...

verification_commands:
- ...
TASK
```

## Input Rules

- Keep `starting_points` to paths, symbols, errors, or reproduction hints.
- Do not paste full source files, long logs, call-chain analysis, line-by-line implementation steps, or large docs.
- Do not provide an allowed-files list unless the user explicitly requires a hard file limit.
- Use `forbidden_changes` for real boundaries: no commit/push/branch/history rewrite, no dependency changes, no generated files, no unrelated worktree edits.

## After Kimi

Inspect Kimi output and the repo diff. Run or verify the requested commands. Report:

- changed files
- summary of behavior changed
- verification commands and results
- blockers or risks

Use `KIMI_WORKER_DRY_RUN=1` before the script command to inspect `/tmp/kimi_prompt.txt` without invoking Kimi.
