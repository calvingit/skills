# Codex CLI Usage

## Execution Modes

## Analysis

Use for investigation without modification.

```bash
codex exec --sandbox read-only "task"
```

## Write

Use for authorized changes.

```bash
codex exec --sandbox workspace-write --full-auto "task"
```

## Full Access

Only use when explicitly approved.

```bash
codex exec --sandbox danger-full-access --full-auto "task"
```

## Structured Output

For agent-to-agent workflows prefer JSON output when supported by the installed Codex CLI version.

Example:

```bash
codex exec --json "task"
```

## Session

Prefer explicit session identifiers when multiple agents are running.

`--last` is a convenience shortcut, not a reliable multi-agent identifier.
