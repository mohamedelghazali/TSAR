"""Fail-closed output verification and task evidence for controlled integrations.

This module records observed checks; it does not claim a local JSON file is
signed, tamper-proof, or proof that a scanner has no false negatives.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

_SHA1 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_STATUSES = frozenset({"PASS", "FAIL", "BLOCKED", "NOT_RUN"})


class OutputGateError(RuntimeError):
    """Generated output cannot be accepted because verification is incomplete."""


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    tool: str
    version: str
    exit_code: int | None
    artifact_sha256: str | None = None
    detail: str | None = None


def _canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _valid_hash_map(value: Mapping[str, str], label: str) -> dict[str, str]:
    if not isinstance(value, Mapping) or not value:
        raise OutputGateError(f"{label} must be a non-empty mapping")
    result = dict(value)
    for name, digest in result.items():
        if not isinstance(name, str) or not name or not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            raise OutputGateError(f"{label} contains an invalid SHA-256 entry")
    return result


class OutputGate:
    """Run required checks on actual changed files and emit verifiable evidence."""

    def __init__(
        self,
        *,
        task_id: str,
        agent: str,
        adapter_version: str,
        tsar_commit_sha: str,
        manifest_version: str,
        manifest_sha256: str,
        policy_hashes: Mapping[str, str],
        domains: Iterable[str],
        enforcement_level: str,
    ) -> None:
        if not task_id or not agent or not adapter_version:
            raise OutputGateError("Task, agent, and adapter identity are required")
        if not isinstance(tsar_commit_sha, str) or not _SHA1.fullmatch(tsar_commit_sha):
            raise OutputGateError("TSAR commit SHA must be a 40-character immutable SHA")
        if not manifest_version or not isinstance(manifest_sha256, str) or not _SHA256.fullmatch(manifest_sha256):
            raise OutputGateError("Manifest version and SHA-256 are required")
        if enforcement_level not in {"E2", "E3", "E4", "E5"}:
            raise OutputGateError("Unsupported enforcement level")
        self.provenance = {
            "repository": "mohamedelghazali/TSAR",
            "commit_sha": tsar_commit_sha,
            "manifest_version": manifest_version,
            "manifest_sha256": manifest_sha256,
            "policy_sha256": _valid_hash_map(policy_hashes, "policy_hashes"),
            "domains": sorted(set(domains)),
            "enforcement_level": enforcement_level,
        }
        if not self.provenance["domains"]:
            raise OutputGateError("At least one applicable policy domain is required")
        self.task_id = task_id
        self.agent = agent
        self.adapter_version = adapter_version

    @staticmethod
    def _file_hashes(changed_files: Iterable[str | Path]) -> dict[str, str]:
        files = sorted({Path(p).resolve() for p in changed_files}, key=str)
        if not files:
            raise OutputGateError("No changed files supplied; output cannot be marked compliant")
        hashes = {}
        for path in files:
            if not path.is_file():
                raise OutputGateError(f"Changed file is missing or not a regular file: {path}")
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        return hashes

    def evaluate(
        self,
        *,
        changed_files: Iterable[str | Path],
        checks: Iterable[CheckResult],
        required_checks: Iterable[str],
        skipped: Mapping[str, str] | None = None,
        output_path: str | Path | None = None,
    ) -> dict[str, Any]:
        file_hashes = self._file_hashes(changed_files)
        check_list = list(checks)
        check_map = {c.name: c for c in check_list}
        if len(check_map) != len(check_list) or any(not c.name for c in check_list):
            raise OutputGateError("Check names must be unique and non-empty")
        for check in check_list:
            if check.status not in _STATUSES or not check.tool or not check.version:
                raise OutputGateError(f"Invalid check result: {check.name}")
            if check.status == "PASS" and check.exit_code != 0:
                raise OutputGateError(f"Passing check must have exit code 0: {check.name}")
            if check.status == "FAIL" and check.exit_code in (None, 0):
                raise OutputGateError(f"Failing check must have a non-zero exit code: {check.name}")
            if check.artifact_sha256 is not None and not _SHA256.fullmatch(check.artifact_sha256):
                raise OutputGateError(f"Invalid artifact hash: {check.name}")

        required = sorted(set(required_checks))
        if not required:
            raise OutputGateError("At least one mandatory output check is required")
        missing = [name for name in required if name not in check_map]
        failed = [name for name in required if name in check_map and check_map[name].status != "PASS"]
        skipped_map = dict(skipped or {})
        if any(not k or not v for k, v in skipped_map.items()):
            raise OutputGateError("Every skipped check must include an explicit reason")
        for name in required:
            if name in skipped_map and name not in check_map:
                failed.append(name)
        status = "PASS" if not missing and not failed else "BLOCKED"
        record = {
            "schema": "tsar/output-evidence/v1",
            "task_id": self.task_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": self.agent,
            "adapter_version": self.adapter_version,
            "provenance": self.provenance,
            "changed_files": file_hashes,
            "checks": [asdict(c) for c in sorted(check_list, key=lambda c: c.name)],
            "required_checks": required,
            "skipped_checks": skipped_map,
            "missing_required_checks": missing,
            "failed_required_checks": sorted(set(failed)),
            "decision": status,
        }
        record["evidence_sha256"] = _canonical_hash(record)
        if output_path is not None:
            self.write(record, output_path)
        if status != "PASS":
            raise OutputGateError(
                "Output acceptance blocked; missing=" + repr(missing) +
                ", failed_or_not_passed=" + repr(sorted(set(failed)))
            )
        return record

    @staticmethod
    def write(record: Mapping[str, Any], output_path: str | Path) -> None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = json.dumps(record, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        fd, temporary = tempfile.mkstemp(prefix=".tsar-evidence-", dir=str(destination.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, destination)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    @staticmethod
    def verify_record(record: Mapping[str, Any]) -> bool:
        """Verify schema and record digest; this is integrity checking, not a signature."""
        if not isinstance(record, Mapping) or record.get("schema") != "tsar/output-evidence/v1":
            return False
        supplied = record.get("evidence_sha256")
        if not isinstance(supplied, str) or not _SHA256.fullmatch(supplied):
            return False
        unsigned = dict(record)
        unsigned.pop("evidence_sha256", None)
        try:
            return _canonical_hash(unsigned) == supplied
        except (TypeError, ValueError):
            return False
