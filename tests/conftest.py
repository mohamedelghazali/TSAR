import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "secret-scanner"))
sys.path.insert(0, str(ROOT / "skills" / "secure-review"))
sys.path.insert(0, str(ROOT / "skills" / "crypto-inventory"))
