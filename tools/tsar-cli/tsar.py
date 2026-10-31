#!/usr/bin/env python3
"""TSAR CLI: scan, inventory, init, lint, version, threat-model."""
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

def run_py(script: Path, *args: str) -> int:
    return subprocess.call([sys.executable, str(script), *args])

def collect_findings(target: str):
    """Return merged findings from secure-review for SARIF emission."""
    sys.path.insert(0, str(SKILLS / "secure-review"))
    import importlib
    review_mod = importlib.import_module("review")
    return review_mod.review(Path(target))

def cmd_scan(args) -> int:
    if args.format == "sarif":
        findings = collect_findings(args.path)
        emit = (ROOT / "tools" / "tsar-cli" / "sarif.py")
        sys.path.insert(0, str(emit.parent))
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

def cmd_init(args) -> int:
    """Bootstrap TSAR into an existing project."""
    target = Path(args.path).resolve()
    if not target.exists():
        print(f"Target does not exist: {target}")
        return 2
    if args.agent not in {"claude", "claude-code", "cursor", "copilot",
                          "windsurf", "windsurf-rc", "generic"}:
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

    # Vendor TSAR locally for offline operation.
    tsar_dir = target / ".tsar"
    if not tsar_dir.exists():
        tsar_dir.mkdir()
    shutil.copytree(SKILLS, tsar_dir / "skills", dirs_exist_ok=True)
    shutil.copytree(SCRIPTS, tsar_dir / "scripts", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "manifest.yaml", tsar_dir / "manifest.yaml")
    print(f"TSAR vendored at {tsar_dir}")

    # Install pre-commit hook.
    hooks = target / ".git" / "hooks"
    if hooks.exists():
        hook_dst = hooks / "pre-commit"
        hook_src = ROOT / "integrations" / "git-hooks" / "pre-commit"
        if not hook_dst.exists() or "TSAR" not in hook_dst.read_text():
            shutil.copyfile(hook_src, hook_dst)
            hook_dst.chmod(0o755)
            print(f"Pre-commit hook installed at {hook_dst}")
        else:
            print(f"Pre-commit hook already present at {hook_dst}")
    else:
        print("Not a git repository; skipping hook installation")

    # Write config for local resolution.
    (target / ".tsar" / "config.json").write_text(json.dumps({
        "manifest_version": "1.0.0",
        "agent": args.agent,
        "vendored": True,
    }, indent=2))
    print("TSAR init complete")
    return 0

def main() -> int:
    p = argparse.ArgumentParser(prog="tsar", description="TSAR security CLI")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("scan", help="run secret scanner and secure review")
    s.add_argument("path", nargs="?", default=".")
    s.add_argument("--format", choices=["text", "sarif"], default="text")
    s.add_argument("--output", default="tsar.sarif")
    s.set_defaults(func=cmd_scan)

    i = sub.add_parser("inventory", help="build cryptographic inventory (CBOM)")
    i.add_argument("path", nargs="?", default=".")
    i.set_defaults(func=cmd_inventory)

    l = sub.add_parser("lint", help="validate TSAR rules")
    l.set_defaults(func=cmd_lint)

    v = sub.add_parser("version", help="compare local and remote manifest version")
    v.set_defaults(func=cmd_check_version)

    t = sub.add_parser("threat-model", help="generate STRIDE threat model")
    t.add_argument("path")
    t.set_defaults(func=cmd_threat_model)

    ini = sub.add_parser("init", help="bootstrap TSAR into a project")
    ini.add_argument("path", nargs="?", default=".")
    ini.add_argument("--agent", required=True,
                     choices=["claude", "claude-code", "cursor", "copilot",
                              "windsurf", "windsurf-rc", "generic"])
    ini.set_defaults(func=cmd_init)

    args = p.parse_args()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
