#!/usr/bin/env python3
"""Run graph/lifecycle/delivery and skill-local CLI regressions."""
from pathlib import Path
import subprocess
import sys

raise SystemExit(subprocess.call([sys.executable, '-m', 'unittest', 'discover', '-s', str(Path(__file__).resolve().parent / 'tests'), '-p', 'test_*.py']))
