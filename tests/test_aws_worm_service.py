"""Behavioral tests for the AWS WORM Lambda using isolated fake AWS clients."""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import pytest
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HANDLER_PATH = Path(__file__).resolve().parents[1] / "aws-worm-service" / "lambda" / "handler.py"


class FakeDynamoDB:
    def __init__(self):
        self.items = {}
        self.transactions = []
        self.transaction_error = None

    def get_item(self, **kwargs):
        key = kwargs["Key"]
        pk, sk = key["pk"]["S"], key["sk"]["S"]
        item = self.items.get((pk, sk))
        return {"Item": item} if item is not None else {}

    def transact_write_items(self, **kwargs):
        self.transactions.append(kwargs)
        if self.transaction_error:
            raise self.transaction_error
        return {}


class FakeS3:
    def __init__(self):
        self.put_args = None
        self.uploads = 0

    def put_object(self, **kwargs):
        self.put_args = kwargs
        self.uploads += 1
        return {"VersionId": "version-0001"}

    def get_object_retention(self, **kwargs):
        return {
            "Retention": {
                "Mode": "COMPLIANCE",
                "RetainUntilDate": self.put_args["ObjectLockRetainUntilDate"],
            }
        }


class FakeKMS:
    def __init__(self, private_key):
        self.private_key = private_key
        self.calls = []

    def sign(self, **kwargs):
        self.calls.append(kwargs)
        return {"Signature": self.private_key.sign(kwargs["Message"])}


class FakeSecrets:
    def get_secret_value(self, **kwargs):
        return {"SecretString": "test-bearer-token"}


@pytest.fixture
def service(monkeypatch):
    for key, value in {
        "ANCHOR_BUCKET": "tsar-test-bucket",
        "ANCHOR_TABLE": "tsar-test-table",
        "SIGNING_KEY_ARN": "arn:aws:kms:us-east-1:111122223333:key/test",
        "TOKEN_SECRET_ARN": "arn:aws:secretsmanager:us-east-1:111122223333:secret:test",
        "SERVICE_ID": "tsar-worm-test",
        "RETENTION_DAYS": "365",
        "ALLOWED_REPOSITORIES": "mohamedelghazali/TSAR",
        "AWS_ACCESS_KEY_ID": "testing",
        "AWS_SECRET_ACCESS_KEY": "testing",
        "AWS_DEFAULT_REGION": "us-east-1",
        "AWS_EC2_METADATA_DISABLED": "true",
    }.items():
        monkeypatch.setenv(key, value)

    module_name = "tsar_worm_handler_test"
    spec = importlib.util.spec_from_file_location(module_name, HANDLER_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    private_key = Ed25519PrivateKey.generate()
    fake_ddb = FakeDynamoDB()
    fake_s3 = FakeS3()
    fake_kms = FakeKMS(private_key)
    module.ddb = fake_ddb
    module.s3 = fake_s3
    module.kms = fake_kms
    module.secrets = FakeSecrets()
    return module, fake_ddb, fake_s3, fake_kms, private_key


def make_request(module, *, evidence=b"reviewed evidence"):
    evidence_path = "evidence/review.md"
    record = {
        "schema": "tsar/lifecycle-run/v1",
        "created_at": "2026-11-07T12:00:00+00:00",
        "task": {"task": "verify WORM anchor service"},
        "provenance": {"upstream_commit_sha": "a" * 40},
        "gates": {"upstream_preflight": "PASS", "design_review": "PASS"},
        "evidence": [{
            "path": evidence_path,
            "sha256": hashlib.sha256(evidence).hexdigest(),
            "size_bytes": len(evidence),
        }],
    }
    raw = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    stable = {
        "repository": "mohamedelghazali/TSAR",
        "created_at": record["created_at"],
        "task": record["task"]["task"],
        "upstream_commit_sha": record["provenance"]["upstream_commit_sha"],
    }
    run_id = module.digest(module.canonical(stable))
    record_sha = module.digest(raw)
    return {
        "schema": "tsar/external-audit-anchor-request/v1",
        "repository": "mohamedelghazali/TSAR",
        "run_id": run_id,
        "record_sha256": record_sha,
        "audit_snapshot_b64": base64.b64encode(raw).decode(),
        "evidence_files_b64": {evidence_path: base64.b64encode(evidence).decode()},
        "integrity_status": "PASS",
        "lifecycle_status": "COMPLETE",
        "gate_states": record["gates"],
        "upstream_commit_sha": record["provenance"]["upstream_commit_sha"],
        "expected_previous_anchor_sha256": None,
        "idempotency_key": module.digest((run_id + ":" + record_sha).encode()),
    }


def test_append_archives_audit_and_evidence_and_returns_kms_ed25519_receipt(service):
    module, ddb, s3, kms, private_key = service
    request = make_request(module)

    receipt = module._append(request)

    assert receipt["sequence"] == 1
    assert receipt["retention_mode"] == "WORM_COMPLIANCE"
    assert receipt["service_id"] == "tsar-worm-test"
    signed = {key: value for key, value in receipt.items() if key != "signature"}
    private_key.public_key().verify(base64.b64decode(receipt["signature"]), module.canonical(signed))
    assert kms.calls[0]["SigningAlgorithm"] == "ED25519_SHA_512"
    assert kms.calls[0]["MessageType"] == "RAW"
    assert s3.put_args["ObjectLockMode"] == "COMPLIANCE"
    assert s3.put_args["ChecksumAlgorithm"] == "SHA256"
    archived = json.loads(s3.put_args["Body"])
    assert base64.b64decode(archived["request"]["audit_snapshot_b64"]) == base64.b64decode(request["audit_snapshot_b64"])
    assert base64.b64decode(archived["request"]["evidence_files_b64"]["evidence/review.md"]) == b"reviewed evidence"
    assert len(ddb.transactions) == 1
    assert len(ddb.transactions[0]["TransactItems"]) == 3


def test_append_rejects_snapshot_digest_mismatch_before_aws_writes(service):
    module, ddb, s3, _, _ = service
    request = make_request(module)
    request["audit_snapshot_b64"] = base64.b64encode(b"""{"tampered":true}""").decode()

    with pytest.raises(ValueError, match="digest"):
        module._append(request)

    assert s3.uploads == 0
    assert ddb.transactions == []


def test_append_rejects_evidence_bytes_that_do_not_match_audit_metadata(service):
    module, ddb, s3, _, _ = service
    request = make_request(module)
    request["evidence_files_b64"]["evidence/review.md"] = base64.b64encode(b"tampered").decode()

    with pytest.raises(ValueError, match="evidence archive bytes"):
        module._append(request)

    assert s3.uploads == 0
    assert ddb.transactions == []


def test_append_returns_existing_idempotency_receipt_without_second_upload(service):
    module, ddb, s3, _, _ = service
    request = make_request(module)
    existing = {
        "schema": "tsar/external-audit-anchor-receipt/v1",
        "service_id": "tsar-worm-test",
        "anchor_id": "already-stored",
        "run_id": request["run_id"],
        "sequence": 1,
        "record_sha256": request["record_sha256"],
        "previous_anchor_sha256": None,
        "anchored_at": datetime.now(timezone.utc).isoformat(),
        "retention_mode": "WORM_COMPLIANCE",
        "retain_until": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat(),
        "signature": "stored-signature",
    }
    ddb.items[("IDEM#" + request["idempotency_key"], "REQUEST")] = {
        "record_sha256": {"S": request["record_sha256"]},
        "run_id": {"S": request["run_id"]},
        "receipt": {"S": json.dumps(existing)},
    }

    result = module._append(request)

    assert result == existing
    assert s3.uploads == 0
    assert ddb.transactions == []


def test_append_reports_transaction_conflict_and_keeps_unindexed_object(service):
    module, ddb, s3, _, _ = service
    request = make_request(module)
    ddb.transaction_error = ClientError(
        {"Error": {"Code": "TransactionCanceledException", "Message": "conditional conflict"}},
        "TransactWriteItems",
    )

    with pytest.raises(ValueError, match="concurrent append"):
        module._append(request)

    assert s3.uploads == 1
    assert ddb.transactions
