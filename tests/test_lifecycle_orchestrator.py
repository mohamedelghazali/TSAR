"""Tests for fail-closed lifecycle run initialization."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import types

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))
import lifecycle_orchestrator as orchestrator


def make_root(tmp_path):
    root = tmp_path / "repo"
    (root / "tools" / "tsar-cli").mkdir(parents=True)
    (root / "manifest.yaml").write_text(
        "active_files:\n  core: [system/CORE_DIRECTIVE.md]\n  api: [rules/api/rest.md]\n  development: [rules/development/secure-sdlc.md]\n",
        encoding="utf-8",
    )
    (root / "tools" / "tsar-cli" / "verify_upstream.py").write_text("# verifier stub\n")
    return root


def fake_run(report_status="PASS", returncode=0):
    def run(command, **kwargs):
        report = Path(command[command.index("--report") + 1])
        report.write_text(json.dumps({
            "status": report_status,
            "repository": "mohamedelghazali/TSAR",
            "commit_sha": "a" * 40,
            "manifest_version": "1.1.1",
            "manifest_sha256": "b" * 64,
            "loaded_policy_sha256": {"system/CORE_DIRECTIVE.md": "c" * 64},
            "selected_domains": ["core", "api"],
            "verifier": "tsar-upstream-preflight",
            "errors": ["upstream unavailable"] if report_status != "PASS" else [],
        }))
        return types.SimpleNamespace(returncode=returncode, stdout="", stderr="")
    return run


def test_start_records_only_preflight_as_pass(tmp_path):
    root = make_root(tmp_path)
    audit = tmp_path / "audit.json"
    record = orchestrator.start_lifecycle(
        "Build an API", repo_root=root, audit_file=audit,
        domains=["api"], run=fake_run(),
    )
    assert record["state"] == "preflight"
    assert record["gates"]["upstream_preflight"] == "PASS"
    assert record["gates"]["core_policy_review"] == "PENDING"
    assert record["provenance"]["upstream_commit_sha"] == "a" * 40
    assert json.loads(audit.read_text()) == record
    assert audit.stat().st_mode & 0o777 == 0o600


def test_preflight_failure_writes_no_audit(tmp_path):
    root = make_root(tmp_path)
    audit = tmp_path / "audit.json"
    with pytest.raises(orchestrator.LifecycleStartError, match="preflight failed"):
        orchestrator.start_lifecycle(
            "Build an API", repo_root=root, audit_file=audit,
            domains=["api"], run=fake_run("FAIL", 2),
        )
    assert not audit.exists()


def test_existing_audit_is_never_overwritten(tmp_path):
    root = make_root(tmp_path)
    audit = tmp_path / "audit.json"
    audit.write_text("keep")
    with pytest.raises(orchestrator.LifecycleStartError, match="already exists"):
        orchestrator.start_lifecycle(
            "Build an API", repo_root=root, audit_file=audit,
            domains=["api"], run=fake_run(),
        )
    assert audit.read_text() == "keep"


def test_unknown_upstream_domain_fails_preflight_closed(tmp_path):
    root = make_root(tmp_path)
    audit = tmp_path / "audit.json"
    with pytest.raises(orchestrator.LifecycleStartError, match="preflight failed"):
        orchestrator.start_lifecycle(
            "Build an API", repo_root=root, audit_file=audit,
            domains=["api"], run=fake_run("FAIL", 2),
        )
