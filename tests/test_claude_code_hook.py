from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "tsar-cli"))
from claude_code_hook import ClaudeHookError, _audit_file, handle_event


SHA = "a" * 40
MANIFEST = b"""version: "1.2.0"
active_files:
  core:
    - system/CORE_DIRECTIVE.md
  development:
    - rules/development/secure-sdlc.md
"""
POLICIES = {
    "system/CORE_DIRECTIVE.md": b"# Core directive\nAlways follow TSAR.\n",
    "rules/development/secure-sdlc.md": b"# Secure SDLC\nReview changes.\n",
}


def report():
    return {
        "status": "PASS",
        "repository": "mohamedelghazali/TSAR",
        "commit_sha": SHA,
        "manifest_version": "1.2.0",
        "manifest_sha256": hashlib.sha256(MANIFEST).hexdigest(),
        "loaded_policy_sha256": {
            path: hashlib.sha256(data).hexdigest() for path, data in POLICIES.items()
        },
        "selected_domains": ["core", "development"],
    }


def fetcher(url):
    if url.endswith("/manifest.yaml"):
        return MANIFEST
    path = url.split(SHA + "/", 1)[1]
    return POLICIES[path]


def event(tmp_path, name="PreToolUse", **extra):
    return {
        "hook_event_name": name,
        "session_id": "session-123",
        "cwd": str(tmp_path),
        **extra,
    }


def setup_env(monkeypatch, tmp_path, scopes="repo:read,repo:write"):
    monkeypatch.setenv("TSAR_CLAUDE_DOMAINS", "development")
    monkeypatch.setenv("TSAR_CLAUDE_SCOPES", scopes)
    monkeypatch.setenv("TSAR_CLAUDE_AUDIT_DIR", str(tmp_path / "private-audit"))
    monkeypatch.setenv("CLAUDE_CODE_DISABLE_FILE_MENTIONS", "1")


def prime_session(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    result = handle_event(
        event(tmp_path, "UserPromptSubmit", prompt="Implement a secure endpoint"),
        preflight=lambda root, domains: report(),
        policy_fetcher=fetcher,
    )
    context = result["hookSpecificOutput"]["additionalContext"]
    assert "Before any other tool call, read every policy file" in context
    paths = context.split("Policy files:\n", 1)[1].splitlines()
    for index, path in enumerate(paths):
        handle_event(
            event(tmp_path, "PostToolUse", tool_name="Read", tool_use_id=f"policy-{index}",
                  tool_input={"file_path": path}),
        )
    return paths


def test_user_prompt_submit_injects_pinned_policy_paths_and_materializes_hashed_files(
    tmp_path, monkeypatch
):
    paths = prime_session(tmp_path, monkeypatch)
    assert len(paths) == 2
    for path in paths:
        assert Path(path).is_file()
    state_files = list((tmp_path / "private-audit").rglob("*.state.json"))
    assert len(state_files) == 1
    state = json.loads(state_files[0].read_text(encoding="utf-8"))
    assert state["tsar_commit_sha"] == SHA
    assert set(state["read_policy_files"]) == set(paths)


def test_prompt_is_blocked_when_file_mention_bypass_is_not_disabled(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    monkeypatch.delenv("CLAUDE_CODE_DISABLE_FILE_MENTIONS")
    with pytest.raises(ClaudeHookError, match="@file Read-hook bypass"):
        handle_event(
            event(tmp_path, "UserPromptSubmit"),
            preflight=lambda root, domains: report(),
            policy_fetcher=fetcher,
        )
def test_user_prompt_submit_fails_closed_when_preflight_fails(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    def fail(_root, _domains):
        raise ClaudeHookError("upstream unavailable")
    with pytest.raises(ClaudeHookError, match="upstream unavailable"):
        handle_event(
            event(tmp_path, "UserPromptSubmit"),
            preflight=fail,
            policy_fetcher=fetcher,
        )


def test_non_policy_tool_is_blocked_until_every_policy_file_was_read(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    handle_event(
        event(tmp_path, "UserPromptSubmit"),
        preflight=lambda root, domains: report(),
        policy_fetcher=fetcher,
    )
    result = handle_event(
        event(tmp_path, tool_name="Write", tool_use_id="tool-1",
              tool_input={"file_path": str(tmp_path / "new.py"), "content": "x"}),
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "Read every pinned TSAR policy file" in result["hookSpecificOutput"]["permissionDecisionReason"]


def test_partial_policy_read_is_rejected(tmp_path, monkeypatch):
    setup_env(monkeypatch, tmp_path)
    handle_event(
        event(tmp_path, "UserPromptSubmit"),
        preflight=lambda root, domains: report(),
        policy_fetcher=fetcher,
    )
    state_files = list((tmp_path / "private-audit").rglob("*.state.json"))
    state = json.loads(state_files[0].read_text(encoding="utf-8"))
    policy_path = next(iter(state["required_policy_files"]))
    result = handle_event(
        event(tmp_path, tool_name="Read", tool_use_id="partial-read",
              tool_input={"file_path": policy_path, "offset": 1, "limit": 1}),
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "read in full" in result["hookSpecificOutput"]["permissionDecisionReason"]
def test_read_tool_is_authorized_and_audited_after_policy_read(tmp_path, monkeypatch):
    prime_session(tmp_path, monkeypatch)
    target = tmp_path / "src" / "app.py"
    target.parent.mkdir()
    target.write_text("print('safe')", encoding="utf-8")
    result = handle_event(
        event(tmp_path, tool_name="Read", tool_use_id="tool-2",
              tool_input={"file_path": str(target)}),
    )
    assert result is None
    records = list((tmp_path / "private-audit").rglob("claude-*.jsonl"))
    audit = [json.loads(line) for line in records[0].read_text(encoding="utf-8").splitlines()]
    assert any(item.get("decision") == "ALLOW" for item in audit)


def test_write_tool_requires_explicit_repo_write_scope(tmp_path, monkeypatch):
    prime_session(tmp_path, monkeypatch)
    monkeypatch.setenv("TSAR_CLAUDE_SCOPES", "repo:read")
    result = handle_event(
        event(tmp_path, tool_name="Write", tool_use_id="tool-3",
              tool_input={"file_path": str(tmp_path / "new.py"), "content": "x"}),
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert "missing_authorization_scope" in result["hookSpecificOutput"]["permissionDecisionReason"]


def test_write_tool_passes_boundary_but_keeps_native_permission_prompt(tmp_path, monkeypatch):
    prime_session(tmp_path, monkeypatch)
    result = handle_event(
        event(tmp_path, tool_name="Write", tool_use_id="tool-4",
              tool_input={"file_path": str(tmp_path / "new.py"), "content": "x"}),
    )
    assert result is None


@pytest.mark.parametrize("tool_name", ["Bash", "PowerShell", "Agent", "WebFetch", "mcp__db__query"])
def test_unregistered_tools_are_rejected_by_strict_profile(tmp_path, monkeypatch, tool_name):
    prime_session(tmp_path, monkeypatch)
    with pytest.raises(ClaudeHookError, match="not registered"):
        handle_event(
            event(tmp_path, tool_name=tool_name, tool_use_id="tool-5", tool_input={"command": "echo x"}),
        )


def test_path_escape_is_rejected_before_boundary_authorization(tmp_path, monkeypatch):
    prime_session(tmp_path, monkeypatch)
    outside = tmp_path.parent / "outside.txt"
    with pytest.raises(ClaudeHookError, match="escapes"):
        handle_event(
            event(tmp_path, tool_name="Read", tool_use_id="tool-6",
                  tool_input={"file_path": str(outside)}),
        )


def test_audit_symlink_failure_blocks_pre_tool_use(tmp_path, monkeypatch):
    prime_session(tmp_path, monkeypatch)
    audit_path = _audit_file(tmp_path.resolve(), "session-123")
    audit_path.unlink()
    audit_path.symlink_to(tmp_path / "target.jsonl")
    result = handle_event(
        event(tmp_path, tool_name="Read", tool_use_id="tool-7",
              tool_input={"file_path": str(tmp_path / "file.txt")}),
    )
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert not (tmp_path / "target.jsonl").exists()


def test_post_tool_use_records_provider_execution(tmp_path, monkeypatch):
    prime_session(tmp_path, monkeypatch)
    handle_event(
        event(tmp_path, "PostToolUse", tool_name="Read", tool_use_id="tool-8",
              tool_input={"file_path": str(tmp_path / "src.py")}),
    )
    records = list((tmp_path / "private-audit").rglob("claude-*.jsonl"))
    lines = [json.loads(line) for line in records[0].read_text(encoding="utf-8").splitlines()]
    assert any(item.get("outcome") == "EXECUTED" and item.get("tool_use_id") == "tool-8" for item in lines)
