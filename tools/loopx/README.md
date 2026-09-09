# loopx

`loopx` is the shared engineering workflow CLI for ticket graphs and Loop capability orchestration.

```bash
python3 -m pip install ./tools/loopx
loopx --help
loopx graph inspect <task-dir>
loopx worker providers
loopx worker run <workspace> --scope src/ --prompt "实现 XXX 需求，修改限于 src/"
```

The CLI emits versioned JSON on stdout. The `worker` command is an internal Loop adapter.

When `--provider` is omitted, loopx uses the current runtime provider when detected (or `LOOPX_RUNTIME_PROVIDER`), then falls back to available providers.

Tests: `cd tools/loopx && PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`.

Build: `python3 -m pip wheel --no-deps tools/loopx` (requires an available setuptools build backend).

Runtime package checks: `python3 tools/loopx/scripts/check.py all`.

Task acceptance uses the task's SPEC and verify evidence. An independent ACCEPTANCE.md is optional; Loop does not execute a second copy of verification commands.
