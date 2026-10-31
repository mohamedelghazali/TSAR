"""Tests for the TSAR orchestrator."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORCH = ROOT / "tools" / "tsar-orchestrator" / "orchestrator.py"

def test_markdown_output(tmp_path):
    (tmp_path / "ok.py").write_text("import os\n")
    out = tmp_path / "report.md"
    r = subprocess.run(
        [sys.executable, str(ORCH), str(tmp_path), "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    assert out.exists()
    text = out.read_text()
    assert "# TSAR Orchestrator Report" in text
    assert "## Summary" in text
    assert "| Step |" in text

def test_json_output(tmp_path):
    (tmp_path / "ok.py").write_text("import os\n")
    out = tmp_path / "report.json"
    r = subprocess.run(
        [sys.executable, str(ORCH), str(tmp_path),
         "--format", "json", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(out.read_text())
    assert "summary" in data
    assert "steps" in data
    assert data["summary"]["total"] >= 4
    assert isinstance(data["steps"], list)

def test_orchestrator_fails_on_secret(tmp_path):
    (tmp_path / "bad.py").write_text('K = "AKIAIOSFODNN7EXAMPLE"\n')
    out = tmp_path / "report.json"
    r = subprocess.run(
        [sys.executable, str(ORCH), str(tmp_path),
         "--format", "json", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 1
    data = json.loads(out.read_text())
    assert data["summary"]["failed"] >= 1

def test_orchestrator_include_subset(tmp_path):
    (tmp_path / "ok.py").write_text("import os\n")
    out = tmp_path / "report.json"
    r = subprocess.run(
        [sys.executable, str(ORCH), str(tmp_path),
         "--include", "secrets",
         "--format", "json", "--output", str(out)],
        capture_output=True, text=True, cwd=ROOT,
    )
    assert r.returncode == 0
    data = json.loads(out.read_text())
    assert data["summary"]["total"] == 1
