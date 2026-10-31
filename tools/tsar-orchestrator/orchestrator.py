#!/usr/bin/env python3
"""TSAR Orchestrator: run all checks in a single pipeline and emit a unified report."""
import argparse
import concurrent.futures
import datetime
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS = ROOT / "skills"
SCRIPTS = ROOT / "scripts"
TOOLS = ROOT / "tools"

@dataclass
class StepResult:
    name: str
    exit_code: int
    duration: float
    stdout: str = ""
    stderr: str = ""
    skipped: bool = False

@dataclass
class PipelineResult:
    started_at: str
    finished_at: str = ""
    duration: float = 0.0
    steps: list = field(default_factory=list)
    summary: dict = field(default_factory=dict)

def _run(name: str, cmd: list[str], cwd: Path, timeout: int = 600) -> StepResult:
    start = time.time()
    try:
        r = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return StepResult(name, r.returncode, time.time() - start, r.stdout, r.stderr)
    except subprocess.TimeoutExpired:
        return StepResult(name, 124, time.time() - start, "", "timeout")
    except FileNotFoundError as exc:
        return StepResult(name, 127, time.time() - start, "", str(exc))

def step_lint(root: Path) -> StepResult:
    return _run("lint", [sys.executable, str(root / "scripts" / "lint_rules.py")], root)

def step_secrets(target: Path) -> StepResult:
    return _run("secrets", [sys.executable, str(SKILLS / "secret-scanner" / "scanner.py"), str(target)], ROOT)

def step_review(target: Path) -> StepResult:
    return _run("review", [sys.executable, str(SKILLS / "secure-review" / "review.py"), str(target)], ROOT)

def step_cbom(target: Path) -> StepResult:
    return _run("cbom", [sys.executable, str(SKILLS / "crypto-inventory" / "inventory.py"), str(target)], ROOT)

def step_compliance(framework: str) -> StepResult:
    return _run("compliance", [sys.executable, str(TOOLS / "tsar-cli" / "tsar.py"), "compliance", framework], ROOT)

def summarize(steps: list[StepResult]) -> dict:
    return {
        "total": len(steps),
        "passed": sum(1 for s in steps if s.exit_code == 0 and not s.skipped),
        "failed": sum(1 for s in steps if s.exit_code != 0 and not s.skipped),
        "skipped": sum(1 for s in steps if s.skipped),
        "max_duration_s": round(max((s.duration for s in steps), default=0.0), 3),
    }

def render_markdown(result: PipelineResult) -> str:
    lines = []
    lines.append(f"# TSAR Orchestrator Report")
    lines.append("")
    lines.append(f"Started: {result.started_at}")
    lines.append(f"Finished: {result.finished_at}")
    lines.append(f"Duration: {result.duration:.2f}s")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    s = result.summary
    lines.append(f"- Steps: {s['total']}")
    lines.append(f"- Passed: {s['passed']}")
    lines.append(f"- Failed: {s['failed']}")
    lines.append(f"- Skipped: {s['skipped']}")
    lines.append("")
    lines.append("## Steps")
    lines.append("")
    lines.append("| Step | Exit | Duration | Status |")
    lines.append("|---|---|---|---|")
    for step in result.steps:
        status = "SKIPPED" if step.skipped else ("PASS" if step.exit_code == 0 else "FAIL")
        lines.append(f"| {step.name} | {step.exit_code} | {step.duration:.2f}s | {status} |")
    lines.append("")
    failures = [s for s in result.steps if s.exit_code != 0 and not s.skipped]
    if failures:
        lines.append("## Failures")
        lines.append("")
        for step in failures:
            lines.append(f"### {step.name}")
            lines.append("")
            lines.append("```")
            lines.append((step.stdout + step.stderr).strip()[:4000])
            lines.append("```")
            lines.append("")
    return "\n".join(lines)

def run_pipeline(target: Path, include: set[str], compliance: list[str], parallel: bool, root: Path) -> PipelineResult:
    started = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    steps = []

    if "lint" in include:
        steps.append(step_lint(root))
    if "secrets" in include:
        steps.append(step_secrets(target))
    if "review" in include:
        steps.append(step_review(target))
    if "cbom" in include:
        steps.append(step_cbom(target))
    for fw in compliance:
        steps.append(step_compliance(fw))

    return PipelineResult(
        started_at=started,
        finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        duration=sum(s.duration for s in steps),
        steps=steps,
        summary=summarize(steps),
    )

def main() -> int:
    p = argparse.ArgumentParser(prog="tsar-orchestrator")
    p.add_argument("path", nargs="?", default=".")
    p.add_argument("--include", default="lint,secrets,review,cbom")
    p.add_argument("--compliance", default="")
    p.add_argument("--format", choices=["json", "markdown"], default="markdown")
    p.add_argument("--output", default="")
    args = p.parse_args()

    target = Path(args.path).resolve()
    include = {s.strip() for s in args.include.split(",") if s.strip()}
    compliance = [s.strip() for s in args.compliance.split(",") if s.strip()]

    result = run_pipeline(target, include, compliance, True, ROOT)

    if args.format == "json":
        payload = json.dumps({
            "started_at": result.started_at,
            "finished_at": result.finished_at,
            "duration": result.duration,
            "summary": result.summary,
            "steps": [
                {"name": s.name, "exit_code": s.exit_code,
                 "duration": s.duration, "skipped": s.skipped,
                 "stdout": s.stdout, "stderr": s.stderr}
                for s in result.steps
            ],
        }, indent=2)
    else:
        payload = render_markdown(result)

    if args.output:
        Path(args.output).write_text(payload)
        print(f"Report written to {args.output}")
    else:
        print(payload)

    return 0 if result.summary["failed"] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
