---
name: pi-agent
description: Use Pi for external review or bounded implementation.
---

# Pi Agent

Use Pi's native CLI and session files. Do not start an MCP server, daemon, or persistent background Pi process.

## Route the request

Choose exactly one mode and read its reference:

- Adviser or second opinion: [adviser.md](references/adviser.md)
- Independent multi-model review: [committee.md](references/committee.md)
- User-authorized code implementation: [implementer.md](references/implementer.md)

For every mode, also read:

- [session-protocol.md](references/session-protocol.md)
- [error-handling.md](references/error-handling.md)

## Shared constraints

- Verify `pi` is installed and the requested model is available before starting: run `pi --list-models` and check the model appears in its output. `pi` has no `model list` subcommand — `pi model list` is parsed as a chat prompt, not a CLI command.
- Store prompts, reports, metadata, and Pi JSONL sessions outside the target repository under `PI_SKILLS_STATE_HOME`.
- Run one foreground `pi --print` turn at a time per member. After the turn, Pi must exit.
- Continue only with the exact absolute JSONL path passed to `pi --session`; never use `--continue` or `--resume`.
- Review modes enable only `read,grep,find,ls`.
- Implementation mode requires an isolated clean linked Git worktree and explicit `allowed_paths`.
- Do not commit, push, change branches, rewrite history, delete the worktree, or modify Git metadata from Pi.
- Treat Pi output as an external claim. The primary agent must inspect source, diff, configuration, and verification evidence before accepting it.
- Do not auto-retry failed turns. Report bounded failure state and let the primary agent decide whether new evidence justifies another turn in the original session.

Use the provider environment extension only when runtime provider registration is needed. It is a no-op when `PI_SKILLS_PROVIDER_*` variables are absent.

For long-running turns, optionally load `extensions/heartbeat.js` with an absolute `PI_SKILLS_HEARTBEAT_FILE` outside the target repository. The extension only emits phase and freshness evidence; use `extensions/heartbeat_monitor.js` from the host to classify it. Do not treat a fresh heartbeat as proof of task success.
