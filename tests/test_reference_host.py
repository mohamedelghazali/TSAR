"""End-to-end conformance tests for the E6 reference host adapter."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "tsar-cli"))

from reference_host import (
    CheckCommand,
    ReferenceHost,
    ReferenceHostError,
)
from tool_boundary import (
    ActionClass,
    AuthorizationContext,
    ToolBoundaryError,
    ToolSpec,
)

COMMIT = "a" * 40
CORE = {
    "system/CORE_DIRECTIVE.md": b"# Core\nRead before work.\n",
    "system/DO_NOT_GENERATE.md": b"# Do not generate\n",
    "system/ENFORCEMENT_LEVELS.md": b"# Enforcement\nStrict.\n",
    "system/LIFECYCLE.md": b"# Lifecycle\n",
}
DOMAIN = {"rules/development/secure-sdlc.md": b"# Secure SDLC\n"}
MANIFEST = (
    "repository: https://github.com/mohamedelghazali/TSAR\n"
    "version: 1.2.0\n"
    "lifecycle:\n  fail_closed: true\n  fetch_before_task: true\n"
    "enforcement:\n  default_mode: strict\n  allow_advisory_fallback: false\n"
    "active_files:\n  core:\n"
    + "".join(f"    - {path}\n" for path in CORE)
    + "  development:\n    - rules/development/secure-sdlc.md\n"
).encode()


def build_host(tmp_path, *, preflight_status="PASS", check_exit_codes=None, tamper_policy=False):
    root = tmp_path / "project"
    (root / "tools" / "tsar-cli").mkdir(parents=True)
    (root / "manifest.yaml").write_bytes(MANIFEST)
    (root / "tools" / "tsar-cli" / "verify_upstream.py").write_text("# test stub\n")
    payloads = {"manifest.yaml": MANIFEST, **CORE, **DOMAIN}
    hashes = {path: hashlib.sha256(raw).hexdigest() for path, raw in payloads.items()}
    events = []
    check_exit_codes = dict(check_exit_codes or {})

    def runner(command, **kwargs):
        if any(str(item).endswith("verify_upstream.py") for item in command):
            report_path = Path(command[command.index("--report") + 1])
            report_path.write_text(json.dumps({
                "status": preflight_status,
                "repository": "mohamedelghazali/TSAR",
                "commit_sha": COMMIT,
                "manifest_version": "1.2.0",
                "manifest_sha256": hashes["manifest.yaml"],
                "loaded_policy_sha256": {key: value for key, value in hashes.items() if key != "manifest.yaml"},
                "selected_domains": ["core", "development"],
                "errors": [] if preflight_status == "PASS" else ["test preflight failure"],
            }), encoding="utf-8")
            return SimpleNamespace(returncode=0 if preflight_status == "PASS" else 2, stdout="", stderr="")
        name = str(command[0])
        code = check_exit_codes.get(name, 0)
        return SimpleNamespace(returncode=code, stdout=f"{name} output", stderr="")

    def fetcher(url):
        path = url.rsplit(f"/{COMMIT}/", 1)[-1]
        raw = payloads[path]
        if tamper_policy and path == "system/CORE_DIRECTIVE.md":
            return raw + b"tampered"
        return raw

    spec = ToolSpec(
        name="repo.write",
        action_class=ActionClass.REPOSITORY_WRITE,
        operations=frozenset({"write"}),
        resources=frozenset({"repo:demo"}),
        required_scope="repo:write",
    )
    host = ReferenceHost(
        repo_root=root,
        tool_registry={"repo.write": spec},
        dispatchers={"repo.write": lambda args: {"written": args["content"]}},
        authorization=AuthorizationContext("operator-1", frozenset({"repo:write"})),
        approval_verifier=lambda token, digest, actor: True,
        audit_sink=events.append,
        required_checks=[
            CheckCommand("secret_scan", ("secret-scan", "."), "secret-scanner", "1.0"),
            CheckCommand("secure_code_review", ("secure-review", "."), "secure-review", "1.0"),
            CheckCommand("tests", ("pytest", "-q"), "pytest", "8.0"),
        ],
        process_runner=runner,
        policy_fetcher=fetcher,
    )
    return host, root, events


def run_successful_agent(context):
    assert set(context.policy_files) == set(CORE) | set(DOMAIN)
    assert context.policy_instruction.startswith("Before making changes")
    (context_root / "app.py").write_text("print('safe')\n", encoding="utf-8")
    return context.dispatch_tool(
        "repo.write", "write", "repo:demo", {"content": "verified"}
    )


@pytest.fixture
def context_root(tmp_path):
    return tmp_path / "project"


def test_reference_host_completes_controlled_path_and_keeps_reviewer_gate_pending(tmp_path):
    host, root, events = build_host(tmp_path)
    def agent(context):
        assert set(context.policy_files) == set(CORE) | set(DOMAIN)
        assert context.tsar_commit_sha == COMMIT
        assert context.dispatch_tool(
            "repo.write", "write", "repo:demo", {"content": "verified"}
        ) == {"written": "verified"}
        (root / "app.py").write_text("print('safe')\n", encoding="utf-8")

    result = host.run_task(
        "Implement a secure module",
        agent,
        task_id="e6-test-001",
        agent_id="test-agent",
        audit_file=".tsar/runs/e6-test-001.json",
        output_evidence_file=".tsar/evidence/e6-test-001.json",
        changed_files_provider=lambda: ["app.py"],
        domains=["development"],
    )
    assert result.status == "PASS"
    assert result.tsar_commit_sha == COMMIT
    assert result.selected_domains == ("core", "development")
    assert result.tool_events == 2
    assert len(events) == 2
    evidence = json.loads((root / result.output_evidence_file).read_text())
    assert evidence["decision"] == "PASS"
    assert evidence["provenance"]["enforcement_level"] == "E6"
    audit = json.loads((root / result.audit_file).read_text())
    assert audit["gates"]["output_verification"] == "PENDING"


def test_preflight_failure_blocks_agent_and_creates_no_audit(tmp_path):
    host, root, _ = build_host(tmp_path, preflight_status="FAIL")
    called = []
    with pytest.raises(ReferenceHostError, match="preflight blocked"):
        host.run_task(
            "Implement a secure module", lambda context: called.append(True),
            task_id="blocked", agent_id="test-agent",
            audit_file=".tsar/runs/blocked.json",
            output_evidence_file=".tsar/evidence/blocked.json",
            changed_files_provider=lambda: ["app.py"],
            domains=["development"],
        )
    assert called == []
    assert not (root / ".tsar/runs/blocked.json").exists()


def test_pinned_policy_hash_mismatch_blocks_before_agent(tmp_path):
    host, root, _ = build_host(tmp_path, tamper_policy=True)
    called = []
    with pytest.raises(ReferenceHostError, match="hash mismatch"):
        host.run_task(
            "Implement a secure module", lambda context: called.append(True),
            task_id="tampered", agent_id="test-agent",
            audit_file=".tsar/runs/tampered.json",
            output_evidence_file=".tsar/evidence/tampered.json",
            changed_files_provider=lambda: ["app.py"],
            domains=["development"],
        )
    assert called == []


def test_unregistered_tool_is_denied_and_audited(tmp_path):
    host, root, events = build_host(tmp_path)
    def agent(context):
        context.dispatch_tool("unregistered", "write", "repo:demo", {})
    with pytest.raises(ReferenceHostError, match="Agent execution failed"):
        host.run_task(
            "Implement a secure module", agent,
            task_id="denied", agent_id="test-agent",
            audit_file=".tsar/runs/denied.json",
            output_evidence_file=".tsar/evidence/denied.json",
            changed_files_provider=lambda: ["app.py"],
            domains=["development"],
        )
    assert events[-1]["decision"] == "DENY"


def test_failed_required_check_writes_blocked_output_evidence(tmp_path):
    host, root, _ = build_host(tmp_path, check_exit_codes={"pytest": 1})
    def agent(_context):
        (root / "app.py").write_text("print('safe')\n", encoding="utf-8")
    result = host.run_task(
        "Implement a secure module", agent,
        task_id="failed-check", agent_id="test-agent",
        audit_file=".tsar/runs/failed-check.json",
        output_evidence_file=".tsar/evidence/failed-check.json",
        changed_files_provider=lambda: ["app.py"],
        domains=["development"],
    )
    assert result.status == "BLOCKED"
    evidence = json.loads((root / result.output_evidence_file).read_text())
    assert evidence["decision"] == "BLOCKED"
    assert evidence["failed_required_checks"] == ["tests"]


def test_changed_file_outside_project_is_rejected(tmp_path):
    host, root, _ = build_host(tmp_path)
    outside = tmp_path / "outside.py"
    outside.write_text("unsafe", encoding="utf-8")
    def agent(_context):
        (root / "app.py").write_text("print('safe')\n", encoding="utf-8")
    with pytest.raises(ReferenceHostError, match="inside the project root"):
        host.run_task(
            "Implement a secure module", agent,
            task_id="outside", agent_id="test-agent",
            audit_file=".tsar/runs/outside.json",
            output_evidence_file=".tsar/evidence/outside.json",
            changed_files_provider=lambda: [outside],
            domains=["development"],
        )


def test_host_requires_all_mandatory_check_classes(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    spec = ToolSpec(
        name="repo.write", action_class=ActionClass.REPOSITORY_WRITE,
        operations=frozenset({"write"}), resources=frozenset({"repo:demo"}),
        required_scope="repo:write",
    )
    from reference_host import ReferenceHostError
    with pytest.raises(ReferenceHostError, match="must uniquely include"):
        ReferenceHost(
            repo_root=root, tool_registry={"repo.write": spec},
            dispatchers={"repo.write": lambda args: None},
            authorization=AuthorizationContext("operator-1", frozenset({"repo:write"})),
            approval_verifier=lambda *args: True, audit_sink=lambda event: None,
            required_checks=[CheckCommand("tests", ("pytest", "-q"), "pytest", "8.0")],
        )
