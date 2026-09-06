#!/usr/bin/env python3
"""Single reproducible acceptance entrypoint for loopx."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "tools" / "loopx"


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("$", " ".join(command), file=sys.stderr)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def unit() -> None:
    run([sys.executable, "-m", "unittest", "discover", "-s", "tools/loopx/tests", "-p", "test_*.py"])


def cli() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PACKAGE / "src")
    for command in (("--help",), ("version",), ("loop", "run", "--help"), ("worker", "--help"), ("worker", "providers"), ("graph", "inspect", "--help")):
        run([sys.executable, "-m", "loopx", *command], env=env)


def package() -> None:
    with tempfile.TemporaryDirectory(prefix="loopx-check-") as directory:
        output = Path(directory)
        run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", str(output), str(PACKAGE)])
        wheel = next(output.glob("loopx-*.whl"))
        venv = output / "venv"
        run([sys.executable, "-m", "venv", str(venv)])
        pip = venv / "bin" / "pip"
        executable = venv / "bin" / "loopx"
        run([str(pip), "install", "--no-index", "--no-deps", str(wheel)])
        run([str(executable), "--help"])
        run([str(executable), "version"])
        names = subprocess.check_output([sys.executable, "-c", "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1]); print('\\n'.join(z.namelist()))", str(wheel)], text=True)
        if "loopx/contracts/worker-result.schema.json" not in names or "loopx/contracts/cli-envelope.schema.json" not in names:
            raise RuntimeError("wheel is missing public contract schemas")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=("unit", "cli", "package", "all"))
    target = parser.parse_args(argv).target
    if target in {"unit", "all"}: unit()
    if target in {"cli", "all"}: cli()
    if target in {"package", "all"}: package()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
