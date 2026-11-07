from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "tsar-cli"))
from output_verification import CheckResult, OutputGate, OutputGateError


SHA = "a" * 40
HASH = "b" * 64


def gate():
    return OutputGate(
        task_id="task-123", agent="test-agent", adapter_version="1.0.0",
        tsar_commit_sha=SHA, manifest_version="1.2.0",
        manifest_sha256=HASH, policy_hashes={"CORE_DIRECTIVE.md": HASH},
        domains=["python"], enforcement_level="E4",
    )


def check(name="secret-scan", status="PASS", code=0):
    return CheckResult(name, status, "scanner", "2.1", code, HASH)


def test_pass_records_changed_file_and_policy_provenance(tmp_path):
    changed = tmp_path / "output.py"
    changed.write_text("print('safe')", encoding="utf-8")
    path = tmp_path / "evidence.json"
    record = gate().evaluate(
        changed_files=[changed], checks=[check()],
        required_checks=["secret-scan"], output_path=path,
    )
    assert record["decision"] == "PASS"
    assert record["provenance"]["commit_sha"] == SHA
    assert record["changed_files"][str(changed.resolve())] == hashlib.sha256(b"print('safe')").hexdigest()
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert OutputGate.verify_record(saved)


def test_missing_required_check_blocks_and_never_returns_compliant(tmp_path):
    changed = tmp_path / "out.txt"
    changed.write_text("x", encoding="utf-8")
    path = tmp_path / "blocked.json"
    with pytest.raises(OutputGateError, match="Output acceptance blocked"):
        gate().evaluate(changed_files=[changed], checks=[], required_checks=["tests"], output_path=path)
    record = json.loads(path.read_text(encoding="utf-8"))
    assert record["decision"] == "BLOCKED"
    assert record["missing_required_checks"] == ["tests"]


def test_failed_or_not_run_required_check_blocks(tmp_path):
    changed = tmp_path / "out.txt"
    changed.write_text("x", encoding="utf-8")
    for result in (check(status="FAIL", code=1), check(status="NOT_RUN", code=None)):
        with pytest.raises(OutputGateError):
            gate().evaluate(changed_files=[changed], checks=[result], required_checks=["secret-scan"])


def test_skipped_check_is_not_passed(tmp_path):
    changed = tmp_path / "out.txt"
    changed.write_text("x", encoding="utf-8")
    with pytest.raises(OutputGateError):
        gate().evaluate(changed_files=[changed], checks=[], required_checks=["tests"],
                        skipped={"tests": "tool unavailable"})


def test_empty_changed_files_cannot_be_compliant():
    with pytest.raises(OutputGateError, match="No changed files"):
        gate().evaluate(changed_files=[], checks=[check()], required_checks=["secret-scan"])


def test_invalid_policy_hash_is_rejected():
    with pytest.raises(OutputGateError, match="SHA-256"):
        OutputGate(task_id="t", agent="a", adapter_version="1", tsar_commit_sha=SHA,
                   manifest_version="1.2.0", manifest_sha256=HASH,
                   policy_hashes={"rule": "bad"}, domains=["python"], enforcement_level="E4")


def test_tampered_evidence_fails_integrity_check(tmp_path):
    changed = tmp_path / "out.txt"
    changed.write_text("x", encoding="utf-8")
    record = gate().evaluate(changed_files=[changed], checks=[check()], required_checks=["secret-scan"])
    record["decision"] = "BLOCKED"
    assert not OutputGate.verify_record(record)
