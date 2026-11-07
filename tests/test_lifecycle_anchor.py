"""Tests for signed external WORM lifecycle audit anchoring."""
import base64
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import sys

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))
from lifecycle_anchor import (
    LifecycleAnchorError, _canonical, _receipt_digest, _run_id, _verify_receipt,
    _validate_endpoint,
)


def make_receipt(private, *, run_id="run-123", record_sha256="a" * 64,
                 previous=None, sequence=1, retention_mode="WORM_COMPLIANCE"):
    signed = {
        "schema": "tsar/external-audit-anchor-receipt/v1",
        "service_id": "vault-prod",
        "anchor_id": "anchor-0001",
        "run_id": run_id,
        "sequence": sequence,
        "record_sha256": record_sha256,
        "previous_anchor_sha256": previous,
        "anchored_at": datetime.now(timezone.utc).isoformat(),
        "retention_mode": retention_mode,
        "retain_until": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
    }
    return {**signed, "signature": base64.b64encode(private.sign(_canonical(signed))).decode("ascii")}


def test_run_id_is_stable_and_bound_to_repository_and_run_identity():
    record = {
        "created_at": "2026-11-07T12:00:00+00:00",
        "task": {"task": "review lifecycle"},
        "provenance": {"upstream_commit_sha": "b" * 40},
    }
    first = _run_id(record, "mohamedelghazali/TSAR")
    assert first == _run_id(record, "mohamedelghazali/TSAR")
    assert first != _run_id(record, "other/repository")


def test_valid_signed_compliance_receipt_is_accepted():
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    receipt = make_receipt(private)
    result = _verify_receipt(
        receipt, service_id="vault-prod", public_key=public,
        run_id="run-123", record_sha256="a" * 64,
    )
    assert result["retention_mode"] == "WORM_COMPLIANCE"
    assert _receipt_digest(receipt)


def test_modified_receipt_signature_is_rejected():
    private = Ed25519PrivateKey.generate()
    public = private.public_key()
    receipt = make_receipt(private)
    receipt["sequence"] = 2
    with pytest.raises(LifecycleAnchorError, match="signature"):
        _verify_receipt(receipt, service_id="vault-prod", public_key=public, run_id="run-123")


def test_non_compliance_retention_is_rejected_even_when_signed():
    private = Ed25519PrivateKey.generate()
    with pytest.raises(LifecycleAnchorError, match="COMPLIANCE"):
        _verify_receipt(
            make_receipt(private, retention_mode="GOVERNANCE"),
            service_id="vault-prod", public_key=private.public_key(), run_id="run-123",
        )


def test_receipt_for_another_audit_snapshot_is_rejected():
    private = Ed25519PrivateKey.generate()
    with pytest.raises(LifecycleAnchorError, match="current audit"):
        _verify_receipt(
            make_receipt(private), service_id="vault-prod",
            public_key=private.public_key(), run_id="run-123", record_sha256="c" * 64,
        )


def test_wrong_service_identity_is_rejected():
    private = Ed25519PrivateKey.generate()
    with pytest.raises(LifecycleAnchorError, match="identity mismatch"):
        _verify_receipt(
            make_receipt(private), service_id="untrusted-service",
            public_key=private.public_key(), run_id="run-123",
        )


@pytest.mark.parametrize("endpoint", [
    "http://anchor.example",
    "https://anchor.example/path?token=secret",
    "https://anchor.example/path#fragment",
])
def test_endpoint_must_be_https_and_free_of_embedded_credentials(endpoint):
    with pytest.raises(LifecycleAnchorError, match="HTTPS"):
        _validate_endpoint(endpoint)


def test_https_endpoint_is_normalized():
    assert _validate_endpoint("https://anchor.example/base/") == "https://anchor.example/base"
