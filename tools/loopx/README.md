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


Each `loop run` executes one attempt, serially: implement → verify → review. The caller continues on `retry` and selects the next ticket after `completed`; a frontier batch stops on any other result. `--ticket T001` selects an explicit recovery target. There are no ticket/capability parallelism switches in this runtime.

After a requirement change, stop workers and block active attempts before reconciliation. Graph `stale_authority` identifies tickets needing an impact decision; `retain_contract` confirms unchanged contracts/evidence without discarding historical done records. See [amendment rules](../../engineering/to-tickets/references/amendment.md).

Final delivery is separate from `all_active_done`:

```bash
loopx loop delivery-prepare <task-dir> --workspace <repo-root>
# Run verify and code-review on this snapshot; save their receipt under <task-dir>/.loop/.
loopx loop delivery-complete <task-dir> --input <task-dir>/.loop/delivery-input.json
loopx loop status <task-dir>
```

The final receipt must cover all current SPEC AC IDs. Changes to requirements, graph, Git HEAD, workspace code or submodules invalidate it. Commands and receipt format: [final review](../../engineering/loop/references/delivery-review.md).
