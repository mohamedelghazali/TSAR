"""Tests for lifecycle audit evidence integrity verification."""
import hashlib
import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))
from lifecycle_evidence import LifecycleEvidenceError, attest_gate, verify_audit


def make_run(tmp_path):
    root = tmp_path / "project"
    (root / "evidence").mkdir(parents=True)
    evidence = root / "evidence" / "review.txt"
    evidence.write_text("independent review notes", encoding="utf-8")
    audit = root / "run.json"
    audit.write_text(json.dumps({
        "schema": "tsar/lifecycle-run/v1",
        "gates": {"upstream_preflight": "PASS", "core_policy_review": "PENDING"},
        "evidence": [],
    }), encoding="utf-8")
    return root, audit, evidence


def test_verify_audit_passes_for_unchanged_evidence(tmp_path):
    root, audit, evidence = make_run(tmp_path)
    attest_gate(audit, repo_root=root, gate="core_policy_review",
                evidence_file="evidence/review.txt", actor="reviewer")
    result = verify_audit(audit, repo_root=root)
    assert result["status"] == "PASS"
    assert result["evidence_count"] == 1


def test_verify_audit_detects_modified_evidence(tmp_path):
    root, audit, evidence = make_run(tmp_path)
    attest_gate(audit, repo_root=root, gate="core_policy_review",
                evidence_file="evidence/review.txt", actor="reviewer")
    evidence.write_text("modified after review", encoding="utf-8")
    result = verify_audit(audit, repo_root=root)
    assert result["status"] == "FAIL"
    assert result["findings"][0]["status"] == "HASH_MISMATCH"


def test_verify_audit_detects_missing_evidence(tmp_path):
    root, audit, evidence = make_run(tmp_path)
    attest_gate(audit, repo_root=root, gate="core_policy_review",
                evidence_file="evidence/review.txt", actor="reviewer")
    evidence.unlink()
    result = verify_audit(audit, repo_root=root)
    assert result["status"] == "FAIL"
    assert result["findings"][0]["status"] == "MISSING_OR_UNSAFE"


def test_verify_audit_detects_gate_without_evidence(tmp_path):
    root, audit, _ = make_run(tmp_path)
    record = json.loads(audit.read_text())
    record["gates"]["core_policy_review"] = "PASS"
    audit.write_text(json.dumps(record), encoding="utf-8")
    result = verify_audit(audit, repo_root=root)
    assert result["status"] == "FAIL"
    assert any("no evidence" in item.get("reason", "") for item in result["findings"])


def test_verify_audit_rejects_duplicate_gate_evidence(tmp_path):
    root, audit, _ = make_run(tmp_path)
    attest_gate(audit, repo_root=root, gate="core_policy_review",
                evidence_file="evidence/review.txt", actor="reviewer")
    record = json.loads(audit.read_text())
    record["evidence"].append(dict(record["evidence"][0]))
    audit.write_text(json.dumps(record), encoding="utf-8")
    result = verify_audit(audit, repo_root=root)
    assert result["status"] == "FAIL"
    assert any(item.get("reason") == "duplicate evidence entry for gate" for item in result["findings"])


def test_verify_audit_rejects_invalid_record(tmp_path):
    root, audit, _ = make_run(tmp_path)
    audit.write_text('{"schema":"wrong"}', encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError):
        verify_audit(audit, repo_root=root)
