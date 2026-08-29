# Implementer

Use this mode only when the user explicitly authorizes Pi to implement a bounded code task. Pi works in an isolated linked Git worktree; the primary checkout is never an implementation target.

## Five-stage execution contract

1. **Preflight**: the host verifies Pi, the requested model/provider, a clean linked worktree, `allowed_paths`, ownership reservations, and a task-appropriate timeout before starting the implementation turn. A preflight result reduces startup risk; it does not guarantee that later provider, approval, or tool failures cannot occur.
2. **One slice**: the prompt names one independently reviewable acceptance criterion, its owned paths, allowed commands, and a narrow verification command. Pi must return `ownership_request` when the real seam exceeds that boundary instead of expanding scope.
3. **Bounded implementation**: Pi edits only the owned slice and may run the narrow verification. It does not decide cross-slice architecture or acceptance.
4. **Primary-agent acceptance**: after Pi exits, the primary agent inspects the real diff and call paths, runs the complete required verification, then performs simplification and review.
5. **Disposition**: only the primary agent classifies the result as `accepted`, `rejected`, or a handoff to a clean worktree. `completed` means only that the Pi turn produced valid artifacts, not that the code was accepted.

The implementation prompt must state the slice, acceptance criterion, `allowed_paths`, allowed commands, verification command, timeout expectation, and prohibition on taking ownership of later slices.

## Preconditions

Before starting, verify all of the following from the host:

1. `workspace_path` is the canonical root of a linked Git worktree.
2. `.git` is a file, not a directory.
3. `git status --porcelain` is empty.
4. `allowed_paths` is a non-empty JSON array of repository-relative paths.
5. No path is absolute, contains `..`, targets `.git`, or escapes through a symlink.
6. No other active Pi implementation owns the same canonical worktree. Reserve it under the external state root for the duration of the turn and remove the reservation only after the exact Pi process exits.

If a previous reservation appears stale, confirm its recorded process is gone before removing it. Do not guess.

The host preflight must run before creating the formal implementation prompt or allowing edits. If a prerequisite fails, return a bounded `blocked` or `failed` result and do not start the implementation turn.

## Invocation

Write the agreed task, constraints, allowed paths, required verification, and prohibition on Git mutations into the prompt. Then run:

```bash
PI_SKILLS_WORKTREE="$WORKTREE" \
PI_SKILLS_ALLOWED_PATHS="$ALLOWED_PATHS_JSON" \
PI_SKILLS_HEARTBEAT_FILE="$MEMBER_DIR/heartbeat.json" \
pi \
  --model "$MODEL" \
  --tools read,grep,find,ls,bash,edit,write \
  --session-dir "$MEMBER_DIR" \
  --name "$RUN_ID-$MEMBER_ID" \
  --no-extensions \
  --extension "$PI_AGENT_SKILL/extensions/provider_env.js" \
  --extension "$PI_AGENT_SKILL/extensions/worktree_guard.js" \
  --extension "$PI_AGENT_SKILL/extensions/heartbeat.js" \
  --no-skills \
  --no-prompt-templates \
  --print "@$PROMPT_FILE" > "$REPORT_FILE"
```

Pi may inspect code, edit owned paths, run targeted tests/analyzers/formatters, and run necessary code generation. It may not commit, push, create/delete/switch branches, reset, clean, rebase, change remotes, modify `.git`, write outside the worktree, or bypass the guard with another interpreter or shell.

The guard is a defense-in-depth policy for a trusted agent, not an OS sandbox. Bash can invoke project scripts, so use this mode only with trusted repositories, prompts, providers, and models.

## Primary-agent verification

After Pi exits, the primary agent must:

1. Read the real `git status --porcelain` and complete diff.
2. Reject any changed path outside `allowed_paths` as `policy_violation`; preserve the diff for inspection instead of hiding it.
3. Inspect the implementation and its actual call paths.
4. Independently run the minimum necessary verification; Pi's report is not proof.
5. Run the repository's simplification step when applicable.
6. Perform the primary-agent review and independent Pi cross-review required by the project workflow.
7. Classify the result as `accepted` only after those checks pass. Otherwise preserve the diff and classify it as `rejected` or `partial`.
8. Leave commit, push, worktree removal, and rollback decisions to the primary agent/user workflow.

On a failed or blocked turn, preserve the prompt, report fragment, session, and diff. The primary agent may continue in place only when the diff is small, in-scope, and directionally clear; otherwise use a clean linked worktree. Never discard or auto-continue a partial diff without inspection.
