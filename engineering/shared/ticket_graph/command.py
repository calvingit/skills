"""Argument parsing and JSON results shared by skill-local entrypoints."""
import argparse
import json
import sys
import subprocess
from pathlib import Path
from .contracts import emit, envelope, problem


class CommandParser(argparse.ArgumentParser):
    def error(self, message):
        emit(envelope(self.prog, ok=False, problems=[problem('contract', 'invalid_arguments', message)]))
        self.exit(2)


def parser(description):
    return CommandParser(description=description)


def task_argument(p):
    p.add_argument('task_dir', type=lambda value: Path(value).expanduser().resolve())


def request(source):
    value = json.loads(sys.stdin.read() if source == '-' else Path(source).read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Input must be a JSON object.')
    return value


def run(operation, action):
    try:
        payload, code = action()
    except (ValueError, OSError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        payload, code = envelope(operation, ok=False, problems=[problem('contract', 'invalid_request', str(exc))]), 2
    emit(payload)
    return code
