"""Tests for SARIF emission."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "tsar-cli" / "tsar.py"

def test_sarif_output(tmp_path):
    (tmp_path / "bad.py").write_text("eval(user_input)\n")
    out = tmp_path / "results.sarif"
    r = subprocess.run(
        [sys.executable, str(CLI), "scan", str(tmp_path),
         "--format", "sarif", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["version"] == "2.1.0"
    runs = data["runs"]
    assert len(runs) == 1
    assert runs[0]["tool"]["driver"]["name"] == "TSAR"
    assert any("eval_usage" in rule["id"] for rule in runs[0]["tool"]["driver"]["rules"])

def test_sarif_clean(tmp_path):
    (tmp_path / "ok.py").write_text("import os\n")
    out = tmp_path / "results.sarif"
    r = subprocess.run(
        [sys.executable, str(CLI), "scan", str(tmp_path),
         "--format", "sarif", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["runs"][0]["results"] == []


def test_sarif_includes_secret_scanner_findings(tmp_path):
    (tmp_path / "credential.py").write_text(f'AWS_KEY = "{ "AKIAIOS" + "FODNN7EXAMPLE" }' + "\n")
    out = tmp_path / "secrets.sarif"
    r = subprocess.run(
        [sys.executable, str(CLI), "scan", str(tmp_path),
         "--format", "sarif", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 1
    data = json.loads(out.read_text())
    results = data["runs"][0]["results"]
    assert any(result["ruleId"] == "tsar/aws_key" for result in results)
