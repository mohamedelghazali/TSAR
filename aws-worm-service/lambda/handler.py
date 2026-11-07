"""AWS-backed TSAR external WORM anchor API.

Runtime: AWS Lambda Python 3.12. All durable append ordering is committed in
DynamoDB transactions; audit snapshots and signed receipts are retained in S3
Object Lock COMPLIANCE mode. An S3 object written before a failed DynamoDB
transaction is an immutable orphan, never a visible anchor.
"""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
import re
import uuid
from pathlib import PurePosixPath

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.types import TypeSerializer

s3 = boto3.client("s3")
ddb = boto3.client("dynamodb")
kms = boto3.client("kms")
secrets = boto3.client("secretsmanager")
_serializer = TypeSerializer()

BUCKET = os.environ["ANCHOR_BUCKET"]
TABLE = os.environ["ANCHOR_TABLE"]
KMS_KEY_ID = os.environ["SIGNING_KEY_ARN"]
TOKEN_SECRET_ARN = os.environ["TOKEN_SECRET_ARN"]
SERVICE_ID = os.environ["SERVICE_ID"]
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "365"))
ALLOWED_REPOSITORIES = set(filter(None, os.environ.get("ALLOWED_REPOSITORIES", "mohamedelghazali/TSAR").split(",")))
_RUN_ID = re.compile(r"^[0-9a-f]{64}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(value).hexdigest()


def av(item):
    return {key: _serializer.serialize(value) for key, value in item.items()}


def response(status, body):
    return {"statusCode": status, "headers": {"content-type": "application/json", "cache-control": "no-store"}, "body": json.dumps(body, separators=(",", ":"))}


def _authorized(event):
    headers = {str(k).lower(): v for k, v in (event.get("headers") or {}).items()}
    supplied = headers.get("authorization", "")
    if not supplied.startswith("Bearer "):
        return False
    secret = secrets.get_secret_value(SecretId=TOKEN_SECRET_ARN)["SecretString"]
    return hmac.compare_digest(supplied[7:], secret)


def _sign(unsigned):
    result = kms.sign(
        KeyId=KMS_KEY_ID,
        Message=canonical(unsigned),
        MessageType="RAW",
        SigningAlgorithm="ED25519_SHA_512",
    )
    return base64.b64encode(result["Signature"]).decode("ascii")


def _latest(run_id):
    state = ddb.get_item(
        TableName=TABLE,
        Key=av({"pk": "RUN#" + run_id, "sk": "STATE"}),
        ConsistentRead=True,
    ).get("Item")
    if not state:
        return None, 0
    seq = int(state["sequence"]["N"])
    item = ddb.get_item(
        TableName=TABLE,
        Key=av({"pk": "RUN#" + run_id, "sk": "ANCHOR#" + str(seq).zfill(20)}),
        ConsistentRead=True,
    ).get("Item")
    if not item:
        raise RuntimeError("anchor state references a missing anchor record")
    return json.loads(item["receipt"]["S"]), seq


def _put_snapshot(run_id, anchor_id, request, receipt, retain_until):
    key = "runs/" + run_id + "/" + anchor_id + ".json"
    body = canonical({"request": request, "receipt": receipt})
    result = s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=body,
        ContentType="application/json",
        ContentMD5=base64.b64encode(hashlib.md5(body).digest()).decode("ascii"),
        ObjectLockMode="COMPLIANCE",
        ObjectLockRetainUntilDate=retain_until,
        Metadata={"run-id": run_id, "record-sha256": request["record_sha256"]},
    )
    version_id = result.get("VersionId")
    if not version_id:
        raise RuntimeError("S3 did not return a version ID; versioning is required")
    locked = s3.get_object_retention(Bucket=BUCKET, Key=key, VersionId=version_id)["Retention"]
    if locked.get("Mode") != "COMPLIANCE" or locked.get("RetainUntilDate") < retain_until:
        raise RuntimeError("S3 did not confirm the required COMPLIANCE retention")
    return key, version_id


def _append(request):
    required = {
        "schema": "tsar/external-audit-anchor-request/v1",
        "integrity_status": "PASS",
    }
    if any(request.get(k) != v for k, v in required.items()):
        raise ValueError("unsupported request schema or integrity status")
    run_id = request.get("run_id")
    record_sha = request.get("record_sha256")
    idem = request.get("idempotency_key")
    repository = request.get("repository")
    if not isinstance(run_id, str) or not _RUN_ID.fullmatch(run_id):
        raise ValueError("invalid run_id")
    if not isinstance(record_sha, str) or not _SHA256.fullmatch(record_sha):
        raise ValueError("invalid record_sha256")
    if not isinstance(idem, str) or not _SHA256.fullmatch(idem):
        raise ValueError("invalid idempotency_key")
    if repository not in ALLOWED_REPOSITORIES:
        raise ValueError("repository is not authorized")
    expected_idempotency_key = digest((run_id + ":" + record_sha).encode("utf-8"))
    if idem != expected_idempotency_key:
        raise ValueError("idempotency_key does not match run and record identity")
    if not isinstance(request.get("gate_states"), dict):
        raise ValueError("gate_states must be an object")
    encoded_snapshot = request.get("audit_snapshot_b64")
    if not isinstance(encoded_snapshot, str):
        raise ValueError("audit_snapshot_b64 is required")
    try:
        audit_bytes = base64.b64decode(encoded_snapshot, validate=True)
        if not audit_bytes or len(audit_bytes) > 4 * 1024 * 1024:
            raise ValueError("audit snapshot must be between 1 byte and 4 MiB")
        audit_record = json.loads(audit_bytes)
    except (ValueError, json.JSONDecodeError) as exc:
        raise ValueError("audit snapshot is not valid bounded Base64 JSON") from exc
    if digest(audit_bytes) != record_sha:
        raise ValueError("audit snapshot digest does not match record_sha256")
    if not isinstance(audit_record, dict) or audit_record.get("schema") != "tsar/lifecycle-run/v1":
        raise ValueError("audit snapshot schema is invalid")
    task = audit_record.get("task")
    provenance = audit_record.get("provenance")
    stable_identity = {
        "repository": repository,
        "created_at": audit_record.get("created_at"),
        "task": task.get("task") if isinstance(task, dict) else None,
        "upstream_commit_sha": provenance.get("upstream_commit_sha") if isinstance(provenance, dict) else None,
    }
    if not all(isinstance(value, str) and value for value in stable_identity.values()):
        raise ValueError("audit snapshot is missing stable run identity fields")
    if digest(canonical(stable_identity)) != run_id:
        raise ValueError("audit snapshot run identity does not match run_id")
    if request.get("upstream_commit_sha") != stable_identity["upstream_commit_sha"]:
        raise ValueError("upstream commit does not match audit snapshot")
    if request.get("gate_states") != audit_record.get("gates"):
        raise ValueError("gate states do not match audit snapshot")
    evidence_entries = audit_record.get("evidence", [])
    evidence_files = request.get("evidence_files_b64")
    if not isinstance(evidence_entries, list) or not isinstance(evidence_files, dict):
        raise ValueError("evidence archive collection is invalid")
    expected_evidence = {}
    for entry in evidence_entries:
        if not isinstance(entry, dict):
            raise ValueError("audit evidence entry is invalid")
        path = entry.get("path")
        parts = PurePosixPath(path).parts if isinstance(path, str) else ()
        if (not path or "\\" in path or PurePosixPath(path).is_absolute()
                or any(part in {"", ".", ".."} for part in parts)
                ):
            raise ValueError("audit evidence path is unsafe")
        if path in expected_evidence and expected_evidence[path] != (entry.get("sha256"), entry.get("size_bytes")):
            raise ValueError("duplicate evidence path has conflicting metadata")
        size = entry.get("size_bytes")
        sha = entry.get("sha256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 1 or not isinstance(sha, str) or not _SHA256.fullmatch(sha):
            raise ValueError("audit evidence metadata is invalid")
        expected_evidence[path] = (sha, size)
    if set(evidence_files) != set(expected_evidence):
        raise ValueError("evidence archive paths do not match the audit record")
    archived_bytes = len(audit_bytes)
    for path, encoded in evidence_files.items():
        if not isinstance(encoded, str) or len(encoded) > 7 * 1024 * 1024:
            raise ValueError("evidence archive entry is invalid or too large")
        try:
            evidence_bytes = base64.b64decode(encoded, validate=True)
        except ValueError as exc:
            raise ValueError("evidence archive entry is not valid Base64") from exc
        expected_sha, expected_size = expected_evidence[path]
        if len(evidence_bytes) != expected_size or digest(evidence_bytes) != expected_sha:
            raise ValueError("evidence archive bytes do not match audit evidence metadata")
        archived_bytes += len(evidence_bytes)
    if archived_bytes > 4 * 1024 * 1024:
        raise ValueError("audit and evidence archive exceeds the 4 MiB limit")

    existing_idem = ddb.get_item(
        TableName=TABLE,
        Key=av({"pk": "IDEM#" + idem, "sk": "REQUEST"}),
        ConsistentRead=True,
    ).get("Item")
    if existing_idem:
        if existing_idem["record_sha256"]["S"] != record_sha or existing_idem["run_id"]["S"] != run_id:
            raise ValueError("idempotency key was reused with different content")
        return json.loads(existing_idem["receipt"]["S"])

    previous, sequence = _latest(run_id)
    previous_digest = digest(canonical(previous)) if previous else None
    if request.get("expected_previous_anchor_sha256") != previous_digest:
        raise ValueError("stale expected_previous_anchor_sha256; fetch latest and retry")

    next_sequence = sequence + 1
    anchor_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).replace(microsecond=0)
    retain_until = now + timedelta(days=RETENTION_DAYS)
    unsigned = {
        "schema": "tsar/external-audit-anchor-receipt/v1",
        "service_id": SERVICE_ID,
        "anchor_id": anchor_id,
        "run_id": run_id,
        "sequence": next_sequence,
        "record_sha256": record_sha,
        "previous_anchor_sha256": previous_digest,
        "anchored_at": now.isoformat().replace("+00:00", "Z"),
        "retention_mode": "WORM_COMPLIANCE",
        "retain_until": retain_until.isoformat().replace("+00:00", "Z"),
    }
    receipt = dict(unsigned, signature=_sign(unsigned))
    object_key, version_id = _put_snapshot(run_id, anchor_id, request, receipt, retain_until)

    anchor_item = {
        "pk": "RUN#" + run_id,
        "sk": "ANCHOR#" + str(next_sequence).zfill(20),
        "receipt": canonical(receipt).decode("utf-8"),
        "receipt_sha256": digest(canonical(receipt)),
        "record_sha256": record_sha,
        "object_key": object_key,
        "object_version_id": version_id,
    }
    idem_item = {
        "pk": "IDEM#" + idem, "sk": "REQUEST", "run_id": run_id,
        "record_sha256": record_sha, "receipt": canonical(receipt).decode("utf-8"),
    }
    state_item = {
        "pk": "RUN#" + run_id, "sk": "STATE", "sequence": next_sequence,
        "latest_receipt_sha256": digest(canonical(receipt)),
        "latest_record_sha256": record_sha,
    }
    actions = [
        {"Put": {"TableName": TABLE, "Item": av(anchor_item), "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)"}},
        {"Put": {"TableName": TABLE, "Item": av(idem_item), "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)"}},
    ]
    if sequence == 0:
        actions.append({"Put": {"TableName": TABLE, "Item": av(state_item), "ConditionExpression": "attribute_not_exists(pk) AND attribute_not_exists(sk)"}})
    else:
        actions.append({"Update": {
            "TableName": TABLE,
            "Key": av({"pk": "RUN#" + run_id, "sk": "STATE"}),
            "UpdateExpression": "SET #seq = :next, latest_receipt_sha256 = :receipt, latest_record_sha256 = :record",
            "ConditionExpression": "#seq = :previous AND latest_receipt_sha256 = :previous_receipt",
            "ExpressionAttributeNames": {"#seq": "sequence"},
            "ExpressionAttributeValues": av({
                ":next": next_sequence, ":receipt": digest(canonical(receipt)),
                ":record": record_sha, ":previous": sequence,
                ":previous_receipt": previous_digest,
            }),
        }})
    try:
        ddb.transact_write_items(TransactItems=actions, ClientRequestToken=hashlib.sha256((run_id + idem).encode()).hexdigest()[:36])
    except ClientError as exc:
        # The immutable S3 object may remain as an orphan; it is never indexed
        # as the accepted latest anchor. The caller must GET latest and retry.
        raise ValueError("concurrent append or duplicate idempotency key; fetch latest and retry") from exc
    return receipt


def lambda_handler(event, context):
    try:
        if not _authorized(event):
            return response(401, {"error": "unauthorized"})
        method = event.get("requestContext", {}).get("http", {}).get("method", "")
        path = event.get("rawPath", "")
        if method == "POST" and path.endswith("/v1/anchors"):
            request = json.loads(event.get("body") or "{}")
            if not isinstance(request, dict):
                return response(400, {"error": "request must be a JSON object"})
            return response(201, {"receipt": _append(request)})
        match = re.fullmatch(r".*/v1/runs/([0-9a-f]{64})/latest", path)
        if method == "GET" and match:
            receipt, _ = _latest(match.group(1))
            return response(200, {"receipt": receipt}) if receipt else response(404, {"error": "not found"})
        return response(404, {"error": "not found"})
    except (ValueError, json.JSONDecodeError) as exc:
        return response(409 if "stale" in str(exc) or "concurrent" in str(exc) else 400, {"error": str(exc)})
    except Exception:
        # Do not leak AWS exception details, credentials, or internal identifiers.
        return response(500, {"error": "internal service error"})
