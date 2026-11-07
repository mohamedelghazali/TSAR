"""Tests for strict TSAR agent conformance evidence validation."""
import importlib.util
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "tools" / "agent-conformance" / "validate_evidence.py"
SPEC = importlib.util.spec_from_file_location("tsar_agent_evidence", MODULE)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def valid_record():
    return {
        "schema_version": "tsar/agent-conformance-evidence/v1",
        "run_id": "local-test-001",
        "timestamp_utc": "2026-11-07T12:00:00Z",
        "scenario_id": "AC-01",
        "agent": {
            "inventory_name": "GPT", "product": "ChatGPT", "edition": None,
            "model_or_runtime_id": "test-model", "runtime_version": None,
            "integration_mechanism": "system instruction", "access_status": "AVAILABLE",
        },
        "tsar": {
            "repository": "mohamedelghazali/TSAR", "commit_sha": "a" * 40,
            "manifest_version": "1.2.0", "manifest_sha256": "b" * 64,
            "policy_files": [{"path": "system/CORE_DIRECTIVE.md", "sha256": "c" * 64}],
        },
        "assurance": {"claimed_level": "E1", "covered_operations": [], "uncovered_operations": ["tool dispatch"]},
        "result": "PASS",
        "checks": [{"check_id": "AC-01", "status": "PASS", "tool": "manual-evaluator", "version": "1", "command": None, "exit_code": 0, "reason": None}],
        "evidence_artifacts": [{"path": "evidence/output.txt", "sha256": "d" * 64, "kind": "sanitized-response", "sanitized": True}],
    }


def test_valid_record_is_accepted():
    assert validator.validate_record(valid_record())["result"] == "PASS"


def test_unknown_agent_is_rejected():
    record = valid_record()
    record["agent"]["inventory_name"] = "Unknown Agent"
    try:
        validator.validate_record(record)
    except validator.EvidenceValidationError as exc:
        assert "unknown agent" in str(exc)
    else:
        raise AssertionError("unknown agent must be rejected")


def test_non_pass_check_cannot_be_reported_as_overall_pass():
    record = valid_record()
    record["checks"][0]["status"] = "NOT_RUN"
    record["checks"][0]["reason"] = "Provider credentials unavailable"
    record["checks"][0]["exit_code"] = None
    try:
        validator.validate_record(record)
    except validator.EvidenceValidationError as exc:
        assert "overall PASS conflicts" in str(exc)
    else:
        raise AssertionError("contradictory overall PASS must be rejected")


def test_missing_reason_for_blocked_check_is_rejected():
    record = valid_record()
    record["checks"][0].update(status="BLOCKED", exit_code=None, reason=None)
    try:
        validator.validate_record(record)
    except validator.EvidenceValidationError as exc:
        assert "requires a reason" in str(exc)
    else:
        raise AssertionError("blocked check without reason must be rejected")


def test_sensitive_credentials_fields_are_rejected():
    record = valid_record()
    record["agent"]["api_key"] = "never-store-this"
    try:
        validator.validate_record(record)
    except validator.EvidenceValidationError as exc:
        assert "sensitive-looking field" in str(exc)
    else:
        raise AssertionError("credential-bearing evidence must be rejected")


def test_timezone_is_mandatory():
    record = valid_record()
    record["timestamp_utc"] = "2026-11-07T12:00:00"
    try:
        validator.validate_record(record)
    except validator.EvidenceValidationError as exc:
        assert "timezone" in str(exc)
    else:
        raise AssertionError("naive timestamp must be rejected")


def test_result_vocabulary_is_closed():
    record = valid_record()
    record["result"] = "SKIPPED"
    try:
        validator.validate_record(record)
    except validator.EvidenceValidationError as exc:
        assert "invalid result" in str(exc)
    else:
        raise AssertionError("unknown result must be rejected")
