"""Verify report generator produces valid HTML and JSON."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "tools" / "tsar-report" / "generate.py"

def test_html_report(tmp_path):
    (tmp_path / "bad.py").write_text('K = "AKIAIOSFODNN7EXAMPLE"\n')
    out = tmp_path / "report.html"
    r = subprocess.run(
        [sys.executable, str(REPORT), str(tmp_path), "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    html = out.read_text()
    assert "<html" in html
    assert "TSAR Security Report" in html
    assert "high" in html.lower() or "HIGH" in html

def test_json_report(tmp_path):
    (tmp_path / "bad.py").write_text('K = "AKIAIOSFODNN7EXAMPLE"\n')
    out = tmp_path / "report.json"
    r = subprocess.run(
        [sys.executable, str(REPORT), str(tmp_path), "--format", "json", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0
    data = json.loads(out.read_text())
    assert "secrets" in data
    assert "review" in data
    assert "cbom" in data
    assert "generated" in data

def test_clean_report(tmp_path):
    (tmp_path / "ok.py").write_text("import os\n")
    out = tmp_path / "report.json"
    r = subprocess.run(
        [sys.executable, str(REPORT), str(tmp_path), "--format", "json", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0
    data = json.loads(out.read_text())
    assert data["secrets"] == []
