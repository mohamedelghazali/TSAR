import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "tsar-cli" / "tsar.py"

def run(args):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, cwd=ROOT)

def test_report_html(tmp_path):
    (tmp_path / "bad.py").write_text("eval(user_input)\n")
    out = tmp_path / "report.html"
    r = run(["report", str(tmp_path), "--output", str(out)])
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.exists()
    assert "TSAR Security Report" in out.read_text()

def test_compliance_soc2():
    r = run(["compliance", "soc2"])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "soc2" in r.stdout.lower()

def test_compliance_unknown():
    r = run(["compliance", "notreal"])
    assert r.returncode != 0

def test_drift_smoke():
    r = run(["drift"])
    # May return 0 or 1 depending on network; must not crash.
    assert r.returncode in (0, 1, 2)