"""Verify that secure examples do not trigger scanner findings."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECURE_DIR = ROOT / "examples" / "secure"

def test_secure_examples_have_no_blockers():
    r = subprocess.run(
        [sys.executable, "skills/secure-review/review.py", str(SECURE_DIR)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout

def test_secure_examples_have_no_secrets():
    r = subprocess.run(
        [sys.executable, "skills/secret-scanner/scanner.py", str(SECURE_DIR)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout
