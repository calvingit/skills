# Session Protocol

Use Pi's own JSONL session as the only conversation history. The filesystem records where that session and its round artifacts live; it does not duplicate messages in a ledger.

## State root

Resolve the state root without writing to the target repository:

```text
PI_SKILLS_STATE_HOME
or XDG_STATE_HOME/pi-skills
or ~/.local/state/pi-skills
```

Use a stable repository ID derived from the canonical repository root plus a short path hash. Use safe `run-id` and `member-id` values containing only letters, digits, dot, underscore, and hyphen.

```text
<state-home>/<repo-id>/<run-id>/<member-id>/
├── prompt-round-1.md
├── report-round-1.md
├── session.jsonl
├── heartbeat.json       # when heartbeat observation is enabled
└── RUN.md
```

`RUN.md` records mode, canonical workspace path, model, member, exact session path, round number, command exit status, result status, and timestamps. Never record credentials, gateway URLs, request headers, or sensitive prompt data in it.

## First turn

The host performs the implementer preflight before starting this turn: verify Pi and model availability, provider readiness, clean worktree and ownership boundaries, and the task timeout. The preflight does not predict failures that arise later during provider requests or project commands.

Create a new empty member directory and write the complete prompt to `prompt-round-1.md`. Run Pi from the target repository or worktree:

For heartbeat observation, set an absolute path inside the member directory before starting Pi:

```bash
HEARTBEAT_FILE="$MEMBER_DIR/heartbeat.json"
export PI_SKILLS_HEARTBEAT_FILE="$HEARTBEAT_FILE"
export PI_SKILLS_HEARTBEAT_INTERVAL_MS="${PI_SKILLS_HEARTBEAT_INTERVAL_MS:-5000}"
```

```bash
pi \
  --model "$MODEL" \
  --tools read,grep,find,ls \
  --session-dir "$MEMBER_DIR" \
  --name "$RUN_ID-$MEMBER_ID" \
  --no-extensions \
  --extension "$PI_AGENT_SKILL/extensions/provider_env.js" \
  --extension "$PI_AGENT_SKILL/extensions/heartbeat.js" \
  --no-skills \
  --no-prompt-templates \
  --print "@$PROMPT_FILE" > "$REPORT_FILE"
```

Implementation mode replaces the tool list and adds the worktree guard as described in [implementer.md](implementer.md).

While the host execution is running, poll the latest state with:

```bash
node "$PI_AGENT_SKILL/extensions/heartbeat_monitor.js" "$HEARTBEAT_FILE" 15000 120000
```

The first timeout is heartbeat freshness; the second is business-progress freshness. Keep the task-level process timeout separate. A `waiting` result is evidence of prolonged provider/tool inactivity, not proof of a deadlock.

Use the host execution session or PTY for long turns so the primary agent can poll, cancel, and terminate the exact process. The timeout budget belongs to that host call and must be chosen for the task; it is not fixed by this Skill.

After Pi exits:

1. Check the real exit status.
2. Require a non-empty report.
3. Find JSONL files directly inside the new member directory. Require exactly one.
4. Rename that file to `session.jsonl` if necessary and record its exact absolute path.
5. Update `RUN.md` and confirm no Pi process from this turn remains.

If Pi exits before persisting a unique session, do not invent a path or use the latest global session.

## Follow-up turn

Write only the new evidence and question to the next prompt file, then resume the exact member session:

```bash
pi \
  --session "$SESSION_FILE" \
  --model "$MODEL" \
  --tools read,grep,find,ls \
  --no-extensions \
  --extension "$PI_AGENT_SKILL/extensions/provider_env.js" \
  --extension "$PI_AGENT_SKILL/extensions/heartbeat.js" \
  --no-skills \
  --no-prompt-templates \
  --print "@$FOLLOW_UP_FILE" > "$NEXT_REPORT_FILE"
```

Require `SESSION_FILE` to equal the path already recorded for that member. Increment the round only after a successful non-empty report. Do not create a fresh session for disagreement with an existing finding.

## Completion states

- `completed`: requested members or implementation turn completed and artifacts are valid; this is not code acceptance.
- `partial`: at least one committee member completed and at least one failed.
- `failed`: no requested turn produced a usable report/session.
- `blocked`: the turn could not start because a prerequisite, permission, model, or policy check failed.
- `ownership_request`: implementation reached a real seam outside the declared slice; the primary agent must decide whether to resize the task.
- `accepted`: only the primary agent may emit this after independent verification, simplification, and review.
- `rejected`: the primary agent found an out-of-scope, incorrect, or unverified result.
