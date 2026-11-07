"""Claude Code hook adapter for fail-closed TSAR policy and tool checks.

This adapter uses Claude Code's documented UserPromptSubmit and PreToolUse
blocking hooks. It does not claim to intercept @file mentions, tools outside
Claude Code's hook lifecycle, or capabilities exposed by other processes.
"""
from __future__ import annotations

import getpass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Callable, Mapping
import urllib.error
import urllib.request

from tool_boundary import (
    ActionClass,
    ActionRequest,
    AuthorizationContext,
    ToolBoundary,
    ToolBoundaryError,
    ToolSpec,
)

REPOSITORY = "mohamedelghazali/TSAR"
RAW_BASE = f"https://raw.githubusercontent.com/{REPOSITORY}"
DEFAULT_DOMAINS = ("development", "agentic_ai", "ai_security", "secrets")
TOOL_SCOPES = {
    "Read": ("read", "repo:read", ActionClass.READ_ONLY, "file_path"),
    "Glob": ("read", "repo:read", ActionClass.READ_ONLY, None),
    "Grep": ("read", "repo:read", ActionClass.READ_ONLY, None),
    "LS": ("read", "repo:read", ActionClass.READ_ONLY, "path"),
    "Write": ("write", "repo:write", ActionClass.REPOSITORY_WRITE, "file_path"),
    "Edit": ("write", "repo:write", ActionClass.REPOSITORY_WRITE, "file_path"),
    "NotebookEdit": ("write", "repo:write", ActionClass.REPOSITORY_WRITE, "notebook_path"),
}
_SHA1 = re.compile(r"^[0-9a-f]{40}$")


class ClaudeHookError(RuntimeError):
    """A Claude Code hook cannot safely authorize this event."""


def _domains_from_env() -> tuple[str, ...]:
    raw = os.environ.get("TSAR_CLAUDE_DOMAINS", ",".join(DEFAULT_DOMAINS))
    domains = tuple(dict.fromkeys(part.strip() for part in raw.split(",") if part.strip()))
    if not domains:
        raise ClaudeHookError("TSAR_CLAUDE_DOMAINS must select at least one domain")
    return domains


def _scopes_from_env() -> frozenset[str]:
    raw = os.environ.get("TSAR_CLAUDE_SCOPES", "repo:read")
    return frozenset(part.strip() for part in raw.split(",") if part.strip())


def _fetch_bytes(url: str, timeout: int = 20) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "TSAR-Claude-Code-Hook/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise ClaudeHookError(f"Policy fetch returned HTTP {response.status}")
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ClaudeHookError(f"Unable to fetch pinned TSAR policy: {exc}") from exc


def _run_preflight(
    repo_root: Path,
    domains: tuple[str, ...],
    *,
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    verifier = Path(__file__).resolve().with_name("verify_upstream.py")
    if not verifier.is_file():
        raise ClaudeHookError("TSAR upstream verifier is not installed")
    with tempfile.TemporaryDirectory(prefix="tsar-claude-preflight-") as temp_dir:
        report_path = Path(temp_dir) / "preflight.json"
        argv = [sys.executable, str(verifier)]
        for domain in domains:
            argv.extend(["--domain", domain])
        argv.extend(["--report", str(report_path)])
        try:
            completed = runner(
                argv, cwd=str(repo_root), check=False, capture_output=True,
                text=True, timeout=120,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ClaudeHookError(f"TSAR preflight could not complete: {exc}") from exc
        try:
            report = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ClaudeHookError("TSAR preflight did not produce valid evidence") from exc
        if (
            getattr(completed, "returncode", 1) != 0
            or not isinstance(report, dict)
            or report.get("status") != "PASS"
            or report.get("repository") != REPOSITORY
            or not isinstance(report.get("commit_sha"), str)
            or not _SHA1.fullmatch(report["commit_sha"])
            or not isinstance(report.get("manifest_sha256"), str)
            or not isinstance(report.get("loaded_policy_sha256"), dict)
            or not isinstance(report.get("selected_domains"), list)
        ):
            raise ClaudeHookError("TSAR upstream preflight failed or returned incomplete evidence")
        if tuple(report["selected_domains"]) != ("core", *domains):
            raise ClaudeHookError("TSAR preflight selected-domain provenance does not match configuration")
        return report


def _load_policy_context(report: Mapping[str, Any]) -> str:
    commit = report["commit_sha"]
    manifest_raw = _fetch_bytes(f"{RAW_BASE}/{commit}/manifest.yaml")
    if hashlib.sha256(manifest_raw).hexdigest() != report["manifest_sha256"]:
        raise ClaudeHookError("Pinned manifest changed after TSAR preflight")
    try:
        import yaml
        manifest = yaml.safe_load(manifest_raw)
    except Exception as exc:
        raise ClaudeHookError(f"Cannot parse pinned TSAR manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("version") != report.get("manifest_version"):
        raise ClaudeHookError("Pinned TSAR manifest identity mismatch")
    active = manifest.get("active_files")
    if not isinstance(active, dict):
        raise ClaudeHookError("Pinned TSAR manifest has no active policy inventory")
    paths: list[str] = []
    for domain in report["selected_domains"]:
        entries = active.get(domain)
        if not isinstance(entries, list) or not entries or any(not isinstance(p, str) for p in entries):
            raise ClaudeHookError(f"Invalid active policy group: {domain}")
        paths.extend(entries)
    expected = report["loaded_policy_sha256"]
    if len(paths) != len(set(paths)) or set(paths) != set(expected):
        raise ClaudeHookError("Preflight policy hash inventory does not match pinned manifest")
    sections = [
        "MANDATORY TSAR POLICY CONTEXT",
        f"Repository: {REPOSITORY}",
        f"Pinned commit: {commit}",
        f"Manifest version: {report['manifest_version']}",
        "Read and apply every policy section below before performing implementation work.",
        "These instructions do not override system, platform, safety, legal, or explicit user authorization constraints.",
    ]
    for path in paths:
        if path.startswith("/") or "\\" in path or any(part in {"", ".", ".."} for part in path.split("/")):
            raise ClaudeHookError("Pinned manifest contains an unsafe policy path")
        raw = _fetch_bytes(f"{RAW_BASE}/{commit}/{path}")
        if hashlib.sha256(raw).hexdigest() != expected.get(path):
            raise ClaudeHookError(f"Pinned policy hash mismatch: {path}")
        try:
            body = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ClaudeHookError(f"Policy is not UTF-8: {path}") from exc
        sections.extend([f"\n--- TSAR POLICY: {path} ---\n", body])
    return "\n".join(sections)


def _safe_resource(repo_root: Path, tool_name: str, tool_input: Mapping[str, Any]) -> str:
    _operation, _scope, _action, path_field = TOOL_SCOPES[tool_name]
    supplied = tool_input.get(path_field) if path_field else None
    if supplied is None:
        candidate = repo_root
    elif not isinstance(supplied, str) or not supplied:
        raise ClaudeHookError("Tool path must be a non-empty string")
    else:
        raw = Path(supplied)
        if any(part in {"", ".", ".."} for part in raw.parts):
            raise ClaudeHookError("Tool path contains traversal components")
        candidate = raw if raw.is_absolute() else repo_root / raw
    try:
        resolved = candidate.resolve(strict=False)
        relative = resolved.relative_to(repo_root)
    except (OSError, ValueError) as exc:
        raise ClaudeHookError("Tool path escapes the trusted project root") from exc
    current = repo_root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ClaudeHookError("Symlink paths are not accepted by the TSAR Claude hook")
    return "project:" + (relative.as_posix() if relative.parts else ".")


def _audit_file(repo_root: Path, session_id: str) -> Path:
    identity = hashlib.sha256(str(repo_root).encode("utf-8")).hexdigest()[:24]
    session = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]
    base = Path(os.environ.get("TSAR_CLAUDE_AUDIT_DIR", str(Path.home() / ".tsar" / "audit")))
    return base / identity / f"claude-{session}.jsonl"


def _append_audit(path: Path, event: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(str(path), flags, 0o600)
    try:
        data = (json.dumps(dict(event), sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        with os.fdopen(fd, "ab") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _request_for_tool(
    repo_root: Path, payload: Mapping[str, Any], principal: str
) -> tuple[ActionRequest, ToolSpec]:
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_name, str) or tool_name not in TOOL_SCOPES:
        raise ClaudeHookError(f"Tool is not registered in the TSAR Claude strict profile: {tool_name!r}")
    if not isinstance(tool_input, dict):
        raise ClaudeHookError("Claude tool_input must be a JSON object")
    operation, scope, action_class, _path_field = TOOL_SCOPES[tool_name]
    resource = _safe_resource(repo_root, tool_name, tool_input)
    spec = ToolSpec(
        name=tool_name,
        action_class=action_class,
        operations=frozenset({operation}),
        resources=frozenset({resource}),
        required_scope=scope,
    )
    request = ActionRequest(
        tool=tool_name,
        operation=operation,
        resource=resource,
        actor=principal,
        arguments=tool_input,
    )
    return request, spec


def handle_event(
    payload: Mapping[str, Any],
    *,
    preflight: Callable[[Path, tuple[str, ...]], dict[str, Any]] = _run_preflight,
    policy_loader: Callable[[Mapping[str, Any]], str] = _load_policy_context,
) -> dict[str, Any] | None:
    if not isinstance(payload, Mapping):
        raise ClaudeHookError("Hook input must be a JSON object")
    event = payload.get("hook_event_name")
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd:
        raise ClaudeHookError("Claude hook input is missing cwd")
    repo_root = Path(cwd).expanduser().resolve(strict=True)
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise ClaudeHookError("Claude hook input is missing session_id")
    domains = _domains_from_env()
    audit_path = _audit_file(repo_root, session_id)
    audit_base = {
        "provider": "claude-code",
        "session_id": session_id,
        "cwd": str(repo_root),
    }

    if event == "UserPromptSubmit":
        report = preflight(repo_root, domains)
        context = policy_loader(report)
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }

    if event == "PreToolUse":
        report = preflight(repo_root, domains)
        tool_use_id = payload.get("tool_use_id")
        if not isinstance(tool_use_id, str) or not tool_use_id:
            raise ClaudeHookError("PreToolUse event is missing tool_use_id")
        principal = os.environ.get("TSAR_CLAUDE_PRINCIPAL") or getpass.getuser()
        request, spec = _request_for_tool(repo_root, payload, principal)
        scopes = _scopes_from_env()
        def sink(event_record: Mapping[str, Any]) -> None:
            _append_audit(audit_path, {
                **audit_base,
                "tool_use_id": tool_use_id,
                "tsar_commit_sha": report["commit_sha"],
                "manifest_version": report["manifest_version"],
                **dict(event_record),
            })
        boundary = ToolBoundary(
            {spec.name: spec},
            AuthorizationContext(principal, scopes),
            approval_verifier=lambda _approval, _digest, _actor: False,
            audit_sink=sink,
        )
        try:
            boundary.authorize(request)
        except ToolBoundaryError as exc:
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": str(exc),
                }
            }
        return None

    if event in {"PostToolUse", "PostToolUseFailure"}:
        _append_audit(audit_path, {
            **audit_base,
            "tool_use_id": payload.get("tool_use_id"),
            "tool_name": payload.get("tool_name"),
            "outcome": "EXECUTED" if event == "PostToolUse" else "TOOL_FAILED",
            "event": event,
        })
        return None

    raise ClaudeHookError(f"Unsupported Claude Code hook event: {event!r}")


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw)
        result = handle_event(payload)
        if result is not None:
            sys.stdout.write(json.dumps(result, ensure_ascii=False) + "\n")
        return 0
    except Exception as exc:
        message = f"TSAR Claude Code hook BLOCKED: {exc}"
        sys.stderr.write(message + "\n")
        event = None
        try:
            event = payload.get("hook_event_name")
        except Exception:
            pass
        if event == "UserPromptSubmit":
            sys.stdout.write(json.dumps({"decision": "block", "reason": message}) + "\n")
        elif event == "PreToolUse":
            sys.stdout.write(json.dumps({
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": message,
                }
            }) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
