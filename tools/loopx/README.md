# loopx

Ticket state and delivery progress helpers for Engineering Skills. Loop uses the current runtime's native subagents; this package does not start agents, select providers, manage sessions, or parse their reports.

```bash
python3 -m pip install ./tools/loopx
loopx graph inspect <task-dir>
loopx graph start --help
loopx loop status <task-dir>
loopx loop delivery-prepare <task-dir> --workspace <repo-root>
loopx loop delivery-complete <task-dir> --input <task-dir>/.loop/delivery-input.json
```

Commands emit JSON state records. Subagent reports remain text/Markdown strings, interpreted by Loop. There is no worker command or loop run command. See [state commands and completion inputs](../../docs/loop-runtime.md).

Tests, CLI, wheel build, and clean installation: `python3 tools/loopx/scripts/check.py all` from the repository root. Package checks use the locally installed setuptools (>=68) and wheel without network dependency downloads.

This is an unreleased contract change: previous worker receipts and completion inputs are not supported. Current completion input uses the original review string and the caller's explicit approval; no schema converter or migration layer is provided. Existing ticket history is not automatically rewritten.
