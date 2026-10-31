"""Tests for `tsar init`."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "tsar-cli" / "tsar.py"

def run(args, cwd):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, cwd=cwd)

def test_init_claude(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hooks").mkdir()
    r = run(["init", ".", "--agent", "claude"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".tsar" / "manifest.yaml").exists()
    assert (tmp_path / ".git" / "hooks" / "pre-commit").exists()

def test_init_cursor(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hooks").mkdir()
    r = run(["init", ".", "--agent", "cursor"], cwd=tmp_path)
    assert r.returncode == 0
    assert (tmp_path / ".cursorrules").exists()

def test_init_copilot(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hooks").mkdir()
    r = run(["init", ".", "--agent", "copilot"], cwd=tmp_path)
    assert r.returncode == 0
    assert (tmp_path / ".github" / "copilot-instructions.md").exists()

def test_init_unknown_agent(tmp_path):
    r = run(["init", ".", "--agent", "notreal"], cwd=tmp_path)
    assert r.returncode != 0

def test_init_writes_config(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hooks").mkdir()
    r = run(["init", ".", "--agent", "claude"], cwd=tmp_path)
    assert r.returncode == 0
    cfg = (tmp_path / ".tsar" / "config.json").read_text()
    assert "manifest_version" in cfg
    assert "claude" in cfg
