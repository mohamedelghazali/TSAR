"""Cryptographically authenticated lifecycle gate attestations."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import base64
import hashlib
import json
import os
from pathlib import Path
import stat

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


class LifecycleEvidenceError(RuntimeError):
    """Raised when lifecycle evidence or reviewer authorization is invalid."""


def _canonical(value: dict) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _open_regular_file(path: Path) -> tuple[int, os.stat_result]:
    """Open a regular file without following a final-component symlink."""
    parent = path.parent.resolve(strict=True)
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if os.name == "posix" and os.open in os.supports_dir_fd:
        dir_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow)
        try:
            fd = os.open(path.name, flags | nofollow, dir_fd=dir_fd)
        finally:
            os.close(dir_fd)
    else:
        if path.is_symlink():
            raise LifecycleEvidenceError("symlink files are not accepted")
        fd = os.open(parent / path.name, flags | nofollow)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode):
        os.close(fd)
        raise LifecycleEvidenceError("expected a regular file")
    return fd, info


def _read_regular_file(path: Path) -> tuple[bytes, os.stat_result]:
    fd, info = _open_regular_file(path)
    try:
        chunks = []
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks), info
    finally:
        os.close(fd)


def _open_project_file(root: Path, parts: tuple[str, ...]) -> int:
    """Walk from a pinned project-root descriptor; reject symlinks at every component."""
    if os.name != "posix" or os.open not in os.supports_dir_fd:
        current = root
        for part in parts:
            current = current / part
            if current.is_symlink():
                raise LifecycleEvidenceError("symlinks are not accepted in project evidence paths")
        fd = os.open(current, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            os.close(fd)
            raise LifecycleEvidenceError("evidence must be a regular file inside the project root")
        return fd

    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    current_fd = os.open(root, directory_flags)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, directory_flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        file_fd = os.open(
            parts[-1],
            os.O_RDONLY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0),
            dir_fd=current_fd,
        )
    finally:
        os.close(current_fd)
    if not stat.S_ISREG(os.fstat(file_fd).st_mode):
        os.close(file_fd)
        raise LifecycleEvidenceError("evidence must be a regular file inside the project root")
    return file_fd


def _safe_relative_file(root: Path, supplied: str) -> tuple[Path, str, int]:
    if not isinstance(supplied, str) or not supplied:
        raise LifecycleEvidenceError("file path must be a non-empty relative path")
    candidate = Path(supplied)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise LifecycleEvidenceError("file path must be a safe relative path")
    parts = candidate.parts
    if not parts:
        raise LifecycleEvidenceError("file path must identify a regular file")
    fd = _open_project_file(root, parts)
    digest, size = hashlib.sha256(), 0
    try:
        while True:
            chunk = os.read(fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
    finally:
        os.close(fd)
    if not size:
        raise LifecycleEvidenceError("empty evidence files are not accepted")
    return root.joinpath(*parts), digest.hexdigest(), size


def _audit_context_digest(record: dict) -> str:
    """Bind every immutable run field and the exact gate set, excluding mutable gate decisions."""
    immutable = {
        key: value for key, value in record.items()
        if key not in {"gates", "evidence", "updated_at"}
    }
    gate_names = sorted(record.get("gates", {}))
    return _sha256_bytes(_canonical({"immutable": immutable, "gate_names": gate_names}))


def _load_audit(audit_file: Path, root: Path) -> tuple[Path, dict, bytes]:
    raw = Path(audit_file).expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    try:
        parent = raw.parent.resolve(strict=True)
    except OSError as exc:
        raise LifecycleEvidenceError(f"cannot resolve lifecycle audit directory: {exc}") from exc
    audit = parent / raw.name
    if not parent.is_relative_to(root):
        raise LifecycleEvidenceError("audit file must be inside the project root")
    try:
        raw_bytes, _ = _read_regular_file(audit)
        record = json.loads(raw_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(f"cannot read lifecycle audit record: {exc}") from exc
    if not isinstance(record, dict) or record.get("schema") != "tsar/lifecycle-run/v1":
        raise LifecycleEvidenceError("unsupported lifecycle audit schema")
    if not isinstance(record.get("gates"), dict) or not record["gates"]:
        raise LifecycleEvidenceError("audit gates must be a non-empty object")
    if record["gates"].get("upstream_preflight") != "PASS":
        raise LifecycleEvidenceError("upstream_preflight must remain PASS")
    if any(state not in {"PENDING", "PASS", "FAIL"} for state in record["gates"].values()):
        raise LifecycleEvidenceError("audit contains an invalid lifecycle gate state")
    if not isinstance(record.get("evidence", []), list):
        raise LifecycleEvidenceError("audit evidence collection must be a list")
    return audit, record, raw_bytes


def _load_keyring(keyring_file: Path, root: Path) -> dict[str, dict]:
    raw = Path(keyring_file).expanduser()
    if not raw.is_absolute():
        raw = Path.cwd() / raw
    try:
        parent = raw.parent.resolve(strict=True)
    except OSError as exc:
        raise LifecycleEvidenceError(f"cannot resolve trusted reviewer keyring directory: {exc}") from exc
    keyring_path = parent / raw.name
    if parent.is_relative_to(root):
        raise LifecycleEvidenceError("trusted reviewer keyring must be outside the project root")
    try:
        keyring_bytes, keyring_info = _read_regular_file(keyring_path)
        if os.name == "posix" and keyring_info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
            raise LifecycleEvidenceError("trusted reviewer keyring must not be group- or world-writable")
        data = json.loads(keyring_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(f"cannot read trusted reviewer keyring: {exc}") from exc
    if not isinstance(data, dict) or data.get("schema") != "tsar/trusted-reviewers/v1":
        raise LifecycleEvidenceError("unsupported trusted reviewer keyring schema")
    keys = data.get("keys")
    if not isinstance(keys, list):
        raise LifecycleEvidenceError("trusted reviewer keyring keys must be a list")
    result = {}
    seen_ids = set()
    for item in keys:
        if not isinstance(item, dict):
            raise LifecycleEvidenceError("trusted reviewer key entry must be an object")
        key_id, actor, encoded = item.get("key_id"), item.get("actor"), item.get("public_key")
        gates = item.get("allowed_gates")
        if (not isinstance(key_id, str) or not key_id or key_id in seen_ids
                or not isinstance(actor, str) or not actor.strip()
                or not isinstance(encoded, str) or not isinstance(gates, list)
                or not all(isinstance(g, str) and g for g in gates)
                or not isinstance(item.get("active"), bool)):
            raise LifecycleEvidenceError("invalid or duplicate trusted reviewer key entry")
        seen_ids.add(key_id)
        if item["active"]:
            try:
                public_bytes = base64.b64decode(encoded, validate=True)
                if len(public_bytes) != 32:
                    raise ValueError("Ed25519 public keys must be 32 bytes")
                item = dict(item)
                item["_public_key"] = Ed25519PublicKey.from_public_bytes(public_bytes)
                result[key_id] = item
            except (ValueError, TypeError) as exc:
                raise LifecycleEvidenceError(f"invalid public key for reviewer {key_id}") from exc
    return result


def build_attestation_payload(audit_file: Path, *, repo_root: Path, gate: str,
                              evidence_file: str, key_id: str, keyring_file: Path,
                              decision: str = "PASS", issued_at: str | None = None) -> dict:
    """Build the exact payload a trusted reviewer must sign with their private key."""
    root = Path(repo_root).resolve(strict=True)
    audit, record, audit_bytes = _load_audit(audit_file, root)
    key = _load_keyring(keyring_file, root).get(key_id)
    if key is None or not key["active"]:
        raise LifecycleEvidenceError("reviewer key is not trusted or is inactive")
    provenance = record.get("provenance", {})
    if not isinstance(provenance, dict):
        raise LifecycleEvidenceError("audit provenance must be an object")
    if gate not in record["gates"] or gate == "upstream_preflight":
        raise LifecycleEvidenceError("unknown or reserved lifecycle gate")
    if record["gates"][gate] != "PENDING":
        raise LifecycleEvidenceError("only PENDING gates may receive an attestation")
    if gate not in key["allowed_gates"]:
        raise LifecycleEvidenceError("reviewer key is not authorized for this gate")
    if decision not in {"PASS", "FAIL"}:
        raise LifecycleEvidenceError("decision must be PASS or FAIL")
    evidence_path, digest, size = _safe_relative_file(root, evidence_file)
    timestamp = issued_at or datetime.now(timezone.utc).isoformat()
    try:
        if not isinstance(timestamp, str):
            raise ValueError("timestamp must be a string")
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError("timezone required")
        if parsed > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("timestamp is in the future")
    except (TypeError, ValueError) as exc:
        raise LifecycleEvidenceError("issued_at must be a timezone-aware ISO-8601 timestamp") from exc
    return {
        "schema": "tsar/reviewer-attestation-payload/v1",
        "audit_path": audit.relative_to(root).as_posix(),
        "audit_binding": "tsar/lifecycle-context/v1",
        "audit_sha256": _audit_context_digest(record),
        "upstream_commit_sha": provenance.get("upstream_commit_sha"),
        "gate": gate,
        "decision": decision,
        "key_id": key_id,
        "actor": key["actor"],
        "evidence_path": evidence_path.relative_to(root).as_posix(),
        "evidence_sha256": digest,
        "evidence_size_bytes": size,
        "issued_at": timestamp,
    }


def _verify_signature(payload: dict, signature_b64: str, key: dict) -> bytes:
    try:
        signature = base64.b64decode(signature_b64, validate=True)
        if len(signature) != 64:
            raise ValueError("Ed25519 signatures must be 64 bytes")
        key["_public_key"].verify(signature, _canonical(payload))
        return signature
    except (ValueError, TypeError, InvalidSignature) as exc:
        raise LifecycleEvidenceError("reviewer signature is invalid") from exc


def attest_gate(audit_file: Path, *, repo_root: Path, gate: str, evidence_file: str,
                attestation_file: Path, trusted_reviewers_file: Path) -> dict:
    """Verify an authorized Ed25519 reviewer attestation before updating a pending gate."""
    root = Path(repo_root).resolve(strict=True)
    audit, record, audit_bytes = _load_audit(audit_file, root)
    try:
        raw_attestation = Path(attestation_file).expanduser()
        if not raw_attestation.is_absolute():
            raw_attestation = Path.cwd() / raw_attestation
        attestation_parent = raw_attestation.parent.resolve(strict=True)
        attestation_bytes, _ = _read_regular_file(attestation_parent / raw_attestation.name)
        envelope = json.loads(attestation_bytes)
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(f"cannot read reviewer attestation: {exc}") from exc
    if not isinstance(envelope, dict) or envelope.get("schema") != "tsar/reviewer-attestation/v1":
        raise LifecycleEvidenceError("unsupported reviewer attestation schema")
    payload, key_id, signature_b64 = envelope.get("payload"), envelope.get("key_id"), envelope.get("signature")
    if not isinstance(payload, dict) or not isinstance(key_id, str) or not isinstance(signature_b64, str):
        raise LifecycleEvidenceError("reviewer attestation envelope is incomplete")
    keys = _load_keyring(trusted_reviewers_file, root)
    key = keys.get(key_id)
    if key is None:
        raise LifecycleEvidenceError("reviewer key is not trusted or is inactive")
    if gate not in key["allowed_gates"]:
        raise LifecycleEvidenceError("reviewer key is not authorized for this gate")
    expected = build_attestation_payload(
        audit, repo_root=root, gate=gate, evidence_file=evidence_file,
        key_id=key_id, keyring_file=trusted_reviewers_file,
        decision=payload.get("decision"),
        issued_at=payload.get("issued_at"),
    )
    if payload != expected or payload.get("actor") != key["actor"]:
        raise LifecycleEvidenceError("signed payload does not match current audit, gate, evidence, or reviewer identity")
    signature = _verify_signature(payload, signature_b64, key)
    evidence = {
        "gate": gate, "decision": payload["decision"], "actor": key["actor"],
        "reviewer_key_id": key_id, "recorded_at": payload["issued_at"],
        "path": payload["evidence_path"], "sha256": payload["evidence_sha256"],
        "size_bytes": payload["evidence_size_bytes"],
        "attestation": {"schema": envelope["schema"], "key_id": key_id,
                        "payload": payload, "signature": signature_b64},
        "signature_sha256": _sha256_bytes(signature),
    }
    lock = audit.with_name(audit.name + ".lock")
    try:
        lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise LifecycleEvidenceError("another audit update is in progress; retry later") from exc
    try:
        current_audit, current, current_bytes = _load_audit(audit, root)
        if current_bytes != audit_bytes or current["gates"].get(gate) != "PENDING":
            raise LifecycleEvidenceError("audit changed or gate is no longer pending; regenerate the attestation")
        current.setdefault("evidence", []).append(evidence)
        current["gates"][gate] = payload["decision"]
        current["updated_at"] = payload["issued_at"]
        fd, temp_name = __import__("tempfile").mkstemp(prefix=f".{audit.name}.", dir=str(audit.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(current, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temp_name, 0o600)
            os.replace(temp_name, audit)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(f"cannot update lifecycle audit record: {exc}") from exc
    finally:
        os.close(lock_fd)
        try:
            lock.unlink()
        except OSError:
            pass
    return current


def verify_audit(audit_file: Path, *, repo_root: Path, trusted_reviewers_file: Path) -> dict:
    """Re-hash evidence and verify each detached reviewer signature against the external keyring."""
    root = Path(repo_root).resolve(strict=True)
    audit, record, _ = _load_audit(audit_file, root)
    keys = _load_keyring(trusted_reviewers_file, root)
    provenance = record.get("provenance", {})
    if not isinstance(provenance, dict):
        raise LifecycleEvidenceError("audit provenance must be an object")
    entries = record.get("evidence", [])
    findings, seen = [], set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            findings.append({"index": index, "status": "INVALID", "reason": "evidence entry is not an object"})
            continue
        gate = entry.get("gate")
        if not isinstance(gate, str) or gate not in record["gates"] or gate == "upstream_preflight" or gate in seen:
            findings.append({"index": index, "status": "INVALID", "reason": "unknown, reserved, or duplicate evidence gate"})
            continue
        seen.add(gate)
        if entry.get("decision") not in {"PASS", "FAIL"} or record["gates"].get(gate) != entry.get("decision"):
            findings.append({"index": index, "gate": gate, "status": "INVALID", "reason": "gate decision does not match evidence"})
            continue
        try:
            _, digest, size = _safe_relative_file(root, entry.get("path", ""))
        except (LifecycleEvidenceError, OSError) as exc:
            findings.append({"index": index, "gate": gate, "status": "MISSING_OR_UNSAFE", "reason": str(exc)})
            continue
        if digest != entry.get("sha256") or size != entry.get("size_bytes"):
            findings.append({"index": index, "gate": gate, "status": "HASH_MISMATCH"})
            continue
        envelope = entry.get("attestation")
        try:
            if not isinstance(envelope, dict) or envelope.get("schema") != "tsar/reviewer-attestation/v1":
                raise LifecycleEvidenceError("missing signed reviewer attestation")
            key_id = envelope.get("key_id")
            if not isinstance(key_id, str):
                raise LifecycleEvidenceError("reviewer key ID must be a string")
            key = keys.get(key_id)
            payload = envelope.get("payload")
            if key is None or not isinstance(payload, dict):
                raise LifecycleEvidenceError("reviewer key is not trusted or payload is invalid")
            if gate not in key["allowed_gates"]:
                raise LifecycleEvidenceError("reviewer is not authorized for this gate")
            expected_fields = {
                "schema": "tsar/reviewer-attestation-payload/v1",
                "audit_path": audit.relative_to(root).as_posix(),
                "audit_binding": "tsar/lifecycle-context/v1",
                "audit_sha256": _audit_context_digest(record),
                "gate": gate, "decision": entry["decision"], "actor": key["actor"],
                "key_id": key_id, "evidence_path": entry["path"],
                "evidence_sha256": digest, "evidence_size_bytes": size,
                "upstream_commit_sha": provenance.get("upstream_commit_sha"),
                "issued_at": entry.get("recorded_at"),
            }
            if payload.get("audit_binding") != "tsar/lifecycle-context/v1":
                raise LifecycleEvidenceError("unsupported or missing lifecycle audit binding")
            if payload.get("audit_sha256") != _audit_context_digest(record):
                raise LifecycleEvidenceError("signed lifecycle context digest does not match current audit record")
            try:
                issued = datetime.fromisoformat(str(payload.get("issued_at", "")).replace("Z", "+00:00"))
                if issued.tzinfo is None or issued > datetime.now(timezone.utc) + timedelta(minutes=5):
                    raise ValueError("invalid attestation timestamp")
            except ValueError as exc:
                raise LifecycleEvidenceError("signed reviewer timestamp is invalid") from exc
            if any(payload.get(name) != value for name, value in expected_fields.items()):
                raise LifecycleEvidenceError("signed reviewer payload does not match audit entry")
            signature = _verify_signature(payload, envelope.get("signature", ""), key)
            if entry.get("actor") != key["actor"] or entry.get("reviewer_key_id") != key_id:
                raise LifecycleEvidenceError("recorded reviewer identity does not match trusted key")
            if entry.get("signature_sha256") != _sha256_bytes(signature):
                raise LifecycleEvidenceError("signature digest does not match audit entry")
        except LifecycleEvidenceError as exc:
            findings.append({"index": index, "gate": gate, "status": "UNAUTHENTICATED", "reason": str(exc)})
            continue
        findings.append({"index": index, "gate": gate, "status": "PASS", "sha256": digest, "reviewer_key_id": key_id})
    for gate, state in record["gates"].items():
        if gate != "upstream_preflight" and state in {"PASS", "FAIL"} and gate not in seen:
            findings.append({"gate": gate, "status": "INVALID", "reason": "gate has a decision but no evidence entry"})
    integrity_valid = all(item["status"] == "PASS" for item in findings)
    gate_states = [state for gate, state in record["gates"].items() if gate != "upstream_preflight"]
    if any(state == "FAIL" for state in gate_states):
        lifecycle_status = "FAILED"
    elif any(state == "PENDING" for state in gate_states):
        lifecycle_status = "IN_PROGRESS"
    else:
        lifecycle_status = "COMPLETE"
    if not integrity_valid or lifecycle_status == "FAILED":
        overall_status = "FAIL"
    elif lifecycle_status == "IN_PROGRESS":
        overall_status = "INCOMPLETE"
    else:
        overall_status = "PASS"
    return {
        "schema": "tsar/lifecycle-audit-verification/v3",
        "audit_file": audit.relative_to(root).as_posix(),
        "status": overall_status,
        "integrity_status": "PASS" if integrity_valid else "FAIL",
        "lifecycle_status": lifecycle_status,
        "evidence_count": len(entries),
        "findings": findings,
        "limitations": [
            "Ed25519 signatures authenticate possession of a trusted private key, not the human behind it.",
            "Reviewer authorization depends on protecting the external keyring and private keys.",
            "Signatures bind the audit snapshot and evidence bytes at signing time; the local audit remains unsigned and can be deleted.",
            "A valid signature does not establish evidence truth or replace independent review and organizational controls.",
        ],
    }
