"""Package-local execution graph CLI entrypoint."""

from pathlib import Path
import sys

SRC = Path(__file__).resolve().parents[2]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from loopx.graph.execution_graph.cli import main

__all__ = ["main"]

if __name__ == "__main__":
    raise SystemExit(main())
