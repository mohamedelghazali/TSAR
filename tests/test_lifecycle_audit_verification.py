"""Tests for cryptographically authenticated lifecycle audit verification."""
import base64
import json
from pathlib import Path
import sys

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))
from lifecycle_evidence import (
    LifecycleEvidenceError,
    attest_gate,
    build_attestation_payload,
    verify_audit,
)


def make_run(tmp_path):
    root = tmp_path / "project"
    (root / "evidence").mkdir(parents=True)
    evidence = root / "evidence" / "review.txt"
    evidence.write_text("independent review notes", encoding="utf-8")
    audit = root / "run.json"
    audit.write_text(json.dumps({
        "schema": "tsar/lifecycle-run/v1",
        "task": {
            "task": "Review the TSAR lifecycle implementation",
            "strict_required": True,
            "required_gates": ["upstream_preflight", "core_policy_review"],
        },
        "provenance": {"upstream_commit_sha": "a" * 40},
        "gates": {
            "upstream_preflight": "PASS",
            "core_policy_review": "PENDING",
        },
        "evidence": [],
    }), encoding="utf-8")

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    keyring = tmp_path / "trusted-reviewers.json"
    keyring.write_text(json.dumps({
        "schema": "tsar/trusted-reviewers/v1",
        "keys": [{
            "key_id": "reviewer-01",
            "actor": "security-reviewer",
            "public_key": base64.b64encode(public_key).decode("ascii"),
            "allowed_gates": ["core_policy_review"],
            "active": True,
        }],
    }), encoding="utf-8")
    keyring.chmod(0o600)
    return root, audit, evidence, keyring, private_key


def sign_attestation(root, audit, keyring, private_key):
    payload = build_attestation_payload(
        audit,
        repo_root=root,
        gate="core_policy_review",
        evidence_file="evidence/review.txt",
        key_id="reviewer-01",
        keyring_file=keyring,
    )
    canonical = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    envelope = {
        "schema": "tsar/reviewer-attestation/v1",
        "key_id": "reviewer-01",
        "payload": payload,
        "signature": base64.b64encode(private_key.sign(canonical)).decode("ascii"),
    }
    attestation = root / "reviewer-attestation.json"
    attestation.write_text(json.dumps(envelope), encoding="utf-8")
    return attestation


def attest(root, audit, keyring, private_key):
    attestation = sign_attestation(root, audit, keyring, private_key)
    return attest_gate(
        audit,
        repo_root=root,
        gate="core_policy_review",
        evidence_file="evidence/review.txt",
        attestation_file=attestation,
        trusted_reviewers_file=keyring,
    )


def test_verify_audit_passes_for_unchanged_evidence(tmp_path):
    root, audit, _, keyring, private_key = make_run(tmp_path)
    result = attest(root, audit, keyring, private_key)

    assert result["gates"]["core_policy_review"] == "PASS"
    verified = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert verified["status"] == "PASS"
    assert verified["evidence_count"] == 1
    assert verified["findings"][0]["status"] == "PASS"


def test_verify_audit_detects_modified_evidence(tmp_path):
    root, audit, evidence, keyring, private_key = make_run(tmp_path)
    attest(root, audit, keyring, private_key)
    evidence.write_text("modified after review", encoding="utf-8")

    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["status"] == "FAIL"
    assert result["findings"][0]["status"] == "HASH_MISMATCH"


def test_verify_audit_detects_missing_evidence(tmp_path):
    root, audit, evidence, keyring, private_key = make_run(tmp_path)
    attest(root, audit, keyring, private_key)
    evidence.unlink()

    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["status"] == "FAIL"
    assert result["findings"][0]["status"] == "MISSING_OR_UNSAFE"


def test_verify_audit_detects_gate_without_evidence(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["gates"]["core_policy_review"] = "PASS"
    audit.write_text(json.dumps(record), encoding="utf-8")

    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["status"] == "FAIL"
    assert any(
        "no evidence" in item.get("reason", "")
        for item in result["findings"]
    )


def test_verify_audit_rejects_duplicate_gate_evidence(tmp_path):
    root, audit, _, keyring, private_key = make_run(tmp_path)
    attest(root, audit, keyring, private_key)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["evidence"].append(dict(record["evidence"][0]))
    audit.write_text(json.dumps(record), encoding="utf-8")

    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["status"] == "FAIL"
    assert any(item["status"] == "INVALID" for item in result["findings"])


def test_verify_audit_rejects_invalid_record(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    audit.write_text('{"schema":"wrong"}', encoding="utf-8")

    with pytest.raises(LifecycleEvidenceError, match="unsupported lifecycle audit schema"):
        verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)


def test_empty_evidence_is_incomplete_not_a_success(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["integrity_status"] == "PASS"
    assert result["lifecycle_status"] == "IN_PROGRESS"
    assert result["status"] == "INCOMPLETE"
    assert result["evidence_count"] == 0


def test_audit_context_tampering_invalidates_signed_attestation(tmp_path):
    root, audit, _, keyring, private_key = make_run(tmp_path)
    attest(root, audit, keyring, private_key)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["task"] = {"description": "tampered after reviewer approval"}
    audit.write_text(json.dumps(record), encoding="utf-8")
    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["integrity_status"] == "FAIL"
    assert result["status"] == "FAIL"
    assert any(item["status"] == "UNAUTHENTICATED" for item in result["findings"])


def test_gate_set_tampering_invalidates_signed_attestation(tmp_path):
    root, audit, _, keyring, private_key = make_run(tmp_path)
    attest(root, audit, keyring, private_key)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["gates"]["release_approval"] = "PENDING"
    audit.write_text(json.dumps(record), encoding="utf-8")
    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["integrity_status"] == "FAIL"
    assert result["status"] == "FAIL"


def test_symlinked_parent_directory_is_rejected_for_evidence(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    (root / "evidence-link").symlink_to(root / "evidence", target_is_directory=True)
    with pytest.raises((LifecycleEvidenceError, OSError)):
        from lifecycle_evidence import _safe_relative_file
        _safe_relative_file(root, "evidence-link/review.txt")


def test_audit_symlink_is_rejected(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    link = root / "audit-link.json"
    link.symlink_to(audit)
    with pytest.raises(LifecycleEvidenceError):
        verify_audit(link, repo_root=root, trusted_reviewers_file=keyring)


def test_audit_without_review_gates_is_rejected(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["gates"] = {"upstream_preflight": "PASS"}
    audit.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError, match="does not match the signed task plan"):
        verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)


def test_missing_required_gate_is_rejected_before_attestation(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["gates"].pop("core_policy_review")
    audit.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError, match="does not match the signed task plan"):
        verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)


def test_unplanned_gate_is_rejected(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["gates"]["release_approval"] = "PENDING"
    audit.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError, match="does not match the signed task plan"):
        verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)


def test_duplicate_required_gate_in_task_plan_is_rejected(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["task"]["required_gates"].append("core_policy_review")
    audit.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError, match="unique list"):
        verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)


def test_non_strict_task_plan_is_rejected(tmp_path):
    root, audit, _, keyring, _ = make_run(tmp_path)
    record = json.loads(audit.read_text(encoding="utf-8"))
    record["task"]["strict_required"] = False
    audit.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(LifecycleEvidenceError, match="strict enforcement"):
        verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
