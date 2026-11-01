"""Tests for `tsar init`."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "tsar-cli" / "tsar.py"

def run(args, cwd):
    return subprocess.run([sys.executable, str(CLI), *args],
                          capture_output=True, text=True, cwd=cwd)

def test_init_defaults_to_universal_instructions(tmp_path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hooks").mkdir()
    r = run(["init", str(tmp_path)], cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (tmp_path / "AGENTS.md").exists()
    cfg = (tmp_path / ".tsar" / "config.json").read_text(encoding="utf-8")
    assert '"agent": "generic"' in cfg


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
    assert not (tmp_path / ".cursorrules").exists() or (tmp_path / ".cursorrules").is_file()


def test_init_rolls_back_previous_installation_if_promotion_fails(tmp_path, monkeypatch):
    """A failed stage promotion must restore the prior .tsar directory."""
    import importlib.util
    from types import SimpleNamespace

    target = tmp_path
    old_tsar = target / ".tsar"
    old_tsar.mkdir()
    sentinel = old_tsar / "operator-data.txt"
    sentinel.write_text("must survive rollback", encoding="utf-8")

    spec = importlib.util.spec_from_file_location("tsar_cli_for_init_test", CLI)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)

    real_replace = module.os.replace

    def fail_stage_promotion(source, destination):
        source_path = Path(source)
        destination_path = Path(destination)
        if source_path.name.startswith(".tsar-stage-") and destination_path == old_tsar:
            raise OSError("simulated atomic promotion failure")
        return real_replace(source, destination)

    monkeypatch.setattr(module.os, "replace", fail_stage_promotion)
    result = module.cmd_init(SimpleNamespace(path=str(target), agent="generic"))

    assert result == 1
    assert sentinel.read_text(encoding="utf-8") == "must survive rollback"
    assert not list(target.glob(".tsar-stage-*"))
    assert not list(target.glob(".tsar.backup.*"))
