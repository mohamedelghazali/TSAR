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
    if args.format == "sarif":
        sys.path.insert(0, str(SKILLS / "secure-review"))
        import importlib
        review_mod = importlib.import_module("review")
        findings = review_mod.review(Path(args.path))
        sys.path.insert(0, str(SKILLS / "secret-scanner"))
        secret_mod = importlib.import_module("scanner")
        findings.extend(
            (path, line, kind, "HIGH", "Potential secret or credential detected.")
            for path, line, kind in secret_mod.scan(Path(args.path))
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

def cmd_init(args) -> int:
    import yaml

    target = Path(args.path).resolve()
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
    destination = target / destination_name
    if not prompt_source.is_file():
        print(f"Prompt not found: {prompt_source}", file=sys.stderr)
        return 2
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(prompt_source, destination)

    tsar_dir = target / ".tsar"
    tsar_dir.mkdir(parents=True, exist_ok=True)
    for source_name in ("skills", "scripts", "rules", "system"):
        shutil.copytree(ROOT / source_name, tsar_dir / source_name, dirs_exist_ok=True)
    shutil.copytree(TOOLS / "tsar-report", tsar_dir / "tsar-report", dirs_exist_ok=True)
    shutil.copy2(ROOT / "manifest.yaml", tsar_dir / "manifest.yaml")
    manifest = yaml.safe_load((ROOT / "manifest.yaml").read_text(encoding="utf-8")) or {}
    version = str(manifest.get("version", "unknown"))
    (tsar_dir / "config.json").write_text(json.dumps({
        "manifest_version": version, "agent": args.agent, "vendored": True,
    }, indent=2) + "\n", encoding="utf-8")

    hook_source = ROOT / "integrations" / "git-hooks" / "pre-commit"
    tsar_hook = tsar_dir / "pre-commit"
    if hook_source.is_file():
        shutil.copy2(hook_source, tsar_hook)
        tsar_hook.chmod(0o755)
    hooks_dir = target / ".git" / "hooks"
    if hooks_dir.is_dir() and hook_source.is_file():
        hook_destination = hooks_dir / "pre-commit"
        if not hook_destination.exists():
            shutil.copy2(hook_source, hook_destination)
            hook_destination.chmod(0o755)
        else:
            existing = hook_destination.read_text(encoding="utf-8", errors="replace")
            if "TSAR" not in existing:
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
                hook_destination.write_text(wrapper, encoding="utf-8")
                hook_destination.chmod(0o755)
            else:
                print("Existing pre-commit hook already contains TSAR; left unchanged.")
    print(f"TSAR vendored at {tsar_dir}; manifest version {version}")
    return 0
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

    d = sub.add_parser("drift")
    d.set_defaults(func=cmd_drift)

    ini = sub.add_parser("init")
    ini.add_argument("path", nargs="?", default=".")
    ini.add_argument("--agent", required=True,
                     choices=["claude", "claude-code", "cursor", "copilot",
                              "windsurf", "windsurf-rc", "generic"])
    ini.set_defaults(func=cmd_init)

    args = p.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
