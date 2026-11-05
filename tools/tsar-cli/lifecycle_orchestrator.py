"""Fail-closed lifecycle run initialization with evidence-backed preflight.

This module starts a run; it does not execute implementation or attest review gates.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Iterable, Sequence

from lifecycle_engine import classify_task


class LifecycleStartError(RuntimeError):
    """Raised when a lifecycle run cannot be safely initialized."""


def _write_exclusive(path: Path, payload: dict) -> None:
    path = path.expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    fd = os.open(str(path), flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def start_lifecycle(
    task: str,
    *,
    repo_root: Path,
    audit_file: Path,
    domains: Iterable[str] = (),
    impact: str = "auto",
    python_executable: str = sys.executable,
    run=subprocess.run,
) -> dict:
    """Run pinned upstream preflight and persist an auditable, non-overwriting run record."""
    root = Path(repo_root).resolve()
    manifest_path = root / "manifest.yaml"
    verifier = root / "tools" / "tsar-cli" / "verify_upstream.py"
    if not manifest_path.is_file() or not verifier.is_file():
        raise LifecycleStartError("TSAR manifest or upstream verifier is missing")
    try:
        import yaml
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict) or not isinstance(manifest.get("active_files"), dict):
            raise ValueError("manifest active_files mapping is missing")
        plan = classify_task(
            task,
            explicit_domains=domains,
            impact=impact,
            available_domains=manifest["active_files"].keys(),
        )
    except Exception as exc:
        raise LifecycleStartError(f"task planning failed: {exc}") from exc

    with tempfile.TemporaryDirectory(prefix="tsar-preflight-") as temp_dir:
        report_path = Path(temp_dir) / "preflight.json"
        command: Sequence[str] = [
            python_executable, str(verifier), "--report", str(report_path),
        ]
        for domain in plan.domains:
            command.extend(["--domain", domain])
        try:
            completed = run(
                list(command), cwd=str(root), check=False,
                capture_output=True, text=True, timeout=180,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise LifecycleStartError(f"upstream preflight could not run: {exc}") from exc

        try:
            evidence = json.loads(report_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise LifecycleStartError("preflight produced no valid evidence report") from exc
        if completed.returncode != 0 or evidence.get("status") != "PASS":
            errors = evidence.get("errors", [])
            raise LifecycleStartError(
                "upstream preflight failed; lifecycle remains blocked: "
                + "; ".join(str(item) for item in errors)
            )
        required = ("commit_sha", "manifest_version", "manifest_sha256", "loaded_policy_sha256")
        if any(not evidence.get(key) for key in required):
            raise LifecycleStartError("preflight PASS report is missing required provenance fields")
        if evidence.get("repository") != "mohamedelghazali/TSAR":
            raise LifecycleStartError("preflight report repository identity mismatch")

    gate_status = {gate: "PENDING" for gate in plan.required_gates}
    gate_status["upstream_preflight"] = "PASS"
    record = {
        "schema": "tsar/lifecycle-run/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "task": plan.to_dict(),
        "state": "preflight",
        "status": "IN_PROGRESS",
        "provenance": {
            "repository": evidence["repository"],
            "upstream_commit_sha": evidence["commit_sha"],
            "manifest_version": evidence["manifest_version"],
            "manifest_sha256": evidence["manifest_sha256"],
            "loaded_policy_sha256": evidence["loaded_policy_sha256"],
            "selected_domains": evidence.get("selected_domains", []),
            "verifier": evidence.get("verifier"),
        },
        "gates": gate_status,
        "limitations": [
            "Only upstream preflight is attested by this run initializer.",
            "Policy review, implementation, tests, scanning, independent review, and release approval remain pending.",
            "This record is local evidence, not a signed attestation or tamper-proof audit log.",
            "The initializer does not execute commands from the manifest or repository content.",
        ],
    }
    try:
        _write_exclusive(Path(audit_file), record)
    except FileExistsError as exc:
        raise LifecycleStartError("audit file already exists; refusing to overwrite it") from exc
    except OSError as exc:
        raise LifecycleStartError(f"cannot securely create audit file: {exc}") from exc
    return record
