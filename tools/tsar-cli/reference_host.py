"""Reference host adapter composing TSAR E2-E5 controls on one controlled path.

This is an integration contract for a host that owns agent invocation and tool
dispatch. It is not a sandbox and cannot constrain tools exposed outside it.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Iterable, Mapping, Sequence
import urllib.error
import urllib.request

import yaml

from lifecycle_orchestrator import LifecycleStartError, start_lifecycle
from output_verification import CheckResult, OutputGate, OutputGateError
from tool_boundary import (
    ActionRequest,
    AuthorizationContext,
    ToolBoundary,
    ToolBoundaryError,
    ToolSpec,
)

REPOSITORY = "mohamedelghazali/TSAR"
RAW_BASE = "https://raw.githubusercontent.com/mohamedelghazali/TSAR"
REQUIRED_CORE = frozenset({
    "system/CORE_DIRECTIVE.md",
    "system/DO_NOT_GENERATE.md",
    "system/ENFORCEMENT_LEVELS.md",
    "system/LIFECYCLE.md",
})
REQUIRED_CHECKS = frozenset({"secret_scan", "secure_code_review", "tests"})


class ReferenceHostError(RuntimeError):
    """The controlled host path cannot continue safely."""


@dataclass(frozen=True)
class CheckCommand:
    """Trusted host-owned command configuration; never construct from model output."""

    name: str
    argv: tuple[str, ...]
    tool: str
    version: str
    timeout_seconds: int = 300


@dataclass(frozen=True)
class HostContext:
    """Only verified policy text and the guarded dispatch function reach the agent."""

    task_id: str
    agent_id: str
    tsar_commit_sha: str
    manifest_version: str
    selected_domains: tuple[str, ...]
    policy_files: Mapping[str, str]
    policy_instruction: str
    dispatch_tool: Callable[..., Any]


@dataclass(frozen=True)
class HostRunResult:
    status: str
    task_id: str
    audit_file: str
    output_evidence_file: str | None
    tsar_commit_sha: str
    manifest_version: str
    selected_domains: tuple[str, ...]
    check_results: tuple[Mapping[str, Any], ...]
    tool_events: int
    lifecycle_output_gate: str


def _default_fetcher(url: str, timeout: int = 20) -> bytes:
    request = urllib.request.Request(
        url, headers={"User-Agent": "TSAR-Reference-Host/1.0"}
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                raise ReferenceHostError(f"Policy fetch returned HTTP {response.status}")
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ReferenceHostError(f"Unable to fetch pinned policy content: {exc}") from exc


def _safe_project_path(root: Path, supplied: str | Path) -> Path:
    raw = Path(supplied)
    if raw.is_absolute() or "\\" in str(supplied) or any(part in {"", ".", ".."} for part in raw.parts):
        raise ReferenceHostError("Audit and evidence paths must be safe project-relative paths")
    current = root
    for part in raw.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise ReferenceHostError("Symlink directories are not accepted for host evidence")
    destination = root / raw
    if destination.is_symlink():
        raise ReferenceHostError("Symlink evidence destinations are not accepted")
    if not destination.parent.resolve().is_relative_to(root):
        raise ReferenceHostError("Evidence destination escapes the project root")
    return destination


def _safe_changed_files(root: Path, supplied: Iterable[str | Path]) -> list[Path]:
    result: list[Path] = []
    seen: set[Path] = set()
    for item in supplied:
        raw = Path(item)
        candidate = raw if raw.is_absolute() else root / raw
        try:
            lexical_parts = candidate.absolute().relative_to(root).parts
        except ValueError as exc:
            raise ReferenceHostError("Changed files must remain inside the project root") from exc
        current = root
        for part in lexical_parts:
            current = current / part
            if current.is_symlink():
                raise ReferenceHostError("Symlink changed files are not accepted")
        try:
            resolved = candidate.resolve(strict=True)
        except OSError as exc:
            raise ReferenceHostError(f"Changed file is missing: {item}") from exc
        if not resolved.is_relative_to(root):
            raise ReferenceHostError("Changed files must remain inside the project root")
        if not resolved.is_file():
            raise ReferenceHostError(f"Changed path is not a regular file: {item}")
        if resolved not in seen:
            seen.add(resolved)
            result.append(resolved)
    if not result:
        raise ReferenceHostError("Host change collector returned no changed files")
    return sorted(result, key=str)


class ReferenceHost:
    """Run preflight, inject pinned policy, gate tools, and emit E6 host evidence.

    The host owns agent invocation, tool registration, authorization identity,
    approval verification, audit persistence, check commands, and changed-file
    discovery. All these dependencies are trusted configuration, not model input.
    """

    def __init__(
        self,
        *,
        repo_root: str | Path,
        tool_registry: Mapping[str, ToolSpec],
        dispatchers: Mapping[str, Callable[[Mapping[str, Any]], Any]],
        authorization: AuthorizationContext,
        approval_verifier: Callable[[Any, str, str], bool],
        audit_sink: Callable[[Mapping[str, Any]], None],
        required_checks: Sequence[CheckCommand],
        process_runner: Callable[..., Any] = subprocess.run,
        policy_fetcher: Callable[[str], bytes] = _default_fetcher,
    ) -> None:
        self.root = Path(repo_root).expanduser().resolve(strict=True)
        if (
            not tool_registry
            or set(tool_registry) != set(dispatchers)
            or any(key != spec.name for key, spec in tool_registry.items())
        ):
            raise ReferenceHostError("Every registered tool must have one matching trusted dispatcher and ToolSpec name")
        if not callable(audit_sink) or not callable(approval_verifier):
            raise ReferenceHostError("Approval verification and durable audit sink are required")
        self.authorization = authorization
        self.registry = dict(tool_registry)
        self.dispatchers = dict(dispatchers)
        self.approval_verifier = approval_verifier
        self.audit_sink = audit_sink
        self.process_runner = process_runner
        self.policy_fetcher = policy_fetcher

        commands = list(required_checks)
        if any(not isinstance(item, CheckCommand) for item in commands):
            raise ReferenceHostError("Required checks must use trusted CheckCommand objects")
        names = [item.name for item in commands]
        if len(names) != len(set(names)) or not REQUIRED_CHECKS.issubset(set(names)):
            raise ReferenceHostError(
                "Trusted checks must uniquely include secret_scan, secure_code_review, and tests"
            )
        for item in commands:
            if (
                not isinstance(item, CheckCommand)
                or not item.name
                or not item.argv
                or any(not isinstance(arg, str) or not arg for arg in item.argv)
                or not item.tool
                or not item.version
                or item.timeout_seconds < 1
            ):
                raise ReferenceHostError("Invalid trusted check command configuration")
        self.check_commands = tuple(commands)

    def _load_pinned_policy(self, provenance: Mapping[str, Any]) -> tuple[dict[str, str], tuple[str, ...]]:
        commit = provenance.get("upstream_commit_sha")
        version = provenance.get("manifest_version")
        expected_hashes = provenance.get("loaded_policy_sha256")
        domains = provenance.get("selected_domains")
        if (
            not isinstance(commit, str) or len(commit) != 40
            or not isinstance(version, str) or not isinstance(expected_hashes, dict)
            or not isinstance(domains, list) or "core" not in domains
        ):
            raise ReferenceHostError("Lifecycle preflight provenance is incomplete")
        manifest_raw = self.policy_fetcher(f"{RAW_BASE}/{commit}/manifest.yaml")
        if hashlib.sha256(manifest_raw).hexdigest() != provenance.get("manifest_sha256"):
            raise ReferenceHostError("Pinned manifest bytes do not match preflight SHA-256")
        try:
            manifest = yaml.safe_load(manifest_raw)
        except yaml.YAMLError as exc:
            raise ReferenceHostError("Pinned manifest cannot be parsed") from exc
        lifecycle = manifest.get("lifecycle") if isinstance(manifest, dict) else None
        enforcement = manifest.get("enforcement") if isinstance(manifest, dict) else None
        if (
            not isinstance(manifest, dict)
            or not isinstance(lifecycle, dict)
            or not isinstance(enforcement, dict)
            or manifest.get("repository") != f"https://github.com/{REPOSITORY}"
            or manifest.get("version") != version
            or lifecycle.get("fail_closed") is not True
            or enforcement.get("default_mode") != "strict"
            or enforcement.get("allow_advisory_fallback") is not False
        ):
            raise ReferenceHostError("Pinned manifest identity or strict-mode settings are invalid")
        active = manifest.get("active_files")
        if (not isinstance(active, dict) or not isinstance(active.get("core"), list)
                or set(active["core"]) != REQUIRED_CORE):
            raise ReferenceHostError("Pinned manifest does not contain the exact four-file core policy set")
        if any(not isinstance(domain, str) or domain not in active for domain in domains):
            raise ReferenceHostError("Preflight selected an unknown manifest domain")

        paths: list[str] = []
        for domain in domains:
            domain_paths = active.get(domain)
            if not isinstance(domain_paths, list) or not domain_paths:
                raise ReferenceHostError(f"Selected domain has no active policy files: {domain}")
            paths.extend(domain_paths)
        if len(paths) != len(set(paths)) or set(paths) != set(expected_hashes):
            raise ReferenceHostError("Preflight policy hash inventory does not match selected manifest domains")

        policy_files: dict[str, str] = {}
        for path in paths:
            if (
                not isinstance(path, str) or path.startswith("/")
                or "\\" in path or any(part in {"", ".", ".."} for part in path.split("/"))
            ):
                raise ReferenceHostError("Pinned manifest contains an unsafe policy path")
            raw = self.policy_fetcher(f"{RAW_BASE}/{commit}/{path}")
            digest = hashlib.sha256(raw).hexdigest()
            if digest != expected_hashes.get(path):
                raise ReferenceHostError(f"Pinned policy hash mismatch: {path}")
            try:
                policy_files[path] = raw.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ReferenceHostError(f"Policy file is not UTF-8: {path}") from exc
        if set(policy_files) != REQUIRED_CORE.union(
            path for domain in domains if domain != "core" for path in active[domain]
        ):
            raise ReferenceHostError("Not every required core and selected domain policy was loaded")
        return policy_files, tuple(domains)

    def _run_checks(self) -> list[CheckResult]:
        results: list[CheckResult] = []
        for command in self.check_commands:
            try:
                completed = self.process_runner(
                    list(command.argv),
                    cwd=str(self.root),
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=command.timeout_seconds,
                )
                exit_code = completed.returncode
                if not isinstance(exit_code, int):
                    raise OSError("check runner returned a non-integer exit code")
                stdout = completed.stdout or ""
                stderr = completed.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")
                artifact = hashlib.sha256(
                    (str(stdout) + "\n" + str(stderr)).encode("utf-8")
                ).hexdigest()
                results.append(CheckResult(
                    name=command.name,
                    status="PASS" if exit_code == 0 else "FAIL",
                    tool=command.tool,
                    version=command.version,
                    exit_code=exit_code,
                    artifact_sha256=artifact,
                    detail=None if exit_code == 0 else f"command exited {exit_code}",
                ))
            except subprocess.TimeoutExpired:
                results.append(CheckResult(
                    name=command.name, status="BLOCKED", tool=command.tool,
                    version=command.version, exit_code=None,
                    detail=f"command timed out after {command.timeout_seconds}s",
                ))
            except OSError as exc:
                results.append(CheckResult(
                    name=command.name, status="BLOCKED", tool=command.tool,
                    version=command.version, exit_code=None,
                    detail=f"command could not execute: {type(exc).__name__}",
                ))
        return results

    def run_task(
        self,
        task: str,
        agent: Callable[[HostContext], Any],
        *,
        task_id: str,
        agent_id: str,
        audit_file: str | Path,
        output_evidence_file: str | Path,
        changed_files_provider: Callable[[], Iterable[str | Path]],
        domains: Iterable[str] = (),
        impact: str = "auto",
    ) -> HostRunResult:
        """Execute one synchronous agent task through the controlled reference path."""
        if not callable(agent) or not callable(changed_files_provider):
            raise ReferenceHostError("Agent and host changed-file collector must be callable")
        if not task_id or not agent_id:
            raise ReferenceHostError("Task and agent identities are required")
        audit_path = _safe_project_path(self.root, audit_file)
        output_path = _safe_project_path(self.root, output_evidence_file)
        if audit_path == output_path:
            raise ReferenceHostError("Audit and output evidence paths must be different")
        if audit_path.exists() or output_path.exists():
            raise ReferenceHostError("Refusing to overwrite existing lifecycle or output evidence")
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            audit = start_lifecycle(
                task,
                repo_root=self.root,
                audit_file=audit_path,
                domains=domains,
                impact=impact,
                run=self.process_runner,
            )
        except LifecycleStartError as exc:
            raise ReferenceHostError(f"Upstream preflight blocked the host path: {exc}") from exc

        provenance = audit["provenance"]
        policy_files, selected_domains = self._load_pinned_policy(provenance)
        events: list[Mapping[str, Any]] = []

        def persist_event(event: Mapping[str, Any]) -> None:
            self.audit_sink(event)
            events.append(dict(event))

        boundary = ToolBoundary(
            self.registry,
            self.authorization,
            approval_verifier=self.approval_verifier,
            audit_sink=persist_event,
        )

        def dispatch_tool(
            tool: str,
            operation: str,
            resource: str,
            arguments: Mapping[str, Any],
            approval: Any = None,
        ) -> Any:
            request = ActionRequest(
                tool=tool,
                operation=operation,
                resource=resource,
                actor=self.authorization.principal,
                arguments=arguments,
                approval=approval,
            )
            dispatcher = self.dispatchers.get(tool)
            if dispatcher is None:
                def reject_unregistered(_arguments: Mapping[str, Any]) -> Any:
                    raise ToolBoundaryError("unregistered tool reached the host dispatcher")
                dispatcher = reject_unregistered
            return boundary.dispatch(request, dispatcher)

        context = HostContext(
            task_id=task_id,
            agent_id=agent_id,
            tsar_commit_sha=provenance["upstream_commit_sha"],
            manifest_version=provenance["manifest_version"],
            selected_domains=selected_domains,
            policy_files=MappingProxyType(dict(policy_files)),
            policy_instruction=(
                "Before making changes, read and apply every supplied TSAR policy file. "
                "The four system/ core directives are mandatory. Apply all selected domain "
                "rules. If a policy is unclear or conflicts with higher-priority instructions, "
                "stop and report the conflict. Use only the supplied guarded tool dispatcher."
            ),
            dispatch_tool=dispatch_tool,
        )
        try:
            agent(context)
        except Exception as exc:
            raise ReferenceHostError(
                f"Agent execution failed; lifecycle remains incomplete: {type(exc).__name__}; "
                f"audit={audit_path.relative_to(self.root).as_posix()}"
            ) from exc

        try:
            changed_files = _safe_changed_files(self.root, changed_files_provider())
        except Exception as exc:
            raise ReferenceHostError(
                f"Host could not establish the actual changed-file set; acceptance blocked: {exc}"
            ) from exc

        gate = OutputGate(
            task_id=task_id,
            agent=agent_id,
            adapter_version="1.0.0",
            tsar_commit_sha=provenance["upstream_commit_sha"],
            manifest_version=provenance["manifest_version"],
            manifest_sha256=provenance["manifest_sha256"],
            policy_hashes=provenance["loaded_policy_sha256"],
            domains=selected_domains,
            enforcement_level="E6",
        )
        checks = self._run_checks()
        try:
            gate.evaluate(
                changed_files=changed_files,
                checks=checks,
                required_checks=[item.name for item in self.check_commands],
                output_path=output_path,
            )
            status = "PASS"
        except OutputGateError:
            status = "BLOCKED"

        return HostRunResult(
            status=status,
            task_id=task_id,
            audit_file=audit_path.relative_to(self.root).as_posix(),
            output_evidence_file=output_path.relative_to(self.root).as_posix(),
            tsar_commit_sha=provenance["upstream_commit_sha"],
            manifest_version=provenance["manifest_version"],
            selected_domains=selected_domains,
            check_results=tuple(
                {
                    "name": item.name,
                    "status": item.status,
                    "tool": item.tool,
                    "version": item.version,
                    "exit_code": item.exit_code,
                    "artifact_sha256": item.artifact_sha256,
                }
                for item in checks
            ),
            tool_events=len(events),
            lifecycle_output_gate=audit["gates"]["output_verification"],
        )

    def registry_dispatcher(self, tool: str) -> Callable[[Mapping[str, Any]], Any]:
        """Resolve a registered dispatch function from trusted host configuration.

        The tool registry is policy metadata. The host must provide an explicit
        dispatcher mapping; no function is inferred from a model-supplied name.
        """
        dispatcher = self.dispatchers.get(tool)
        if dispatcher is None:
            raise ToolBoundaryError(f"No trusted host dispatcher registered for tool: {tool}")
        return dispatcher
