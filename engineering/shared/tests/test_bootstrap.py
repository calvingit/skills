from pathlib import Path
import sys
ENGINEERING = Path(__file__).resolve().parents[2]
for path in (ENGINEERING / 'shared', ENGINEERING / 'to-tickets/scripts', ENGINEERING / 'loop/scripts'):
    sys.path.insert(0, str(path))
