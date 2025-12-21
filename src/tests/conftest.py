import sys
from pathlib import Path

# Ensure src/ is importable during tests when tests live under src/tests
# Resolve project root two levels up from this file: /project/src/tests -> /project
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
