#!/usr/bin/env python3
"""TSAR CLI: scan, inventory, init, lint, version, threat-model, report, drift."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS = ROOT / "skills"
SCRIPTS = ROOT / "scripts"
TOOLS = ROOT / "tools"

def run_py(script: Path, *args: str) -> int:
    return subprocess.call([sys.executable, str(script), *args])

def cmd_scan(args) -> int:
    target = Path(args.path).expanduser()
    if not target.exists() or not (target.is_file() or target.is_dir()):
        print(f"Invalid scan target: {target}", file=sys.stderr)
        return 2
    if args.format == "sarif":
        sys.path.insert(0, str(SKILLS / "secure-review"))
        import importlib
        review_mod = importlib.import_module("review")
        findings = review_mod.review(target)
        sys.path.insert(0, str(SKILLS / "secret-scanner"))
        secret_mod = importlib.import_module("scanner")
        findings.extend(
            (path, line, kind, "HIGH", "Potential secret or credential detected.")
            for path, line, kind in secret_mod.scan(target)
        )
        sys.path.insert(0, str(TOOLS / "tsar-cli"))
        import sarif as sarif_mod
        out = Path(args.output or "tsar.sarif")
        out.parent.mkdir(parents=True, exist_ok=True)
        sarif_mod.emit(findings, out)
        print(f"SARIF written to {out}")
        return 1 if any(f[3] == "HIGH" for f in findings) else 0
    rc = 0
    rc |= run_py(SKILLS / "secret-scanner" / "scanner.py", args.path)
    rc |= run_py(SKILLS / "secure-review" / "review.py", args.path)
    print(f"TSAR scan exit code: {rc}")
    return rc

def cmd_inventory(args) -> int:
    return run_py(SKILLS / "crypto-inventory" / "inventory.py", args.path)

def cmd_lint(_args) -> int:
    return run_py(SCRIPTS / "lint_rules.py")

def cmd_check_version(_args) -> int:
    return run_py(SCRIPTS / "check_manifest_version.py")

def cmd_threat_model(args) -> int:
    return run_py(SKILLS / "threat-modeler" / "model.py", args.path)

def cmd_report(args) -> int:
    report = TOOLS / "tsar-report" / "generate.py"
    argv = [str(report), args.path, "--format", args.format, "--output", args.output]
    return subprocess.call([sys.executable, *argv])

def cmd_compliance(args) -> int:
    """Print rule coverage for a compliance framework."""
    framework_file = ROOT / "docs" / "compliance" / f"{args.framework}.md"
    if not framework_file.exists():
        print(f"Unknown framework: {args.framework}")
        return 2
    text = framework_file.read_text()
    import re
    rules = sorted(set(re.findall(r"rules/[\w\-/]+\.md", text)))
    missing = [r for r in rules if not (ROOT / r).exists()]
    print(f"Framework: {args.framework}")
    print(f"Referenced rules: {len(rules)}")
    if missing:
        print("Missing:")
        for m in missing:
            print(f"  - {m}")
        return 1
    print("All referenced rules exist.")
    return 0

def cmd_lifecycle_plan(args) -> int:
    """Create a deterministic lifecycle plan; this does not approve or execute work."""
    import yaml
    sys.path.insert(0, str(TOOLS / "tsar-cli"))
    from lifecycle_engine import classify_task

    try:
        manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8"))
        domains = manifest.get("active_files", {})
        plan = classify_task(
            args.task,
            explicit_domains=args.domain,
            impact=args.impact,
            available_domains=domains.keys(),
        )
    except Exception as exc:
        print(f"Lifecycle planning failed: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(plan.to_dict(), indent=2, ensure_ascii=False))
    return 0



def cmd_lifecycle_start(args) -> int:
    """Start a lifecycle run only after evidence-backed upstream preflight."""
    sys.path.insert(0, str(TOOLS / "tsar-cli"))
    from lifecycle_orchestrator import LifecycleStartError, start_lifecycle

    try:
        record = start_lifecycle(
            args.task,
            repo_root=ROOT,
            audit_file=Path(args.audit_file),
            domains=args.domain,
            impact=args.impact,
        )
    except LifecycleStartError as exc:
        print(f"Lifecycle start BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(record, indent=2, ensure_ascii=False))
    print(f"Audit record: {Path(args.audit_file)}")
    return 0

def cmd_lifecycle_evidence(args) -> int:
    """Attach hashed evidence to one pending lifecycle gate."""
    sys.path.insert(0, str(TOOLS / "tsar-cli"))
    from lifecycle_evidence import LifecycleEvidenceError, attest_gate
    try:
        record = attest_gate(
            Path(args.audit_file), repo_root=ROOT, gate=args.gate,
            evidence_file=args.evidence, actor=args.actor, decision=args.decision,
        )
    except LifecycleEvidenceError as exc:
        print(f"Lifecycle evidence REJECTED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(record, indent=2, ensure_ascii=False))
    return 0


def cmd_verify_upstream(args) -> int:
    """Verify the authoritative upstream snapshot before security-sensitive work."""
    script = Path(__file__).resolve().with_name("verify_upstream.py")
    argv = [str(script)]
    for domain in args.domain:
        argv.extend(["--domain", domain])
    if args.report:
        argv.extend(["--report", args.report])
    if args.repo_root:
        argv.extend(["--repo-root", args.repo_root])
    return subprocess.call([sys.executable, *argv])


def cmd_drift(args) -> int:
    """Compare local manifest and remote; report drift."""
    import urllib.request
    import yaml
    local = yaml.safe_load((ROOT / "manifest.yaml").read_text())
    url = local["lifecycle"]["check_url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "TSAR-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            remote = yaml.safe_load(resp.read())
    except Exception as exc:
        print(f"WARN: cannot fetch remote manifest: {exc}")
        return 2
    lv, rv = local.get("version"), remote.get("version")
    if lv == rv:
        print(f"No drift: version {lv}")
        return 0
    print(f"DRIFT: local={lv} remote={rv}")
    local_files = set()
    for files in local.get("active_files", {}).values():
        local_files.update(files)
    remote_files = set()
    for files in remote.get("active_files", {}).values():
        remote_files.update(files)
    added = sorted(remote_files - local_files)
    removed = sorted(local_files - remote_files)
    if added:
        print("Files added upstream:")
        for f in added:
            print(f"  + {f}")
    if removed:
        print("Files removed upstream:")
        for f in removed:
            print(f"  - {f}")
    if not added and not removed:
        print("File set unchanged; content may differ.")
    return 1

def _atomic_replace_directory(staged_dir: Path, destination: Path, backup: Path) -> None:
    """Promote a staged directory and restore the previous tree if promotion fails."""
    previous_moved = False
    if destination.exists():
        os.replace(destination, backup)
        previous_moved = True
    try:
        os.replace(staged_dir, destination)
    except Exception as install_error:
        if previous_moved and backup.exists() and not destination.exists():
            try:
                os.replace(backup, destination)
            except Exception as rollback_error:
                raise RuntimeError(
                    f"promotion failed ({install_error}); rollback failed ({rollback_error}); "
                    f"the previous installation remains at {backup}"
                ) from rollback_error
        raise


def cmd_init(args) -> int:
    """Install or refresh the vendored TSAR tree without discarding user data."""
    import tempfile
    import yaml

    target = Path(args.path).expanduser().resolve()
    if not target.is_dir():
        print(f"Target directory does not exist: {target}", file=sys.stderr)
        return 2

    prompt_map = {
        "claude": ("claude.md", "CLAUDE.md"),
        "claude-code": ("claude-code.md", "CLAUDE.md"),
        "cursor": ("cursor.md", ".cursorrules"),
        "copilot": ("github-copilot.md", ".github/copilot-instructions.md"),
        "windsurf": ("windsurf.md", ".windsurfrules"),
        "windsurf-rc": ("windsurf.md", ".windsurfrules"),
        "generic": ("universal.md", "AGENTS.md"),
    }
    if args.agent not in prompt_map:
        print(f"Unknown agent: {args.agent}", file=sys.stderr)
        return 2

    prompt_name, destination_name = prompt_map[args.agent]
    prompt_source = ROOT / "prompts" / prompt_name
    if not prompt_source.is_file():
        print(f"Prompt not found: {prompt_source}", file=sys.stderr)
        return 2

    tsar_dir = target / ".tsar"
    if tsar_dir.is_symlink() or (tsar_dir.exists() and not tsar_dir.is_dir()):
        print(f"Refusing to replace non-directory TSAR path: {tsar_dir}", file=sys.stderr)
        return 2

    manifest_path = ROOT / "manifest.yaml"
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print(f"Cannot read TSAR manifest: {exc}", file=sys.stderr)
        return 2

    version = str(manifest.get("version", "unknown"))
    stage_dir = None
    backup_dir = target / f".tsar.backup.{time.time_ns()}"
    managed_entries = {"skills", "scripts", "rules", "system", "tsar-report",
                       "manifest.yaml", "config.json", "pre-commit"}

    try:
        stage_dir = Path(tempfile.mkdtemp(prefix=".tsar-stage-", dir=str(target)))

        # Preserve user-managed top-level entries. The complete previous .tsar
        # tree is also retained as a timestamped backup for recovery.
        if tsar_dir.is_dir():
            for child in tsar_dir.iterdir():
                if child.name in managed_entries:
                    continue
                destination = stage_dir / child.name
                if child.is_dir() and not child.is_symlink():
                    shutil.copytree(child, destination, symlinks=True)
                elif child.is_symlink():
                    destination.symlink_to(os.readlink(child), target_is_directory=child.is_dir())
                else:
                    shutil.copy2(child, destination)

        ignore_generated = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")
        for source_name in ("skills", "scripts", "rules", "system"):
            shutil.copytree(
                ROOT / source_name,
                stage_dir / source_name,
                ignore=ignore_generated,
                symlinks=True,
            )
        shutil.copytree(
            TOOLS / "tsar-report",
            stage_dir / "tsar-report",
            ignore=ignore_generated,
            symlinks=True,
        )
        shutil.copy2(manifest_path, stage_dir / "manifest.yaml")
        (stage_dir / "config.json").write_text(
            json.dumps({
                "manifest_version": version,
                "agent": args.agent,
                "vendored": True,
            }, indent=2) + "\n",
            encoding="utf-8",
        )

        hook_source = ROOT / "integrations" / "git-hooks" / "pre-commit"
        if hook_source.is_file():
            shutil.copy2(hook_source, stage_dir / "pre-commit")
            (stage_dir / "pre-commit").chmod(0o755)

        # Move the previous tree aside, then promote the fully prepared tree.
        # If promotion fails, restore the previous tree before returning.
        _atomic_replace_directory(stage_dir, tsar_dir, backup_dir)
        stage_dir = None

    except Exception as exc:
        if stage_dir is not None and stage_dir.exists():
            shutil.rmtree(stage_dir, ignore_errors=True)
        print(f"TSAR installation failed: {exc}",
              file=sys.stderr)
        return 1

    if backup_dir.exists():
        print(f"Previous TSAR installation retained at {backup_dir.name}")

    partial_failure = False

    # Never overwrite an existing agent instruction file: it may contain
    # project-specific guidance maintained by the user.
    destination = target / destination_name
    if destination.exists() or destination.is_symlink():
        print(f"Existing agent file preserved: {destination}")
    else:
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            prompt_temp = destination.with_name(f".{destination.name}.tsar-{time.time_ns()}.tmp")
            shutil.copy2(prompt_source, prompt_temp)
            try:
                os.link(prompt_temp, destination)
                prompt_temp.unlink()
            except FileExistsError:
                prompt_temp.unlink(missing_ok=True)
                print(f"Agent file appeared during installation; preserved: {destination}")
            except (AttributeError, NotImplementedError, OSError):
                if destination.exists():
                    prompt_temp.unlink(missing_ok=True)
                    print(f"Agent file appeared during installation; preserved: {destination}")
                else:
                    os.replace(prompt_temp, destination)
        except Exception as exc:
            partial_failure = True
            print(f"WARNING: TSAR installed, but agent prompt was not created: {exc}",
                  file=sys.stderr)

    # Install the hook without destroying a pre-existing user hook.
    hooks_dir = target / ".git" / "hooks"
    hook_source = ROOT / "integrations" / "git-hooks" / "pre-commit"
    if hooks_dir.is_dir() and hook_source.is_file():
        hook_destination = hooks_dir / "pre-commit"
        try:
            if not hook_destination.exists():
                hook_temp = hooks_dir / f".pre-commit.tsar-{time.time_ns()}.tmp"
                shutil.copy2(hook_source, hook_temp)
                hook_temp.chmod(0o755)
                try:
                    os.link(hook_temp, hook_destination)
                    hook_temp.unlink()
                except (AttributeError, NotImplementedError, OSError):
                    if hook_destination.exists():
                        hook_temp.unlink(missing_ok=True)
                    else:
                        os.replace(hook_temp, hook_destination)
            else:
                existing = hook_destination.read_text(encoding="utf-8", errors="replace")
                if "TSAR_DIR=" not in existing and "TSAR pre-commit hook" not in existing:
                    backup_name = f"pre-commit.user-backup.{time.time_ns()}"
                    backup_path = hooks_dir / backup_name
                    shutil.copy2(hook_destination, backup_path)
                    wrapper = (
                        "#!/usr/bin/env bash\nset -euo pipefail\n"
                        + 'HOOK_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"\n'
                        + f'"$HOOK_DIR/{backup_name}" "$@"\n'
                        + 'export TSAR_DIR="$(git rev-parse --show-toplevel)/.tsar"\n'
                        + '"$TSAR_DIR/pre-commit" "$@"\n'
                    )
                    wrapper_temp = hooks_dir / f".pre-commit.tsar-{time.time_ns()}.tmp"
                    wrapper_temp.write_text(wrapper, encoding="utf-8")
                    wrapper_temp.chmod(0o755)
                    os.replace(wrapper_temp, hook_destination)
                else:
                    print("Existing TSAR pre-commit integration preserved.")
        except Exception as exc:
            partial_failure = True
            print(f"WARNING: TSAR installed, but Git hook setup failed: {exc}",
                  file=sys.stderr)

    print(f"TSAR v{version} installed at {tsar_dir}")
    return 1 if partial_failure else 0

def main() -> int:
    p = argparse.ArgumentParser(prog="tsar", description="TSAR security CLI")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan")
    s.add_argument("path", nargs="?", default=".")
    s.add_argument("--format", choices=["text", "sarif"], default="text")
    s.add_argument("--output", default="tsar.sarif")
    s.set_defaults(func=cmd_scan)

    i = sub.add_parser("inventory")
    i.add_argument("path", nargs="?", default=".")
    i.set_defaults(func=cmd_inventory)

    l = sub.add_parser("lint")
    l.set_defaults(func=cmd_lint)

    v = sub.add_parser("version")
    v.set_defaults(func=cmd_check_version)

    t = sub.add_parser("threat-model")
    t.add_argument("path")
    t.set_defaults(func=cmd_threat_model)

    r = sub.add_parser("report")
    r.add_argument("path", nargs="?", default=".")
    r.add_argument("--format", choices=["html", "json"], default="html")
    r.add_argument("--output", default="tsar-report.html")
    r.set_defaults(func=cmd_report)

    c = sub.add_parser("compliance")
    c.add_argument("framework", choices=["soc2", "iso27001", "pci-dss", "hipaa", "gdpr"])
    c.set_defaults(func=cmd_compliance)

    lp = sub.add_parser("lifecycle-plan", help="Create a deterministic TSAR lifecycle plan")
    lp.add_argument("task", help="Short description of the engineering task")
    lp.add_argument("--domain", action="append", default=[], help="Explicit applicable manifest domain; repeat as needed")
    lp.add_argument("--impact", choices=["auto", "standard", "high"], default="auto")
    lp.set_defaults(func=cmd_lifecycle_plan)


    ls = sub.add_parser("lifecycle-start", help="Start an evidence-backed TSAR lifecycle run")
    ls.add_argument("task", help="Engineering task description")
    ls.add_argument("--audit-file", required=True, help="New audit JSON path; existing files are never overwritten")
    ls.add_argument("--domain", action="append", default=[], help="Applicable manifest domain; repeat as needed")
    ls.add_argument("--impact", choices=["auto", "standard", "high"], default="auto")
    ls.set_defaults(func=cmd_lifecycle_start)

    le = sub.add_parser("lifecycle-evidence", help="Attach hashed evidence to a pending lifecycle gate")
    le.add_argument("--audit-file", required=True, help="Existing lifecycle audit JSON path")
    le.add_argument("--gate", required=True, help="Gate name from the lifecycle audit record")
    le.add_argument("--evidence", required=True, help="Evidence file path relative to the TSAR project root")
    le.add_argument("--actor", required=True, help="Reviewer or operator identifier (not authenticated)")
    le.add_argument("--decision", choices=["PASS", "FAIL"], default="PASS")
    le.set_defaults(func=cmd_lifecycle_evidence)

    u = sub.add_parser("verify-upstream")
    u.add_argument("--domain", action="append", default=[],
                   help="Applicable manifest domain; repeat as needed")
    u.add_argument("--report", help="Write a JSON verification report")
    u.add_argument("--repo-root", help="Optional local TSAR checkout for version checks")
    u.set_defaults(func=cmd_verify_upstream)

    d = sub.add_parser("drift")
    d.set_defaults(func=cmd_drift)

    ini = sub.add_parser("init")
    ini.add_argument("path", nargs="?", default=".")
    ini.add_argument("--agent", required=False, default="generic",
                     choices=["claude", "claude-code", "cursor", "copilot",
                              "windsurf", "windsurf-rc", "generic"])
    ini.set_defaults(func=cmd_init)

    args = p.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
