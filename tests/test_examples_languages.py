"""Verify every secure example passes scanners."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECURE = ROOT / "examples" / "secure"

LANGUAGES = ["python", "node", "go", "rust", "java", "kotlin", "swift"]

def test_all_languages_present():
    for lang in LANGUAGES:
        assert (SECURE / lang).exists(), f"missing {lang}"

def test_secure_examples_clean():
    r = subprocess.run(
        [sys.executable, "skills/secure-review/review.py", str(SECURE)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout
