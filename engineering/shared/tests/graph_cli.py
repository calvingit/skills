"""Test adapter: exercise the owning production entrypoint for each old graph test."""
import subprocess
import sys
from pathlib import Path
E = Path(__file__).resolve().parents[2]

def invoke(script, args):
    result = subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True)
    print(result.stdout, end='')
    print(result.stderr, end='', file=sys.stderr)
    return result.returncode

def invoke_loop(args):
    operation, *rest = args
    return invoke(E / 'loop/scripts' / ('frontier' if operation == 'status' else 'update-status'), rest if operation == 'status' else args)

def main(args):
    operation, *rest = args
    if operation in ['create-batch', 'reconcile-batch']:
        return invoke(E / 'to-tickets/scripts/create-graph', args)
    if operation in ['inspect', 'list', 'show']:
        return invoke(E / 'loop/scripts/graph-query', args)
    if operation in ['start', 'retry']:
        return invoke(E / 'loop/scripts/record-attempt', args)
    return invoke(E / 'loop/scripts/update-status', args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
