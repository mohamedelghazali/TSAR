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
    assert (tmp_path / ".tsar" / "rules" / "crypto" / "algorithms.md").exists()
    assert (tmp_path / ".tsar" / "system" / "CORE_DIRECTIVE.md").exists()
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


def test_init_preserves_existing_custom_hook(tmp_path):
    hooks = tmp_path / ".git" / "hooks"
    hooks.mkdir(parents=True)
    original = "#!/usr/bin/env bash\n echo custom-hook\n"
    (hooks / "pre-commit").write_text(original)
    r = run(["init", ".", "--agent", "claude"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    backups = list(hooks.glob("pre-commit.user-backup.*"))
    assert len(backups) == 1
    assert backups[0].read_text() == original
    wrapper = (hooks / "pre-commit").read_text()
    assert "TSAR_DIR=" in wrapper
    assert "pre-commit.user-backup." in wrapper
    assert (tmp_path / ".tsar" / "pre-commit").exists()


def test_init_preserves_existing_agent_file(tmp_path):
    (tmp_path / "CLAUDE.md").write_text("# Project-specific instructions\nKeep these rules.\n")
    r = run(["init", ".", "--agent", "claude"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "CLAUDE.md").read_text() == (
        "# Project-specific instructions\nKeep these rules.\n"
    )


def test_init_refresh_removes_stale_managed_files_and_keeps_backup(tmp_path):
    old_tsar = tmp_path / ".tsar"
    stale = old_tsar / "skills" / "obsolete-skill" / "old.py"
    stale.parent.mkdir(parents=True)
    stale.write_text("stale")
    (old_tsar / "operator-notes.txt").write_text("user data")

    r = run(["init", ".", "--agent", "generic"], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (tmp_path / ".tsar" / "skills" / "obsolete-skill").exists()
    assert (tmp_path / ".tsar" / "operator-notes.txt").read_text() == "user data"

    backups = list(tmp_path.glob(".tsar.backup.*"))
    assert len(backups) == 1
    assert (backups[0] / "skills" / "obsolete-skill" / "old.py").read_text() == "stale"


def test_init_refresh_is_repeatable(tmp_path):
    first = run(["init", ".", "--agent", "claude"], cwd=tmp_path)
    assert first.returncode == 0, first.stdout + first.stderr
    first_config = (tmp_path / ".tsar" / "config.json").read_text()

    second = run(["init", ".", "--agent", "cursor"], cwd=tmp_path)
    assert second.returncode == 0, second.stdout + second.stderr
    assert (tmp_path / ".tsar" / "manifest.yaml").exists()
    assert (tmp_path / ".tsar" / "config.json").read_text() != first_config
    assert (tmp_path / "CLAUDE.md").exists()
    assert (tmp_path / ".cursorrules").is_file()


def test_atomic_directory_swap_restores_previous_tree_on_promotion_failure(tmp_path, monkeypatch):
    import importlib.util
    import pytest

    cli_path = ROOT / "tools" / "tsar-cli" / "tsar.py"
    spec = importlib.util.spec_from_file_location("tsar_cli_atomic_test", cli_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    destination = tmp_path / ".tsar"
    destination.mkdir()
    (destination / "old.txt").write_text("previous")
    staged = tmp_path / ".tsar-stage"
    staged.mkdir()
    (staged / "new.txt").write_text("next")
    backup = tmp_path / ".tsar.backup"

    real_replace = module.os.replace

    def fail_promotion(source, target):
        if Path(source) == staged and Path(target) == destination:
            raise OSError("simulated promotion failure")
        return real_replace(source, target)

    monkeypatch.setattr(module.os, "replace", fail_promotion)
    with pytest.raises(OSError, match="simulated promotion failure"):
        module._atomic_replace_directory(staged, destination, backup)

    assert (destination / "old.txt").read_text() == "previous"
    assert not (destination / "new.txt").exists()
    assert staged.exists()
    assert not backup.exists()
