#!/usr/bin/env python3
"""TSAR CLI: scan, inventory, init, lint, version, threat-model, report, drift."""
import argparse
import json
import os
import shutil
import subprocess
import sys
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
        sys.path.insert(0, str(TOOLS / "tsar-cli"))
        import sarif as sarif_mod
        out = Path(args.output or "tsar.sarif")
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
    target = Path(args.path).resolve()
    if not target.exists():
        print(f"Target does not exist: {target}")
        return 2
    valid = {"claude", "claude-code", "cursor", "copilot",
             "windsurf", "windsurf-rc", "generic"}
    if args.agent not in valid:
        print(f"Unknown agent: {args.agent}")
        return 2
    prompt_src = {
        "claude": ROOT / "prompts" / "claude.md",
        "claude-code": ROOT / "prompts" / "claude-code.md",
        "cursor": ROOT / "prompts" / "cursor.md",
        "copilot": ROOT / "prompts" / "github-copilot.md",
        "windsurf": ROOT / "prompts" / "windsurf.md",
        "windsurf-rc": ROOT / "prompts" / "windsurf.md",
        "generic": ROOT / "prompts" / "universal.md",
    }[args.agent]
    dest = {
        "claude": target / "CLAUDE.md",
        "claude-code": target / "CLAUDE.md",
        "cursor": target / ".cursorrules",
        "copilot": target / ".github" / "copilot-instructions.md",
        "windsurf": target / ".windsurfrules",
        "windsurf-rc": target / ".windsurfrules",
        "generic": target / "AGENTS.md",
    }[args.agent]
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(prompt_src, dest)
    print(f"Prompt written to {dest}")

    tsar_dir = target / ".tsar"
    tsar_dir.mkdir(exist_ok=True)
    shutil.copytree(SKILLS, tsar_dir / "skills", dirs_exist_ok=True)
    shutil.copytree(SCRIPTS, tsar_dir / "scripts", dirs_exist_ok=True)
    shutil.copytree(TOOLS / "tsar-report", tsar_dir / "tsar-report", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "manifest.yaml", tsar_dir / "manifest.yaml")
    print(f"TSAR vendored at {tsar_dir}")

    hooks = target / ".git" / "hooks"
    if hooks.exists():
        hook_dst = hooks / "pre-commit"
        hook_src = ROOT / "integrations" / "git-hooks" / "pre-commit"
        if not hook_dst.exists() or "TSAR" not in hook_dst.read_text():
            shutil.copyfile(hook_src, hook_dst)
            hook_dst.chmod(0o755)
            print(f"Pre-commit hook installed at {hook_dst}")

    (tsar_dir / "config.json").write_text(json.dumps({
        "manifest_version": "1.0.0",
        "agent": args.agent,
        "vendored": True,
    }, indent=2))
    print("TSAR init complete")
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
