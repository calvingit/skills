# loopx

`loopx` is the shared engineering workflow CLI for ticket graphs and provider-neutral workers.

```bash
python3 -m pip install ./tools/loopx
loopx --help
loopx graph inspect <task-dir>
loopx worker providers
loopx worker run <workspace> --prompt "实现 XXX 需求，并运行验证命令"
```

The CLI emits versioned JSON on stdout. Provider-specific commands are internal adapters; callers use the prompt-based `worker` interface.

When `--provider` is omitted, loopx uses the current runtime provider when detected (or `LOOPX_RUNTIME_PROVIDER`), then falls back to available providers.

Tests: `cd tools/loopx && PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_*.py'`.

Build: `python3 -m pip wheel --no-deps tools/loopx` (requires an available setuptools build backend).

Acceptance: `python3 tools/loopx/scripts/check.py all`.
