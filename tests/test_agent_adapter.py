"""Tests for the fail-closed agent launch adapter."""
import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "tsar-cli" / "agent_adapter.py"
SPEC = importlib.util.spec_from_file_location("tsar_agent_adapter", MODULE_PATH)
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def valid_report():
    return {
        "status": "PASS",
        "commit_sha": "a" * 40,
        "manifest_version": "1.2.0",
        "manifest_sha256": "b" * 64,
    }


def test_blocks_when_preflight_fails(tmp_path):
    launched = []
    def runner(command, **kwargs):
        launched.append(command)
        return 2

    try:
        adapter.run_agent(["agent", "run"], report_path=tmp_path / "report.json", runner=runner)
    except adapter.AgentGateError as exc:
        assert "launch blocked" in str(exc)
    else:
        raise AssertionError("Expected fail-closed block")
    assert len(launched) == 1


def test_blocks_when_report_is_missing_or_invalid(tmp_path):
    def runner(command, **kwargs):
        return 0

    try:
        adapter.run_agent(["agent"], report_path=tmp_path / "missing.json", runner=runner)
    except adapter.AgentGateError as exc:
        assert "missing or invalid" in str(exc)
    else:
        raise AssertionError("Expected missing-report block")


def test_blocks_when_report_is_not_pass(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(json.dumps({**valid_report(), "status": "FAIL"}), encoding="utf-8")
    def runner(command, **kwargs):
        return 0

    try:
        adapter.run_agent(["agent"], report_path=report, runner=runner)
    except adapter.AgentGateError as exc:
        assert "not PASS" in str(exc)
    else:
        raise AssertionError("Expected non-PASS block")


def test_blocks_when_command_is_empty(tmp_path):
    try:
        adapter.run_agent([], report_path=tmp_path / "report.json", runner=lambda *a, **k: 0)
    except adapter.AgentGateError as exc:
        assert "No agent command" in str(exc)
    else:
        raise AssertionError("Expected empty-command block")


def test_launches_only_after_valid_preflight_and_exports_provenance(tmp_path):
    report = tmp_path / "report.json"
    report.write_text(json.dumps(valid_report()), encoding="utf-8")
    calls = []

    def runner(command, **kwargs):
        calls.append((command, kwargs))
        return 0

    rc = adapter.run_agent(
        ["agent", "run", "--safe"],
        domains=["ai_security"],
        report_path=report,
        runner=runner,
    )
    assert rc == 0
    assert len(calls) == 2
    child_env = calls[1][1]["env"]
    assert child_env["TSAR_PREFLIGHT_STATUS"] == "PASS"
    assert child_env["TSAR_UPSTREAM_COMMIT_SHA"] == "a" * 40
    assert child_env["TSAR_MANIFEST_VERSION"] == "1.2.0"
    assert child_env["TSAR_PREFLIGHT_REPORT"] == str(report.resolve())
    assert calls[0][0][-2:] == ["--domain", "ai_security"]
