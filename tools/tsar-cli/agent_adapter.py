"""Fail-closed launcher for agent commands with an upstream TSAR preflight gate.

This adapter gates only the command it launches. It does not intercept tools
used by an already-running agent or prove that the child agent obeys policy.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, Sequence


class AgentGateError(RuntimeError):
    """Raised when TSAR preflight cannot authorize launching the child agent."""


def run_agent(
    command: Sequence[str],
    *,
    domains: Sequence[str] = (),
    report_path: Path,
    cwd: Path | None = None,
    runner: Callable[..., int] = subprocess.call,
) -> int:
    """Run a child agent only after a successful upstream preflight.

    The child receives the report path, pinned commit, and manifest version
    through environment variables. The report contains hashes and validation
    metadata; the child integration must separately load the referenced policy
    files into its supported instruction/context mechanism.
    """
    if not command:
        raise AgentGateError("No agent command supplied; use '-- COMMAND [ARGS...]'")

    report = report_path.expanduser().resolve()
    report.parent.mkdir(parents=True, exist_ok=True)
    verifier = Path(__file__).resolve().with_name("verify_upstream.py")
    argv = [sys.executable, str(verifier)]
    for domain in domains:
        argv.extend(["--domain", domain])
    argv.extend(["--report", str(report)])

    try:
        preflight_rc = runner(argv, cwd=str(cwd) if cwd else None)
    except OSError as exc:
        raise AgentGateError(f"Unable to execute TSAR upstream preflight: {exc}") from exc

    if preflight_rc != 0:
        raise AgentGateError(f"Upstream preflight exited with status {preflight_rc}; agent launch blocked")
    try:
        evidence = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AgentGateError(f"Preflight report is missing or invalid: {exc}") from exc

    sha = evidence.get("commit_sha")
    version = evidence.get("manifest_version")
    if (
        evidence.get("status") != "PASS"
        or not isinstance(sha, str)
        or len(sha) != 40
        or not isinstance(version, str)
        or not evidence.get("manifest_sha256")
    ):
        raise AgentGateError("Preflight report is incomplete or not PASS; agent launch blocked")

    env = os.environ.copy()
    env.update({
        "TSAR_PREFLIGHT_STATUS": "PASS",
        "TSAR_PREFLIGHT_REPORT": str(report),
        "TSAR_UPSTREAM_COMMIT_SHA": sha,
        "TSAR_MANIFEST_VERSION": version,
    })
    return runner(list(command), cwd=str(cwd) if cwd else None, env=env)


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Launch an agent command only after fail-closed TSAR upstream preflight"
    )
    parser.add_argument("--domain", action="append", default=[], help="Applicable TSAR domain; repeat as needed")
    parser.add_argument("--report", default=".tsar/preflight/agent-launch.json", help="Preflight JSON report path")
    parser.add_argument("--cwd", help="Working directory for preflight and child agent")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Child agent command after --")
    args = parser.parse_args(argv)
    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    try:
        return run_agent(
            command,
            domains=args.domain,
            report_path=Path(args.report),
            cwd=Path(args.cwd).expanduser().resolve() if args.cwd else None,
        )
    except AgentGateError as exc:
        print(f"TSAR AGENT GATE: BLOCKED — {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
