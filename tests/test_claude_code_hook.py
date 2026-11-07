from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "tsar-cli"))
from claude_code_hook import ClaudeHookError, handle_event


SHA = "a" * 40
HASH = "b" * 64


def report():
    return {
        "status": "PASS",
        "repository": "mohamedelghazali/TSAR",
        "commit_sha": SHA,
        "manifest_version": "1.2.0",
        "manifest_sha256": HASH,
        "loaded_policy_sha256": {"system/CORE_DIRECTIVE.md": HASH},
        "selected_domains": ["core", "development", "agentic_ai", "ai_security", "secrets"],
    }


def event(tmp_path, name="PreToolUse", **extra):
    return {
        "hook_event_name": name,
        "session_id": "session-123",
        "cwd": str(tmp_path),
        **extra,
    }


def setup_env(monkeypatch, tmp_path, scopes="repo:read,repo:write"):
    monkeypatch.setenv("TSAR_CLAUDE_SCOPES", scopes)
    monkeypatch.setenv("TSAR_CLAUDE_AUDIT_DIR", str(tmp_path / "private-audit"))


def test_user_prompt_submit_injects_verified_policy_context(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    result = handle_event(
        event(tmp_path, "UserPromptSubmit", prompt="Implement a secure endpoint"),
        preflight=lambda root, domains: report(),
        policy_loader=lambda evidence: "PINNED POLICY CONTEXT",
    )
    assert result["hookSpecificOutput"]["hookEventName"] == "UserPromptSubmit"
    assert result["hookSpecificOutput"]["additionalContext"] == "PINNED POLICY CONTEXT"


def test_user_prompt_submit_fails_closed_when_preflight_fails(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    def fail(_root, _domains):
        raise ClaudeHookError("upstream unavailable")
    with pytest.raises(ClaudeHookError, match="upstream unavailable"):
        handle_event(
            event(tmp_path, "UserPromptSubmit"),
            preflight=fail,
            policy_loader=lambda _report: pytest.fail("policy must not load"),
        )


def test_read_tool_is_authorized_and_audited_without_bypassing_provider_permission(
    tmp_path, monkeypatch
):
    setup_env(monkeypatch, tmp_path)
    (tmp_path / "src").mkdir()
    target = tmp_path / "src" / "app.py"
    target.write_text("print('safe')", encoding="utf-8")
    result = handle_event(
        event(tmp_path, tool_name="Read", tool_use_id="tool-1",
              tool_input={"file_path": str(target)}),
        preflight=lambda root, domains: report(),
    )
    assert result is None
    records = list((tmp_path / "private-audit").rglob("*.jsonl"))
    assert len(records) == 1
    audit = [json.loads(line) for line in records[0].read_text(encoding="utf-8").splitlines()]
    assert len(audit) == 1
    assert audit[0]["decision"] == "ALLOW"
    assert "outcome" not in audit[0]


def test_write_tool_requires_explicit_repo_write_scope(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path, scopes="repo:read")
    with pytest.raises(ClaudeHookError, match="Tool action denied"):
        handle_event(
            event(tmp_path, tool_name="Write", tool_use_id="tool-2",
                  tool_input={"file_path": str(tmp_path / "new.py"), "content": "x"}),
            preflight=lambda root, domains: report(),
        )
    records = list((tmp_path / "private-audit").rglob("*.jsonl"))
    assert len(records) == 1
    audit = json.loads(records[0].read_text(encoding="utf-8").splitlines()[0])
    assert audit["decision"] == "DENY"
    assert audit["reason"] == "missing_authorization_scope"


def test_write_tool_passes_boundary_but_leaves_native_permission_prompt_intact(
    tmp_path, monkeypatch
):
    setup_env(monkeypatch, tmp_path, scopes="repo:write")
    result = handle_event(
        event(tmp_path, tool_name="Write", tool_use_id="tool-3",
              tool_input={"file_path": str(tmp_path / "new.py"), "content": "x"}),
        preflight=lambda root, domains: report(),
    )
    assert result is None


@pytest.mark.parametrize("tool_name", ["Bash", "PowerShell", "Agent", "WebFetch", "mcp__db__query"])
def test_unregistered_tools_are_rejected_by_strict_profile(tmp_path, monkeypatch, tool_name):
    setup_env(monkeypatch, tmp_path)
    with pytest.raises(ClaudeHookError, match="not registered"):
        handle_event(
            event(tmp_path, tool_name=tool_name, tool_use_id="tool-4", tool_input={"command": "echo x"}),
            preflight=lambda root, domains: report(),
        )


def test_path_escape_is_rejected_before_boundary_authorization(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    outside = tmp_path.parent / "outside.txt"
    with pytest.raises(ClaudeHookError, match="escapes"):
        handle_event(
            event(tmp_path, tool_name="Read", tool_use_id="tool-5",
                  tool_input={"file_path": str(outside)}),
            preflight=lambda root, domains: report(),
        )


def test_audit_storage_failure_blocks_pre_tool_use(tmp_path, monkeypatch):
    audit_parent = tmp_path / "not-a-directory"
    audit_parent.write_text("x", encoding="utf-8")
    monkeypatch.setenv("TSAR_CLAUDE_AUDIT_DIR", str(audit_parent))
    monkeypatch.setenv("TSAR_CLAUDE_SCOPES", "repo:read")
    with pytest.raises(OSError):
        handle_event(
            event(tmp_path, tool_name="Read", tool_use_id="tool-6",
                  tool_input={"file_path": str(tmp_path / "file.txt")}),
            preflight=lambda root, domains: report(),
        )


def test_post_tool_use_records_outcome_after_execution(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    handle_event(
        event(tmp_path, "PostToolUse", tool_name="Read", tool_use_id="tool-7"),
        preflight=lambda root, domains: report(),
    )
    records = list((tmp_path / "private-audit").rglob("*.jsonl"))
    audit = json.loads(records[0].read_text(encoding="utf-8").splitlines()[0])
    assert audit["outcome"] == "EXECUTED"
    assert audit["tool_use_id"] == "tool-7"
