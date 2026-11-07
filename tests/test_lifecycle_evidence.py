"""Tests for cryptographically authenticated lifecycle gate attestations."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))
from lifecycle_evidence import (
    LifecycleEvidenceError, attest_gate, build_attestation_payload, verify_audit,
)


def setup_run(tmp_path):
    root = tmp_path / "project"
    root.mkdir()
    (root / "evidence").mkdir()
    (root / "evidence" / "review.txt").write_text("reviewed threat model", encoding="utf-8")
    audit = root / "run.json"
    audit.write_text(json.dumps({
        "schema": "tsar/lifecycle-run/v1",
        "provenance": {"upstream_commit_sha": "a" * 40},
        "gates": {"upstream_preflight": "PASS", "core_policy_review": "PENDING", "release_approval": "PENDING"},
        "evidence": [],
    }), encoding="utf-8")
    private = Ed25519PrivateKey.generate()
    public = private.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    keyring = tmp_path / "trusted-reviewers.json"
    keyring.write_text(json.dumps({
        "schema": "tsar/trusted-reviewers/v1",
        "keys": [{
            "key_id": "reviewer-01", "actor": "security-reviewer",
            "public_key": base64.b64encode(public).decode(),
            "allowed_gates": ["core_policy_review"], "active": True,
        }],
    }), encoding="utf-8")
    keyring.chmod(0o600)
    return root, audit, keyring, private


def sign_request(root, audit, keyring, private, *, gate="core_policy_review",
                 evidence="evidence/review.txt", decision="PASS", key_id="reviewer-01"):
    payload = build_attestation_payload(
        audit, repo_root=root, gate=gate, evidence_file=evidence,
        key_id=key_id, keyring_file=keyring, decision=decision,
    )
    signature = base64.b64encode(private.sign(json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode())).decode()
    envelope = {"schema": "tsar/reviewer-attestation/v1", "key_id": key_id,
                "payload": payload, "signature": signature}
    attestation = root / "reviewer-attestation.json"
    attestation.write_text(json.dumps(envelope), encoding="utf-8")
    return attestation


def test_signed_authorized_reviewer_attestation_is_accepted_and_verifiable(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    attestation = sign_request(root, audit, keyring, private)
    result = attest_gate(
        audit, repo_root=root, gate="core_policy_review",
        evidence_file="evidence/review.txt", attestation_file=attestation,
        trusted_reviewers_file=keyring,
    )
    entry = result["evidence"][0]
    assert result["gates"]["core_policy_review"] == "PASS"
    assert entry["actor"] == "security-reviewer"
    assert entry["reviewer_key_id"] == "reviewer-01"
    verified = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert verified["integrity_status"] == "PASS"
    assert verified["status"] == "INCOMPLETE"
    assert verified["lifecycle_status"] == "IN_PROGRESS"
    assert verified["findings"][0]["status"] == "PASS"


def test_modified_payload_signature_is_rejected(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    attestation = sign_request(root, audit, keyring, private)
    envelope = json.loads(attestation.read_text())
    envelope["payload"]["actor"] = "forged-reviewer"
    attestation.write_text(json.dumps(envelope))
    with pytest.raises(LifecycleEvidenceError, match="does not match"):
        attest_gate(audit, repo_root=root, gate="core_policy_review",
                    evidence_file="evidence/review.txt", attestation_file=attestation,
                    trusted_reviewers_file=keyring)


def test_unauthorized_gate_is_rejected(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    with pytest.raises(LifecycleEvidenceError, match="not authorized"):
        build_attestation_payload(audit, repo_root=root, gate="release_approval",
                                  evidence_file="evidence/review.txt", key_id="reviewer-01",
                                  keyring_file=keyring)


def test_tampered_evidence_fails_later_verification(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    attestation = sign_request(root, audit, keyring, private)
    attest_gate(audit, repo_root=root, gate="core_policy_review",
                evidence_file="evidence/review.txt", attestation_file=attestation,
                trusted_reviewers_file=keyring)
    (root / "evidence" / "review.txt").write_text("changed", encoding="utf-8")
    assert verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)["status"] == "FAIL"


def test_unsigned_legacy_entry_fails_closed(tmp_path):
    root, audit, keyring, _ = setup_run(tmp_path)
    data = json.loads(audit.read_text())
    data["gates"]["core_policy_review"] = "PASS"
    import hashlib
    evidence_bytes = (root / "evidence" / "review.txt").read_bytes()
    data["evidence"] = [{
        "gate": "core_policy_review", "decision": "PASS", "actor": "untrusted",
        "path": "evidence/review.txt", "sha256": hashlib.sha256(evidence_bytes).hexdigest(),
        "size_bytes": len(evidence_bytes),
    }]
    audit.write_text(json.dumps(data))
    result = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert result["status"] == "FAIL"
    assert result["findings"][0]["status"] == "UNAUTHENTICATED"


def test_reviewer_keyring_must_be_outside_project_and_not_writable(tmp_path):
    root, audit, keyring, _ = setup_run(tmp_path)
    inside = root / "keyring.json"
    inside.write_text(keyring.read_text())
    with pytest.raises(LifecycleEvidenceError, match="outside"):
        build_attestation_payload(audit, repo_root=root, gate="core_policy_review",
                                  evidence_file="evidence/review.txt", key_id="reviewer-01",
                                  keyring_file=inside)


def test_only_pending_gates_can_be_attested(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    data = json.loads(audit.read_text())
    data["gates"]["core_policy_review"] = "PASS"
    audit.write_text(json.dumps(data))
    with pytest.raises(LifecycleEvidenceError, match="PENDING"):
        build_attestation_payload(audit, repo_root=root, gate="core_policy_review",
                                  evidence_file="evidence/review.txt", key_id="reviewer-01",
                                  keyring_file=keyring)



@pytest.mark.parametrize("path", ["../outside.txt", "/tmp/evidence.txt"])
def test_path_escape_is_rejected(tmp_path, path):
    root, audit, keyring, private = setup_run(tmp_path)
    with pytest.raises(LifecycleEvidenceError):
        build_attestation_payload(audit, repo_root=root, gate="core_policy_review",
                                  evidence_file=path, key_id="reviewer-01",
                                  keyring_file=keyring)


def test_symlink_evidence_is_rejected(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    (root / "evidence" / "link.txt").symlink_to(root / "evidence" / "review.txt")
    with pytest.raises(LifecycleEvidenceError, match="symlinks"):
        build_attestation_payload(audit, repo_root=root, gate="core_policy_review",
                                  evidence_file="evidence/link.txt", key_id="reviewer-01",
                                  keyring_file=keyring)


def test_upstream_preflight_cannot_be_overridden(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    with pytest.raises(LifecycleEvidenceError, match="reserved"):
        build_attestation_payload(audit, repo_root=root, gate="upstream_preflight",
                                  evidence_file="evidence/review.txt", key_id="reviewer-01",
                                  keyring_file=keyring)


def test_fail_decision_is_preserved_in_signed_attestation(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    attestation = sign_request(root, audit, keyring, private, decision="FAIL")
    result = attest_gate(audit, repo_root=root, gate="core_policy_review",
                         evidence_file="evidence/review.txt", attestation_file=attestation,
                         trusted_reviewers_file=keyring)
    assert result["gates"]["core_policy_review"] == "FAIL"
    verified = verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)
    assert verified["integrity_status"] == "PASS"
    assert verified["lifecycle_status"] == "FAILED"
    assert verified["status"] == "FAIL"



def test_modified_signature_bytes_are_rejected(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    attestation = sign_request(root, audit, keyring, private)
    envelope = json.loads(attestation.read_text())
    raw = bytearray(base64.b64decode(envelope["signature"]))
    raw[0] ^= 1
    envelope["signature"] = base64.b64encode(raw).decode()
    attestation.write_text(json.dumps(envelope))
    with pytest.raises(LifecycleEvidenceError, match="signature is invalid"):
        attest_gate(audit, repo_root=root, gate="core_policy_review",
                    evidence_file="evidence/review.txt", attestation_file=attestation,
                    trusted_reviewers_file=keyring)


def test_malformed_reviewer_key_id_in_audit_fails_closed(tmp_path):
    root, audit, keyring, private = setup_run(tmp_path)
    attestation = sign_request(root, audit, keyring, private)
    attest_gate(audit, repo_root=root, gate="core_policy_review",
                evidence_file="evidence/review.txt", attestation_file=attestation,
                trusted_reviewers_file=keyring)
    data = json.loads(audit.read_text())
    data["evidence"][0]["attestation"]["key_id"] = []
    audit.write_text(json.dumps(data))
    assert verify_audit(audit, repo_root=root, trusted_reviewers_file=keyring)["status"] == "FAIL"
