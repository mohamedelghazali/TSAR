"""External, signed WORM anchor client for TSAR lifecycle audit snapshots.

The remote service is an independently administered trust boundary. This client
fails closed unless the service returns an Ed25519-signed COMPLIANCE-retention receipt.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from lifecycle_evidence import LifecycleEvidenceError, _read_regular_file, verify_audit


class LifecycleAnchorError(RuntimeError):
    """Raised when external audit anchoring or verification fails."""


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _run_id(record: dict, repository: str) -> str:
    task = record.get("task", {})
    provenance = record.get("provenance", {})
    stable = {
        "repository": repository,
        "created_at": record.get("created_at"),
        "task": task.get("task") if isinstance(task, dict) else None,
        "upstream_commit_sha": provenance.get("upstream_commit_sha") if isinstance(provenance, dict) else None,
    }
    if not all(isinstance(value, str) and value for value in stable.values()):
        raise LifecycleAnchorError("audit is missing stable run identity fields")
    return _sha256(_canonical(stable))


def _load_audit(audit_file: Path, repo_root: Path) -> tuple[dict, bytes]:
    root = Path(repo_root).resolve(strict=True)
    raw = Path(audit_file).expanduser()
    if not raw.is_absolute():
        raw = root / raw
    try:
        parent = raw.parent.resolve(strict=True)
        if not parent.is_relative_to(root):
            raise LifecycleAnchorError("audit file must be inside the project root")
        data, _ = _read_regular_file(parent / raw.name)
        record = json.loads(data)
    except (OSError, json.JSONDecodeError, LifecycleEvidenceError) as exc:
        raise LifecycleAnchorError(f"cannot safely read lifecycle audit: {exc}") from exc
    if not isinstance(record, dict) or record.get("schema") != "tsar/lifecycle-run/v1":
        raise LifecycleAnchorError("unsupported lifecycle audit schema")
    return record, data


def _load_service_trust(trust_file: Path, repo_root: Path) -> tuple[str, Ed25519PublicKey]:
    root = Path(repo_root).resolve(strict=True)
    raw = Path(trust_file).expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    try:
        parent = raw.parent.resolve(strict=True)
        if parent.is_relative_to(root):
            raise LifecycleAnchorError("external anchor service trust key must be outside the project root")
        data, info = _read_regular_file(parent / raw.name)
        if os.name == "posix" and info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise LifecycleAnchorError("external anchor service trust key must not be group- or world-writable")
        config = json.loads(data)
    except (OSError, json.JSONDecodeError, LifecycleEvidenceError) as exc:
        raise LifecycleAnchorError(f"cannot safely read external anchor trust key: {exc}") from exc
    if not isinstance(config, dict) or config.get("schema") != "tsar/audit-anchor-trust/v1":
        raise LifecycleAnchorError("unsupported external anchor trust schema")
    service_id, encoded = config.get("service_id"), config.get("public_key")
    if not isinstance(service_id, str) or not service_id.strip() or not isinstance(encoded, str):
        raise LifecycleAnchorError("external anchor trust key is incomplete")
    try:
        raw_key = base64.b64decode(encoded, validate=True)
        if len(raw_key) != 32:
            raise ValueError("Ed25519 public keys must be 32 bytes")
        return service_id, Ed25519PublicKey.from_public_bytes(raw_key)
    except (ValueError, TypeError) as exc:
        raise LifecycleAnchorError("external anchor service public key is invalid") from exc


def _validate_endpoint(endpoint: str) -> str:
    parsed = urlsplit(endpoint)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password
            or parsed.query or parsed.fragment):
        raise LifecycleAnchorError("anchor endpoint must be an HTTPS origin/base path without credentials, query, or fragment")
    return endpoint.rstrip("/")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise LifecycleAnchorError("external anchor service redirects are not accepted")


def _request_json(url: str, *, token: str, method: str, payload: dict | None, timeout: int) -> dict:
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "TSAR-CLI/1.0",
    }
    body = None
    if payload is not None:
        body = _canonical(payload)
        headers["Content-Type"] = "application/json"
    request = Request(url, data=body, headers=headers, method=method)
    try:
        with build_opener(_NoRedirect).open(request, timeout=timeout) as response:
            if response.status not in {200, 201}:
                raise LifecycleAnchorError(f"external anchor service returned HTTP {response.status}")
            result = json.loads(response.read())
    except HTTPError as exc:
        if exc.code == 404:
            raise
        raise LifecycleAnchorError(f"external anchor service rejected the request (HTTP {exc.code})") from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        raise LifecycleAnchorError(f"external anchor service request failed: {exc}") from exc
    if not isinstance(result, dict):
        raise LifecycleAnchorError("external anchor service returned a non-object response")
    return result


def _receipt_digest(receipt: dict) -> str:
    return _sha256(_canonical(receipt))


def _verify_receipt(receipt: dict, *, service_id: str, public_key: Ed25519PublicKey,
                    run_id: str, record_sha256: str | None = None) -> dict:
    if not isinstance(receipt, dict) or receipt.get("schema") != "tsar/external-audit-anchor-receipt/v1":
        raise LifecycleAnchorError("external anchor receipt schema is invalid")
    signature_b64 = receipt.get("signature")
    signed = {key: value for key, value in receipt.items() if key != "signature"}
    required = ("service_id", "anchor_id", "run_id", "sequence", "record_sha256",
                "previous_anchor_sha256", "anchored_at", "retention_mode", "retain_until")
    if any(key not in signed for key in required):
        raise LifecycleAnchorError("external anchor receipt is missing required fields")
    if signed["service_id"] != service_id or signed["run_id"] != run_id:
        raise LifecycleAnchorError("external anchor receipt service or run identity mismatch")
    if not isinstance(signed["anchor_id"], str) or not signed["anchor_id"]:
        raise LifecycleAnchorError("external anchor receipt ID is invalid")
    if not isinstance(signed["sequence"], int) or isinstance(signed["sequence"], bool) or signed["sequence"] < 1:
        raise LifecycleAnchorError("external anchor sequence is invalid")
    if not re.fullmatch(r"[0-9a-f]{64}", str(signed["record_sha256"])):
        raise LifecycleAnchorError("external anchor record digest is invalid")
    if record_sha256 is not None and signed["record_sha256"] != record_sha256:
        raise LifecycleAnchorError("external anchor does not match the current audit snapshot")
    previous = signed["previous_anchor_sha256"]
    if previous is not None and not re.fullmatch(r"[0-9a-f]{64}", str(previous)):
        raise LifecycleAnchorError("external anchor previous-receipt digest is invalid")
    if signed["retention_mode"] != "WORM_COMPLIANCE":
        raise LifecycleAnchorError("external service did not attest COMPLIANCE-mode WORM retention")
    try:
        anchored_at = datetime.fromisoformat(signed["anchored_at"].replace("Z", "+00:00"))
        retain_until = datetime.fromisoformat(signed["retain_until"].replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        if anchored_at.tzinfo is None or retain_until.tzinfo is None:
            raise ValueError("timezone required")
        if anchored_at > now.replace(microsecond=0) + timedelta(minutes=5):
            raise ValueError("anchor timestamp is in the future")
        if retain_until <= now:
            raise ValueError("retention period has expired")
        signature = base64.b64decode(signature_b64, validate=True)
        if len(signature) != 64:
            raise ValueError("Ed25519 signatures must be 64 bytes")
        public_key.verify(signature, _canonical(signed))
    except (AttributeError, TypeError, ValueError, InvalidSignature) as exc:
        raise LifecycleAnchorError("external anchor receipt signature or retention timestamps are invalid") from exc
    return receipt


def _verified_latest(endpoint: str, *, token: str, timeout: int, service_id: str,
                     public_key: Ed25519PublicKey, run_id: str) -> dict | None:
    try:
        response = _request_json(
            f"{endpoint}/v1/runs/{run_id}/latest",
            token=token, method="GET", payload=None, timeout=timeout,
        )
    except HTTPError as exc:
        if exc.code == 404:
            return None
        raise LifecycleAnchorError(f"cannot retrieve latest external anchor (HTTP {exc.code})") from exc
    receipt = response.get("receipt")
    return _verify_receipt(receipt, service_id=service_id, public_key=public_key, run_id=run_id)


def _save_receipt(path: Path, receipt: dict) -> None:
    destination = Path(path).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(str(destination), flags, 0o600)
    except FileExistsError as exc:
        raise LifecycleAnchorError("receipt output already exists; refusing to overwrite it") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(receipt, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            destination.unlink()
        except OSError:
            pass
        raise


def anchor_audit(audit_file: Path, *, repo_root: Path, trusted_reviewers_file: Path,
                 endpoint: str, service_trust_file: Path, receipt_file: Path | None = None,
                 token_env: str = "TSAR_AUDIT_ANCHOR_TOKEN", timeout: int = 20,
                 repository: str = "mohamedelghazali/TSAR") -> dict:
    """Append a verified lifecycle snapshot to the independently administered WORM service."""
    root = Path(repo_root).resolve(strict=True)
    endpoint = _validate_endpoint(endpoint)
    token = os.environ.get(token_env, "")
    if not token:
        raise LifecycleAnchorError(f"required bearer token environment variable is unset: {token_env}")
    try:
        audit_result = verify_audit(
            Path(audit_file), repo_root=root, trusted_reviewers_file=Path(trusted_reviewers_file)
        )
    except LifecycleEvidenceError as exc:
        raise LifecycleAnchorError(f"lifecycle evidence verification failed: {exc}") from exc
    if audit_result.get("integrity_status") != "PASS":
        raise LifecycleAnchorError("only an audit with PASS evidence integrity can be externally anchored")
    record, raw_audit = _load_audit(Path(audit_file), root)
    run_id = _run_id(record, repository)
    record_digest = _sha256(raw_audit)
    service_id, public_key = _load_service_trust(Path(service_trust_file), root)
    previous = _verified_latest(
        endpoint, token=token, timeout=timeout, service_id=service_id,
        public_key=public_key, run_id=run_id,
    )
    previous_digest = _receipt_digest(previous) if previous else None
    if previous and previous["record_sha256"] == record_digest:
        receipt = previous
        result_status = "ALREADY_ANCHORED"
    else:
        request_payload = {
            "schema": "tsar/external-audit-anchor-request/v1",
            "repository": repository,
            "run_id": run_id,
            "record_sha256": record_digest,
            "integrity_status": audit_result.get("integrity_status"),
            "lifecycle_status": audit_result.get("lifecycle_status"),
            "gate_states": record.get("gates"),
            "upstream_commit_sha": record.get("provenance", {}).get("upstream_commit_sha"),
            "expected_previous_anchor_sha256": previous_digest,
            "idempotency_key": _sha256(f"{run_id}:{record_digest}".encode("utf-8")),
        }
        response = _request_json(
            f"{endpoint}/v1/anchors", token=token, method="POST",
            payload=request_payload, timeout=timeout,
        )
        receipt = response.get("receipt")
        signed = _verify_receipt(
            receipt, service_id=service_id, public_key=public_key,
            run_id=run_id, record_sha256=record_digest,
        )
        expected_sequence = previous["sequence"] + 1 if previous else 1
        if signed["sequence"] != expected_sequence or signed["previous_anchor_sha256"] != previous_digest:
            raise LifecycleAnchorError("external anchor sequence/previous-receipt chain is discontinuous")
        result_status = "ANCHORED"
    if receipt_file is not None:
        _save_receipt(Path(receipt_file), receipt)
    return {
        "status": result_status,
        "run_id": run_id,
        "record_sha256": record_digest,
        "receipt": receipt,
    }


def verify_external_anchor(audit_file: Path, *, repo_root: Path, trusted_reviewers_file: Path,
                            endpoint: str, service_trust_file: Path,
                            token_env: str = "TSAR_AUDIT_ANCHOR_TOKEN", timeout: int = 20,
                            repository: str = "mohamedelghazali/TSAR") -> dict:
    """Verify that the remote WORM service still exposes the latest signed snapshot."""
    root = Path(repo_root).resolve(strict=True)
    endpoint = _validate_endpoint(endpoint)
    token = os.environ.get(token_env, "")
    if not token:
        raise LifecycleAnchorError(f"required bearer token environment variable is unset: {token_env}")
    try:
        audit_result = verify_audit(
            Path(audit_file), repo_root=root, trusted_reviewers_file=Path(trusted_reviewers_file)
        )
    except LifecycleEvidenceError as exc:
        raise LifecycleAnchorError(f"lifecycle evidence verification failed: {exc}") from exc
    if audit_result.get("integrity_status") != "PASS":
        raise LifecycleAnchorError("local lifecycle evidence integrity is not PASS")
    record, raw_audit = _load_audit(Path(audit_file), root)
    run_id = _run_id(record, repository)
    service_id, public_key = _load_service_trust(Path(service_trust_file), root)
    latest = _verified_latest(
        endpoint, token=token, timeout=timeout, service_id=service_id,
        public_key=public_key, run_id=run_id,
    )
    if latest is None:
        raise LifecycleAnchorError("remote WORM service has no anchor for this lifecycle run")
    digest = _sha256(raw_audit)
    if latest["record_sha256"] != digest:
        raise LifecycleAnchorError("remote latest anchor is missing or stale relative to the local audit")
    return {
        "status": "PASS",
        "run_id": run_id,
        "record_sha256": digest,
        "sequence": latest["sequence"],
        "anchor_id": latest["anchor_id"],
        "retention_mode": latest["retention_mode"],
        "retain_until": latest["retain_until"],
        "receipt_sha256": _receipt_digest(latest),
    }
