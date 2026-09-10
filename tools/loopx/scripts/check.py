#!/usr/bin/env python3
"""Single reproducible acceptance entrypoint for loopx."""

from __future__ import annotations

import argparse
import os
import shutil
import zipfile
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
    for command in (("--help",), ("version",), ("loop", "status", "--help"), ("loop", "delivery-complete", "--help"), ("graph", "inspect", "--help")):
        run([sys.executable, "-m", "loopx", *command], env=env)


def package() -> None:
    with tempfile.TemporaryDirectory(prefix="loopx-check-") as directory:
        output = Path(directory)
        source = output / "source"
        # A reused setuptools build directory can ship modules deleted from src.
        shutil.copytree(PACKAGE, source, ignore=shutil.ignore_patterns("build", "dist", "*.egg-info", "__pycache__", "*.pyc"))
        run([sys.executable, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--no-index", "--wheel-dir", str(output), str(source)])
        wheel = next(output.glob("loopx-*.whl"))
        venv = output / "venv"
        run([sys.executable, "-m", "venv", str(venv)])
        pip = venv / "bin" / "pip"
        executable = venv / "bin" / "loopx"
        run([str(pip), "install", "--no-index", "--no-deps", str(wheel)])
        run([str(executable), "--help"])
        run([str(executable), "version"])
        with zipfile.ZipFile(wheel) as archive:
            names = set(archive.namelist())
        expected = {path.relative_to(PACKAGE / "src").as_posix()
                    for path in (PACKAGE / "src" / "loopx").rglob("*")
                    if path.is_file() and path.suffix in {".py", ".json"}}
        shipped = {name for name in names if name.startswith("loopx/")}
        if shipped != expected:
            raise RuntimeError(f"Wheel differs from current source: missing={expected - shipped}, extra={shipped - expected}")



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
