"""Strict standard-library validator for TSAR agent conformance evidence v1."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

AGENTS = {
    "Claude (chat)", "Claude Code", "GPT", "DeepSeek-Coder", "Qwen-Coder",
    "Gemini", "Llama", "Cursor", "GitHub Copilot", "Manus", "Windsurf",
    "SuperNinja", "Replit Agent", "Devin", "Kimi",
}
RESULTS = {"PASS", "FAIL", "BLOCKED", "NOT_RUN", "NOT_APPLICABLE"}
LEVELS = {f"E{i}" for i in range(7)}
SHA256 = re.compile(r"^[a-fA-F0-9]{64}$")
SHA1 = re.compile(r"^[a-fA-F0-9]{40}$")
SENSITIVE_KEY = re.compile(r"(?:token|secret|password|api[_-]?key|private[_-]?key|cookie|authorization)", re.I)


class EvidenceValidationError(ValueError):
    """Raised when a conformance evidence record is incomplete or unsafe."""


def _object(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise EvidenceValidationError(f"{label} must be an object")
    return value


def _string(value: Any, label: str, *, nullable: bool = False) -> None:
    if nullable and value is None:
        return
    if not isinstance(value, str) or not value.strip():
        raise EvidenceValidationError(f"{label} must be a non-empty string")


def _digest(value: Any, label: str, pattern: re.Pattern[str]) -> None:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise EvidenceValidationError(f"{label} must be a valid hexadecimal digest")


def _reject_sensitive_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if SENSITIVE_KEY.search(str(key)):
                raise EvidenceValidationError(f"sensitive-looking field is forbidden at {path}.{key}")
            _reject_sensitive_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_sensitive_keys(child, f"{path}[{index}]")


def validate_record(record: Any) -> dict:
    data = _object(record, "record")
    _reject_sensitive_keys(data)
    required = {
        "schema_version", "run_id", "timestamp_utc", "scenario_id", "agent",
        "tsar", "assurance", "result", "checks", "evidence_artifacts",
    }
    missing = required - data.keys()
    extra = data.keys() - required - {"notes"}
    if missing or extra:
        raise EvidenceValidationError(f"top-level fields mismatch (missing={sorted(missing)}, extra={sorted(extra)})")
    if data["schema_version"] != "tsar/agent-conformance-evidence/v1":
        raise EvidenceValidationError("unsupported schema_version")
    _string(data["run_id"], "run_id")
    _string(data["scenario_id"], "scenario_id")
    if not re.fullmatch(r"AC-[0-9]{2}", data["scenario_id"]):
        raise EvidenceValidationError("scenario_id must match AC-NN")
    timestamp = data["timestamp_utc"]
    _string(timestamp, "timestamp_utc")
    try:
        parsed = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EvidenceValidationError("timestamp_utc must be ISO-8601 date-time") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise EvidenceValidationError("timestamp_utc must include a timezone")

    agent = _object(data["agent"], "agent")
    agent_fields = {"inventory_name", "product", "edition", "model_or_runtime_id", "runtime_version", "integration_mechanism", "access_status"}
    if agent.keys() != agent_fields:
        raise EvidenceValidationError("agent fields do not match schema")
    if agent["inventory_name"] not in AGENTS:
        raise EvidenceValidationError("unknown agent inventory_name")
    for field in ("product", "integration_mechanism"):
        _string(agent[field], f"agent.{field}")
    for field in ("edition", "model_or_runtime_id", "runtime_version"):
        _string(agent[field], f"agent.{field}", nullable=True)
    if agent["access_status"] not in {"AVAILABLE", "UNAVAILABLE", "UNAUTHENTICATED", "NOT_APPLICABLE"}:
        raise EvidenceValidationError("invalid agent.access_status")

    tsar = _object(data["tsar"], "tsar")
    if tsar.keys() != {"repository", "commit_sha", "manifest_version", "manifest_sha256", "policy_files"}:
        raise EvidenceValidationError("tsar fields do not match schema")
    _string(tsar["repository"], "tsar.repository")
    if "/" not in tsar["repository"] or any(ch.isspace() for ch in tsar["repository"]):
        raise EvidenceValidationError("tsar.repository must be owner/repository")
    _digest(tsar["commit_sha"], "tsar.commit_sha", SHA1)
    _string(tsar["manifest_version"], "tsar.manifest_version")
    _digest(tsar["manifest_sha256"], "tsar.manifest_sha256", SHA256)
    if not isinstance(tsar["policy_files"], list):
        raise EvidenceValidationError("tsar.policy_files must be a list")
    for index, item in enumerate(tsar["policy_files"]):
        policy = _object(item, f"tsar.policy_files[{index}]")
        if policy.keys() != {"path", "sha256"}:
            raise EvidenceValidationError(f"tsar.policy_files[{index}] fields mismatch")
        _string(policy["path"], f"tsar.policy_files[{index}].path")
        _digest(policy["sha256"], f"tsar.policy_files[{index}].sha256", SHA256)

    assurance = _object(data["assurance"], "assurance")
    if assurance.keys() != {"claimed_level", "covered_operations", "uncovered_operations"}:
        raise EvidenceValidationError("assurance fields do not match schema")
    if assurance["claimed_level"] not in LEVELS:
        raise EvidenceValidationError("invalid assurance.claimed_level")
    for field in ("covered_operations", "uncovered_operations"):
        values = assurance[field]
        if not isinstance(values, list) or any(not isinstance(item, str) for item in values):
            raise EvidenceValidationError(f"assurance.{field} must be a list of strings")

    if data["result"] not in RESULTS:
        raise EvidenceValidationError("invalid result")
    if not isinstance(data["checks"], list) or not data["checks"] or not isinstance(data["evidence_artifacts"], list) or not data["evidence_artifacts"]:
        raise EvidenceValidationError("checks and evidence_artifacts must be non-empty lists")
    for index, item in enumerate(data["checks"]):
        check = _object(item, f"checks[{index}]")
        allowed = {"check_id", "status", "tool", "version", "command", "exit_code", "reason"}
        if check.keys() != allowed:
            raise EvidenceValidationError(f"checks[{index}] fields do not match schema")
        for field in ("check_id", "tool"):
            _string(check[field], f"checks[{index}].{field}")
        if check["status"] not in RESULTS:
            raise EvidenceValidationError(f"checks[{index}].status is invalid")
        for field in ("version", "command", "reason"):
            _string(check[field], f"checks[{index}].{field}", nullable=True)
        if check["exit_code"] is not None and (isinstance(check["exit_code"], bool) or not isinstance(check["exit_code"], int)):
            raise EvidenceValidationError(f"checks[{index}].exit_code must be integer or null")
        if check["status"] in {"NOT_RUN", "NOT_APPLICABLE", "BLOCKED"} and not check["reason"]:
            raise EvidenceValidationError(f"checks[{index}] requires a reason for {check['status']}")
        if check["status"] == "PASS" and check["exit_code"] not in (0, None):
            raise EvidenceValidationError(f"checks[{index}] PASS must have exit_code 0 or null")

    for index, item in enumerate(data["evidence_artifacts"]):
        artifact = _object(item, f"evidence_artifacts[{index}]")
        allowed = {"path", "sha256", "kind", "sanitized"}
        if artifact.keys() - allowed or not {"path", "sha256", "kind"} <= artifact.keys():
            raise EvidenceValidationError(f"evidence_artifacts[{index}] fields do not match schema")
        _string(artifact["path"], f"evidence_artifacts[{index}].path")
        artifact_path = Path(artifact["path"])
        if artifact_path.is_absolute() or ".." in artifact_path.parts or "." in artifact_path.parts:
            raise EvidenceValidationError(f"evidence_artifacts[{index}].path must be a safe relative path")
        _digest(artifact["sha256"], f"evidence_artifacts[{index}].sha256", SHA256)
        _string(artifact["kind"], f"evidence_artifacts[{index}].kind")
        if "sanitized" in artifact and not isinstance(artifact["sanitized"], bool):
            raise EvidenceValidationError(f"evidence_artifacts[{index}].sanitized must be boolean")

    if "notes" in data and (not isinstance(data["notes"], list) or any(not isinstance(note, str) for note in data["notes"])):
        raise EvidenceValidationError("notes must be a list of strings")

    # Overall PASS is impossible if any required check is failed, blocked, skipped, or not applicable.
    if data["result"] == "PASS" and any(item["status"] != "PASS" for item in data["checks"]):
        raise EvidenceValidationError("overall PASS conflicts with non-PASS check evidence")
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a TSAR agent runtime conformance evidence JSON record")
    parser.add_argument("record", type=Path, help="Path to evidence JSON")
    args = parser.parse_args(argv)
    try:
        record = json.loads(args.record.read_text(encoding="utf-8"))
        validate_record(record)
    except (OSError, json.JSONDecodeError, EvidenceValidationError) as exc:
        print(f"TSAR AGENT EVIDENCE: INVALID — {exc}", file=sys.stderr)
        return 2
    print("TSAR AGENT EVIDENCE: VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
