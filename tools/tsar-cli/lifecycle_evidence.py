"""Evidence-backed lifecycle gate updates; hashes do not prove truth or authorization."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile


class LifecycleEvidenceError(RuntimeError):
    """Raised when lifecycle evidence cannot safely update a run."""


def _safe_evidence(root: Path, supplied: str) -> tuple[Path, str, int]:
    candidate = Path(supplied)
    if candidate.is_absolute() or any(part in {"", ".", ".."} for part in candidate.parts):
        raise LifecycleEvidenceError("evidence path must be a safe relative path")
    current = root
    for part in candidate.parts:
        current = current / part
        if current.is_symlink():
            raise LifecycleEvidenceError("symlinks are not accepted in evidence paths")
    resolved = current.resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise LifecycleEvidenceError("evidence must be a regular file inside the project root")
    digest, size = hashlib.sha256(), 0
    with resolved.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            size += len(chunk)
            digest.update(chunk)
    if not size:
        raise LifecycleEvidenceError("empty evidence files are not accepted")
    return resolved, digest.hexdigest(), size


def attest_gate(audit_file: Path, *, repo_root: Path, gate: str,
                evidence_file: str, actor: str, decision: str = "PASS") -> dict:
    """Attach a SHA-256 evidence reference and update one pending gate atomically."""
    root = Path(repo_root).resolve(strict=True)
    raw_audit = Path(audit_file).expanduser()
    if raw_audit.is_symlink():
        raise LifecycleEvidenceError("audit symlinks are not accepted")
    audit = raw_audit.resolve(strict=True)
    if not audit.is_file() or not audit.is_relative_to(root):
        raise LifecycleEvidenceError("audit file must be a regular file inside the project root")
    try:
        initial = json.loads(audit.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LifecycleEvidenceError(f"cannot read lifecycle audit record: {exc}") from exc
    if initial.get("schema") != "tsar/lifecycle-run/v1":
        raise LifecycleEvidenceError("unsupported lifecycle audit schema")
    if not isinstance(initial.get("gates"), dict) or gate not in initial["gates"]:
        raise LifecycleEvidenceError(f"unknown lifecycle gate: {gate}")
    if gate == "upstream_preflight":
        raise LifecycleEvidenceError("upstream_preflight is reserved for the upstream verifier")
    if initial["gates"][gate] != "PENDING":
        raise LifecycleEvidenceError("only PENDING gates may receive evidence")
    if decision not in {"PASS", "FAIL"}:
        raise LifecycleEvidenceError("decision must be PASS or FAIL")
    if not isinstance(actor, str) or not actor.strip() or len(actor.strip()) > 200:
        raise LifecycleEvidenceError("actor must be a non-empty identifier of at most 200 characters")

    evidence_path, digest, size = _safe_evidence(root, evidence_file)
    evidence = {
        "gate": gate, "decision": decision, "actor": actor.strip(),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "path": evidence_path.relative_to(root).as_posix(),
        "sha256": digest, "size_bytes": size,
    }
    lock = audit.with_name(audit.name + ".lock")
    try:
        lock_fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise LifecycleEvidenceError("another audit update is in progress; retry later") from exc
    try:
        current = json.loads(audit.read_text(encoding="utf-8"))
        if current.get("schema") != "tsar/lifecycle-run/v1" or current.get("gates", {}).get(gate) != "PENDING":
            raise LifecycleEvidenceError("audit changed or gate is no longer pending")
        current.setdefault("evidence", []).append(evidence)
        current["gates"][gate] = decision
        current["updated_at"] = evidence["recorded_at"]
        fd, temp_name = tempfile.mkstemp(prefix=f".{audit.name}.", dir=str(audit.parent))
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
