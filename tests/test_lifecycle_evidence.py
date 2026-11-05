"""Tests for evidence-backed lifecycle gate updates."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))
from lifecycle_evidence import LifecycleEvidenceError, attest_gate


def setup_run(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    evidence_dir = root / "evidence"
    evidence_dir.mkdir()
    evidence = evidence_dir / "review.txt"
    evidence.write_text("reviewed threat model", encoding="utf-8")
    audit = root / "run.json"
    audit.write_text(json.dumps({
        "schema": "tsar/lifecycle-run/v1",
        "gates": {"upstream_preflight": "PASS", "core_policy_review": "PENDING"},
        "evidence": [],
    }), encoding="utf-8")
    return root, audit, evidence


def test_attest_gate_records_hash_and_actor(tmp_path):
    root, audit, evidence = setup_run(tmp_path)
    result = attest_gate(
        audit, repo_root=root, gate="core_policy_review",
        evidence_file="evidence/review.txt", actor="security-reviewer",
    )
    entry = result["evidence"][0]
    assert result["gates"]["core_policy_review"] == "PASS"
    assert entry["sha256"] == hashlib.sha256(evidence.read_bytes()).hexdigest()
    assert entry["path"] == "evidence/review.txt"
    assert entry["actor"] == "security-reviewer"
    assert json.loads(audit.read_text()) == result
    assert audit.stat().st_mode & 0o777 == 0o600


def test_failed_decision_is_recorded_as_fail(tmp_path):
    root, audit, _ = setup_run(tmp_path)
    result = attest_gate(
        audit, repo_root=root, gate="core_policy_review",
        evidence_file="evidence/review.txt", actor="reviewer", decision="FAIL",
    )
    assert result["gates"]["core_policy_review"] == "FAIL"


@pytest.mark.parametrize("path", ["../outside.txt", "/tmp/evidence.txt"])
def test_path_escape_is_rejected(tmp_path, path):
    root, audit, _ = setup_run(tmp_path)
    with pytest.raises(LifecycleEvidenceError):
        attest_gate(audit, repo_root=root, gate="core_policy_review",
                    evidence_file=path, actor="reviewer")


def test_symlink_evidence_is_rejected(tmp_path):
    root, audit, evidence = setup_run(tmp_path)
    link = root / "evidence" / "link.txt"
    link.symlink_to(evidence)
    with pytest.raises(LifecycleEvidenceError, match="symlinks"):
        attest_gate(audit, repo_root=root, gate="core_policy_review",
                    evidence_file="evidence/link.txt", actor="reviewer")


def test_upstream_preflight_cannot_be_overridden(tmp_path):
    root, audit, _ = setup_run(tmp_path)
    with pytest.raises(LifecycleEvidenceError, match="reserved"):
        attest_gate(audit, repo_root=root, gate="upstream_preflight",
                    evidence_file="evidence/review.txt", actor="reviewer")


def test_non_pending_gate_cannot_be_re_attested(tmp_path):
    root, audit, _ = setup_run(tmp_path)
    data = json.loads(audit.read_text())
    data["gates"]["core_policy_review"] = "PASS"
    audit.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError, match="PENDING"):
        attest_gate(audit, repo_root=root, gate="core_policy_review",
                    evidence_file="evidence/review.txt", actor="reviewer")
