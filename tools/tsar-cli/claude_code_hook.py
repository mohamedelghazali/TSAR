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
import time
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
POLICY_STATE_TTL_SECONDS = 6 * 60 * 60
TOOL_SCOPES = {
    "Read": ("read", "repo:read", ActionClass.READ_ONLY, "file_path"),
    "Glob": ("read", "repo:read", ActionClass.READ_ONLY, "path"),
    "Grep": ("read", "repo:read", ActionClass.READ_ONLY, "path"),
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


def _principal_from_host() -> str:
    configured = os.environ.get("TSAR_CLAUDE_PRINCIPAL")
    if configured:
        return configured
    if hasattr(os, "getuid"):
        return f"uid:{os.getuid()}"
    return f"local-user:{getpass.getuser()}"

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


def _write_state(path: Path, state: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        raise ClaudeHookError("TSAR session state must not be a symlink")
    payload = json.dumps(dict(state), sort_keys=True, ensure_ascii=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=".tsar-state-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _prepare_policy_cache(
    report: Mapping[str, Any],
    *,
    audit_path: Path,
    session_id: str,
    repo_root: Path,
    fetcher: Callable[[str], bytes] = _fetch_bytes,
) -> tuple[dict[str, Any], list[str]]:
    commit = report["commit_sha"]
    manifest_raw = fetcher(f"{RAW_BASE}/{commit}/manifest.yaml")
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

    policy_root = audit_path.parent / "policy" / commit
    required: dict[str, str] = {}
    for relative in paths:
        if relative.startswith("/") or "\\" in relative or any(
            part in {"", ".", ".."} for part in relative.split("/")
        ):
            raise ClaudeHookError("Pinned manifest contains an unsafe policy path")
        raw = fetcher(f"{RAW_BASE}/{commit}/{relative}")
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected.get(relative):
            raise ClaudeHookError(f"Pinned policy hash mismatch: {relative}")
        destination = policy_root.joinpath(*relative.split("/"))
        destination.parent.mkdir(parents=True, exist_ok=True)
        current = policy_root
        for part in relative.split("/"):
            current = current / part
            if current.is_symlink():
                raise ClaudeHookError("Policy cache contains a symlink path")
        if destination.exists():
            if not destination.is_file() or hashlib.sha256(destination.read_bytes()).hexdigest() != digest:
                raise ClaudeHookError(f"Existing policy cache file is modified: {relative}")
        else:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
            if hasattr(os, "O_NOFOLLOW"):
                flags |= os.O_NOFOLLOW
            fd = os.open(str(destination), flags, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
        required[str(destination.resolve(strict=True))] = digest

    state = {
        "schema": "tsar/claude-code-session/v1",
        "session_id": session_id,
        "repo_root": str(repo_root),
        "tsar_commit_sha": commit,
        "manifest_version": report["manifest_version"],
        "manifest_sha256": report["manifest_sha256"],
        "policy_cache_root": str(policy_root.resolve()),
        "created_at": time.time(),
        "required_policy_files": required,
        "read_policy_files": [],
    }
    return state, sorted(required)


def _load_session_state(path: Path, *, session_id: str, repo_root: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ClaudeHookError("No trusted TSAR policy session exists; submit the prompt again")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ClaudeHookError("TSAR policy session state is missing or invalid") from exc
    if (
        not isinstance(state, dict)
        or state.get("schema") != "tsar/claude-code-session/v1"
        or state.get("session_id") != session_id
        or state.get("repo_root") != str(repo_root)
        or not isinstance(state.get("required_policy_files"), dict)
        or not isinstance(state.get("policy_cache_root"), str)
        or not isinstance(state.get("read_policy_files"), list)
        or not isinstance(state.get("created_at"), (int, float))
        or time.time() - state["created_at"] > POLICY_STATE_TTL_SECONDS
        or time.time() < state["created_at"]
    ):
        raise ClaudeHookError("TSAR policy session is stale or has invalid provenance; submit the prompt again")
    for path_text, digest in state["required_policy_files"].items():
        target = Path(path_text)
        if (
            not isinstance(digest, str)
            or target.is_symlink()
            or not target.is_file()
            or hashlib.sha256(target.read_bytes()).hexdigest() != digest
        ):
            raise ClaudeHookError("A cached TSAR policy file is missing or modified")
    return state


def _safe_resource(
    repo_root: Path,
    tool_name: str,
    tool_input: Mapping[str, Any],
    state: Mapping[str, Any],
) -> str:
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
    except OSError as exc:
        raise ClaudeHookError("Tool path cannot be resolved safely") from exc
    policy_files = state.get("required_policy_files", {})
    if tool_name == "Read" and str(resolved) in policy_files:
        policy_root = Path(state["policy_cache_root"])
        try:
            policy_relative = resolved.relative_to(policy_root)
        except ValueError as exc:
            raise ClaudeHookError("Policy file is outside the verified TSAR cache") from exc
        return "tsar-policy:" + policy_relative.as_posix()
    if tool_name == "Glob":
        pattern = tool_input.get("pattern")
        normalized_pattern = pattern.replace(chr(92), "/") if isinstance(pattern, str) else ""
        if (
            not normalized_pattern
            or normalized_pattern.startswith("/")
            or re.match(r"^[A-Za-z]:/", normalized_pattern)
            or any(part == ".." for part in normalized_pattern.split("/"))
        ):
            raise ClaudeHookError("Glob pattern must not traverse outside the project root")
    try:
        lexical_relative = candidate.absolute().relative_to(repo_root)
    except ValueError as exc:
        raise ClaudeHookError("Tool path escapes the trusted project root") from exc
    current = repo_root
    for part in lexical_relative.parts:
        current = current / part
        if current.is_symlink():
            raise ClaudeHookError("Symlink paths are not accepted by the TSAR Claude hook")
    try:
        relative = resolved.relative_to(repo_root)
    except ValueError as exc:
        raise ClaudeHookError("Tool path resolves outside the trusted project root") from exc
    return "project:" + (relative.as_posix() if relative.parts else ".")

def _audit_file(repo_root: Path, session_id: str) -> Path:
    identity = hashlib.sha256(str(repo_root).encode("utf-8")).hexdigest()[:24]
    session = hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]
    base = Path(os.environ.get("TSAR_CLAUDE_AUDIT_DIR", str(Path.home() / ".tsar" / "audit")))
    return base / identity / f"claude-{session}.jsonl"


def _assert_no_audit_reparse_points(path: Path) -> None:
    """Reject symlinks and Windows junctions in every existing audit path component."""
    absolute = path.absolute()
    current = Path(absolute.anchor)
    try:
        for part in absolute.parts[1:]:
            current = current / part
            if current.is_symlink():
                raise ClaudeHookError("TSAR audit path must not contain symlinks")
            is_junction = getattr(current, "is_junction", None)
            if is_junction is not None and is_junction():
                raise ClaudeHookError("TSAR audit path must not contain junctions")
    except OSError as exc:
        raise ClaudeHookError(f"Unable to validate TSAR audit path: {exc}") from exc


def _append_audit(path: Path, event: Mapping[str, Any]) -> None:
    # O_NOFOLLOW is not available on Windows. Check every existing component
    # before and after opening so a symlink/junction is rejected on all hosts.
    _assert_no_audit_reparse_points(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    _assert_no_audit_reparse_points(path)
    flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(str(path), flags, 0o600)
    try:
        _assert_no_audit_reparse_points(path)
        data = (json.dumps(dict(event), sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        with os.fdopen(fd, "ab") as stream:
            fd = -1
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass
        raise


def _request_for_tool(
    repo_root: Path, payload: Mapping[str, Any], principal: str,
    state: Mapping[str, Any],
) -> tuple[ActionRequest, ToolSpec]:
    tool_name = payload.get("tool_name")
    tool_input = payload.get("tool_input")
    if not isinstance(tool_name, str) or tool_name not in TOOL_SCOPES:
        raise ClaudeHookError(f"Tool is not registered in the TSAR Claude strict profile: {tool_name!r}")
    if not isinstance(tool_input, dict):
        raise ClaudeHookError("Claude tool_input must be a JSON object")
    operation, scope, action_class, _path_field = TOOL_SCOPES[tool_name]
    resource = _safe_resource(repo_root, tool_name, tool_input, state)
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
    policy_fetcher: Callable[[str], bytes] = _fetch_bytes,
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
    if event in {"UserPromptSubmit", "PreToolUse"} and os.environ.get("CLAUDE_CODE_DISABLE_FILE_MENTIONS") != "1":
        raise ClaudeHookError("Set CLAUDE_CODE_DISABLE_FILE_MENTIONS=1 in user or managed Claude Code settings to close the @file Read-hook bypass")
    domains = tuple(domain for domain in _domains_from_env() if domain != "core")
    if not domains:
        raise ClaudeHookError("At least one non-core TSAR policy domain must be selected")
    audit_path = _audit_file(repo_root, session_id)
    state_path = audit_path.with_suffix(".state.json")
    audit_base = {
        "provider": "claude-code",
        "session_id": session_id,
        "cwd": str(repo_root),
    }

    if event == "UserPromptSubmit":
        report = preflight(repo_root, domains)
        state, policy_paths = _prepare_policy_cache(
            report,
            audit_path=audit_path,
            session_id=session_id,
            repo_root=repo_root,
            fetcher=policy_fetcher,
        )
        _write_state(state_path, state)
        instructions = [
            "TSAR STRICT MODE IS ACTIVE.",
            f"Verified upstream commit: {report['commit_sha']}",
            f"Manifest version: {report['manifest_version']}",
            "Before any other tool call, read every policy file listed below using the Read tool.",
            "TSAR blocks all non-policy tool calls until every listed file has been read successfully.",
            "After reading them, follow their constraints throughout this task. A tool permission prompt remains controlled by Claude Code.",
            "Policy files:",
            *policy_paths,
        ]
        return {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": "\n".join(instructions),
            }
        }

    if event == "PreToolUse":
        state = _load_session_state(state_path, session_id=session_id, repo_root=repo_root)
        tool_use_id = payload.get("tool_use_id")
        if not isinstance(tool_use_id, str) or not tool_use_id:
            raise ClaudeHookError("PreToolUse event is missing tool_use_id")
        tool_name = payload.get("tool_name")
        tool_input = payload.get("tool_input")
        required = set(state["required_policy_files"])
        read = set(state["read_policy_files"])
        if len(read) != len(state["read_policy_files"]) or not read.issubset(required):
            raise ClaudeHookError("TSAR policy-read state is malformed")
        if read != required:
            if tool_name != "Read" or not isinstance(tool_input, dict):
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Read every pinned TSAR policy file before using any other tool.",
                    }
                }
            file_path = tool_input.get("file_path")
            try:
                canonical = str(Path(file_path).expanduser().resolve(strict=True))
            except (TypeError, OSError) as exc:
                raise ClaudeHookError("Policy Read path is invalid or missing") from exc
            if canonical not in required or canonical in read:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Only unread pinned TSAR policy files may be read before policy loading is complete.",
                    }
                }
            if "offset" in tool_input or "limit" in tool_input:
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "deny",
                        "permissionDecisionReason": "Pinned TSAR policy files must be read in full; partial Read requests are not accepted.",
                    }
                }

        principal = _principal_from_host()
        request, spec = _request_for_tool(repo_root, payload, principal, state)
        scopes = _scopes_from_env()

        def sink(event_record: Mapping[str, Any]) -> None:
            _append_audit(audit_path, {
                **audit_base,
                "tool_use_id": tool_use_id,
                "tsar_commit_sha": state["tsar_commit_sha"],
                "manifest_version": state["manifest_version"],
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
        state = _load_session_state(state_path, session_id=session_id, repo_root=repo_root)
        tool_name = payload.get("tool_name")
        tool_input = payload.get("tool_input")
        tool_use_id = payload.get("tool_use_id")
        outcome = "EXECUTED" if event == "PostToolUse" else "TOOL_FAILED"
        state_changed = False
        if event == "PostToolUse" and tool_name == "Read" and isinstance(tool_input, dict):
            file_path = tool_input.get("file_path")
            try:
                canonical = str(Path(file_path).expanduser().resolve(strict=True))
            except (TypeError, OSError):
                canonical = ""
            expected = state["required_policy_files"].get(canonical)
            if expected is not None:
                if hashlib.sha256(Path(canonical).read_bytes()).hexdigest() != expected:
                    raise ClaudeHookError("Read policy file does not match its pinned SHA-256")
                read = set(state["read_policy_files"])
                read.add(canonical)
                state["read_policy_files"] = sorted(read)
                state_changed = True
        _append_audit(audit_path, {
            **audit_base,
            "tool_use_id": tool_use_id,
            "tool_name": tool_name,
            "outcome": outcome,
            "event": event,
            "tsar_commit_sha": state["tsar_commit_sha"],
        })
        if state_changed:
            _write_state(state_path, state)
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
